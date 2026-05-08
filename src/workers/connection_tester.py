"""Connection tester worker.

Runs the SMTP connection test in a background thread and posts the result
to a queue.Queue for the UI to consume via root.after() polling.

Queue message format:
    {
        "type": "connection_result",
        "success": bool,
        "error": str,   # empty string on success
    }

Usage:
    import queue
    import threading

    q = queue.Queue()
    stop_event = threading.Event()

    worker = ConnectionTester(
        email="you@gmail.com",
        password="app-password",
        result_queue=q,
        stop_event=stop_event,
    )
    worker.start()

    # In the UI:
    def _poll():
        try:
            msg = q.get_nowait()
            # handle msg
        except queue.Empty:
            root.after(100, _poll)
"""

from __future__ import annotations

import queue
import threading

from src.core import email_sender, smtp_config as smtp_config_module


class ConnectionTester(threading.Thread):
    """Background thread that tests SMTP credentials.

    Resolves the correct :class:`~src.core.models.SmtpConfig` from the
    email domain internally, so the UI step file has **zero** core imports.

    Calls ``src.core.email_sender.test_connection()`` and posts a single
    ``connection_result`` message to *result_queue* when done (or when
    cancelled via *stop_event*).

    Args:
        email: Sender email address.  The SMTP host/port are auto-detected
            from the domain (gmail.com, outlook.com, yahoo.com, etc.).
        password: App password (never written to disk).
        result_queue: Queue shared with the UI layer.  The worker only
            *puts* to this queue — never reads from it.
        stop_event: Caller sets this to signal the worker to abort.
            Because the SMTP call is blocking the event is checked
            *after* it returns; it prevents posting a stale result when
            the user has already cancelled.
    """

    def __init__(
        self,
        email: str,
        password: str,
        result_queue: "queue.Queue[dict]",
        stop_event: threading.Event,
    ) -> None:
        super().__init__(daemon=True, name="ConnectionTester")
        self._email = email
        self._password = password
        self._queue = result_queue
        self._stop_event = stop_event

    # ------------------------------------------------------------------
    # Thread entry point
    # ------------------------------------------------------------------

    def run(self) -> None:
        """Resolve SMTP config, run the connection test, post the result.

        If *stop_event* is set before the result is posted the message
        is discarded so the UI does not receive a stale result.
        """
        # Resolve config from email domain (pure lookup — no I/O)
        config = smtp_config_module.get_smtp_config(self._email)

        if config is None:
            success = False
            error = (
                "Email domain not recognised. "
                "Only Gmail, Outlook, and Yahoo are supported."
            )
        else:
            success, error = email_sender.test_connection(
                email=self._email,
                password=self._password,
                config=config,
            )

        # Respect cancellation — don't update the UI if the user
        # already navigated away or cancelled.
        if self._stop_event.is_set():
            return

        self._queue.put(
            {
                "type": "connection_result",
                "success": success,
                "error": error,
            }
        )
