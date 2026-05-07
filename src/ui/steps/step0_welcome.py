"""Step 0 — Welcome & System Check.

Shows the DakBabu app name, a brief instruction summary, and a Word
detection status area.  The step exposes a ``set_word_status`` method
so app.py (via workers in Phase 4) can update the UI when detection
completes.

Layout (centered card):
    ┌──────────────────────────────────────────────────┐
    │           ✉  DakBabu                             │
    │      Bulk Personalized Email Sender              │
    │                                                  │
    │  Send personalized emails with PDF attachments   │
    │  to multiple recipients in just a few steps.     │
    │                                                  │
    │  ┌────────────────────────────────────────────┐  │
    │  │ ℹ  Checking for Microsoft Word…           │  │
    │  └────────────────────────────────────────────┘  │
    │                                                  │
    │            [ Get Started → ]                     │
    └──────────────────────────────────────────────────┘

All visual values imported from src.ui.theme.  Zero business logic.
"""

from __future__ import annotations

import customtkinter as ctk

from src.ui.theme import (
    COLOR_BACKGROUND,
    COLOR_ON_SURFACE,
    COLOR_ON_SURFACE_VARIANT,
    COLOR_OUTLINE_VARIANT,
    COLOR_PRIMARY_CONTAINER,
    COLOR_PRIMARY_HOVER,
    COLOR_ON_PRIMARY,
    COLOR_SURFACE_CONTAINER_LOWEST,
    FONT_FAMILY,
    FONT_H1,
    FONT_H3,
    FONT_BODY_LG,
    FONT_BODY_MD,
    RADIUS_CARD,
    RADIUS_PILL,
    BORDER_WIDTH_DEFAULT,
    SPACING_CONTAINER_PADDING,
    SPACING_STACK_GAP,
    ICON_MAIL,
    ICON_ARROW_RIGHT,
)
from src.ui.components.info_box import InfoBox
from src.ui.components.status_badge import StatusBadge, BadgeVariant


# ---------------------------------------------------------------------------
# Constants local to this step
# ---------------------------------------------------------------------------
_CARD_MAX_WIDTH: int = 560
_TITLE_ICON_FONT: tuple[str, int, str] = (FONT_FAMILY, 36, "normal")
_GET_STARTED_WIDTH: int = 160
_GET_STARTED_HEIGHT: int = 40
_GET_STARTED_FONT: tuple[str, int, str] = (FONT_FAMILY, 14, "bold")


class Step0Welcome(ctk.CTkFrame):
    """Welcome screen with Word detection status.

    The step renders immediately in a "checking" state.  Once app.py
    calls ``set_word_status()`` the info box updates to reflect the
    result.  The "Get Started" button calls the ``on_proceed`` callback
    so app.py can navigate forward.

    Args:
        master: Parent widget (the content area in App).
        on_proceed: Callback invoked when "Get Started" is clicked.
    """

    def __init__(
        self,
        master: ctk.CTkBaseClass,
        on_proceed: callable | None = None,
    ) -> None:
        super().__init__(
            master=master,
            fg_color=COLOR_BACKGROUND,
            corner_radius=0,
        )

        self._on_proceed = on_proceed
        self._word_detected: bool | None = None  # None = still checking

        # Stretch content area
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._build()

    # ------------------------------------------------------------------
    # StepFrame protocol
    # ------------------------------------------------------------------

    def validate(self) -> bool:
        """Allow proceeding once Word status is known (or always in Phase 3)."""
        return True

    def get_data(self) -> dict:
        """Return Word detection result."""
        return {"word_detected": self._word_detected}

    def on_enter(self) -> None:
        """Called when this step becomes visible."""
        pass

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set_word_status(
        self,
        detected: bool,
        version: str = "",
    ) -> None:
        """Update the Word detection display.

        Args:
            detected: Whether MS Word was found.
            version: Word version string (e.g. "16.0"), shown on success.
        """
        self._word_detected = detected

        if detected:
            self._info_box.set_text(
                f"Microsoft Word detected{f' (v{version})' if version else ''}. "
                "You're all set to convert documents to PDF."
            )
            # Show success badge
            if self._status_badge is not None:
                self._status_badge.destroy()
            self._status_badge = StatusBadge(
                master=self._badge_frame,
                variant=BadgeVariant.CONNECTION_OK,
                text="Word is ready",
            )
            self._status_badge.pack(pady=(4, 0))
        else:
            self._info_box.set_text(
                "Microsoft Word was not found. DakBabu needs Word "
                "to convert documents to PDF. Please install Word "
                "and restart the app."
            )
            if self._status_badge is not None:
                self._status_badge.destroy()
            self._status_badge = StatusBadge(
                master=self._badge_frame,
                variant=BadgeVariant.FAILED,
                text="Word not found",
            )
            self._status_badge.pack(pady=(4, 0))

    # ------------------------------------------------------------------
    # Private — build
    # ------------------------------------------------------------------

    def _build(self) -> None:
        """Assemble the welcome card layout."""
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

        # -- Mail icon --
        icon_label = ctk.CTkLabel(
            master=inner,
            text=ICON_MAIL,
            font=_TITLE_ICON_FONT,
            text_color=COLOR_PRIMARY_CONTAINER,
        )
        icon_label.pack(pady=(0, 4))

        # -- App title --
        title = ctk.CTkLabel(
            master=inner,
            text="DakBabu",
            font=FONT_H1,
            text_color=COLOR_ON_SURFACE,
        )
        title.pack()

        # -- Subtitle --
        subtitle = ctk.CTkLabel(
            master=inner,
            text="Bulk Personalized Email Sender",
            font=FONT_H3,
            text_color=COLOR_ON_SURFACE_VARIANT,
        )
        subtitle.pack(pady=(4, 0))

        # -- Description --
        desc = ctk.CTkLabel(
            master=inner,
            text=(
                "Send personalized emails with unique PDF attachments\n"
                "to multiple recipients — in just a few steps."
            ),
            font=FONT_BODY_LG,
            text_color=COLOR_ON_SURFACE_VARIANT,
            justify="center",
        )
        desc.pack(pady=(SPACING_STACK_GAP, 0))

        # -- Info box (Word status) --
        self._info_box = InfoBox(
            master=inner,
            text="Checking for Microsoft Word…",
        )
        self._info_box.pack(fill="x", pady=(SPACING_STACK_GAP, 0))

        # -- Badge area --
        self._badge_frame = ctk.CTkFrame(
            master=inner,
            fg_color="transparent",
            corner_radius=0,
        )
        self._badge_frame.pack(pady=(4, 0))
        self._status_badge: StatusBadge | None = None

        # -- Get Started button --
        get_started_btn = ctk.CTkButton(
            master=inner,
            text=f"Get Started  {ICON_ARROW_RIGHT}",
            font=_GET_STARTED_FONT,
            width=_GET_STARTED_WIDTH,
            height=_GET_STARTED_HEIGHT,
            corner_radius=RADIUS_PILL,
            fg_color=COLOR_PRIMARY_CONTAINER,
            hover_color=COLOR_PRIMARY_HOVER,
            text_color=COLOR_ON_PRIMARY,
            border_width=0,
            command=self._handle_proceed,
        )
        get_started_btn.pack(pady=(SPACING_STACK_GAP + 8, 0))

    # ------------------------------------------------------------------
    # Private — handlers
    # ------------------------------------------------------------------

    def _handle_proceed(self) -> None:
        """Forward navigation when 'Get Started' is clicked."""
        if self._on_proceed is not None:
            self._on_proceed()
