# DakBabu — TODO

> Master task list derived from ARCHITECTURE.md. Check off tasks as completed.
> Each phase must be fully done before starting the next.

---

## Phase 1: Foundation

- [x] Create folder structure (`src/`, `src/core/`, `src/ui/`, `src/ui/components/`, `src/ui/steps/`, `src/workers/`, `assets/`, `tests/`)
- [x] Create all `__init__.py` files
- [x] Create `requirements.txt` with pinned versions:
  - customtkinter
  - openpyxl
  - python-docx
  - docx2pdf
  - pyinstaller
  - pywin32 (for COM automation / Word detection)
  - pytest (dev dependency)
- [x] Install dependencies into `.venv`
- [x] Create `src/core/models.py` — define all dataclasses:
  - `Recipient` (name, email, extra_fields dict, status)
  - `SendResult` (recipient, success, error_message, timestamp)
  - `SmtpConfig` (host, port, use_tls)
  - `EmailContent` (subject, body_html, placeholders_used)
  - `ValidationResult` (is_valid, errors list, warnings list)
- [x] Create `src/ui/theme.py` — extract ALL design tokens from `stitch_ui/step1_credentials/DESIGN.md`:
  - Color palette (primary, surface, error, success, etc.)
  - Typography (font family, sizes, weights for h1/h2/h3/body/label)
  - Spacing (container padding, stack gap, inline gap, section margin)
  - Border radii (card, input, pill button)
  - Elevation (border colors, shadow values)

**Phase 1 exit criteria:** Running `python -m src.main` doesn't crash (can be an empty window). All imports resolve.

---

## Phase 2: Core Logic

### 2a. Excel Reader
- [x] `src/core/excel_reader.py`:
  - Read .xlsx first row as headers (case-insensitive)
  - Find `Email` column (required) — error if missing
  - Treat all other columns as data columns
  - Validate email format per row (basic regex)
  - Detect duplicate emails — return count
  - Skip empty rows silently
  - Return list of `Recipient` objects + `ValidationResult`
- [x] `tests/test_excel_reader.py`:
  - Test: valid file with Name + Email columns
  - Test: missing Email column → error
  - Test: invalid email format → marked invalid
  - Test: duplicate emails → warning with count
  - Test: empty rows → skipped
  - Test: case-insensitive header matching
  - Test: extra columns preserved in Recipient.extra_fields

### 2b. Template Engine
- [x] `src/core/template_engine.py`:
  - Scan .docx for all `{{...}}` placeholders using regex
  - Return set of placeholder names found (lowercased)
  - Cross-validate placeholders against Excel column set
  - Generate personalized .docx copy for a given Recipient
  - Replace ALL occurrences (not just first) — case-insensitive
  - Handle placeholder inside Word doc runs (python-docx splits text across runs)
- [x] `tests/test_template_engine.py`:
  - Test: scan finds all placeholders
  - Test: case-insensitive matching
  - Test: multiple occurrences all replaced
  - Test: cross-validation catches missing columns
  - Test: cross-validation allows unused columns (no error)
  - Test: placeholder split across Word runs is handled

### 2c. Email Formatter
- [x] `src/core/email_formatter.py`:
  - Convert rich-text markup (bold/italic/underline tags) to HTML
  - Input: structured text with formatting metadata
  - Output: clean HTML string (`<strong>`, `<em>`, `<u>`, `<br>`)
  - Replace placeholders in the HTML string — all occurrences, case-insensitive

### 2d. Email Sender
- [x] `src/core/smtp_config.py`:
  - Domain → SmtpConfig lookup table (Gmail, Outlook, Yahoo)
  - Fallback for unknown domains
- [x] `src/core/email_sender.py`:
  - `test_connection(email, password, smtp_config)` → bool + error message
  - `send_email(email, password, smtp_config, to, subject, body_html, pdf_path)` → SendResult
  - MIME multipart: text/html body + application/pdf attachment
  - TLS/STARTTLS handling
- [x] `tests/test_smtp_config.py`:
  - Test: gmail.com → correct config
  - Test: outlook.com → correct config
  - Test: unknown domain → fallback
- [x] `tests/test_email_sender.py`:
  - Test: successful send (mocked SMTP)
  - Test: authentication failure (mocked)
  - Test: network error (mocked)

### 2e. PDF Converter & Word Checker
- [x] `src/core/pdf_converter.py`:
  - Convert .docx → .pdf using docx2pdf
  - Use `tempfile.TemporaryDirectory` for temp file management
  - Return Path to generated PDF
  - Handle conversion errors gracefully
- [x] `src/core/word_checker.py`:
  - Try `win32com.client.Dispatch("Word.Application")`
  - Return (is_available: bool, version: str | None)
  - Handle COM errors without crashing

**Phase 2 exit criteria:** All tests in `tests/` pass. `python -m pytest tests/ -v` shows green.

---

## Phase 3: UI Screens

### 3a. Core UI Framework
- [x] `src/ui/app.py`:
  - Root CTk window (title, icon, min size 900×600, default 1100×750)
  - Wizard navigation: show_step(n), track current step
  - Each step frame: validate(), get_data(), on_enter()
  - WM_DELETE_WINDOW handler for graceful shutdown
- [x] `src/ui/components/nav_bar.py` — match Stitch top header exactly
- [x] `src/ui/components/bottom_bar.py` — Back/Next footer, pill buttons
- [x] `src/ui/components/stepper.py` — step indicator (completed/active/pending)

### 3b. Reusable Components
- [x] `src/ui/components/file_picker.py` — dashed-border file upload area (match Stitch)
- [x] `src/ui/components/info_box.py` — blue info callout with icon
- [x] `src/ui/components/status_badge.py` — pill badges (Sent/Failed/Sending/Pending)
- [x] `src/ui/components/rich_textbox.py`:
  - tkinter.Text widget wrapped in CTk frame
  - Toolbar: Bold (B), Italic (I), Underline (U) buttons
  - Apply formatting via text tags on selected text
  - Export formatted content with tag metadata
- [x] `src/ui/dialogs.py` — error, warning, confirmation popups

### 3c. Wizard Steps
- [x] `src/ui/steps/step0_welcome.py`:
  - Show app name and brief instructions
  - Auto-detect Word in background → show status
  - Proceed button (or auto-proceed if Word found)
- [x] `src/ui/steps/step1_credentials.py` — match `stitch_ui/step1_credentials/screen.png`:
  - Email input, password input (masked + toggle visibility)
  - Info box about App Passwords
  - Test Connection button → shows success/failure badge
  - Next unlocks only after successful test
- [x] `src/ui/steps/step2_files.py` — match `stitch_ui/step2_files/screen.png`:
  - Recipient List section: file picker + recipient count + duplicate warning
  - Word Template section: file picker + placeholder validation result
  - Email Content section: subject input + rich text body
  - Download Sample Excel button
  - Info box with placeholder instructions
  - Warning at >500 recipients
  - Next unlocks only when all sections valid
- [x] `src/ui/steps/step3_preview.py` — match `stitch_ui/step3_preview/screen.png`:
  - Email preview card (To, Subject, Body with formatting)
  - Attachment info row
  - Recipient count confirmation
  - "Start Sending" button
- [x] `src/ui/steps/step4_tracker.py` — match `stitch_ui/step4_tracker/screen.png`:
  - Progress bar with count and percentage
  - Live table: #, Name, Email, Status (with status badges)
  - Stop button (red outline, pill shape)
  - Resume button (after stop)
  - Retry Failed button (after completion/stop, if failures exist)
  - Export Log as CSV button (disabled during send, enabled after)
  - Estimated time remaining
  - Scrollable table area

**Phase 3 exit criteria:** All screens render correctly. Navigation works. No business logic connected yet.

---

## Phase 4: Workers & Integration

- [x] `src/workers/connection_tester.py`:
  - Background thread: calls `core/email_sender.test_connection()`
  - Posts result to queue: `{type: "connection_result", success, error}`
- [x] `src/workers/send_worker.py`:
  - Background thread: iterates through recipients
  - For each: personalize doc → convert to PDF → send email
  - Posts per-recipient status updates to queue
  - Respects stop flag (threading.Event)
  - Supports resume (skip already-sent recipients)
  - Supports retry (re-queue only failed recipients)
  - Cleans up temp files when done or stopped
- [x] Wire Step 1 → connection_tester
- [x] Wire Step 2 → excel_reader + template_engine validation
- [x] Wire Step 3 → template_engine preview generation
- [ ] Wire Step 4 → send_worker (full pipeline)
- [ ] Implement queue polling in each step's `on_enter()`
- [ ] CSV export functionality (export log button)
- [ ] Sample Excel download functionality

**Phase 4 exit criteria:** Full end-to-end flow works. Can send real emails with real Excel/Word files.

---

## Phase 5: Polish & Package

- [ ] Edge case testing:
  - Missing Email column
  - Invalid emails
  - Missing placeholder columns
  - Empty Excel
  - Corrupted Excel/Word files
  - Wrong App Password
  - Network disconnection mid-send
  - Closing app during send
  - Very large Excel (1000+ rows)
- [ ] Create `assets/sample_recipients.xlsx`
- [ ] Place `assets/icon.ico` (user provides this)
- [ ] Create `build.spec` for PyInstaller:
  - `--onefile` mode
  - Bundle assets/ folder
  - Set icon
  - Set app name
- [ ] Build `.exe` and test on a clean Windows machine
- [ ] Create `README.md` with:
  - What the app does
  - How to use it (4 steps)
  - Requirements (Windows + Word)
  - Download link for .exe
- [ ] Final code review:
  - All theme constants used (no hardcoded colors)
  - All paths use pathlib.Path
  - No os.path imports
  - No tkinter imports in core/
  - No business logic in ui/
  - All errors shown as friendly messages
  - Password never on disk

**Phase 5 exit criteria:** `DakBabu.exe` runs on a clean Windows machine with Word installed. All edge cases handled gracefully.
