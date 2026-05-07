"""Top navigation bar — DakBabu branding + step indicator cluster.

Layout (from Stitch step1_credentials/screen.png):
    ┌──────────────────────────────────────────────────────────────┐
    │  DakBabu  Bulk Email Sender   ① Credentials ② Files ...    │
    └──────────────────────────────────────────────────────────────┘

- Fixed height (56 px), white background, 1 px bottom border.
- Left group: app name (bold) + subtitle (muted).
- Center group: Stepper component (numbered step indicators).
- Delegates all step-indicator logic to ``stepper.Stepper``.

All visual values imported from src.ui.theme.  Zero business logic.
"""

from __future__ import annotations

import customtkinter as ctk

from src.ui.theme import (
    COLOR_NAVBAR_BG,
    COLOR_NAVBAR_BORDER,
    COLOR_NAVBAR_TEXT,
    COLOR_NAVBAR_SUBTITLE,
    FONT_FAMILY,
    BORDER_WIDTH_DEFAULT,
    SPACING_INLINE_GAP,
)
from src.ui.components.stepper import Stepper

# ---------------------------------------------------------------------------
# Constants local to this component
# ---------------------------------------------------------------------------
_NAV_HEIGHT: int = 56
_TITLE_FONT: tuple[str, int, str] = (FONT_FAMILY, 18, "bold")
_SUBTITLE_FONT: tuple[str, int, str] = (FONT_FAMILY, 13, "normal")


class NavBar(ctk.CTkFrame):
    """Top header bar with app branding and step navigation indicators.

    Composes a ``Stepper`` widget in its center for step progress display.

    Args:
        master: Parent widget.
        step_labels: Ordered list of step names
            (e.g. ``["Credentials", "Files", "Preview", "Send"]``).
        current_step: Zero-based index of the initially active step.
    """

    def __init__(
        self,
        master: ctk.CTkBaseClass,
        step_labels: list[str],
        current_step: int = 0,
    ) -> None:
        super().__init__(
            master=master,
            fg_color=COLOR_NAVBAR_BG,
            corner_radius=0,
            height=_NAV_HEIGHT,
            border_width=0,
        )
        self.grid_propagate(False)

        self._step_labels = step_labels
        self._current_step = current_step

        # -- Layout: 3 columns (brand | stepper | spacer) -----------------
        self.grid_columnconfigure(0, weight=0)  # brand group
        self.grid_columnconfigure(1, weight=1)  # stepper (centered)
        self.grid_columnconfigure(2, weight=0)  # right spacer
        self.grid_rowconfigure(0, weight=1)

        self._build_brand()
        self._build_stepper()
        self._build_bottom_border()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set_current_step(self, index: int) -> None:
        """Update which step is highlighted as active.

        Delegates to the embedded ``Stepper`` widget.

        Args:
            index: Zero-based step index.
        """
        self._stepper.set_current_step(index)

    # ------------------------------------------------------------------
    # Private — build helpers
    # ------------------------------------------------------------------

    def _build_brand(self) -> None:
        """Create the left-side branding group: title + subtitle."""
        brand_frame = ctk.CTkFrame(
            master=self,
            fg_color="transparent",
            corner_radius=0,
        )
        brand_frame.grid(row=0, column=0, sticky="w", padx=(32, 0))

        # App name
        title_label = ctk.CTkLabel(
            master=brand_frame,
            text="DakBabu",
            font=_TITLE_FONT,
            text_color=COLOR_NAVBAR_TEXT,
        )
        title_label.pack(side="left")

        # Subtitle
        subtitle_label = ctk.CTkLabel(
            master=brand_frame,
            text="Bulk Email Sender",
            font=_SUBTITLE_FONT,
            text_color=COLOR_NAVBAR_SUBTITLE,
        )
        subtitle_label.pack(side="left", padx=(SPACING_INLINE_GAP, 0))

    def _build_stepper(self) -> None:
        """Create the center Stepper component."""
        self._stepper = Stepper(
            master=self,
            step_labels=self._step_labels,
            current_step=self._current_step,
        )
        self._stepper.grid(row=0, column=1, sticky="")

    def _build_bottom_border(self) -> None:
        """Draw a 1 px border line at the bottom of the NavBar."""
        border = ctk.CTkFrame(
            master=self,
            fg_color=COLOR_NAVBAR_BORDER,
            height=BORDER_WIDTH_DEFAULT,
            corner_radius=0,
        )
        border.place(relx=0, rely=1.0, anchor="sw", relwidth=1.0)
