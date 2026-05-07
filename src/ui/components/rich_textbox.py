"""Rich text editor — tkinter.Text with Bold / Italic / Underline toolbar.

Layout (from ARCHITECTURE.md §4 "Email Body — Rich Text"):
    ┌──────────────────────────────────────────────────┐
    │  [ B ]  [ I ]  [ U ]                   toolbar   │
    ├──────────────────────────────────────────────────┤
    │  Dear {{name}},                                  │
    │  Please find your attached document…             │
    │                                                  │
    │                                       text area  │
    └──────────────────────────────────────────────────┘

- Toolbar: three toggle buttons for Bold, Italic, Underline.
- Text area: ``tkinter.Text`` (not CTkTextbox — we need tag support).
- Exports content as a list of ``TextSegment`` objects compatible
  with ``core.email_formatter``.

All visual values imported from src.ui.theme.  Zero business logic.
"""

from __future__ import annotations

import tkinter as tk
from dataclasses import dataclass

import customtkinter as ctk

from src.ui.theme import (
    COLOR_ON_SURFACE,
    COLOR_ON_SURFACE_VARIANT,
    COLOR_OUTLINE_VARIANT,
    COLOR_SURFACE_CONTAINER_LOWEST,
    COLOR_SURFACE_CONTAINER_LOW,
    COLOR_PRIMARY_CONTAINER,
    COLOR_ON_PRIMARY,
    FONT_FAMILY,
    FONT_FAMILY_FALLBACK,
    FONT_BODY_MD,
    RADIUS_DEFAULT,
    BORDER_WIDTH_DEFAULT,
    BORDER_WIDTH_FOCUS,
)

# ---------------------------------------------------------------------------
# Constants local to this component
# ---------------------------------------------------------------------------
_TOOLBAR_HEIGHT: int = 36
_TOOLBAR_BTN_SIZE: int = 28
_TOOLBAR_FONT: tuple[str, int, str] = (FONT_FAMILY, 13, "bold")
_TEXT_FONT_FAMILY: str = FONT_FAMILY
_TEXT_FONT_SIZE: int = 14
_TEXT_PAD: int = 12

# Tag names used inside the tkinter.Text widget
_TAG_BOLD: str = "bold"
_TAG_ITALIC: str = "italic"
_TAG_UNDERLINE: str = "underline"


class RichTextbox(ctk.CTkFrame):
    """Text editor with a Bold / Italic / Underline formatting toolbar.

    Wraps a raw ``tkinter.Text`` widget inside a CTkFrame to match the
    Stitch design.  Formatting is applied via tkinter text tags on the
    current selection.

    The widget exposes ``get_segments()`` which returns a list of
    ``TextSegment`` dataclasses ready for ``core.email_formatter``.

    Args:
        master: Parent widget.
        placeholder: Gray placeholder text shown when the editor is empty.
        height: Visible height in pixels (approximate via rows).
    """

    def __init__(
        self,
        master: ctk.CTkBaseClass,
        placeholder: str = "",
        height: int = 160,
    ) -> None:
        super().__init__(
            master=master,
            fg_color=COLOR_SURFACE_CONTAINER_LOWEST,
            corner_radius=RADIUS_DEFAULT,
            border_width=BORDER_WIDTH_DEFAULT,
            border_color=COLOR_OUTLINE_VARIANT,
        )

        self._placeholder = placeholder
        self._placeholder_active = False

        # Track which toolbar buttons are "pressed"
        self._bold_on = False
        self._italic_on = False
        self._underline_on = False

        self._build_toolbar()
        self._build_text_area(height)
        self._configure_tags()
        self._show_placeholder()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_text(self) -> str:
        """Return the raw text content (no formatting metadata)."""
        if self._placeholder_active:
            return ""
        return self._text.get("1.0", "end-1c")

    def set_text(self, content: str) -> None:
        """Replace the entire text content (plain, no formatting).

        Args:
            content: New plain-text content.
        """
        self._clear_placeholder()
        self._text.delete("1.0", "end")
        self._text.insert("1.0", content)

    def get_segments(self) -> list[dict[str, object]]:
        """Export the formatted content as a list of segment dicts.

        Each dict has keys: ``text``, ``bold``, ``italic``, ``underline``
        — compatible with ``core.email_formatter.TextSegment``.

        Returns:
            A list of segment dictionaries covering the full text.
        """
        if self._placeholder_active:
            return []

        segments: list[dict[str, object]] = []
        text_widget = self._text

        # Walk character-by-character, grouping runs with identical tags
        end_index = text_widget.index("end-1c")
        if text_widget.compare("1.0", ">=", end_index):
            return []

        current_pos = "1.0"
        prev_tags: tuple[str, ...] | None = None
        run_start = current_pos

        while text_widget.compare(current_pos, "<", end_index):
            tags = text_widget.tag_names(current_pos)
            # Filter to only our formatting tags
            fmt_tags = tuple(
                t for t in tags if t in (_TAG_BOLD, _TAG_ITALIC, _TAG_UNDERLINE)
            )

            if prev_tags is not None and fmt_tags != prev_tags:
                # Flush the previous run
                run_text = text_widget.get(run_start, current_pos)
                if run_text:
                    segments.append({
                        "text": run_text,
                        "bold": _TAG_BOLD in prev_tags,
                        "italic": _TAG_ITALIC in prev_tags,
                        "underline": _TAG_UNDERLINE in prev_tags,
                    })
                run_start = current_pos

            prev_tags = fmt_tags
            current_pos = text_widget.index(f"{current_pos}+1c")

        # Flush final run
        if prev_tags is not None:
            run_text = text_widget.get(run_start, end_index)
            if run_text:
                segments.append({
                    "text": run_text,
                    "bold": _TAG_BOLD in prev_tags,
                    "italic": _TAG_ITALIC in prev_tags,
                    "underline": _TAG_UNDERLINE in prev_tags,
                })

        return segments

    # ------------------------------------------------------------------
    # Private — build helpers
    # ------------------------------------------------------------------

    def _build_toolbar(self) -> None:
        """Create the B / I / U formatting toolbar."""
        toolbar = ctk.CTkFrame(
            master=self,
            fg_color=COLOR_SURFACE_CONTAINER_LOW,
            corner_radius=0,
            height=_TOOLBAR_HEIGHT,
        )
        toolbar.pack(fill="x")
        toolbar.pack_propagate(False)

        btn_config = [
            ("B", self._toggle_bold),
            ("I", self._toggle_italic),
            ("U", self._toggle_underline),
        ]

        for label, cmd in btn_config:
            btn = ctk.CTkButton(
                master=toolbar,
                text=label,
                font=_TOOLBAR_FONT,
                width=_TOOLBAR_BTN_SIZE,
                height=_TOOLBAR_BTN_SIZE,
                corner_radius=4,
                fg_color="transparent",
                hover_color=COLOR_OUTLINE_VARIANT,
                text_color=COLOR_ON_SURFACE,
                border_width=0,
                command=cmd,
            )
            btn.pack(side="left", padx=(6 if label == "B" else 2, 0), pady=4)

        # Store refs for active-state highlighting
        self._toolbar_btns: dict[str, ctk.CTkButton] = {}
        for child in toolbar.winfo_children():
            if isinstance(child, ctk.CTkButton):
                self._toolbar_btns[child.cget("text")] = child

    def _build_text_area(self, height: int) -> None:
        """Create the underlying tkinter.Text widget."""
        # Wrapper to add internal padding
        text_frame = ctk.CTkFrame(
            master=self,
            fg_color="transparent",
            corner_radius=0,
        )
        text_frame.pack(fill="both", expand=True)

        self._text = tk.Text(
            master=text_frame,
            wrap="word",
            font=(FONT_FAMILY, _TEXT_FONT_SIZE),
            bg=COLOR_SURFACE_CONTAINER_LOWEST,
            fg=COLOR_ON_SURFACE,
            insertbackground=COLOR_ON_SURFACE,
            selectbackground=COLOR_PRIMARY_CONTAINER,
            selectforeground=COLOR_ON_PRIMARY,
            relief="flat",
            borderwidth=0,
            padx=_TEXT_PAD,
            pady=_TEXT_PAD,
            height=height // 20,  # approximate rows from px
            undo=True,
        )
        self._text.pack(fill="both", expand=True)

        # Focus ring on the outer frame
        self._text.bind("<FocusIn>", self._on_focus_in)
        self._text.bind("<FocusOut>", self._on_focus_out)

        # Placeholder handling
        self._text.bind("<FocusIn>", self._on_focus_in)
        self._text.bind("<FocusOut>", self._on_focus_out)

    def _configure_tags(self) -> None:
        """Set up the tkinter text tags for bold, italic, underline."""
        self._text.tag_configure(
            _TAG_BOLD,
            font=(FONT_FAMILY, _TEXT_FONT_SIZE, "bold"),
        )
        self._text.tag_configure(
            _TAG_ITALIC,
            font=(FONT_FAMILY, _TEXT_FONT_SIZE, "italic"),
        )
        self._text.tag_configure(
            _TAG_UNDERLINE,
            underline=True,
        )

        # Combined tags for simultaneous formatting
        self._text.tag_configure(
            "bold_italic",
            font=(FONT_FAMILY, _TEXT_FONT_SIZE, "bold italic"),
        )

    # ------------------------------------------------------------------
    # Private — placeholder
    # ------------------------------------------------------------------

    def _show_placeholder(self) -> None:
        """Insert gray placeholder text if the editor is empty."""
        if self._placeholder and not self.get_text():
            self._placeholder_active = True
            self._text.insert("1.0", self._placeholder)
            self._text.config(fg=COLOR_ON_SURFACE_VARIANT)

    def _clear_placeholder(self) -> None:
        """Remove placeholder text on focus or programmatic set."""
        if self._placeholder_active:
            self._placeholder_active = False
            self._text.delete("1.0", "end")
            self._text.config(fg=COLOR_ON_SURFACE)

    # ------------------------------------------------------------------
    # Private — focus handlers
    # ------------------------------------------------------------------

    def _on_focus_in(self, _event: object = None) -> None:
        """Highlight the border and clear placeholder."""
        self.configure(
            border_width=BORDER_WIDTH_FOCUS,
            border_color=COLOR_PRIMARY_CONTAINER,
        )
        self._clear_placeholder()

    def _on_focus_out(self, _event: object = None) -> None:
        """Revert the border and restore placeholder if empty."""
        self.configure(
            border_width=BORDER_WIDTH_DEFAULT,
            border_color=COLOR_OUTLINE_VARIANT,
        )
        if not self._text.get("1.0", "end-1c").strip():
            self._show_placeholder()

    # ------------------------------------------------------------------
    # Private — formatting toggles
    # ------------------------------------------------------------------

    def _toggle_tag(self, tag_name: str, btn_key: str, attr: str) -> None:
        """Toggle a formatting tag on the current selection.

        If text is selected, the tag is added or removed on that range.
        If no text is selected, future typed text will carry the tag
        (via the insert mark).
        """
        try:
            sel_start = self._text.index("sel.first")
            sel_end = self._text.index("sel.last")

            # Check if the tag is already applied to the entire selection
            current_tags = self._text.tag_names(sel_start)
            if tag_name in current_tags:
                self._text.tag_remove(tag_name, sel_start, sel_end)
            else:
                self._text.tag_add(tag_name, sel_start, sel_end)
        except tk.TclError:
            # No selection — toggle the state flag for future input
            pass

        # Update the toolbar button highlight
        is_on = getattr(self, attr)
        setattr(self, attr, not is_on)
        btn = self._toolbar_btns.get(btn_key)
        if btn is not None:
            if not is_on:
                btn.configure(
                    fg_color=COLOR_PRIMARY_CONTAINER,
                    text_color=COLOR_ON_PRIMARY,
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=COLOR_ON_SURFACE,
                )

    def _toggle_bold(self) -> None:
        self._toggle_tag(_TAG_BOLD, "B", "_bold_on")

    def _toggle_italic(self) -> None:
        self._toggle_tag(_TAG_ITALIC, "I", "_italic_on")

    def _toggle_underline(self) -> None:
        self._toggle_tag(_TAG_UNDERLINE, "U", "_underline_on")
