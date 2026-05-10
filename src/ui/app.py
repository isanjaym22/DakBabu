"""DakBabu root application window.

Manages the wizard navigation, step switching, and top-level layout.
Integrates NavBar (top), Stepper (inside NavBar), BottomBar (footer),
and a central content area where step frames are swapped.

This file contains ZERO business logic — UI rendering and navigation only.
All visual values are imported from src.ui.theme.
"""

from __future__ import annotations

from typing import Protocol

import customtkinter as ctk

from src.ui.theme import (
    COLOR_BACKGROUND,
    FONT_FAMILY,
    SPACING_CONTAINER_PADDING,
    WINDOW_DEFAULT_HEIGHT,
    WINDOW_DEFAULT_WIDTH,
    WINDOW_MIN_HEIGHT,
    WINDOW_MIN_WIDTH,
    WINDOW_TITLE,
)
from src.ui.components.nav_bar import NavBar
from src.ui.components.bottom_bar import BottomBar


# ---------------------------------------------------------------------------
# Step protocol — every step frame must satisfy this interface
# ---------------------------------------------------------------------------

class StepFrame(Protocol):
    """Protocol that each wizard step frame must implement."""

    def validate(self) -> bool:
        """Return True if the step's data is valid and user can proceed."""
        ...

    def get_data(self) -> dict:
        """Return the step's current data as a dictionary."""
        ...

    def on_enter(self) -> None:
        """Called when the step becomes visible (navigated to)."""
        ...


# ---------------------------------------------------------------------------
# Step definitions — labels and order for the wizard
# ---------------------------------------------------------------------------

STEP_LABELS: list[str] = ["Credentials", "Files", "Preview", "Send"]


# ---------------------------------------------------------------------------
# App — root window and wizard controller
# ---------------------------------------------------------------------------

class App(ctk.CTk):
    """Root application window with wizard navigation.

    Layout (top to bottom):
        - NavBar (fixed top, contains branding + stepper)
        - Content area (stretches, swaps step frames)
        - BottomBar (fixed bottom, Back / Next buttons)
    """

    def __init__(self) -> None:
        super().__init__()

        # -- Window configuration ------------------------------------------
        self.title(WINDOW_TITLE)
        self.geometry(f"{WINDOW_DEFAULT_WIDTH}x{WINDOW_DEFAULT_HEIGHT}")
        self.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        self.configure(fg_color=COLOR_BACKGROUND)
        self.option_add("*Font", f"{FONT_FAMILY} 14")

        # -- Wizard state --------------------------------------------------
        self._current_step: int = 0
        self._steps: list[ctk.CTkFrame] = []
        self.app_state: dict = {}

        # -- Layout: 3 rows (nav, content, bottom) ------------------------
        self.grid_rowconfigure(0, weight=0)  # NavBar — fixed height
        self.grid_rowconfigure(1, weight=1)  # Content — stretches
        self.grid_rowconfigure(2, weight=0)  # BottomBar — fixed height
        self.grid_columnconfigure(0, weight=1)

        # -- NavBar --------------------------------------------------------
        self._nav_bar = NavBar(
            master=self,
            step_labels=STEP_LABELS,
            current_step=self._current_step,
        )
        self._nav_bar.grid(row=0, column=0, sticky="ew")

        # -- Content area --------------------------------------------------
        self._content_frame = ctk.CTkFrame(
            master=self,
            fg_color=COLOR_BACKGROUND,
            corner_radius=0,
        )
        self._content_frame.grid(
            row=1, column=0, sticky="nsew",
            padx=SPACING_CONTAINER_PADDING,
            pady=0,
        )
        self._content_frame.grid_rowconfigure(0, weight=1)
        self._content_frame.grid_columnconfigure(0, weight=1)

        # -- BottomBar -----------------------------------------------------
        self._bottom_bar = BottomBar(
            master=self,
            on_back=self._go_back,
            on_next=self._go_next,
        )
        self._bottom_bar.grid(row=2, column=0, sticky="ew")

        # -- Graceful shutdown ---------------------------------------------
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        # -- Initial UI state ----------------------------------------------
        self._update_navigation()

    # ------------------------------------------------------------------
    # Public API — step management
    # ------------------------------------------------------------------

    def add_step(self, step_frame: ctk.CTkFrame) -> None:
        """Register a step frame with the wizard.

        Args:
            step_frame: A CTkFrame instance that satisfies the StepFrame
                protocol.  It will be placed inside the content area but
                hidden until its turn.
        """
        step_frame.grid(
            row=0, column=0, sticky="nsew",
            in_=self._content_frame,
        )
        step_frame.grid_remove()  # hide until shown
        self._steps.append(step_frame)

        # Show the first step immediately
        if len(self._steps) == 1:
            self.show_step(0)

    def show_step(self, index: int) -> None:
        """Switch to the step at *index*.

        Hides the current step, shows the target step, and updates
        the NavBar stepper + BottomBar button states.

        Args:
            index: Zero-based step index.
        """
        if index < 0 or index >= len(self._steps):
            return

        # Hide current
        if self._steps:
            for step in self._steps:
                step.grid_remove()

        # Show target
        self._current_step = index
        self._steps[index].grid()

        # Notify the step it is now visible
        step = self._steps[index]
        if hasattr(step, "on_enter") and callable(step.on_enter):
            step.on_enter()

        self._update_navigation()

    @property
    def content_frame(self) -> ctk.CTkFrame:
        """Return the content area frame (used as master for step frames)."""
        return self._content_frame

    @property
    def current_step(self) -> int:
        """Return the zero-based index of the currently visible step."""
        return self._current_step

    # ------------------------------------------------------------------
    # Private — navigation callbacks
    # ------------------------------------------------------------------

    def _go_back(self) -> None:
        """Navigate to the previous step if not at the first step."""
        if self._current_step > 0:
            self.show_step(self._current_step - 1)

    def _go_next(self) -> None:
        """Navigate to the next step if validation passes.

        If the current step implements ``validate()`` and it returns
        False, navigation is blocked.
        """
        if self._current_step >= len(self._steps) - 1:
            return

        current = self._steps[self._current_step]
        if hasattr(current, "validate") and callable(current.validate):
            if not current.validate():
                return

        self.show_step(self._current_step + 1)

    def _update_navigation(self) -> None:
        """Sync NavBar stepper and BottomBar states with current step."""
        self._nav_bar.set_current_step(self._current_step)

        # Back button: disabled on first step
        is_first = self._current_step == 0
        self._bottom_bar.set_back_enabled(not is_first)

        # Next button: disabled on last step (or when no steps exist)
        is_last = (
            len(self._steps) == 0
            or self._current_step >= len(self._steps) - 1
        )
        self._bottom_bar.set_next_enabled(not is_last)

    def _on_close(self) -> None:
        """Handle window close — graceful shutdown.

        Placeholder for Phase 4 cleanup (cancel threads, delete temp
        files).  For now, just destroy the window.
        """
        self.destroy()
