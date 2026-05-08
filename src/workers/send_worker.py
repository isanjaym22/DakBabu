"""Send worker — batch email sending in a background thread.

Iterates through a list of Recipient objects, generating a personalized
.docx, converting it to PDF, and sending the email with the PDF attached.
Posts per-recipient progress updates and a final summary to a queue.Queue
for the UI to consume via root.after() polling.

Queue message formats:

    Progress (per-recipient):
        {
            "type": "progress",
            "index": int,           # position in the full recipients list
            "recipient": Recipient,
            "success": bool,
            "error": str,           # empty string on success
            "sent_count": int,      # running total of successful sends
            "total": int,           # total recipients being processed
        }

    Completion:
        {"type": "done", "sent": int, "failed": int}

    Stopped (user cancelled):
        {"type": "stopped", "sent": int, "remaining": int}

Usage:
    import queue
    import threading

    q = queue.Queue()
    stop_event = threading.Event()

    worker = SendWorker(
        recipients=recipients,
        template_path=Path("template.docx"),
        email="you@gmail.com",
        password="app-password",
        subject="Hello {{name}}",
        body_html="<p>Dear {{name}},</p>",
        result_queue=q,
        stop_event=stop_event,
    )
    worker.start()

    # Resume from index 5 (skip 0-4):
    worker = SendWorker(..., start_index=5)

    # Retry only failed indexes:
    worker = SendWorker(..., retry_indexes=[2, 7, 14])
"""

from __future__ import annotations

import queue
import tempfile
import threading
import time
from pathlib import Path

from src.core import email_sender, smtp_config as smtp_config_module
from src.core.models import Recipient, RecipientStatus
from src.core.pdf_converter import convert_docx_to_pdf_in_dir
from src.core.template_engine import (
    generate_personalized_docx,
    replace_placeholders,
)


class SendWorker(threading.Thread):
    """Background thread that sends personalized emails in batch.

    For each recipient the worker:
    1. Generates a personalized .docx from the template.
    2. Converts the .docx to PDF via docx2pdf.
    3. Sends the email with the PDF attached (fresh SMTP connection).
    4. Deletes temp files in a try/finally block.
    5. Posts a progress message to the result queue.

    Supports **resume** (via *start_index* — skips already-sent) and
    **retry** (via *retry_indexes* — only re-sends specific recipients).

    The *stop_event* is checked between every recipient so the user can
    cancel gracefully.

    Args:
        recipients: Full list of Recipient objects from the Excel file.
        template_path: Path to the .docx Word template.
        email: Sender email address.
        password: Sender app password (never written to disk).
        subject: Email subject line (may contain {{placeholders}}).
        body_html: Email body as HTML (may contain {{placeholders}}).
        result_queue: Thread-safe queue for posting status updates.
        stop_event: Set by the caller to request graceful stop.
        start_index: Index to resume from (skips 0..start_index-1).
            Ignored when *retry_indexes* is provided.
        retry_indexes: Specific recipient indexes to retry.
            When provided, *start_index* is ignored and only these
            indexes are processed.
    """

    def __init__(
        self,
        recipients: list[Recipient],
        template_path: Path,
        email: str,
        password: str,
        subject: str,
        body_html: str,
        result_queue: "queue.Queue[dict]",
        stop_event: threading.Event,
        start_index: int = 0,
        retry_indexes: list[int] | None = None,
    ) -> None:
        super().__init__(daemon=True, name="SendWorker")
        self._recipients = recipients
        self._template_path = template_path
        self._email = email
        self._password = password
        self._subject = subject
        self._body_html = body_html
        self._queue = result_queue
        self._stop_event = stop_event
        self._start_index = start_index
        self._retry_indexes = retry_indexes

    # ------------------------------------------------------------------
    # Thread entry point
    # ------------------------------------------------------------------

    def run(self) -> None:
        """Execute the batch send loop.

        Resolves SMTP config once, then iterates through the recipient
        list (respecting resume / retry parameters).  Each recipient
        is processed inside a temp directory that is cleaned up in a
        try/finally block.
        """
        # Resolve SMTP config from the sender's email domain
        config = smtp_config_module.get_smtp_config(self._email)

        if config is None:
            # Cannot proceed without SMTP config — post a single
            # failure for the first recipient and a done message.
            self._queue.put({
                "type": "done",
                "sent": 0,
                "failed": len(self._work_indexes()),
            })
            return

        work_indexes = self._work_indexes()
        total = len(work_indexes)
        sent_count = 0
        failed_count = 0

        for position, idx in enumerate(work_indexes):
            # ── Check stop signal between every recipient ────────
            if self._stop_event.is_set():
                remaining = total - position
                self._queue.put({
                    "type": "stopped",
                    "sent": sent_count,
                    "remaining": remaining,
                })
                return

            recipient = self._recipients[idx]
            success, error = self._process_recipient(recipient, config)

            if success:
                sent_count += 1
            else:
                failed_count += 1

            # ── Post progress update to queue ────────────────────
            self._queue.put({
                "type": "progress",
                "index": idx,
                "recipient": recipient,
                "success": success,
                "error": error,
                "sent_count": sent_count,
                "total": total,
            })

            # Small delay between emails to let the UI update smoothly
            # and be a polite SMTP client.
            if position < total - 1:
                time.sleep(0.3)

        # ── All done ─────────────────────────────────────────────
        self._queue.put({
            "type": "done",
            "sent": sent_count,
            "failed": failed_count,
        })

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _work_indexes(self) -> list[int]:
        """Determine which recipient indexes to process.

        - If *retry_indexes* is set, use those (filtered to valid range).
        - Otherwise, use range starting from *start_index*.

        Returns:
            Sorted list of integer indexes into self._recipients.
        """
        count = len(self._recipients)

        if self._retry_indexes is not None:
            # Filter to valid indexes only
            return sorted(i for i in self._retry_indexes if 0 <= i < count)

        # Resume: skip indexes before start_index
        start = max(0, min(self._start_index, count))
        return list(range(start, count))

    def _process_recipient(
        self,
        recipient: Recipient,
        config,
    ) -> tuple[bool, str]:
        """Process a single recipient: docx → PDF → send → cleanup.

        All temp files are created inside a TemporaryDirectory and
        cleaned up in a try/finally block so files are never left behind.

        Args:
            recipient: The recipient to send to.
            config: Resolved SmtpConfig for the sender's email domain.

        Returns:
            Tuple of (success, error_message).
        """
        temp_dir = None
        try:
            temp_dir = tempfile.TemporaryDirectory()
            temp_path = Path(temp_dir.name)

            # 1. Generate personalized .docx
            docx_out = temp_path / f"{recipient.email}.docx"
            ok, err = generate_personalized_docx(
                self._template_path, recipient, docx_out
            )
            if not ok:
                return False, err

            # 2. Convert .docx → PDF
            ok, err, pdf_path = convert_docx_to_pdf_in_dir(
                docx_out, temp_path
            )
            if not ok or pdf_path is None:
                return False, err

            # 3. Personalize subject and body for this recipient
            data = _build_replacement_data(recipient)
            personalized_subject = replace_placeholders(
                self._subject, data
            )
            personalized_body = replace_placeholders(
                self._body_html, data
            )

            # 4. Send email (fresh SMTP connection per email)
            result = email_sender.send_email(
                email=self._email,
                password=self._password,
                config=config,
                recipient=recipient,
                subject=personalized_subject,
                body_html=personalized_body,
                pdf_path=pdf_path,
            )

            return result.success, result.error_message

        except Exception as exc:
            return False, f"Failed to process email for {recipient.email}: {exc}"

        finally:
            # Always clean up temp files
            if temp_dir is not None:
                try:
                    temp_dir.cleanup()
                except Exception:
                    pass  # Best-effort cleanup — don't crash the worker


def _build_replacement_data(recipient: Recipient) -> dict[str, str]:
    """Build a flat placeholder→value dict from a Recipient.

    Mirrors ``template_engine._build_replacement_data`` but is kept
    local to avoid relying on a private function.

    Args:
        recipient: The recipient to extract data from.

    Returns:
        Dict mapping lowercase placeholder names to string values.
    """
    data: dict[str, str] = {}
    if recipient.name:
        data["name"] = recipient.name
    data.update(recipient.extra_fields)
    return data
