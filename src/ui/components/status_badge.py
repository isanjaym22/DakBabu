"""Pill-shaped status badges — Sent / Failed / Sending / Pending.

Layout (from Stitch step4_tracker/code.html):
    ┌──────────────────┐
    │  ✓  Sent         │  green-50 bg, green-700 text
    ├──────────────────┤
    │  ✗  Failed       │  error-container bg, error text
    ├──────────────────┤
    │  ⏳ Sending…     │  primary-fixed bg, primary text
    ├──────────────────┤
    │  ⏳ Pending      │  surface-container-high bg, outline text
    └──────────────────┘

Each badge is a pill (full-round corners) with an icon + label.

Also includes a "connection success" variant for Step 1 and a
generic "success" variant for Step 2 (file validation).

All visual values imported from src.ui.theme.  Zero business logic.
"""

from __future__ import annotations

from enum import Enum

import customtkinter as ctk

from src.ui.theme import (
    # Sent / success (green)
    COLOR_SUCCESS_BG,
    COLOR_SUCCESS_TEXT,
    # Connection success (emerald)
    COLOR_SUCCESS_BADGE_BG,
    COLOR_SUCCESS_BADGE_TEXT,
    COLOR_SUCCESS_BADGE_BORDER,
    # Failed (red)
    COLOR_ERROR_CONTAINER,
    COLOR_ERROR,
    # Sending (blue)
    COLOR_PRIMARY_FIXED,
    COLOR_PRIMARY,
    # Pending (gray)
    COLOR_SURFACE_CONTAINER_HIGH,
    COLOR_OUTLINE,
    # Warning (amber)
    COLOR_WARNING_BG,
    COLOR_WARNING_TEXT,
    # Structural
    FONT_FAMILY,
    RADIUS_PILL,
    ICON_CHECK,
    ICON_CROSS,
    ICON_HOURGLASS,
    ICON_WARNING,
)

# ---------------------------------------------------------------------------
# Constants local to this component
# ---------------------------------------------------------------------------
_BADGE_FONT: tuple[str, int, str] = (FONT_FAMILY, 12, "bold")
_BADGE_HEIGHT: int = 24
_BADGE_PADX: int = 10
_ICON_GAP: int = 4


class BadgeVariant(Enum):
    """Pre-defined badge colour schemes."""

    SENT = "sent"
    FAILED = "failed"
    SENDING = "sending"
    PENDING = "pending"
    SUCCESS = "success"              # generic green (file validation)
    CONNECTION_OK = "connection_ok"  # emerald (SMTP test)
    WARNING = "warning"              # amber (duplicates, rate limit)


# Map variant → (bg_color, text_color, border_color | None, icon, default_label)
_VARIANT_MAP: dict[BadgeVariant, tuple[str, str, str | None, str, str]] = {
    BadgeVariant.SENT: (
        COLOR_SUCCESS_BG, COLOR_SUCCESS_TEXT, None,
        ICON_CHECK, "Sent",
    ),
    BadgeVariant.FAILED: (
        COLOR_ERROR_CONTAINER, COLOR_ERROR, None,
        ICON_CROSS, "Failed",
    ),
    BadgeVariant.SENDING: (
        COLOR_PRIMARY_FIXED, COLOR_PRIMARY, None,
        ICON_HOURGLASS, "Sending…",
    ),
    BadgeVariant.PENDING: (
        COLOR_SURFACE_CONTAINER_HIGH, COLOR_OUTLINE, None,
        ICON_HOURGLASS, "Pending",
    ),
    BadgeVariant.SUCCESS: (
        COLOR_SUCCESS_BG, COLOR_SUCCESS_TEXT, None,
        ICON_CHECK, "Success",
    ),
    BadgeVariant.CONNECTION_OK: (
        COLOR_SUCCESS_BADGE_BG, COLOR_SUCCESS_BADGE_TEXT,
        COLOR_SUCCESS_BADGE_BORDER,
        ICON_CHECK, "Connection successful!",
    ),
    BadgeVariant.WARNING: (
        COLOR_WARNING_BG, COLOR_WARNING_TEXT, None,
        ICON_WARNING, "Warning",
    ),
}


class StatusBadge(ctk.CTkFrame):
    """Pill-shaped status badge with icon + text.

    The badge adjusts its colours automatically based on the chosen
    ``BadgeVariant``.  A custom label can override the default text.

    Args:
        master: Parent widget.
        variant: One of the ``BadgeVariant`` enum values.
        text: Override label text.  If ``None``, uses the variant default.
    """

    def __init__(
        self,
        master: ctk.CTkBaseClass,
        variant: BadgeVariant = BadgeVariant.PENDING,
        text: str | None = None,
    ) -> None:
        bg, fg, border, icon, default_label = _VARIANT_MAP[variant]

        super().__init__(
            master=master,
            fg_color=bg,
            corner_radius=RADIUS_PILL,
            border_width=1 if border else 0,
            border_color=border or bg,
            height=_BADGE_HEIGHT,
        )

        self._variant = variant
        self._display_text = text if text is not None else default_label

        # Prevent the frame from resizing to fill parent
        self.pack_propagate(False)

        # Content: icon + label packed horizontally
        self._icon_label = ctk.CTkLabel(
            master=self,
            text=icon,
            font=_BADGE_FONT,
            text_color=fg,
        )
        self._icon_label.pack(side="left", padx=(_BADGE_PADX, 0))

        self._text_label = ctk.CTkLabel(
            master=self,
            text=self._display_text,
            font=_BADGE_FONT,
            text_color=fg,
        )
        self._text_label.pack(side="left", padx=(_ICON_GAP, _BADGE_PADX))

        # Let the frame auto-size to its text content width
        self.pack_propagate(True)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set_variant(self, variant: BadgeVariant, text: str | None = None) -> None:
        """Change the badge variant (and optionally the label).

        Args:
            variant: New ``BadgeVariant``.
            text: Override label text.  ``None`` → variant default.
        """
        bg, fg, border, icon, default_label = _VARIANT_MAP[variant]
        self._variant = variant
        self._display_text = text if text is not None else default_label

        self.configure(
            fg_color=bg,
            border_width=1 if border else 0,
            border_color=border or bg,
        )
        self._icon_label.configure(text=icon, text_color=fg)
        self._text_label.configure(text=self._display_text, text_color=fg)
