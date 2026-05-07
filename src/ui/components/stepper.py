"""Step indicator bar — shows wizard progress as numbered circles.

Layout (from Stitch step1_credentials/screen.png + DESIGN.md):
    ① Credentials   ② Files   ③ Preview   ④ Send

States per step:
    - **Completed** (index < current): blue filled circle + ✓ + blue label.
    - **Active** (index == current): blue filled circle + white number + blue label.
    - **Pending** (index > current): gray-bordered circle + gray number + gray label.

This is a standalone reusable widget used inside NavBar but can be
placed anywhere.  All visual values imported from src.ui.theme.
Zero business logic.
"""

from __future__ import annotations

import customtkinter as ctk

from src.ui.theme import (
    COLOR_NAVBAR_ACTIVE,
    COLOR_NAVBAR_INACTIVE,
    COLOR_ON_PRIMARY,
    COLOR_OUTLINE_VARIANT,
    COLOR_PRIMARY_CONTAINER,
    FONT_FAMILY,
    ICON_CHECK,
)

# ---------------------------------------------------------------------------
# Constants local to this component
# ---------------------------------------------------------------------------
_CIRCLE_SIZE: int = 24
_CIRCLE_FONT: tuple[str, int, str] = (FONT_FAMILY, 12, "bold")
_LABEL_FONT: tuple[str, int, str] = (FONT_FAMILY, 13, "bold")
_STEP_GAP: int = 24
_ICON_LABEL_GAP: int = 6


class Stepper(ctk.CTkFrame):
    """Horizontal step indicator with numbered circles and labels.

    Each step is displayed as a small circle (with a number or checkmark)
    followed by a text label.  Visual state automatically updates when
    ``set_current_step`` is called.

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
            fg_color="transparent",
            corner_radius=0,
        )

        self._step_labels = step_labels
        self._current_step = current_step

        # Widget refs for dynamic updates
        self._circles: list[ctk.CTkLabel] = []
        self._labels: list[ctk.CTkLabel] = []

        self._build_steps()
        self._refresh()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set_current_step(self, index: int) -> None:
        """Update which step is highlighted as active.

        Steps before *index* → completed (checkmark).
        Step at *index* → active (filled blue).
        Steps after *index* → pending (gray outline).

        Args:
            index: Zero-based step index.
        """
        if index < 0 or index >= len(self._step_labels):
            return
        self._current_step = index
        self._refresh()

    @property
    def current_step(self) -> int:
        """Return the zero-based index of the active step."""
        return self._current_step

    @property
    def step_count(self) -> int:
        """Return the total number of steps."""
        return len(self._step_labels)

    # ------------------------------------------------------------------
    # Private — build
    # ------------------------------------------------------------------

    def _build_steps(self) -> None:
        """Create circle + label pairs for each step."""
        for i, label_text in enumerate(self._step_labels):
            step_item = ctk.CTkFrame(
                master=self,
                fg_color="transparent",
                corner_radius=0,
            )
            pad_left = _STEP_GAP if i > 0 else 0
            step_item.pack(side="left", padx=(pad_left, 0))

            # Number / checkmark circle
            circle = ctk.CTkLabel(
                master=step_item,
                text=str(i + 1),
                font=_CIRCLE_FONT,
                width=_CIRCLE_SIZE,
                height=_CIRCLE_SIZE,
                corner_radius=_CIRCLE_SIZE // 2,
                fg_color=COLOR_OUTLINE_VARIANT,
                text_color=COLOR_NAVBAR_INACTIVE,
            )
            circle.pack(side="left")
            self._circles.append(circle)

            # Step label text
            lbl = ctk.CTkLabel(
                master=step_item,
                text=label_text,
                font=_LABEL_FONT,
                text_color=COLOR_NAVBAR_INACTIVE,
            )
            lbl.pack(side="left", padx=(_ICON_LABEL_GAP, 0))
            self._labels.append(lbl)

    # ------------------------------------------------------------------
    # Private — refresh visuals
    # ------------------------------------------------------------------

    def _refresh(self) -> None:
        """Re-apply colors to circles and labels based on current step."""
        for i, (circle, label) in enumerate(
            zip(self._circles, self._labels)
        ):
            if i < self._current_step:
                # Completed — blue circle with checkmark
                circle.configure(
                    text=ICON_CHECK,
                    fg_color=COLOR_PRIMARY_CONTAINER,
                    text_color=COLOR_ON_PRIMARY,
                )
                label.configure(text_color=COLOR_NAVBAR_ACTIVE)
            elif i == self._current_step:
                # Active — blue circle with white number
                circle.configure(
                    text=str(i + 1),
                    fg_color=COLOR_PRIMARY_CONTAINER,
                    text_color=COLOR_ON_PRIMARY,
                )
                label.configure(text_color=COLOR_NAVBAR_ACTIVE)
            else:
                # Pending — gray circle with gray number
                circle.configure(
                    text=str(i + 1),
                    fg_color=COLOR_OUTLINE_VARIANT,
                    text_color=COLOR_NAVBAR_INACTIVE,
                )
                label.configure(text_color=COLOR_NAVBAR_INACTIVE)
