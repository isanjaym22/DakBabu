"""Dashed-border file-picker area — click to browse, shows selected file.

Layout (from Stitch step2_files/screen.png + code.html):
    ┌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌┐
    ╎               📄 (icon)                           ╎
    ╎       Upload Excel or CSV file                    ╎
    ╎        Click or drag and drop                     ╎
    └╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌┘

After a file is selected the area collapses to show the filename
with a ✗ clear button.

All visual values imported from src.ui.theme.  Zero business logic.
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable

import customtkinter as ctk

from src.ui.theme import (
    COLOR_OUTLINE,
    COLOR_OUTLINE_VARIANT,
    COLOR_ON_SURFACE_VARIANT,
    COLOR_SURFACE_CONTAINER_LOW,
    COLOR_SURFACE_CONTAINER,
    COLOR_ON_SURFACE,
    FONT_BODY_MD,
    FONT_FAMILY,
    FONT_LABEL_SM,
    RADIUS_DEFAULT,
    ICON_CROSS,
    BORDER_WIDTH_DEFAULT,
)

# ---------------------------------------------------------------------------
# Constants local to this component
# ---------------------------------------------------------------------------
_DROPZONE_PAD_Y: int = 32
_DROPZONE_PAD_X: int = 24
_ICON_FONT: tuple[str, int, str] = (FONT_FAMILY, 28, "normal")
_PRIMARY_FONT: tuple[str, int, str] = FONT_BODY_MD
_HINT_FONT: tuple[str, int, str] = (FONT_FAMILY, 12, "normal")
_FILE_FONT: tuple[str, int, str] = FONT_BODY_MD
_CLEAR_FONT: tuple[str, int, str] = (FONT_FAMILY, 14, "bold")


class FilePicker(ctk.CTkFrame):
    """Dashed-border file selector with empty and selected states.

    In the **empty state** the widget shows a centered icon, primary text
    (e.g. "Upload Excel or CSV file") and a hint ("Click or drag and
    drop").  Clicking anywhere opens a file dialog filtered by
    ``filetypes``.

    In the **selected state** the zone is replaced by a single row
    showing the filename and a clear (✗) button.

    Args:
        master: Parent widget.
        icon: Unicode character shown in the empty state.
        primary_text: Bold prompt text (first line).
        hint_text: Italic hint text (second line).
        filetypes: Sequence of (label, pattern) tuples for the file
            dialog, e.g. ``[("Excel files", "*.xlsx")]``.
        on_file_selected: Callback receiving a ``pathlib.Path`` when the
            user picks a file.
        on_file_cleared: Callback with no args when the file is removed.
    """

    def __init__(
        self,
        master: ctk.CTkBaseClass,
        icon: str = "📄",
        primary_text: str = "Upload file",
        hint_text: str = "Click or drag and drop",
        filetypes: list[tuple[str, str]] | None = None,
        on_file_selected: Callable[[Path], None] | None = None,
        on_file_cleared: Callable[[], None] | None = None,
    ) -> None:
        super().__init__(
            master=master,
            fg_color="transparent",
            corner_radius=0,
        )

        self._icon = icon
        self._primary_text = primary_text
        self._hint_text = hint_text
        self._filetypes = filetypes or [("All files", "*.*")]
        self._on_file_selected = on_file_selected
        self._on_file_cleared = on_file_cleared

        self._selected_path: Path | None = None

        # Containers for the two visual states
        self._empty_frame: ctk.CTkFrame | None = None
        self._selected_frame: ctk.CTkFrame | None = None

        self._build_empty_state()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def selected_path(self) -> Path | None:
        """Return the currently selected file path, or ``None``."""
        return self._selected_path

    def set_file(self, path: Path) -> None:
        """Programmatically set a file (e.g. after drag-and-drop).

        Args:
            path: File path to display.
        """
        self._selected_path = path
        self._show_selected_state()
        if self._on_file_selected is not None:
            self._on_file_selected(path)

    def clear(self) -> None:
        """Remove the current selection and revert to the empty state."""
        self._selected_path = None
        self._show_empty_state()
        if self._on_file_cleared is not None:
            self._on_file_cleared()

    # ------------------------------------------------------------------
    # Private — build helpers
    # ------------------------------------------------------------------

    def _build_empty_state(self) -> None:
        """Create the dashed-border drop-zone with icon + text."""
        self._empty_frame = ctk.CTkFrame(
            master=self,
            fg_color=COLOR_SURFACE_CONTAINER_LOW,
            corner_radius=RADIUS_DEFAULT,
            border_width=2,
            border_color=COLOR_OUTLINE_VARIANT,
        )
        self._empty_frame.pack(fill="x", expand=True)

        # Make the entire zone clickable
        self._empty_frame.bind("<Button-1>", self._handle_browse)

        # Pad inner content
        inner = ctk.CTkFrame(
            master=self._empty_frame,
            fg_color="transparent",
            corner_radius=0,
        )
        inner.pack(
            padx=_DROPZONE_PAD_X,
            pady=_DROPZONE_PAD_Y,
        )
        inner.bind("<Button-1>", self._handle_browse)

        # Icon
        icon_label = ctk.CTkLabel(
            master=inner,
            text=self._icon,
            font=_ICON_FONT,
            text_color=COLOR_OUTLINE,
        )
        icon_label.pack()
        icon_label.bind("<Button-1>", self._handle_browse)

        # Primary text
        primary_label = ctk.CTkLabel(
            master=inner,
            text=self._primary_text,
            font=_PRIMARY_FONT,
            text_color=COLOR_ON_SURFACE_VARIANT,
        )
        primary_label.pack(pady=(4, 0))
        primary_label.bind("<Button-1>", self._handle_browse)

        # Hint text (italic feel via smaller + muted)
        hint_label = ctk.CTkLabel(
            master=inner,
            text=self._hint_text,
            font=_HINT_FONT,
            text_color=COLOR_OUTLINE,
        )
        hint_label.pack(pady=(2, 0))
        hint_label.bind("<Button-1>", self._handle_browse)

    def _build_selected_state(self) -> None:
        """Create the filename row with a clear button."""
        self._selected_frame = ctk.CTkFrame(
            master=self,
            fg_color=COLOR_SURFACE_CONTAINER,
            corner_radius=RADIUS_DEFAULT,
            border_width=BORDER_WIDTH_DEFAULT,
            border_color=COLOR_OUTLINE_VARIANT,
        )
        self._selected_frame.pack(fill="x")

        # Grid: filename (stretches) | clear button
        self._selected_frame.grid_columnconfigure(0, weight=1)
        self._selected_frame.grid_columnconfigure(1, weight=0)
        self._selected_frame.grid_rowconfigure(0, weight=1)

        filename = ""
        if self._selected_path is not None:
            filename = self._selected_path.name

        self._filename_label = ctk.CTkLabel(
            master=self._selected_frame,
            text=f"📎  {filename}",
            font=_FILE_FONT,
            text_color=COLOR_ON_SURFACE,
            anchor="w",
        )
        self._filename_label.grid(
            row=0, column=0, sticky="w", padx=(16, 0), pady=12,
        )

        clear_btn = ctk.CTkButton(
            master=self._selected_frame,
            text=ICON_CROSS,
            font=_CLEAR_FONT,
            width=32,
            height=32,
            corner_radius=4,
            fg_color="transparent",
            hover_color=COLOR_SURFACE_CONTAINER_LOW,
            text_color=COLOR_OUTLINE,
            border_width=0,
            command=self.clear,
        )
        clear_btn.grid(row=0, column=1, padx=(0, 8), pady=0)

    # ------------------------------------------------------------------
    # Private — state switching
    # ------------------------------------------------------------------

    def _show_empty_state(self) -> None:
        """Switch to empty (drop-zone) state."""
        if self._selected_frame is not None:
            self._selected_frame.destroy()
            self._selected_frame = None
        if self._empty_frame is None:
            self._build_empty_state()

    def _show_selected_state(self) -> None:
        """Switch to file-selected state."""
        if self._empty_frame is not None:
            self._empty_frame.destroy()
            self._empty_frame = None
        if self._selected_frame is not None:
            self._selected_frame.destroy()
            self._selected_frame = None
        self._build_selected_state()

    # ------------------------------------------------------------------
    # Private — event handlers
    # ------------------------------------------------------------------

    def _handle_browse(self, _event: object = None) -> None:
        """Open the native file dialog and process the result."""
        from tkinter import filedialog

        filepath = filedialog.askopenfilename(
            filetypes=self._filetypes,
        )
        if filepath:
            self.set_file(Path(filepath))
