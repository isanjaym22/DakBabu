# CLAUDE.md — AI Coding Assistant Context

> This file provides context for AI coding assistants (Claude, Gemini, etc.)
> working on the DakBabu project. Read this file first before making changes.

## Project Overview

DakBabu is a **Windows desktop app** for non-technical college staff to send
personalized bulk emails with PDF attachments. Built with Python 3.11+ and
customtkinter. Packaged as a single `.exe` via PyInstaller.

**Read these files before doing anything:**
1. `SPEC.md` — Full product specification
2. `ARCHITECTURE.md` — Tech stack, folder structure, design decisions
3. `TODO.md` — Current progress and remaining tasks
4. `stitch_ui/` — Visual design reference (HTML + PNG screenshots)

---

## Critical Rules — Do NOT Violate

### Architecture Boundary (The Hard Rule)

```
src/core/     →  ZERO tkinter/customtkinter imports. Pure Python only.
src/ui/       →  ZERO file I/O, SMTP, Excel, or Word operations.
src/workers/  →  Bridge between ui/ and core/ using threading + queue.Queue.
```

**If you find yourself importing `tkinter` in `core/`, you are doing it wrong.**
**If you find yourself calling `openpyxl` in `ui/`, you are doing it wrong.**

### Path Handling
```python
# CORRECT
from pathlib import Path
file_path = Path("data") / "recipients.xlsx"

# WRONG — never use os.path
import os
file_path = os.path.join("data", "recipients.xlsx")
```

### Thread Safety
- All long-running operations (SMTP test, batch send, PDF conversion) run in
  background threads via `src/workers/`.
- UI updates happen through `queue.Queue` + `root.after()` polling.
- **Never call tkinter methods from a worker thread.** Post to the queue instead.

### Error Handling
- **Never let an exception crash the app.** Catch everything, show a friendly
  error dialog via `src/ui/dialogs.py`.
- Every user-facing error must be understandable by someone who has never used
  a terminal.
- Bad: `"SMTPAuthenticationError: (535, b'5.7.8 Username and Password...')"` 
- Good: `"Could not connect. Please check your email and App Password are correct."`

### Password Safety
- The App Password is held in a Python variable only during the session.
- **Never write it to disk.** No config files, no logs, no temp files.
- Clear it when the app closes.

---

## Design System

The UI must faithfully reproduce the designs in `stitch_ui/`. Key tokens:

| Token | Value |
|---|---|
| Font | Inter (fallback: Segoe UI) |
| Primary Blue | `#2563EB` |
| Background | `#FAF8FF` |
| Surface (cards) | `#FFFFFF` |
| Border | `#C3C6D7` |
| Text Primary | `#191B23` |
| Text Secondary | `#434655` |
| Error Red | `#BA1A1A` |
| Success Green | emerald-50/700 tones |
| Button radius | `9999` (pill shape) |
| Card radius | `10px` |
| Input radius | `8px` |
| Container padding | `32px` |

All design tokens are centralized in `src/ui/theme.py`. **Never hardcode colors
or fonts in step/component files.** Always import from theme.

---

## Placeholder Engine Rules

- Regex pattern: `\{\{([^}]+)\}\}` — matches anything inside `{{ }}`
- Matching is **case-insensitive**: `{{Name}}` matches Excel column `name`
- **All occurrences** of the same placeholder are replaced (not just the first)
- Cross-validation: every placeholder in the doc/email must have a matching
  Excel column. Missing columns = error. Unused columns = silently ignored.
- The `Email` column is special — it is the send target, never a placeholder.

---

## File-by-File Responsibilities

| File | Does | Does NOT |
|---|---|---|
| `core/excel_reader.py` | Read .xlsx, validate columns, detect dupes, count recipients | Display UI, show dialogs |
| `core/template_engine.py` | Scan placeholders, cross-validate, generate personalized .docx copies | Touch tkinter, show errors |
| `core/pdf_converter.py` | Convert .docx → .pdf via docx2pdf, manage temp files | Display progress bars |
| `core/email_sender.py` | SMTP connection, test credentials, send email with attachment | Update UI elements |
| `core/email_formatter.py` | Convert rich-text markup (bold/italic/underline) to HTML | Parse tkinter text tags directly |
| `core/smtp_config.py` | Map email domains to SMTP settings | Show dropdowns or UI |
| `core/word_checker.py` | Detect MS Word via COM automation | Show dialogs |
| `core/models.py` | Define dataclasses (Recipient, SendResult, etc.) | Contain logic |
| `ui/theme.py` | Centralize all design tokens (colors, fonts, spacing) | Contain widget code |
| `ui/app.py` | Root window, wizard navigation, step switching | Business logic |
| `ui/components/*` | Reusable widgets (stepper, file picker, etc.) | File I/O, SMTP |
| `ui/steps/*` | One frame per wizard step | Direct core/ calls |
| `workers/send_worker.py` | Background thread for batch sending, queue updates | Call tkinter directly |
| `workers/connection_tester.py` | Background thread for SMTP test | Call tkinter directly |

---

## Common Pitfalls

1. **Forgetting to replace ALL placeholder occurrences.** Use `re.sub` with
   a compiled case-insensitive pattern, not `str.replace`.

2. **Blocking the UI thread.** Any operation that takes > 100ms must go through
   a worker thread. This includes: SMTP connect, Excel parsing of large files,
   Word-to-PDF conversion.

3. **Temp file leaks.** Always use `tempfile.TemporaryDirectory` as a context
   manager. Register `atexit` and `WM_DELETE_WINDOW` handlers as safety nets.

4. **Hardcoding colors/fonts.** Always use `theme.py` constants. If you need a
   new color, add it to theme.py first.

5. **Using os.path.** Use `pathlib.Path`. Always. The spec is explicit about this.

6. **Forgetting case-insensitive matching.** Column headers and placeholder
   names are matched with `.lower()`. Don't assume consistent casing.

7. **Calling tkinter from a thread.** This will cause random crashes. Always
   post to a queue and let the main thread process it via `root.after()`.

---

## Testing

- Unit tests live in `tests/` and cover `src/core/` only.
- No GUI tests — the UI layer is thin enough to verify manually.
- Run tests with: `python -m pytest tests/ -v`
- Mock SMTP connections in tests — never send real emails in tests.

---

## Build & Package

```bash
# Install dependencies
pip install -r requirements.txt

# Run in development
python -m src.main

# Build standalone .exe
pyinstaller build.spec
```

The `.exe` is a single file — no installer, no dependencies for the end user.
The target machine only needs Microsoft Word for PDF conversion.
