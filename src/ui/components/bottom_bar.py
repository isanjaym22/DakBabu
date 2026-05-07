"""Bottom navigation bar — Back / Next footer with pill-shaped buttons.

Layout (from Stitch step1_credentials/screen.png + code.html):
    ┌──────────────────────────────────────────────────────────────┐
    │  ← BACK                                          NEXT →    │
    └──────────────────────────────────────────────────────────────┘

- Fixed height (56 px), white background, 1 px top border.
- Back button: left-aligned, pill, outline style.
    - Enabled: dark text + gray border.
    - Disabled: light text + light border, not clickable.
- Next button: right-aligned, pill, filled primary blue.
    - Enabled: blue bg + white text.
    - Disabled: light text + light border, not clickable.
- Both buttons: uppercase label-sm text with arrow icons.

All visual values imported from src.ui.theme.  Zero business logic.
"""

from __future__ import annotations

from typing import Callable

import customtkinter as ctk

from src.ui.theme import (
    COLOR_NAVBAR_BG,
    COLOR_NAVBAR_BORDER,
    COLOR_PRIMARY_CONTAINER,
    COLOR_PRIMARY_HOVER,
    COLOR_ON_PRIMARY,
    COLOR_BUTTON_SECONDARY_TEXT,
    COLOR_BUTTON_SECONDARY_BORDER,
    COLOR_BUTTON_DISABLED_TEXT,
    COLOR_BUTTON_DISABLED_BORDER,
    FONT_FAMILY,
    RADIUS_PILL,
    BORDER_WIDTH_DEFAULT,
    ICON_ARROW_LEFT,
    ICON_ARROW_RIGHT,
)

# ---------------------------------------------------------------------------
# Constants local to this component
# ---------------------------------------------------------------------------
_BAR_HEIGHT: int = 56
_BUTTON_FONT: tuple[str, int, str] = (FONT_FAMILY, 12, "bold")
_BUTTON_HEIGHT: int = 36
_BACK_WIDTH: int = 110
_NEXT_WIDTH: int = 120
_BAR_PADX: int = 40  # px-10 from Stitch HTML (40px)


class BottomBar(ctk.CTkFrame):
    """Back / Next footer bar with pill-shaped buttons.

    The bar sits at the bottom of the App window and controls wizard
    navigation.  Button states (enabled / disabled) are managed by
    the parent ``App`` via ``set_back_enabled`` / ``set_next_enabled``.

    Args:
        master: Parent widget.
        on_back: Callback invoked when the Back button is clicked.
        on_next: Callback invoked when the Next button is clicked.
    """

    def __init__(
        self,
        master: ctk.CTkBaseClass,
        on_back: Callable[[], None] | None = None,
        on_next: Callable[[], None] | None = None,
    ) -> None:
        super().__init__(
            master=master,
            fg_color=COLOR_NAVBAR_BG,
            corner_radius=0,
            height=_BAR_HEIGHT,
            border_width=0,
        )
        self.grid_propagate(False)

        self._on_back = on_back
        self._on_next = on_next

        # -- Layout: left spacer | center stretch | right spacer -----------
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0)
        self.grid_rowconfigure(0, weight=1)

        # -- Top border line -----------------------------------------------
        self._build_top_border()

        # -- Back button (left) --------------------------------------------
        self._back_btn = ctk.CTkButton(
            master=self,
            text=f"{ICON_ARROW_LEFT}  BACK",
            font=_BUTTON_FONT,
            width=_BACK_WIDTH,
            height=_BUTTON_HEIGHT,
            corner_radius=RADIUS_PILL,
            fg_color=COLOR_NAVBAR_BG,
            hover_color=COLOR_BUTTON_DISABLED_BORDER,
            text_color=COLOR_BUTTON_SECONDARY_TEXT,
            border_width=BORDER_WIDTH_DEFAULT,
            border_color=COLOR_BUTTON_SECONDARY_BORDER,
            command=self._handle_back,
        )
        self._back_btn.grid(
            row=0, column=0, sticky="w", padx=(_BAR_PADX, 0),
        )

        # -- Next button (right) -------------------------------------------
        self._next_btn = ctk.CTkButton(
            master=self,
            text=f"NEXT  {ICON_ARROW_RIGHT}",
            font=_BUTTON_FONT,
            width=_NEXT_WIDTH,
            height=_BUTTON_HEIGHT,
            corner_radius=RADIUS_PILL,
            fg_color=COLOR_PRIMARY_CONTAINER,
            hover_color=COLOR_PRIMARY_HOVER,
            text_color=COLOR_ON_PRIMARY,
            border_width=0,
            command=self._handle_next,
        )
        self._next_btn.grid(
            row=0, column=2, sticky="e", padx=(0, _BAR_PADX),
        )

        # -- Start with Back disabled (first step) -------------------------
        self.set_back_enabled(False)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set_back_enabled(self, enabled: bool) -> None:
        """Enable or disable the Back button.

        Disabled state: faded text and lighter border, matching the
        Stitch "inactive" style.

        Args:
            enabled: True to enable, False to disable (gray out).
        """
        if enabled:
            self._back_btn.configure(
                state="normal",
                text_color=COLOR_BUTTON_SECONDARY_TEXT,
                border_color=COLOR_BUTTON_SECONDARY_BORDER,
            )
        else:
            self._back_btn.configure(
                state="disabled",
                text_color=COLOR_BUTTON_DISABLED_TEXT,
                border_color=COLOR_BUTTON_DISABLED_BORDER,
            )

    def set_next_enabled(self, enabled: bool) -> None:
        """Enable or disable the Next button.

        Disabled state: outline style with faded text, matching the
        Stitch inactive button pattern.

        Args:
            enabled: True to enable (filled blue), False to disable.
        """
        if enabled:
            self._next_btn.configure(
                state="normal",
                fg_color=COLOR_PRIMARY_CONTAINER,
                text_color=COLOR_ON_PRIMARY,
                border_width=0,
            )
        else:
            self._next_btn.configure(
                state="disabled",
                fg_color=COLOR_NAVBAR_BG,
                text_color=COLOR_BUTTON_DISABLED_TEXT,
                border_width=BORDER_WIDTH_DEFAULT,
                border_color=COLOR_BUTTON_DISABLED_BORDER,
            )

    def set_next_text(self, text: str) -> None:
        """Change the Next button label.

        Useful for the final step where "Next" becomes "Start Sending".

        Args:
            text: New button label (arrow icon will be appended).
        """
        self._next_btn.configure(text=f"{text}  {ICON_ARROW_RIGHT}")

    # ------------------------------------------------------------------
    # Private — handlers
    # ------------------------------------------------------------------

    def _handle_back(self) -> None:
        """Invoke the on_back callback if provided."""
        if self._on_back is not None:
            self._on_back()

    def _handle_next(self) -> None:
        """Invoke the on_next callback if provided."""
        if self._on_next is not None:
            self._on_next()

    def _build_top_border(self) -> None:
        """Draw a 1 px border line at the top of the BottomBar."""
        border = ctk.CTkFrame(
            master=self,
            fg_color=COLOR_NAVBAR_BORDER,
            height=BORDER_WIDTH_DEFAULT,
            corner_radius=0,
        )
        border.place(relx=0, rely=0, anchor="nw", relwidth=1.0)
