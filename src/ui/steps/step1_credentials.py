"""Step 1 — Email Credentials.

Centered card with email input, masked password input (with toggle),
an info box about App Passwords, a Test Connection button, and a
success/failure status badge.

Layout (from stitch_ui/step1_credentials/screen.png):
    ┌──────────────────────────────────────────────────┐
    │  Email Credentials                               │
    │  Enter the Gmail or Outlook account that will    │
    │  send the emails.                                │
    │                                                  │
    │  SENDER EMAIL ADDRESS                            │
    │  ┌──────────────────────────────────────────┐    │
    │  │  you@gmail.com                           │    │
    │  └──────────────────────────────────────────┘    │
    │                                                  │
    │  APP PASSWORD                                    │
    │  ┌──────────────────────────────────────┐ 👁    │
    │  │  XXXX XXXX XXXX XXXX                 │        │
    │  └──────────────────────────────────────┘        │
    │                                                  │
    │  ┌─ℹ─ Use an App Password, not your ─────┐      │
    │  │     regular password.                  │      │
    │  └────────────────────────────────────────┘      │
    │                                                  │
    │          [ Test Connection ]                      │
    │        ✓ Connection successful!                   │
    └──────────────────────────────────────────────────┘

Thread safety:
    - ConnectionTester runs in a daemon background thread.
    - Results flow through queue.Queue → root.after(100) poll.
    - No tkinter calls are ever made from the worker thread.

All visual values imported from src.ui.theme.  Zero business logic.
No direct core/ imports — all core calls go through src.workers.
"""

from __future__ import annotations

import queue
import threading

import customtkinter as ctk

from src.ui.theme import (
    COLOR_BACKGROUND,
    COLOR_ON_SURFACE,
    COLOR_ON_SURFACE_VARIANT,
    COLOR_OUTLINE,
    COLOR_OUTLINE_VARIANT,
    COLOR_PRIMARY_CONTAINER,
    COLOR_PRIMARY_HOVER,
    COLOR_ON_PRIMARY,
    COLOR_SURFACE_CONTAINER_LOWEST,
    COLOR_BUTTON_SECONDARY_TEXT,
    COLOR_BUTTON_SECONDARY_BORDER,
    FONT_FAMILY,
    FONT_H2,
    FONT_BODY_MD,
    FONT_LABEL_SM,
    RADIUS_CARD,
    RADIUS_INPUT,
    RADIUS_PILL,
    BORDER_WIDTH_DEFAULT,
    BORDER_WIDTH_FOCUS,
    SPACING_CONTAINER_PADDING,
    SPACING_STACK_GAP,
    ICON_EYE_OPEN,
    ICON_EYE_CLOSED,
)
from src.ui.components.info_box import InfoBox
from src.ui.components.status_badge import StatusBadge, BadgeVariant
from src.workers.connection_tester import ConnectionTester


# ---------------------------------------------------------------------------
# Constants local to this step
# ---------------------------------------------------------------------------
_CARD_MAX_WIDTH: int = 480
_INPUT_HEIGHT: int = 42
_LABEL_FONT: tuple[str, int, str] = FONT_LABEL_SM
_INPUT_FONT: tuple[str, int, str] = FONT_BODY_MD
_TEST_BTN_WIDTH: int = 160
_TEST_BTN_HEIGHT: int = 38
_TEST_BTN_FONT: tuple[str, int, str] = (FONT_FAMILY, 13, "bold")
_TOGGLE_BTN_SIZE: int = 32
_POLL_INTERVAL_MS: int = 100


class Step1Credentials(ctk.CTkFrame):
    """Credentials entry step — email, app password, test connection.

    Exposes ``get_data()`` returning ``{email, password}`` and a
    ``set_connection_result()`` method for Phase 4 worker integration.

    Args:
        master: Parent widget (the content area in App).
        on_connection_success: Optional callback fired when the connection
            test passes — App can use this to unlock the Next button.
    """

    def __init__(
        self,
        master: ctk.CTkBaseClass,
        on_connection_success: "callable | None" = None,
    ) -> None:
        super().__init__(
            master=master,
            fg_color=COLOR_BACKGROUND,
            corner_radius=0,
        )

        self._connection_tested: bool = False
        self._password_visible: bool = False
        self._on_connection_success = on_connection_success

        # Worker state — recreated for each test attempt
        self._result_queue: queue.Queue[dict] = queue.Queue()
        self._stop_event: threading.Event = threading.Event()
        self._worker: ConnectionTester | None = None

        # Stretch content area
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._build()

    # ------------------------------------------------------------------
    # StepFrame protocol
    # ------------------------------------------------------------------

    def validate(self) -> bool:
        """Allow proceeding only after a successful connection test."""
        return self._connection_tested

    def get_data(self) -> dict:
        """Return current email and password values."""
        return {
            "email": self._email_entry.get().strip(),
            "password": self._password_entry.get(),
        }

    def on_enter(self) -> None:
        """Called when this step becomes visible."""
        pass

    # ------------------------------------------------------------------
    # Public API — for worker integration and external callers
    # ------------------------------------------------------------------

    def set_connection_result(
        self,
        success: bool,
        error_message: str = "",
    ) -> None:
        """Display the result of a connection test.

        Args:
            success: Whether the SMTP test succeeded.
            error_message: Friendly error description on failure.
        """
        self._connection_tested = success

        # Clear previous badge
        for child in self._badge_frame.winfo_children():
            child.destroy()

        if success:
            badge = StatusBadge(
                master=self._badge_frame,
                variant=BadgeVariant.CONNECTION_OK,
            )
            # Notify app so it can enable the Next button
            if self._on_connection_success is not None:
                self._on_connection_success()
        else:
            badge = StatusBadge(
                master=self._badge_frame,
                variant=BadgeVariant.FAILED,
                text=error_message or "Connection failed",
            )
        badge.pack(pady=(8, 0))

        # Re-enable button
        self._test_btn.configure(
            state="normal",
            text="Test Connection",
        )

    def set_testing(self) -> None:
        """Show a 'testing' state on the button while worker runs."""
        self._test_btn.configure(
            state="disabled",
            text="Testing…",
        )
        # Clear previous badge
        for child in self._badge_frame.winfo_children():
            child.destroy()

        badge = StatusBadge(
            master=self._badge_frame,
            variant=BadgeVariant.SENDING,
            text="Connecting…",
        )
        badge.pack(pady=(8, 0))

    # ------------------------------------------------------------------
    # Private — build
    # ------------------------------------------------------------------

    def _build(self) -> None:
        """Assemble the credentials card layout."""
        # Outer centering wrapper
        center = ctk.CTkFrame(
            master=self,
            fg_color="transparent",
            corner_radius=0,
        )
        center.grid(row=0, column=0)

        # Card
        card = ctk.CTkFrame(
            master=center,
            fg_color=COLOR_SURFACE_CONTAINER_LOWEST,
            corner_radius=RADIUS_CARD,
            border_width=BORDER_WIDTH_DEFAULT,
            border_color=COLOR_OUTLINE_VARIANT,
            width=_CARD_MAX_WIDTH,
        )
        card.pack(padx=SPACING_CONTAINER_PADDING, pady=SPACING_CONTAINER_PADDING)

        inner = ctk.CTkFrame(master=card, fg_color="transparent", corner_radius=0)
        inner.pack(
            fill="x",
            padx=SPACING_CONTAINER_PADDING,
            pady=SPACING_CONTAINER_PADDING,
        )

        # -- Heading --
        heading = ctk.CTkLabel(
            master=inner,
            text="Email Credentials",
            font=FONT_H2,
            text_color=COLOR_ON_SURFACE,
            anchor="w",
        )
        heading.pack(fill="x")

        # -- Subtitle --
        subtitle = ctk.CTkLabel(
            master=inner,
            text="Enter the Gmail or Outlook account that will send the emails.",
            font=FONT_BODY_MD,
            text_color=COLOR_ON_SURFACE_VARIANT,
            anchor="w",
            wraplength=_CARD_MAX_WIDTH - 2 * SPACING_CONTAINER_PADDING,
            justify="left",
        )
        subtitle.pack(fill="x", pady=(4, 0))

        # -- Email label --
        email_label = ctk.CTkLabel(
            master=inner,
            text="SENDER EMAIL ADDRESS",
            font=_LABEL_FONT,
            text_color=COLOR_OUTLINE,
            anchor="w",
        )
        email_label.pack(fill="x", pady=(SPACING_STACK_GAP + 4, 0))

        # -- Email entry --
        self._email_entry = ctk.CTkEntry(
            master=inner,
            placeholder_text="you@gmail.com",
            font=_INPUT_FONT,
            height=_INPUT_HEIGHT,
            corner_radius=RADIUS_INPUT,
            border_width=BORDER_WIDTH_DEFAULT,
            border_color=COLOR_OUTLINE_VARIANT,
            fg_color=COLOR_SURFACE_CONTAINER_LOWEST,
            text_color=COLOR_ON_SURFACE,
        )
        self._email_entry.pack(fill="x", pady=(6, 0))

        # -- Password label --
        pw_label = ctk.CTkLabel(
            master=inner,
            text="APP PASSWORD",
            font=_LABEL_FONT,
            text_color=COLOR_OUTLINE,
            anchor="w",
        )
        pw_label.pack(fill="x", pady=(SPACING_STACK_GAP, 0))

        # -- Password row (entry + toggle) --
        pw_row = ctk.CTkFrame(master=inner, fg_color="transparent", corner_radius=0)
        pw_row.pack(fill="x", pady=(6, 0))
        pw_row.grid_columnconfigure(0, weight=1)
        pw_row.grid_columnconfigure(1, weight=0)

        self._password_entry = ctk.CTkEntry(
            master=pw_row,
            placeholder_text="XXXX XXXX XXXX XXXX",
            font=_INPUT_FONT,
            height=_INPUT_HEIGHT,
            corner_radius=RADIUS_INPUT,
            border_width=BORDER_WIDTH_DEFAULT,
            border_color=COLOR_OUTLINE_VARIANT,
            fg_color=COLOR_SURFACE_CONTAINER_LOWEST,
            text_color=COLOR_ON_SURFACE,
            show="•",
        )
        self._password_entry.grid(row=0, column=0, sticky="ew")

        self._toggle_btn = ctk.CTkButton(
            master=pw_row,
            text=ICON_EYE_CLOSED,
            font=(FONT_FAMILY, 16, "normal"),
            width=_TOGGLE_BTN_SIZE,
            height=_TOGGLE_BTN_SIZE,
            corner_radius=4,
            fg_color="transparent",
            hover_color=COLOR_OUTLINE_VARIANT,
            text_color=COLOR_OUTLINE,
            border_width=0,
            command=self._toggle_password_visibility,
        )
        self._toggle_btn.grid(row=0, column=1, padx=(6, 0))

        # -- Info box --
        info = InfoBox(
            master=inner,
            text="Use an App Password, not your regular password.",
        )
        info.pack(fill="x", pady=(SPACING_STACK_GAP, 0))

        # -- Test Connection button (centered) --
        btn_frame = ctk.CTkFrame(master=inner, fg_color="transparent", corner_radius=0)
        btn_frame.pack(pady=(SPACING_STACK_GAP + 4, 0))

        self._test_btn = ctk.CTkButton(
            master=btn_frame,
            text="Test Connection",
            font=_TEST_BTN_FONT,
            width=_TEST_BTN_WIDTH,
            height=_TEST_BTN_HEIGHT,
            corner_radius=RADIUS_PILL,
            fg_color=COLOR_SURFACE_CONTAINER_LOWEST,
            hover_color=COLOR_OUTLINE_VARIANT,
            text_color=COLOR_BUTTON_SECONDARY_TEXT,
            border_width=BORDER_WIDTH_DEFAULT,
            border_color=COLOR_BUTTON_SECONDARY_BORDER,
            command=self._handle_test,
        )
        self._test_btn.pack()

        # -- Badge area (connection result) --
        self._badge_frame = ctk.CTkFrame(
            master=inner,
            fg_color="transparent",
            corner_radius=0,
        )
        self._badge_frame.pack(pady=(0, 0))

    # ------------------------------------------------------------------
    # Private — handlers
    # ------------------------------------------------------------------

    def _toggle_password_visibility(self) -> None:
        """Toggle password masking on/off."""
        self._password_visible = not self._password_visible
        if self._password_visible:
            self._password_entry.configure(show="")
            self._toggle_btn.configure(text=ICON_EYE_OPEN)
        else:
            self._password_entry.configure(show="•")
            self._toggle_btn.configure(text=ICON_EYE_CLOSED)

    def _handle_test(self) -> None:
        """Handle Test Connection click.

        Cancels any in-flight test, starts a fresh ConnectionTester
        background thread, updates the button to 'testing' state, and
        begins polling the result queue with root.after().
        """
        email = self._email_entry.get().strip()
        password = self._password_entry.get()

        if not email or not password:
            # Show a friendly error badge immediately — no need for a thread
            self.set_connection_result(
                success=False,
                error_message="Please enter your email address and App Password.",
            )
            return

        # Cancel any previous in-flight test
        self._stop_event.set()

        # Fresh stop event and queue for this attempt
        self._stop_event = threading.Event()
        self._result_queue = queue.Queue()

        # Update UI to show 'testing' state
        self.set_testing()

        # Launch background worker — never call tkinter from inside it
        self._worker = ConnectionTester(
            email=email,
            password=password,
            result_queue=self._result_queue,
            stop_event=self._stop_event,
        )
        self._worker.start()

        # Begin polling — all UI updates happen here, on the main thread
        self.after(_POLL_INTERVAL_MS, self._poll_queue)

    def _poll_queue(self) -> None:
        """Poll the result queue and update the UI when a message arrives.

        Called repeatedly via root.after() until a result is received.
        Safe to call from the main thread only.
        """
        try:
            msg = self._result_queue.get_nowait()
        except queue.Empty:
            # No result yet — reschedule and keep waiting
            self.after(_POLL_INTERVAL_MS, self._poll_queue)
            return

        if msg.get("type") == "connection_result":
            self.set_connection_result(
                success=msg["success"],
                error_message=msg.get("error", ""),
            )
