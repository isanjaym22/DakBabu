"""Step 3 — Email Preview.

Shows how the first recipient's email will look with all placeholders
filled in.  Displays To, Subject, rendered Body, attachment info, and
recipient count.

Layout (from stitch_ui/step3_preview/screen.png):
    Preview
    This is how the first email will look…

    ┌──────────────────────────────────────────────────┐
    │  To:      priya@example.com                      │
    │  Subject: Thank you, Priya!                      │
    │  ┌──────────────────────────────────────────┐    │
    │  │  Dear Priya,                              │    │
    │  │                                           │    │
    │  │  Thank you for attending our seminar…     │    │
    │  │                                           │    │
    │  │  Best regards,                            │    │
    │  │  DakBabu Team                             │    │
    │  └──────────────────────────────────────────┘    │
    └──────────────────────────────────────────────────┘

    ┌─📎─ A personalized PDF will be attached ─────────┐
    └──────────────────────────────────────────────────┘

              Ready to send to 42 recipients

All visual values imported from src.ui.theme.  Zero business logic.
No direct core/ imports — data flows via app.py shared state.
"""

from __future__ import annotations

import customtkinter as ctk

from src.core import template_engine

from src.ui.theme import (
    COLOR_BACKGROUND,
    COLOR_INFO_BG,
    COLOR_INFO_BORDER,
    COLOR_INFO_TEXT,
    COLOR_ON_SURFACE,
    COLOR_ON_SURFACE_VARIANT,
    COLOR_OUTLINE,
    COLOR_OUTLINE_VARIANT,
    COLOR_SURFACE_CONTAINER_LOWEST,
    COLOR_SURFACE_CONTAINER_LOW,
    FONT_FAMILY,
    FONT_H2,
    FONT_BODY_LG,
    FONT_BODY_MD,
    FONT_LABEL_SM,
    FONT_LABEL_MD,
    RADIUS_CARD,
    RADIUS_DEFAULT,
    BORDER_WIDTH_DEFAULT,
    SPACING_CONTAINER_PADDING,
    SPACING_STACK_GAP,
)


# ---------------------------------------------------------------------------
# Constants local to this step
# ---------------------------------------------------------------------------
_PREVIEW_LABEL_FONT: tuple[str, int, str] = FONT_LABEL_MD
_PREVIEW_VALUE_FONT: tuple[str, int, str] = FONT_BODY_MD
_BODY_FONT: tuple[str, int, str] = FONT_BODY_MD
_RECIPIENT_FONT: tuple[str, int, str] = (FONT_FAMILY, 14, "bold")
_ATTACHMENT_ICON_FONT: tuple[str, int, str] = (FONT_FAMILY, 16, "normal")
_EMAIL_BADGE_FONT: tuple[str, int, str] = (FONT_FAMILY, 13, "bold")


class Step3Preview(ctk.CTkFrame):
    """Email preview step — shows the first recipient's personalized email.

    In Phase 3, static placeholder data is shown.  Phase 4 will call
    ``set_preview()`` to populate with real data from the template
    engine.

    Args:
        master: Parent widget (the content area in App).
    """

    def __init__(
        self,
        master: ctk.CTkBaseClass,
    ) -> None:
        super().__init__(
            master=master,
            fg_color=COLOR_BACKGROUND,
            corner_radius=0,
        )

        # Stretch
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Preview data (Phase 3 defaults)
        self._to_email: str = "priya@example.com"
        self._subject: str = "Thank you, Priya!"
        self._body: str = (
            "Dear Priya,\n\n"
            "Thank you for attending our seminar. We truly appreciate your "
            "presence and the insightful questions you shared during the "
            "session. It was a pleasure having you with us.\n\n"
            "As promised, please find your personalized participation "
            "certificate attached to this email.\n\n"
            "Best regards,\nDakBabu Team"
        )
        self._recipient_count: int = 42

        self._build()

    # ------------------------------------------------------------------
    # StepFrame protocol
    # ------------------------------------------------------------------

    def validate(self) -> bool:
        """Phase 3 placeholder — always allow."""
        return True

    def get_data(self) -> dict:
        """Return preview metadata."""
        return {
            "recipient_count": self._recipient_count,
        }

    def on_enter(self) -> None:
        """Called when this step becomes visible.

        Reads the first recipient from app state, replaces placeholders
        in the composed subject and body, and updates the preview card.
        """
        app = self._get_app()
        if app is None:
            return

        state = getattr(app, "state", {})

        # Gather recipients
        recipients = state.get("recipients", [])
        if not recipients:
            self._update_preview(
                to_email="—",
                subject="—",
                body="No recipients loaded yet.",
                recipient_count=0,
            )
            return

        first = recipients[0]

        # Build replacement data for the first recipient
        data = template_engine._build_replacement_data(first)

        # Read composed subject and body from step 2 state
        subject = state.get("subject", "")
        body = state.get("body_text", "")

        # Replace placeholders
        filled_subject = template_engine.replace_placeholders(subject, data)
        filled_body = template_engine.replace_placeholders(body, data)

        self._update_preview(
            to_email=first.email,
            subject=filled_subject,
            body=filled_body,
            recipient_count=len(recipients),
        )

    # ------------------------------------------------------------------
    # Public API — for Phase 4 integration
    # ------------------------------------------------------------------

    def _update_preview(
        self,
        to_email: str,
        subject: str,
        body: str,
        recipient_count: int,
    ) -> None:
        """Update the preview card with the given data.

        Args:
            to_email: First recipient's email address.
            subject: Personalized subject line.
            body: Personalized email body (plain text with newlines).
            recipient_count: Total number of recipients.
        """
        self._to_email = to_email
        self._subject = subject
        self._body = body
        self._recipient_count = recipient_count

        # Update displayed values
        self._to_value.configure(text=to_email)
        self._subject_value.configure(text=subject)
        self._body_text.configure(state="normal")
        self._body_text.delete("1.0", "end")
        self._body_text.insert("1.0", body)
        self._body_text.configure(state="disabled")
        self._count_label.configure(
            text=f"Ready to send to {recipient_count} recipients"
        )

    def _get_app(self) -> ctk.CTkBaseClass | None:
        """Traverse up to find the root App instance."""
        widget = self
        while widget is not None:
            if hasattr(widget, "state"):
                return widget  # type: ignore[return-value]
            widget = widget.master
        return None

    # ------------------------------------------------------------------
    # Private — build
    # ------------------------------------------------------------------

    def _build(self) -> None:
        """Assemble the preview layout."""
        scroll = ctk.CTkScrollableFrame(
            master=self,
            fg_color=COLOR_BACKGROUND,
            corner_radius=0,
        )
        scroll.grid(row=0, column=0, sticky="nsew")
        scroll.grid_columnconfigure(0, weight=1)

        # -- Page heading --
        heading = ctk.CTkLabel(
            master=scroll,
            text="Preview",
            font=FONT_H2,
            text_color=COLOR_ON_SURFACE,
            anchor="w",
        )
        heading.grid(row=0, column=0, sticky="w", pady=(SPACING_STACK_GAP, 0))

        subtitle = ctk.CTkLabel(
            master=scroll,
            text="This is how the first email will look…",
            font=FONT_BODY_MD,
            text_color=COLOR_ON_SURFACE_VARIANT,
            anchor="w",
        )
        subtitle.grid(row=1, column=0, sticky="w", pady=(4, 0))

        # -- Email preview card --
        card = ctk.CTkFrame(
            master=scroll,
            fg_color=COLOR_SURFACE_CONTAINER_LOWEST,
            corner_radius=RADIUS_CARD,
            border_width=BORDER_WIDTH_DEFAULT,
            border_color=COLOR_OUTLINE_VARIANT,
        )
        card.grid(
            row=2, column=0, sticky="ew",
            pady=(SPACING_STACK_GAP, 0),
        )
        card.grid_columnconfigure(0, weight=1)

        # -- To row --
        to_row = ctk.CTkFrame(
            master=card, fg_color="transparent", corner_radius=0,
        )
        to_row.pack(
            fill="x",
            padx=SPACING_CONTAINER_PADDING,
            pady=(SPACING_CONTAINER_PADDING, 0),
        )

        to_label = ctk.CTkLabel(
            master=to_row,
            text="To:",
            font=_PREVIEW_LABEL_FONT,
            text_color=COLOR_ON_SURFACE_VARIANT,
        )
        to_label.pack(side="left")

        # Email badge
        email_badge = ctk.CTkFrame(
            master=to_row,
            fg_color=COLOR_SURFACE_CONTAINER_LOW,
            corner_radius=RADIUS_DEFAULT,
            border_width=BORDER_WIDTH_DEFAULT,
            border_color=COLOR_OUTLINE_VARIANT,
        )
        email_badge.pack(side="left", padx=(12, 0))

        self._to_value = ctk.CTkLabel(
            master=email_badge,
            text=self._to_email,
            font=_EMAIL_BADGE_FONT,
            text_color=COLOR_ON_SURFACE,
        )
        self._to_value.pack(padx=10, pady=4)

        # -- Subject row --
        subj_row = ctk.CTkFrame(
            master=card, fg_color="transparent", corner_radius=0,
        )
        subj_row.pack(
            fill="x",
            padx=SPACING_CONTAINER_PADDING,
            pady=(SPACING_STACK_GAP, 0),
        )

        subj_label = ctk.CTkLabel(
            master=subj_row,
            text="Subject:",
            font=_PREVIEW_LABEL_FONT,
            text_color=COLOR_ON_SURFACE_VARIANT,
        )
        subj_label.pack(side="left")

        self._subject_value = ctk.CTkLabel(
            master=subj_row,
            text=self._subject,
            font=(FONT_FAMILY, 14, "bold"),
            text_color=COLOR_ON_SURFACE,
        )
        self._subject_value.pack(side="left", padx=(12, 0))

        # -- Body area (inside a bordered sub-card) --
        body_card = ctk.CTkFrame(
            master=card,
            fg_color=COLOR_SURFACE_CONTAINER_LOWEST,
            corner_radius=RADIUS_DEFAULT,
            border_width=BORDER_WIDTH_DEFAULT,
            border_color=COLOR_OUTLINE_VARIANT,
        )
        body_card.pack(
            fill="both", expand=True,
            padx=SPACING_CONTAINER_PADDING,
            pady=(SPACING_STACK_GAP, SPACING_CONTAINER_PADDING),
        )

        import tkinter as tk

        self._body_text = tk.Text(
            master=body_card,
            wrap="word",
            font=(FONT_FAMILY, 14),
            bg=COLOR_SURFACE_CONTAINER_LOWEST,
            fg=COLOR_ON_SURFACE,
            relief="flat",
            borderwidth=0,
            padx=20,
            pady=20,
            height=12,
            state="normal",
        )
        self._body_text.insert("1.0", self._body)
        self._body_text.configure(state="disabled")
        self._body_text.pack(fill="both", expand=True)

        # -- Attachment info bar --
        attach_bar = ctk.CTkFrame(
            master=scroll,
            fg_color=COLOR_INFO_BG,
            corner_radius=RADIUS_DEFAULT,
            border_width=0,
        )
        attach_bar.grid(
            row=3, column=0, sticky="ew",
            pady=(SPACING_STACK_GAP, 0),
        )

        attach_inner = ctk.CTkFrame(
            master=attach_bar,
            fg_color="transparent",
            corner_radius=0,
        )
        attach_inner.pack(fill="x", padx=16, pady=12)

        attach_icon = ctk.CTkLabel(
            master=attach_inner,
            text="📎",
            font=_ATTACHMENT_ICON_FONT,
            text_color=COLOR_INFO_TEXT,
        )
        attach_icon.pack(side="left")

        attach_text = ctk.CTkLabel(
            master=attach_inner,
            text="A personalized PDF will be attached to each email.",
            font=(FONT_FAMILY, 13, "bold"),
            text_color=COLOR_INFO_TEXT,
            anchor="w",
        )
        attach_text.pack(side="left", padx=(10, 0))

        # -- Recipient count --
        self._count_label = ctk.CTkLabel(
            master=scroll,
            text=f"Ready to send to {self._recipient_count} recipients",
            font=_RECIPIENT_FONT,
            text_color=COLOR_ON_SURFACE_VARIANT,
        )
        self._count_label.grid(
            row=4, column=0,
            pady=(SPACING_STACK_GAP, SPACING_STACK_GAP),
        )
