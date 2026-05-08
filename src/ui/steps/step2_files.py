"""Step 2 — Files & Email Content.

Scrollable step with three card sections: Recipient List, Word Template,
and Email Content.  Each card uses components from src/ui/components/.

Layout (from stitch_ui/step2_files/screen.png):
    ┌──────────────────────────────────────────────────────────┐
    │  Upload Files & Write Email                              │
    │                                                          │
    │  ┌─ Recipient List ────────────────────────────────────┐ │
    │  │  [  FilePicker — Upload Excel or CSV file         ] │ │
    │  │  ✓ Found 42 recipients   ⚠ 3 duplicate emails     │ │
    │  └─────────────────────────────────────────────────────┘ │
    │                                                          │
    │  ┌─ Word Template ─────────────────────────────────────┐ │
    │  │  [  FilePicker — Upload Word Document (.docx)     ] │ │
    │  │  ✓ Template looks good                             │ │
    │  └─────────────────────────────────────────────────────┘ │
    │                                                          │
    │  ┌─ Email Content ─────────────────────────────────────┐ │
    │  │  Subject Line                                       │ │
    │  │  ┌──────────────────────────────────────────────┐   │ │
    │  │  │  e.g. Your personalized monthly report       │   │ │
    │  │  └──────────────────────────────────────────────┘   │ │
    │  │  [ B ] [ I ] [ U ]                                  │ │
    │  │  ┌──────────────────────────────────────────────┐   │ │
    │  │  │  Dear {{name}}, please find your…            │   │ │
    │  │  └──────────────────────────────────────────────┘   │ │
    │  │  Use {{name}} anywhere for personalization          │ │
    │  └─────────────────────────────────────────────────────┘ │
    │                                                          │
    │  ┌─ℹ─ Instructions ───────────────────────────────────┐  │
    │  └────────────────────────────────────────────────────┘  │
    │                                                          │
    │           [ ⬇ Download Sample Excel ]                    │
    └──────────────────────────────────────────────────────────┘

All visual values imported from src.ui.theme.  Zero business logic.
No direct core/ imports — data flows via app.py shared state.
"""

from __future__ import annotations

from pathlib import Path

import customtkinter as ctk

from src.core import excel_reader, template_engine
from src.ui.theme import (
    COLOR_BACKGROUND,
    COLOR_ON_SURFACE,
    COLOR_ON_SURFACE_VARIANT,
    COLOR_OUTLINE,
    COLOR_OUTLINE_VARIANT,
    COLOR_PRIMARY_CONTAINER,
    COLOR_PRIMARY_HOVER,
    COLOR_ON_PRIMARY,
    COLOR_SURFACE_CONTAINER_LOWEST,
    COLOR_BUTTON_SECONDARY_TEXT,
    COLOR_BUTTON_SECONDARY_BORDER,
    FONT_FAMILY,
    FONT_H2,
    FONT_H3,
    FONT_BODY_MD,
    FONT_LABEL_SM,
    FONT_LABEL_MD,
    RADIUS_CARD,
    RADIUS_INPUT,
    RADIUS_PILL,
    BORDER_WIDTH_DEFAULT,
    SPACING_CONTAINER_PADDING,
    SPACING_STACK_GAP,
    ICON_DOWNLOAD,
)
from src.ui.components.file_picker import FilePicker
from src.ui.components.info_box import InfoBox
from src.ui.components.rich_textbox import RichTextbox
from src.ui.components.status_badge import StatusBadge, BadgeVariant


# ---------------------------------------------------------------------------
# Constants local to this step
# ---------------------------------------------------------------------------
_SECTION_ICON_FONT: tuple[str, int, str] = (FONT_FAMILY, 18, "normal")
_SUBJECT_HEIGHT: int = 42
_INPUT_FONT: tuple[str, int, str] = FONT_BODY_MD
_HINT_FONT: tuple[str, int, str] = (FONT_FAMILY, 12, "normal")
_DOWNLOAD_BTN_WIDTH: int = 200
_DOWNLOAD_BTN_HEIGHT: int = 36
_DOWNLOAD_BTN_FONT: tuple[str, int, str] = (FONT_FAMILY, 12, "bold")


class Step2Files(ctk.CTkFrame):
    """Files & email content step — upload Excel/Word, compose email.

    Provides ``get_data()`` returning file paths, subject, and body
    segments.  Badge areas are updated via public methods that Phase 4
    workers will call.

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

        # Stretch
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Tracking for overall validation state
        self._excel_valid: bool = False
        self._word_valid: bool = False

        # Stored data from processing
        self._recipients: list = []
        self._duplicate_count: int = 0
        self._placeholders: set[str] = set()
        self._excel_columns: set[str] = set()

        self._build()

    # ------------------------------------------------------------------
    # StepFrame protocol
    # ------------------------------------------------------------------

    def validate(self) -> bool:
        """Allow proceeding only when both Excel and Word are valid."""
        return self._excel_valid and self._word_valid

    def get_data(self) -> dict:
        """Return current file selections and email content."""
        return {
            "excel_path": self._excel_picker.selected_path,
            "word_path": self._word_picker.selected_path,
            "subject": self._subject_entry.get().strip(),
            "body_segments": self._body_editor.get_segments(),
            "body_text": self._body_editor.get_text(),
        }

    def on_enter(self) -> None:
        """Called when this step becomes visible."""
        pass

    # ------------------------------------------------------------------
    # Public API — for Phase 4 integration
    # ------------------------------------------------------------------

    def set_excel_result(
        self,
        recipient_count: int = 0,
        duplicate_count: int = 0,
        warnings: list[str] | None = None,
    ) -> None:
        """Show Excel validation badges.

        Args:
            recipient_count: Number of valid recipients found.
            duplicate_count: Number of duplicate emails detected.
            warnings: Optional list of warning strings.
        """
        # Clear previous badges
        for child in self._excel_badge_frame.winfo_children():
            child.destroy()

        if recipient_count > 0:
            badge = StatusBadge(
                master=self._excel_badge_frame,
                variant=BadgeVariant.SUCCESS,
                text=f"Found {recipient_count} recipients",
            )
            badge.pack(side="left", padx=(0, 8))

        if duplicate_count > 0:
            dup_badge = StatusBadge(
                master=self._excel_badge_frame,
                variant=BadgeVariant.WARNING,
                text=f"{duplicate_count} duplicate emails found",
            )
            dup_badge.pack(side="left")

    def set_word_result(
        self,
        valid: bool = True,
        message: str = "Template looks good",
    ) -> None:
        """Show Word template validation badge.

        Args:
            valid: Whether the template passed validation.
            message: Badge text.
        """
        for child in self._word_badge_frame.winfo_children():
            child.destroy()

        variant = BadgeVariant.SUCCESS if valid else BadgeVariant.FAILED
        badge = StatusBadge(
            master=self._word_badge_frame,
            variant=variant,
            text=message,
        )
        badge.pack(side="left")

    # ------------------------------------------------------------------
    # Private — build
    # ------------------------------------------------------------------

    def _build(self) -> None:
        """Assemble the scrollable step layout."""
        # Scrollable container
        scroll = ctk.CTkScrollableFrame(
            master=self,
            fg_color=COLOR_BACKGROUND,
            corner_radius=0,
        )
        scroll.grid(row=0, column=0, sticky="nsew")
        scroll.grid_columnconfigure(0, weight=1)

        # -- Page heading --
        heading = ctk.CTkLabel(
            master=scroll,
            text="Upload Files & Write Email",
            font=FONT_H2,
            text_color=COLOR_ON_SURFACE,
            anchor="w",
        )
        heading.grid(row=0, column=0, sticky="w", pady=(SPACING_STACK_GAP, 0))

        # -- Section 1: Recipient List --
        self._build_recipient_section(scroll, row=1)

        # -- Section 2: Word Template --
        self._build_template_section(scroll, row=2)

        # -- Section 3: Email Content --
        self._build_email_section(scroll, row=3)

        # -- Info box --
        info = InfoBox(
            master=scroll,
            text=(
                "Your Excel must have a column named Email. "
                "All other column headers become your placeholders — "
                "use {{column_name}} in your Word document or email body. "
                "Column order doesn't matter."
            ),
        )
        info.grid(row=4, column=0, sticky="ew", pady=(SPACING_STACK_GAP, 0))

        # -- Download Sample button (centered) --
        btn_frame = ctk.CTkFrame(
            master=scroll, fg_color="transparent", corner_radius=0,
        )
        btn_frame.grid(row=5, column=0, pady=(SPACING_STACK_GAP, SPACING_STACK_GAP))

        self._download_btn = ctk.CTkButton(
            master=btn_frame,
            text=f"{ICON_DOWNLOAD}  Download Sample Excel",
            font=_DOWNLOAD_BTN_FONT,
            width=_DOWNLOAD_BTN_WIDTH,
            height=_DOWNLOAD_BTN_HEIGHT,
            corner_radius=RADIUS_PILL,
            fg_color=COLOR_SURFACE_CONTAINER_LOWEST,
            hover_color=COLOR_OUTLINE_VARIANT,
            text_color=COLOR_BUTTON_SECONDARY_TEXT,
            border_width=BORDER_WIDTH_DEFAULT,
            border_color=COLOR_BUTTON_SECONDARY_BORDER,
            command=self._handle_download_sample,
        )
        self._download_btn.pack()

    # ------------------------------------------------------------------
    # Private — section builders
    # ------------------------------------------------------------------

    def _build_recipient_section(self, parent: ctk.CTkFrame, row: int) -> None:
        """Build the Recipient List card."""
        card = self._make_section_card(parent, row)

        # Section header
        self._section_header(card, "👥", "Recipient List")

        # File picker
        self._excel_picker = FilePicker(
            master=card,
            icon="📄",
            primary_text="Upload Excel or CSV file",
            hint_text="Click or drag and drop",
            filetypes=[("Excel files", "*.xlsx"), ("CSV files", "*.csv")],
            on_file_selected=self._on_excel_selected,
            on_file_cleared=self._on_excel_cleared,
        )
        self._excel_picker.pack(fill="x", padx=SPACING_CONTAINER_PADDING, pady=(8, 0))

        # Badge row
        self._excel_badge_frame = ctk.CTkFrame(
            master=card, fg_color="transparent", corner_radius=0,
        )
        self._excel_badge_frame.pack(
            fill="x",
            padx=SPACING_CONTAINER_PADDING,
            pady=(8, SPACING_CONTAINER_PADDING),
        )

    def _build_template_section(self, parent: ctk.CTkFrame, row: int) -> None:
        """Build the Word Template card."""
        card = self._make_section_card(parent, row)

        # Section header
        self._section_header(card, "📝", "Word Template")

        # File picker
        self._word_picker = FilePicker(
            master=card,
            icon="📄",
            primary_text="Upload Word Document (.docx)",
            hint_text="This will be attached as a PDF to each email",
            filetypes=[("Word documents", "*.docx")],
            on_file_selected=self._on_word_selected,
            on_file_cleared=self._on_word_cleared,
        )
        self._word_picker.pack(fill="x", padx=SPACING_CONTAINER_PADDING, pady=(8, 0))

        # Badge row
        self._word_badge_frame = ctk.CTkFrame(
            master=card, fg_color="transparent", corner_radius=0,
        )
        self._word_badge_frame.pack(
            fill="x",
            padx=SPACING_CONTAINER_PADDING,
            pady=(8, SPACING_CONTAINER_PADDING),
        )

    def _build_email_section(self, parent: ctk.CTkFrame, row: int) -> None:
        """Build the Email Content card."""
        card = self._make_section_card(parent, row)

        # Section header
        self._section_header(card, "✉", "Email Content")

        content = ctk.CTkFrame(
            master=card, fg_color="transparent", corner_radius=0,
        )
        content.pack(
            fill="x",
            padx=SPACING_CONTAINER_PADDING,
            pady=(0, SPACING_CONTAINER_PADDING),
        )

        # Subject label
        subj_label = ctk.CTkLabel(
            master=content,
            text="Subject Line",
            font=FONT_LABEL_MD,
            text_color=COLOR_ON_SURFACE,
            anchor="w",
        )
        subj_label.pack(fill="x")

        # Subject entry
        self._subject_entry = ctk.CTkEntry(
            master=content,
            placeholder_text="e.g. Your personalized monthly report",
            font=_INPUT_FONT,
            height=_SUBJECT_HEIGHT,
            corner_radius=RADIUS_INPUT,
            border_width=BORDER_WIDTH_DEFAULT,
            border_color=COLOR_OUTLINE_VARIANT,
            fg_color=COLOR_SURFACE_CONTAINER_LOWEST,
            text_color=COLOR_ON_SURFACE,
        )
        self._subject_entry.pack(fill="x", pady=(6, 0))

        # Body editor
        self._body_editor = RichTextbox(
            master=content,
            placeholder="Dear {{name}}, please find your attached document...",
            height=140,
        )
        self._body_editor.pack(fill="x", pady=(SPACING_STACK_GAP, 0))

        # Hint text
        hint = ctk.CTkLabel(
            master=content,
            text="Use {{name}} anywhere for personalization",
            font=_HINT_FONT,
            text_color=COLOR_ON_SURFACE_VARIANT,
            anchor="w",
        )
        hint.pack(fill="x", pady=(4, 0))

    # ------------------------------------------------------------------
    # Private — helpers
    # ------------------------------------------------------------------

    def _make_section_card(
        self,
        parent: ctk.CTkFrame,
        row: int,
    ) -> ctk.CTkFrame:
        """Create a white card frame for a section."""
        card = ctk.CTkFrame(
            master=parent,
            fg_color=COLOR_SURFACE_CONTAINER_LOWEST,
            corner_radius=RADIUS_CARD,
            border_width=BORDER_WIDTH_DEFAULT,
            border_color=COLOR_OUTLINE_VARIANT,
        )
        card.grid(
            row=row, column=0, sticky="ew",
            pady=(SPACING_STACK_GAP, 0),
        )
        return card

    def _section_header(
        self,
        parent: ctk.CTkFrame,
        icon: str,
        title: str,
    ) -> None:
        """Add a section header row (icon + title) inside a card."""
        row = ctk.CTkFrame(
            master=parent, fg_color="transparent", corner_radius=0,
        )
        row.pack(
            fill="x",
            padx=SPACING_CONTAINER_PADDING,
            pady=(SPACING_CONTAINER_PADDING, 0),
        )

        icon_lbl = ctk.CTkLabel(
            master=row,
            text=icon,
            font=_SECTION_ICON_FONT,
            text_color=COLOR_ON_SURFACE_VARIANT,
        )
        icon_lbl.pack(side="left")

        title_lbl = ctk.CTkLabel(
            master=row,
            text=title,
            font=FONT_H3,
            text_color=COLOR_ON_SURFACE,
            anchor="w",
        )
        title_lbl.pack(side="left", padx=(8, 0))

    # ------------------------------------------------------------------
    # Private — event handlers (placeholders for Phase 4)
    # ------------------------------------------------------------------

    def _on_excel_selected(self, path: object) -> None:
        """Read Excel, store recipients in app state, show badges."""
        file_path = Path(str(path))

        recipients, result = excel_reader.read_recipients(file_path)

        # Store in app state
        app = self._get_app()
        if app is not None:
            app.state["recipients"] = recipients
            app.state["excel_path"] = file_path
            app.state["excel_result"] = result

        # Count duplicates
        dupes = excel_reader.get_duplicate_emails(recipients)
        dup_count = sum(max(0, c - 1) for c in dupes.values())

        self._recipients = recipients
        self._duplicate_count = dup_count

        # Extract column names for later cross-validation
        columns, col_error = excel_reader.get_column_names(file_path)
        self._excel_columns = {c.lower() for c in columns}

        # Show badges
        self.set_excel_result(
            recipient_count=len(recipients),
            duplicate_count=dup_count,
            warnings=result.warnings if result.warnings else None,
        )

        self._excel_valid = result.is_valid and len(recipients) > 0
        self._update_next_button()

    def _on_excel_cleared(self) -> None:
        """Handle Excel file removal."""
        for child in self._excel_badge_frame.winfo_children():
            child.destroy()

        self._excel_valid = False
        self._recipients = []
        self._duplicate_count = 0
        self._excel_columns = set()

        app = self._get_app()
        if app is not None:
            app.state.pop("recipients", None)
            app.state.pop("excel_path", None)
            app.state.pop("excel_result", None)

        self._update_next_button()

    def _on_word_selected(self, path: object) -> None:
        """Scan Word doc for placeholders, cross-validate with Excel."""
        file_path = Path(str(path))

        # Scan the Word document for placeholders
        placeholders, error = template_engine.scan_docx_placeholders(file_path)

        if error is not None:
            self.set_word_result(valid=False, message=error)
            self._word_valid = False
            self._update_next_button()
            return

        self._placeholders = placeholders

        # Cross-validate if we have Excel columns already
        if self._excel_columns:
            result = template_engine.cross_validate_placeholders(
                placeholders, self._excel_columns
            )
            self._word_valid = result.is_valid

            if result.is_valid and not result.errors:
                message = (
                    "Template looks good"
                    if not placeholders
                    else f"Found {len(placeholders)} placeholder(s) — all matched"
                )
                self.set_word_result(valid=True, message=message)
            else:
                # Show first error as badge text
                self.set_word_result(
                    valid=False, message=result.errors[0] if result.errors else "Validation failed"
                )
        else:
            # No Excel yet — just report placeholders found
            self._word_valid = True
            message = (
                f"Found {len(placeholders)} placeholder(s)"
                if placeholders
                else "Template looks good"
            )
            self.set_word_result(valid=True, message=message)

        # Store in app state
        app = self._get_app()
        if app is not None:
            app.state["word_path"] = file_path
            app.state["word_placeholders"] = placeholders

        self._update_next_button()

    def _on_word_cleared(self) -> None:
        """Handle Word file removal."""
        for child in self._word_badge_frame.winfo_children():
            child.destroy()

        self._word_valid = False
        self._placeholders = set()

        app = self._get_app()
        if app is not None:
            app.state.pop("word_path", None)
            app.state.pop("word_placeholders", None)

        self._update_next_button()

    def _get_app(self) -> ctk.CTkBaseClass | None:
        """Traverse up to find the root App instance."""
        widget = self
        while widget is not None:
            if hasattr(widget, "_bottom_bar"):
                return widget  # type: ignore[return-value]
            widget = widget.master
        return None

    def _update_next_button(self) -> None:
        """Enable/disable the Next button based on current validation state."""
        app = self._get_app()
        if app is not None and hasattr(app, "_bottom_bar"):
            bottom_bar = app._bottom_bar
            if hasattr(bottom_bar, "set_next_enabled"):
                bottom_bar.set_next_enabled(
                    self._excel_valid and self._word_valid
                )

    def _handle_download_sample(self) -> None:
        """Download the sample Excel — Phase 4 will implement save."""
        pass
