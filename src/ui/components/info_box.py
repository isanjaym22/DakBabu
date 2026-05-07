"""Blue info callout box with left accent border and icon.

Layout (from Stitch step1_credentials/code.html):
    ┌────┬──────────────────────────────────────────────┐
    │ ▌  │  ℹ  Use an App Password, not your regular   │
    │ ▌  │     password.                                │
    └────┴──────────────────────────────────────────────┘

- Blue-50 background (#EFF6FF).
- 4 px left border in blue-600 (#2563EB).
- Info icon (ℹ) in blue-600.
- Text in blue-800 (#1E40AF), 13 px medium.
- Rounded-right corners (8 px).

All visual values imported from src.ui.theme.  Zero business logic.
"""

from __future__ import annotations

import customtkinter as ctk

from src.ui.theme import (
    COLOR_INFO_BG,
    COLOR_INFO_BORDER,
    COLOR_INFO_TEXT,
    COLOR_INFO_ICON,
    FONT_FAMILY,
    ICON_INFO,
    RADIUS_DEFAULT,
)

# ---------------------------------------------------------------------------
# Constants local to this component
# ---------------------------------------------------------------------------
_LEFT_BORDER_WIDTH: int = 4
_PADDING_X: int = 16
_PADDING_Y: int = 12
_ICON_FONT: tuple[str, int, str] = (FONT_FAMILY, 14, "normal")
_TEXT_FONT: tuple[str, int, str] = (FONT_FAMILY, 13, "bold")
_ICON_GAP: int = 10


class InfoBox(ctk.CTkFrame):
    """Blue info callout with a left accent border and ℹ icon.

    Matches the Stitch ``step1_credentials`` info-box design exactly:
    blue-50 background, 4 px blue-600 left border, ℹ icon, blue-800 text.

    Args:
        master: Parent widget.
        text: The informational message to display.
    """

    def __init__(
        self,
        master: ctk.CTkBaseClass,
        text: str = "",
    ) -> None:
        super().__init__(
            master=master,
            fg_color=COLOR_INFO_BG,
            corner_radius=RADIUS_DEFAULT,
            border_width=0,
        )

        self._text = text

        # -- Internal layout -----------------------------------------------
        # We fake the 4 px left border by placing a thin coloured frame
        # on the left edge, because CTkFrame's border_width draws evenly
        # on all sides.
        self._build()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set_text(self, text: str) -> None:
        """Update the displayed message.

        Args:
            text: New message string.
        """
        self._text = text
        self._label.configure(text=text)

    # ------------------------------------------------------------------
    # Private — build
    # ------------------------------------------------------------------

    def _build(self) -> None:
        """Assemble the left-border accent, icon, and text label."""
        # Left accent bar — overlaid on the left edge
        accent = ctk.CTkFrame(
            master=self,
            fg_color=COLOR_INFO_BORDER,
            width=_LEFT_BORDER_WIDTH,
            corner_radius=2,
        )
        accent.place(relx=0, rely=0, anchor="nw", relheight=1.0)

        # Content row (icon + text) with left padding to clear the accent
        content = ctk.CTkFrame(
            master=self,
            fg_color="transparent",
            corner_radius=0,
        )
        content.pack(
            fill="x",
            padx=(_LEFT_BORDER_WIDTH + _PADDING_X, _PADDING_X),
            pady=_PADDING_Y,
        )

        # Icon
        icon_label = ctk.CTkLabel(
            master=content,
            text=ICON_INFO,
            font=_ICON_FONT,
            text_color=COLOR_INFO_ICON,
        )
        icon_label.pack(side="left")

        # Message text
        self._label = ctk.CTkLabel(
            master=content,
            text=self._text,
            font=_TEXT_FONT,
            text_color=COLOR_INFO_TEXT,
            anchor="w",
            wraplength=600,
            justify="left",
        )
        self._label.pack(side="left", padx=(_ICON_GAP, 0), fill="x", expand=True)
