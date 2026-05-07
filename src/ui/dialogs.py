"""Modal dialog helpers — error, warning, confirmation, and info popups.

All dialogs are CTkToplevel windows styled to match the Stitch design
system (card-style centered modal, pill-shaped buttons, themed colors).

Usage:
    from src.ui.dialogs import show_error, show_warning, show_confirm, show_info

    show_error(parent, "Something went wrong", "Could not connect…")
    if show_confirm(parent, "Are you sure?", "This will send 500 emails."):
        ...

All visual values imported from src.ui.theme.  Zero business logic.
"""

from __future__ import annotations

import customtkinter as ctk

from src.ui.theme import (
    COLOR_BACKGROUND,
    COLOR_ERROR,
    COLOR_ERROR_CONTAINER,
    COLOR_ON_ERROR,
    COLOR_ON_SURFACE,
    COLOR_ON_SURFACE_VARIANT,
    COLOR_OUTLINE_VARIANT,
    COLOR_PRIMARY_CONTAINER,
    COLOR_PRIMARY_HOVER,
    COLOR_ON_PRIMARY,
    COLOR_SURFACE_CONTAINER_LOWEST,
    COLOR_WARNING_BG,
    COLOR_WARNING_TEXT,
    COLOR_INFO_BG,
    COLOR_INFO_TEXT,
    COLOR_BUTTON_SECONDARY_TEXT,
    COLOR_BUTTON_SECONDARY_BORDER,
    FONT_FAMILY,
    FONT_H3,
    FONT_BODY_MD,
    RADIUS_CARD,
    RADIUS_PILL,
    BORDER_WIDTH_DEFAULT,
    ICON_CROSS,
    ICON_WARNING,
    ICON_INFO,
    SPACING_STACK_GAP,
    SPACING_CONTAINER_PADDING,
)

# ---------------------------------------------------------------------------
# Constants local to this module
# ---------------------------------------------------------------------------
_DIALOG_MIN_WIDTH: int = 420
_DIALOG_MAX_WIDTH: int = 520
_BUTTON_HEIGHT: int = 36
_BUTTON_WIDTH: int = 120
_BUTTON_FONT: tuple[str, int, str] = (FONT_FAMILY, 12, "bold")
_ICON_FONT: tuple[str, int, str] = (FONT_FAMILY, 28, "normal")


# ===================================================================
# Internal — base dialog builder
# ===================================================================

class _BaseDialog(ctk.CTkToplevel):
    """Base class for all modal dialogs.

    Creates a centered, card-styled CTkToplevel with a title row,
    message body, and an action-button row.  Subclasses / factory
    functions populate the content.

    Args:
        parent: The parent widget (used for centering).
        title: Dialog heading text.
        message: Body message (supports multi-line).
        icon: Unicode icon character shown left of the title.
        icon_color: Color for the icon.
    """

    def __init__(
        self,
        parent: ctk.CTkBaseClass,
        title: str,
        message: str,
        icon: str = "",
        icon_color: str = COLOR_ON_SURFACE,
    ) -> None:
        super().__init__(parent)

        self.title(title)
        self.resizable(False, False)
        self.configure(fg_color=COLOR_BACKGROUND)
        self.transient(parent.winfo_toplevel())
        self.grab_set()

        # Result for confirm dialogs
        self._result: bool = False

        # -- Card container ------------------------------------------------
        self._card = ctk.CTkFrame(
            master=self,
            fg_color=COLOR_SURFACE_CONTAINER_LOWEST,
            corner_radius=RADIUS_CARD,
            border_width=BORDER_WIDTH_DEFAULT,
            border_color=COLOR_OUTLINE_VARIANT,
        )
        self._card.pack(
            fill="both",
            expand=True,
            padx=SPACING_STACK_GAP,
            pady=SPACING_STACK_GAP,
        )

        # -- Title row (icon + heading) ------------------------------------
        title_row = ctk.CTkFrame(
            master=self._card,
            fg_color="transparent",
        )
        title_row.pack(
            fill="x",
            padx=SPACING_CONTAINER_PADDING,
            pady=(SPACING_CONTAINER_PADDING, 0),
        )

        if icon:
            icon_label = ctk.CTkLabel(
                master=title_row,
                text=icon,
                font=_ICON_FONT,
                text_color=icon_color,
            )
            icon_label.pack(side="left", padx=(0, 8))

        heading = ctk.CTkLabel(
            master=title_row,
            text=title,
            font=FONT_H3,
            text_color=COLOR_ON_SURFACE,
            anchor="w",
        )
        heading.pack(side="left", fill="x", expand=True)

        # -- Message body --------------------------------------------------
        body = ctk.CTkLabel(
            master=self._card,
            text=message,
            font=FONT_BODY_MD,
            text_color=COLOR_ON_SURFACE_VARIANT,
            anchor="w",
            justify="left",
            wraplength=_DIALOG_MAX_WIDTH - 2 * SPACING_CONTAINER_PADDING,
        )
        body.pack(
            fill="x",
            padx=SPACING_CONTAINER_PADDING,
            pady=(SPACING_STACK_GAP, 0),
        )

        # -- Button row (populated by subclasses) --------------------------
        self._button_row = ctk.CTkFrame(
            master=self._card,
            fg_color="transparent",
        )
        self._button_row.pack(
            fill="x",
            padx=SPACING_CONTAINER_PADDING,
            pady=SPACING_CONTAINER_PADDING,
        )

        # Center the dialog on screen after building
        self.after(10, self._center)

        # Close on Escape
        self.bind("<Escape>", lambda _e: self._close())

        # Handle window close button
        self.protocol("WM_DELETE_WINDOW", self._close)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _center(self) -> None:
        """Center the dialog relative to the screen."""
        self.update_idletasks()
        w = max(self.winfo_reqwidth(), _DIALOG_MIN_WIDTH)
        h = self.winfo_reqheight()
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")
        self.minsize(w, h)

    def _close(self) -> None:
        """Destroy the dialog and release the grab."""
        self.grab_release()
        self.destroy()

    def _add_primary_button(
        self,
        text: str,
        command: object,
        fg: str = COLOR_PRIMARY_CONTAINER,
        hover: str = COLOR_PRIMARY_HOVER,
        text_color: str = COLOR_ON_PRIMARY,
    ) -> ctk.CTkButton:
        """Add a filled primary-style pill button."""
        btn = ctk.CTkButton(
            master=self._button_row,
            text=text,
            font=_BUTTON_FONT,
            width=_BUTTON_WIDTH,
            height=_BUTTON_HEIGHT,
            corner_radius=RADIUS_PILL,
            fg_color=fg,
            hover_color=hover,
            text_color=text_color,
            border_width=0,
            command=command,
        )
        btn.pack(side="right", padx=(8, 0))
        return btn

    def _add_secondary_button(
        self,
        text: str,
        command: object,
    ) -> ctk.CTkButton:
        """Add an outlined secondary-style pill button."""
        btn = ctk.CTkButton(
            master=self._button_row,
            text=text,
            font=_BUTTON_FONT,
            width=_BUTTON_WIDTH,
            height=_BUTTON_HEIGHT,
            corner_radius=RADIUS_PILL,
            fg_color="transparent",
            hover_color=COLOR_OUTLINE_VARIANT,
            text_color=COLOR_BUTTON_SECONDARY_TEXT,
            border_width=BORDER_WIDTH_DEFAULT,
            border_color=COLOR_BUTTON_SECONDARY_BORDER,
            command=command,
        )
        btn.pack(side="right", padx=(8, 0))
        return btn


# ===================================================================
# Public factory functions
# ===================================================================

def show_error(
    parent: ctk.CTkBaseClass,
    title: str = "Error",
    message: str = "",
) -> None:
    """Show a modal error dialog with a single OK button.

    Args:
        parent: Parent widget for centering.
        title: Dialog heading.
        message: Error description (friendly, non-technical).
    """
    dlg = _BaseDialog(
        parent=parent,
        title=title,
        message=message,
        icon=ICON_CROSS,
        icon_color=COLOR_ERROR,
    )
    dlg._add_primary_button(
        text="OK",
        command=dlg._close,
        fg=COLOR_ERROR,
        hover="#9B1515",
        text_color=COLOR_ON_ERROR,
    )
    dlg.wait_window()


def show_warning(
    parent: ctk.CTkBaseClass,
    title: str = "Warning",
    message: str = "",
) -> None:
    """Show a modal warning dialog with a single OK button.

    Args:
        parent: Parent widget for centering.
        title: Dialog heading.
        message: Warning description.
    """
    dlg = _BaseDialog(
        parent=parent,
        title=title,
        message=message,
        icon=ICON_WARNING,
        icon_color=COLOR_WARNING_TEXT,
    )
    dlg._add_primary_button(text="OK", command=dlg._close)
    dlg.wait_window()


def show_info(
    parent: ctk.CTkBaseClass,
    title: str = "Info",
    message: str = "",
) -> None:
    """Show a modal informational dialog with a single OK button.

    Args:
        parent: Parent widget for centering.
        title: Dialog heading.
        message: Informational text.
    """
    dlg = _BaseDialog(
        parent=parent,
        title=title,
        message=message,
        icon=ICON_INFO,
        icon_color=COLOR_INFO_TEXT,
    )
    dlg._add_primary_button(text="OK", command=dlg._close)
    dlg.wait_window()


def show_confirm(
    parent: ctk.CTkBaseClass,
    title: str = "Confirm",
    message: str = "",
    confirm_text: str = "Confirm",
    cancel_text: str = "Cancel",
) -> bool:
    """Show a modal confirmation dialog with Confirm / Cancel buttons.

    Args:
        parent: Parent widget for centering.
        title: Dialog heading.
        message: Question or description.
        confirm_text: Label for the primary action button.
        cancel_text: Label for the secondary cancel button.

    Returns:
        ``True`` if the user clicked Confirm, ``False`` otherwise.
    """
    dlg = _BaseDialog(
        parent=parent,
        title=title,
        message=message,
        icon=ICON_WARNING,
        icon_color=COLOR_WARNING_TEXT,
    )

    def _confirm() -> None:
        dlg._result = True
        dlg._close()

    dlg._add_primary_button(text=confirm_text, command=_confirm)
    dlg._add_secondary_button(text=cancel_text, command=dlg._close)
    dlg.wait_window()
    return dlg._result
