# DakBabu — Product Specification

## What Is This?
DakBabu is a desktop application that helps non-technical college staff send
personalized bulk emails with PDF attachments. It is named after the Indian
postal worker — reliable, personal, and built for everyone.

## The Problem
A college HOD needs to send personalized thank-you letters or any mass email
with attached documents to seminar attendees. They have an Excel sheet with
names, emails, and other data, plus a Word letter template, and need to send
each person a customized email with their personalized letter attached as a
PDF. They are not technical. It must just work.

## Who Uses It
A non-technical HOD or college staff member on a Windows laptop.
Assume they have never used a terminal. Assume they will make mistakes.
The app must guide them and never crash.

## What They Provide
1. An Excel file (.xlsx) with at least an `Email` column, plus any number of
   data columns (Name, Department, Roll_No, etc.)
2. A Word document (.docx) with `{{placeholder}}` markers that match Excel
   column headers (e.g. `{{name}}`, `{{department}}`)
3. An email subject and body (typed inside the app) also using `{{placeholder}}`
   markers — the body supports basic formatting (Bold, Italic, Underline)

## What the App Does
- Reads each recipient from the Excel file
- Personalizes the Word document by replacing **all** `{{placeholder}}` markers
  with matching column values from each recipient's row
- Converts that personalized Word doc to a PDF
- Sends an email to each recipient with:
  - Their personalized data in the subject and body (placeholders replaced)
  - Their personalized PDF attached
- Shows a live status tracker (Pending / Sending / Sent / Failed) per recipient
- Lets the user retry failed emails selectively
- Lets the user export the final send log as a CSV

## Delivery Format
A single `.exe` file. No Python, no terminal, no installation required.
The target machine must have Microsoft Word installed (required for PDF
conversion). The app auto-detects Word at startup and warns if missing.

## Core Constraints

### Must Have
- Startup check: auto-detect MS Word installation (all versions 2007+)
- 4-step wizard UI (credentials → files → preview → send) preceded by a
  welcome/check screen (Step 0)
- SMTP email sending with App Password support (Gmail, Outlook, Yahoo)
- Dynamic placeholder engine: any Excel column → `{{column_name}}` in the
  Word doc and email body. Case-insensitive matching. All occurrences replaced.
- Cross-validation: every placeholder in the doc/email must have a matching
  Excel column — clear error if not
- Rich text email body with Bold/Italic/Underline toolbar (sent as HTML
  under the hood — user never sees HTML)
- Live per-recipient status tracking during send
- PDF attachment generated per recipient from Word template
- Retry failed emails with selective re-queue
- Stop & Resume: user can stop mid-batch, go back, and continue later
- CSV log export after sending
- Sample Excel template bundled in the app for download
- Warning when recipient count exceeds 500
- Resizable window with minimum 900×600
- Works as a standalone `.exe` via PyInstaller

### Must Not
- Never crash on bad input — show friendly errors instead
- Never send emails without a preview/confirmation step
- Never block the UI during sending — use background threads
- Never leave temp files behind if something fails
- Never persist the App Password to disk — hold in memory only, clear on exit

### Technical Constraints
- Language: Python 3.11+
- GUI must use the provided Stitch-generated UI code as the design reference
  (located in `stitch_ui/` folder). Adapt it to customtkinter components.
  All new UI elements must follow the same design language.
- PDF conversion: docx2pdf (requires MS Word on machine)
- Packaging: PyInstaller into single .exe
- Use pathlib.Path everywhere, never os.path
- Separate UI logic from business logic completely (see ARCHITECTURE.md)
- core/ must never import tkinter; ui/ must never do file I/O or SMTP directly

## Placeholder System

### How It Works
- The first row of the Excel file defines column headers
- The `Email` column is mandatory — it is the send target, not a placeholder
- Every other column (Name, Department, Roll_No, Sl. No., etc.) becomes an
  available `{{placeholder}}`
- Placeholders in the Word doc, email subject, and email body are matched
  against Excel column headers **case-insensitively**
- If the same placeholder appears multiple times in a document or email, **all
  occurrences** are replaced
- If a placeholder in the doc has no matching Excel column, the app shows an
  error and blocks proceeding
- If an Excel column is never used as a placeholder, it is silently ignored —
  no warning

### Sample Excel
The app bundles a downloadable sample Excel to help users get started:

| Email | Name | Department |
|---|---|---|
| priya@example.com | Priya Sharma | Computer Science |
| rohit@example.com | Rohit Verma | Electrical |

Instructions shown in-app:
- Your Excel must have a column named **Email**
- All other column headers become your placeholders
- Use `{{column_name}}` in your Word document or email body
- Column names and placeholder names must match (capitalization doesn't matter)
- Column order doesn't matter

## Edge Cases the App Must Handle
- Excel missing Email column → show clear error, don't proceed
- Invalid email format in Excel → skip that row, mark as Failed in tracker
- Placeholder in Word doc with no matching Excel column → show clear error
  listing the missing columns, block proceeding
- Placeholder in email body with no matching Excel column → show clear error,
  block proceeding
- `{{placeholder}}` missing from email body but present in doc → silently
  allow (no requirement that every placeholder appears everywhere)
- Wrong app password → caught during connection test in Step 1
- One email fails mid-batch → continue the rest, mark that row red, allow retry
- Duplicate emails in Excel → warn with count, let user decide to proceed
- Empty rows in Excel → silently skip
- More than 500 recipients → show yellow warning about provider limits
- App closed during send → clean shutdown, no orphan threads or temp files
- MS Word not installed → detected at startup, friendly error with instructions
- Extra columns in Excel (like Sl. No.) → treated normally, no errors

## The Wizard Flow

### Step 0 — Welcome & System Check
App auto-detects MS Word installation in the background.
If Word is found, proceed automatically. If not, show a friendly message
explaining that Word is required for PDF conversion.

### Step 1 — Credentials
User enters their sending email and App Password.
App auto-detects SMTP settings from the email domain.
A "Test Connection" button verifies credentials before allowing Next.
Password is masked with a toggle-visibility button.

### Step 2 — Files & Email
User selects the Excel file → app immediately shows recipient count and
lists detected columns. Warns if >500 recipients or duplicates found.
User selects the Word template → app scans for all `{{placeholder}}`
markers and cross-validates against Excel columns.
User types the email subject and body using a rich text editor with
Bold/Italic/Underline toolbar. Placeholders work here too.
A "Download Sample Excel" button is available.
Next button only unlocks when all sections are valid.

### Step 3 — Preview
Shows how the email will look for the first recipient with all placeholders
filled in, including formatted text.
Shows the attachment info.
Confirms how many recipients will receive the email.
User confirms before anything is sent.

### Step 4 — Send & Track
Live table showing each recipient's status updating in real time.
Progress bar with count (e.g. "Sending 12 of 42...").
Stop button to abort mid-batch cleanly (finishes current email first).
Resume button to continue from where the user left off.
Retry Failed button to re-queue only the failed rows.
Export Log button (enabled after completion or stop) saves CSV.
User can go Back after stopping to review/fix things.

## What Success Looks Like
A HOD with zero technical knowledge opens DakBabu.exe, follows the steps,
and 50 personalized emails with PDF attachments are sent in under 10 minutes.
If anything goes wrong, they see a friendly message — not a crash.
If some emails fail, they can retry just those. If they need to stop and
come back, they can resume without re-sending already-sent emails.