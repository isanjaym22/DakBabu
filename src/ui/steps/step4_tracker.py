"""Step 4 — Send & Track.

Live tracking table with progress bar, action buttons (Stop, Resume,
Retry Failed, Export Log), and a per-recipient status table.

Layout (from stitch_ui/step4_tracker/screen.png):
    Sending Emails                    Operation ID: #DB-XXXX-XX

    ┌──────────────────────────────────────────────────────────┐
    │  Sending 13 of 42…                       30% Complete   │
    │  ████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░   │
    └──────────────────────────────────────────────────────────┘

    [ ⏹ Stop ]  [ ⬇ Export Log as CSV ]       EST. TIME REMAINING
                                                     ~ 4 minutes
    ┌──────────────────────────────────────────────────────────┐
    │  #    NAME           EMAIL              STATUS           │
    ├──────────────────────────────────────────────────────────┤
    │  10   Priya Sharma   priya@gmail.com    ✓ Sent           │
    │  11   Rohit Verma    rohit@gmail.com    ✓ Sent           │
    │  12   Ananya Iyer    ananya@outlook.com ⏳ Sending…      │
    │  13   Karan Mehta    karan@yahoo.com    ⏳ Pending       │
    │  14   Sneha Patil    sneha@gmail.com    ✗ Failed         │
    │  15   Rahul Gupta    rahul@example.com  ⏳ Pending       │
    └──────────────────────────────────────────────────────────┘

All visual values imported from src.ui.theme.  Zero business logic.
No direct core/ imports — data flows via app.py shared state.
"""

from __future__ import annotations

import tkinter as tk

import customtkinter as ctk

from src.ui.theme import (
    COLOR_BACKGROUND,
    COLOR_ERROR,
    COLOR_ON_SURFACE,
    COLOR_ON_SURFACE_VARIANT,
    COLOR_OUTLINE,
    COLOR_OUTLINE_VARIANT,
    COLOR_PRIMARY_CONTAINER,
    COLOR_PRIMARY_HOVER,
    COLOR_ON_PRIMARY,
    COLOR_SURFACE_CONTAINER_LOWEST,
    COLOR_SURFACE_CONTAINER_LOW,
    COLOR_TABLE_HEADER_BG,
    COLOR_TABLE_ROW_ALT,
    COLOR_PROGRESS_BG,
    COLOR_PROGRESS_FILL,
    COLOR_BUTTON_SECONDARY_TEXT,
    COLOR_BUTTON_SECONDARY_BORDER,
    COLOR_BUTTON_DISABLED_TEXT,
    COLOR_BUTTON_DISABLED_BORDER,
    FONT_FAMILY,
    FONT_H2,
    FONT_BODY_MD,
    FONT_LABEL_SM,
    FONT_LABEL_MD,
    PROGRESS_BAR_HEIGHT,
    RADIUS_CARD,
    RADIUS_PILL,
    RADIUS_DEFAULT,
    BORDER_WIDTH_DEFAULT,
    SPACING_CONTAINER_PADDING,
    SPACING_STACK_GAP,
    SPACING_INLINE_GAP,
    ICON_STOP,
    ICON_PLAY,
    ICON_DOWNLOAD,
    ICON_CHECK,
    ICON_CROSS,
    ICON_HOURGLASS,
)
from src.ui.components.status_badge import StatusBadge, BadgeVariant


# ---------------------------------------------------------------------------
# Constants local to this step
# ---------------------------------------------------------------------------
_ACTION_BTN_HEIGHT: int = 36
_ACTION_BTN_FONT: tuple[str, int, str] = (FONT_FAMILY, 12, "bold")
_TABLE_HEADER_FONT: tuple[str, int, str] = FONT_LABEL_SM
_TABLE_CELL_FONT: tuple[str, int, str] = FONT_BODY_MD
_OP_ID_FONT: tuple[str, int, str] = (FONT_FAMILY, 12, "normal")
_PROGRESS_TEXT_FONT: tuple[str, int, str] = FONT_BODY_MD
_PROGRESS_PCT_FONT: tuple[str, int, str] = (FONT_FAMILY, 14, "bold")
_TIME_LABEL_FONT: tuple[str, int, str] = FONT_LABEL_SM
_TIME_VALUE_FONT: tuple[str, int, str] = (FONT_FAMILY, 14, "bold")

# Column weights for the table
_COL_WIDTHS: list[int] = [60, 180, 250, 140]  # #, Name, Email, Status


# ---------------------------------------------------------------------------
# Demo data for Phase 3 rendering
# ---------------------------------------------------------------------------
_DEMO_ROWS: list[dict[str, str]] = [
    {"num": "10", "name": "Priya Sharma", "email": "priya@gmail.com", "status": "sent"},
    {"num": "11", "name": "Rohit Verma", "email": "rohit@gmail.com", "status": "sent"},
    {"num": "12", "name": "Ananya Iyer", "email": "ananya@outlook.com", "status": "sending"},
    {"num": "13", "name": "Karan Mehta", "email": "karan@yahoo.com", "status": "pending"},
    {"num": "14", "name": "Sneha Patil", "email": "sneha@gmail.com", "status": "failed"},
    {"num": "15", "name": "Rahul Gupta", "email": "rahul@example.com", "status": "pending"},
]

_STATUS_VARIANT_MAP: dict[str, BadgeVariant] = {
    "sent": BadgeVariant.SENT,
    "failed": BadgeVariant.FAILED,
    "sending": BadgeVariant.SENDING,
    "pending": BadgeVariant.PENDING,
}


class Step4Tracker(ctk.CTkFrame):
    """Send tracking step — progress bar, action buttons, live table.

    In Phase 3, static demo data is shown.  Phase 4 will call
    ``update_row()``, ``set_progress()``, etc. to drive the live UI.

    Args:
        master: Parent widget (the content area in App).
    """

    def __init__(
        self,
        master: ctk.CTkBaseClass,
    ) -> None:
        super().__init__(
            master=master,
            fg_color=COLOR_BACKGROUND,
            corner_radius=0,
        )

        self._is_sending: bool = False
        self._total: int = 42
        self._current: int = 13
        self._percent: int = 30

        # Stretch
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._build()

    # ------------------------------------------------------------------
    # StepFrame protocol
    # ------------------------------------------------------------------

    def validate(self) -> bool:
        """Phase 3 — always allow."""
        return True

    def get_data(self) -> dict:
        """Return tracker state."""
        return {
            "is_sending": self._is_sending,
            "total": self._total,
            "current": self._current,
        }

    def on_enter(self) -> None:
        """Called when this step becomes visible."""
        pass

    # ------------------------------------------------------------------
    # Public API — for Phase 4 integration
    # ------------------------------------------------------------------

    def set_progress(self, current: int, total: int) -> None:
        """Update the progress bar and text.

        Args:
            current: Number of emails processed so far.
            total: Total number of recipients.
        """
        self._current = current
        self._total = total
        self._percent = int((current / max(total, 1)) * 100)

        self._progress_text.configure(text=f"Sending {current} of {total}…")
        self._progress_pct.configure(text=f"{self._percent}% Complete")
        self._progress_bar.set(current / max(total, 1))

    def set_sending_state(self, is_sending: bool) -> None:
        """Toggle button states between sending and stopped.

        Args:
            is_sending: True if currently sending.
        """
        self._is_sending = is_sending
        if is_sending:
            self._stop_btn.configure(state="normal")
            self._export_btn.configure(state="disabled")
        else:
            self._stop_btn.configure(state="disabled")
            self._export_btn.configure(state="normal")

    # ------------------------------------------------------------------
    # Private — build
    # ------------------------------------------------------------------

    def _build(self) -> None:
        """Assemble the tracker layout."""
        container = ctk.CTkFrame(
            master=self,
            fg_color=COLOR_BACKGROUND,
            corner_radius=0,
        )
        container.grid(row=0, column=0, sticky="nsew")
        container.grid_rowconfigure(4, weight=1)  # table stretches
        container.grid_columnconfigure(0, weight=1)

        # -- Row 0: Heading + Operation ID --
        header_row = ctk.CTkFrame(
            master=container, fg_color="transparent", corner_radius=0,
        )
        header_row.grid(row=0, column=0, sticky="ew", pady=(SPACING_STACK_GAP, 0))
        header_row.grid_columnconfigure(0, weight=1)

        heading = ctk.CTkLabel(
            master=header_row,
            text="Sending Emails",
            font=FONT_H2,
            text_color=COLOR_ON_SURFACE,
            anchor="w",
        )
        heading.grid(row=0, column=0, sticky="w")

        op_id = ctk.CTkLabel(
            master=header_row,
            text="Operation ID: #DB-8842-13",
            font=_OP_ID_FONT,
            text_color=COLOR_ON_SURFACE_VARIANT,
            anchor="e",
        )
        op_id.grid(row=0, column=1, sticky="e")

        # -- Row 1: Progress card --
        self._build_progress_card(container, row=1)

        # -- Row 2: Action buttons + time estimate --
        self._build_action_row(container, row=2)

        # -- Row 3+4: Table --
        self._build_table(container, row=3)

    def _build_progress_card(self, parent: ctk.CTkFrame, row: int) -> None:
        """Build the progress bar card."""
        card = ctk.CTkFrame(
            master=parent,
            fg_color=COLOR_SURFACE_CONTAINER_LOWEST,
            corner_radius=RADIUS_CARD,
            border_width=BORDER_WIDTH_DEFAULT,
            border_color=COLOR_OUTLINE_VARIANT,
        )
        card.grid(row=row, column=0, sticky="ew", pady=(SPACING_STACK_GAP, 0))
        card.grid_columnconfigure(0, weight=1)

        inner = ctk.CTkFrame(master=card, fg_color="transparent", corner_radius=0)
        inner.pack(fill="x", padx=SPACING_CONTAINER_PADDING, pady=16)
        inner.grid_columnconfigure(0, weight=1)

        # Text row: "Sending X of Y…" ... "Z% Complete"
        text_row = ctk.CTkFrame(
            master=inner, fg_color="transparent", corner_radius=0,
        )
        text_row.pack(fill="x")
        text_row.grid_columnconfigure(0, weight=1)

        self._progress_text = ctk.CTkLabel(
            master=text_row,
            text=f"Sending {self._current} of {self._total}…",
            font=_PROGRESS_TEXT_FONT,
            text_color=COLOR_ON_SURFACE,
            anchor="w",
        )
        self._progress_text.grid(row=0, column=0, sticky="w")

        self._progress_pct = ctk.CTkLabel(
            master=text_row,
            text=f"{self._percent}% Complete",
            font=_PROGRESS_PCT_FONT,
            text_color=COLOR_PRIMARY_CONTAINER,
            anchor="e",
        )
        self._progress_pct.grid(row=0, column=1, sticky="e")

        # Progress bar
        self._progress_bar = ctk.CTkProgressBar(
            master=inner,
            height=PROGRESS_BAR_HEIGHT,
            corner_radius=PROGRESS_BAR_HEIGHT // 2,
            fg_color=COLOR_PROGRESS_BG,
            progress_color=COLOR_PROGRESS_FILL,
        )
        self._progress_bar.pack(fill="x", pady=(8, 0))
        self._progress_bar.set(self._current / max(self._total, 1))

    def _build_action_row(self, parent: ctk.CTkFrame, row: int) -> None:
        """Build the Stop / Export / Time estimate row."""
        action_row = ctk.CTkFrame(
            master=parent, fg_color="transparent", corner_radius=0,
        )
        action_row.grid(row=row, column=0, sticky="ew", pady=(SPACING_STACK_GAP, 0))
        action_row.grid_columnconfigure(1, weight=1)

        # -- Left: Stop + Export buttons --
        btn_group = ctk.CTkFrame(
            master=action_row, fg_color="transparent", corner_radius=0,
        )
        btn_group.grid(row=0, column=0, sticky="w")

        self._stop_btn = ctk.CTkButton(
            master=btn_group,
            text=f"{ICON_STOP}  Stop",
            font=_ACTION_BTN_FONT,
            width=100,
            height=_ACTION_BTN_HEIGHT,
            corner_radius=RADIUS_PILL,
            fg_color=COLOR_SURFACE_CONTAINER_LOWEST,
            hover_color=COLOR_OUTLINE_VARIANT,
            text_color=COLOR_ERROR,
            border_width=BORDER_WIDTH_DEFAULT,
            border_color=COLOR_ERROR,
            command=self._handle_stop,
        )
        self._stop_btn.pack(side="left")

        self._export_btn = ctk.CTkButton(
            master=btn_group,
            text=f"{ICON_DOWNLOAD}  Export Log as CSV",
            font=_ACTION_BTN_FONT,
            width=170,
            height=_ACTION_BTN_HEIGHT,
            corner_radius=RADIUS_PILL,
            fg_color=COLOR_SURFACE_CONTAINER_LOWEST,
            hover_color=COLOR_OUTLINE_VARIANT,
            text_color=COLOR_BUTTON_SECONDARY_TEXT,
            border_width=BORDER_WIDTH_DEFAULT,
            border_color=COLOR_BUTTON_SECONDARY_BORDER,
            command=self._handle_export,
        )
        self._export_btn.pack(side="left", padx=(SPACING_INLINE_GAP, 0))

        # -- Right: Estimated time --
        time_frame = ctk.CTkFrame(
            master=action_row, fg_color="transparent", corner_radius=0,
        )
        time_frame.grid(row=0, column=2, sticky="e")

        time_label = ctk.CTkLabel(
            master=time_frame,
            text="EST. TIME REMAINING",
            font=_TIME_LABEL_FONT,
            text_color=COLOR_OUTLINE,
            anchor="e",
        )
        time_label.pack(anchor="e")

        self._time_value = ctk.CTkLabel(
            master=time_frame,
            text="~ 4 minutes",
            font=_TIME_VALUE_FONT,
            text_color=COLOR_ON_SURFACE,
            anchor="e",
        )
        self._time_value.pack(anchor="e")

    def _build_table(self, parent: ctk.CTkFrame, row: int) -> None:
        """Build the recipient tracking table."""
        table_card = ctk.CTkFrame(
            master=parent,
            fg_color=COLOR_SURFACE_CONTAINER_LOWEST,
            corner_radius=RADIUS_CARD,
            border_width=BORDER_WIDTH_DEFAULT,
            border_color=COLOR_OUTLINE_VARIANT,
        )
        table_card.grid(
            row=row, column=0, sticky="nsew",
            pady=(SPACING_STACK_GAP, SPACING_STACK_GAP),
        )
        table_card.grid_rowconfigure(1, weight=1)
        table_card.grid_columnconfigure(0, weight=1)

        # -- Header row --
        header = ctk.CTkFrame(
            master=table_card,
            fg_color=COLOR_TABLE_HEADER_BG,
            corner_radius=0,
            height=40,
        )
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)
        header.grid_columnconfigure(0, weight=0, minsize=_COL_WIDTHS[0])
        header.grid_columnconfigure(1, weight=1, minsize=_COL_WIDTHS[1])
        header.grid_columnconfigure(2, weight=1, minsize=_COL_WIDTHS[2])
        header.grid_columnconfigure(3, weight=0, minsize=_COL_WIDTHS[3])

        headers = ["#", "NAME", "EMAIL", "STATUS"]
        for i, h in enumerate(headers):
            lbl = ctk.CTkLabel(
                master=header,
                text=h,
                font=_TABLE_HEADER_FONT,
                text_color=COLOR_OUTLINE,
                anchor="w",
            )
            lbl.grid(
                row=0, column=i, sticky="w",
                padx=(16 if i == 0 else 8, 8),
                pady=10,
            )

        # -- Scrollable body --
        body_scroll = ctk.CTkScrollableFrame(
            master=table_card,
            fg_color=COLOR_SURFACE_CONTAINER_LOWEST,
            corner_radius=0,
        )
        body_scroll.grid(row=1, column=0, sticky="nsew")
        body_scroll.grid_columnconfigure(0, weight=0, minsize=_COL_WIDTHS[0])
        body_scroll.grid_columnconfigure(1, weight=1, minsize=_COL_WIDTHS[1])
        body_scroll.grid_columnconfigure(2, weight=1, minsize=_COL_WIDTHS[2])
        body_scroll.grid_columnconfigure(3, weight=0, minsize=_COL_WIDTHS[3])

        self._table_body = body_scroll
        self._row_widgets: list[dict[str, ctk.CTkLabel | StatusBadge]] = []

        # Populate with demo data
        for i, row_data in enumerate(_DEMO_ROWS):
            self._add_table_row(i, row_data)

    def _add_table_row(self, index: int, data: dict[str, str]) -> None:
        """Add a single row to the table body.

        Args:
            index: Row index (for zebra striping).
            data: Dict with keys num, name, email, status.
        """
        row_bg = COLOR_TABLE_ROW_ALT if index % 2 == 1 else "transparent"

        # Row frame for the border-bottom effect
        row_frame = ctk.CTkFrame(
            master=self._table_body,
            fg_color=row_bg,
            corner_radius=0,
            height=48,
        )
        row_frame.grid(row=index, column=0, columnspan=4, sticky="ew")
        row_frame.grid_propagate(False)
        row_frame.grid_columnconfigure(0, weight=0, minsize=_COL_WIDTHS[0])
        row_frame.grid_columnconfigure(1, weight=1, minsize=_COL_WIDTHS[1])
        row_frame.grid_columnconfigure(2, weight=1, minsize=_COL_WIDTHS[2])
        row_frame.grid_columnconfigure(3, weight=0, minsize=_COL_WIDTHS[3])
        row_frame.grid_rowconfigure(0, weight=1)

        # # column
        num_lbl = ctk.CTkLabel(
            master=row_frame,
            text=data["num"],
            font=_TABLE_CELL_FONT,
            text_color=COLOR_ON_SURFACE_VARIANT,
            anchor="w",
        )
        num_lbl.grid(row=0, column=0, sticky="w", padx=(16, 8))

        # Name column
        name_lbl = ctk.CTkLabel(
            master=row_frame,
            text=data["name"],
            font=(FONT_FAMILY, 14, "bold"),
            text_color=COLOR_ON_SURFACE,
            anchor="w",
        )
        name_lbl.grid(row=0, column=1, sticky="w", padx=8)

        # Email column
        email_lbl = ctk.CTkLabel(
            master=row_frame,
            text=data["email"],
            font=_TABLE_CELL_FONT,
            text_color=COLOR_ON_SURFACE_VARIANT,
            anchor="w",
        )
        email_lbl.grid(row=0, column=2, sticky="w", padx=8)

        # Status badge
        variant = _STATUS_VARIANT_MAP.get(data["status"], BadgeVariant.PENDING)
        badge = StatusBadge(
            master=row_frame,
            variant=variant,
        )
        badge.grid(row=0, column=3, sticky="w", padx=8)

        self._row_widgets.append({
            "num": num_lbl,
            "name": name_lbl,
            "email": email_lbl,
            "badge": badge,
            "frame": row_frame,
        })

        # Bottom border
        border = ctk.CTkFrame(
            master=self._table_body,
            fg_color=COLOR_OUTLINE_VARIANT,
            height=1,
            corner_radius=0,
        )
        border.grid(
            row=index, column=0, columnspan=4, sticky="sew",
        )

    # ------------------------------------------------------------------
    # Public — table manipulation (Phase 4)
    # ------------------------------------------------------------------

    def update_row_status(self, index: int, status: str) -> None:
        """Update a single row's status badge.

        Args:
            index: Zero-based row index.
            status: One of 'sent', 'failed', 'sending', 'pending'.
        """
        if 0 <= index < len(self._row_widgets):
            variant = _STATUS_VARIANT_MAP.get(status, BadgeVariant.PENDING)
            self._row_widgets[index]["badge"].set_variant(variant)

    def set_time_remaining(self, text: str) -> None:
        """Update the estimated time remaining display.

        Args:
            text: Time string, e.g. '~ 4 minutes'.
        """
        self._time_value.configure(text=text)

    def clear_table(self) -> None:
        """Remove all rows from the table body."""
        for child in self._table_body.winfo_children():
            child.destroy()
        self._row_widgets.clear()

    def add_recipient_row(
        self,
        index: int,
        num: str,
        name: str,
        email: str,
        status: str = "pending",
    ) -> None:
        """Add a recipient row to the table.

        Args:
            index: Row index.
            num: Display number.
            name: Recipient name.
            email: Recipient email.
            status: Initial status string.
        """
        self._add_table_row(index, {
            "num": num,
            "name": name,
            "email": email,
            "status": status,
        })

    # ------------------------------------------------------------------
    # Private — handlers (Phase 4 will replace)
    # ------------------------------------------------------------------

    def _handle_stop(self) -> None:
        """Handle Stop button click — Phase 4 placeholder."""
        pass

    def _handle_export(self) -> None:
        """Handle Export Log click — Phase 4 placeholder."""
        pass
