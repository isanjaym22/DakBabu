# DakBabu — Product Specification

## What Is This?
DakBabu is a desktop application that helps non-technical college staff send
personalized bulk emails with PDF attachments. It is named after the Indian
postal worker — reliable, personal, and built for everyone.

## The Problem
A college HOD needs to send personalized thank-you letters or any mass email sender with attached doc to seminar attendees. 
They have an Excel sheet with names and emails, a Word letter
template, and need to send each person a customized email with their
personalized letter attached as a PDF. They are not technical. It must
just work.

## Who Uses It
A non-technical HOD or college staff member on a Windows laptop.
Assume they have never used a terminal. Assume they will make mistakes.
The app must guide them and never crash.

## What They Provide
1. An Excel file (.xlsx) with at least two columns: Name and Email
2. A Word document (.docx) with `{{name}}` as a placeholder for the recipient
3. An email subject and body (typed inside the app) also using `{{name}}`

## What the App Does
- Reads each recipient from the Excel file
- Personalizes the Word document by replacing `{{name}}` with each person's name
- Converts that personalized Word doc to a PDF
- Sends an email to each recipient with:
  - Their name in the subject and body
  - Their personalized PDF attached
- Shows a live status tracker (Pending / Sending / Sent / Failed) per recipient
- Lets the user export the final send log as a CSV

## Delivery Format
A single `.exe` file. No Python, no terminal, no installation required.
The target machine will have Microsoft Word installed (required for PDF conversion).

## Core Constraints

### Must Have
- 4-step wizard UI (credentials → files → preview → send)
- SMTP email sending with App Password support (Gmail, Outlook, Yahoo)
- Live per-recipient status tracking during send
- PDF attachment generated per recipient from Word template
- CSV log export after sending
- Works as a standalone `.exe` via PyInstaller

### Must Not
- Never crash on bad input — show friendly errors instead
- Never send emails without a preview/confirmation step
- Never block the UI during sending — use background threads
- Never leave temp files behind if something fails

### Technical Constraints
- Language: Python 3.11+
- GUI must use the provided Stitch-generated UI code as the design reference
  (located in `stitch_ui/` folder). Adapt it to customtkinter components.
- PDF conversion: docx2pdf (requires MS Word on machine)
- Packaging: PyInstaller into single .exe
- Use pathlib.Path everywhere, never os.path
- Separate UI logic from business logic completely

## Edge Cases the App Must Handle
- Excel missing Name or Email column → show clear error, don't proceed
- Invalid email format in Excel → skip that row, mark as Failed in tracker
- `{{name}}` missing from Word doc → warn user, block proceeding
- `{{name}}` missing from email body → warn but allow proceeding
- Wrong app password → caught during connection test in Step 1
- One email fails mid-batch → continue the rest, mark that row red
- Duplicate emails in Excel → warn with count, let user decide to proceed
- Empty rows in Excel → silently skip
- App closed during send → clean shutdown, no orphan threads or temp files

## The 4-Step Wizard Flow

### Step 1 — Credentials
User enters their sending email and App Password.
App auto-detects SMTP settings from the email domain.
A "Test Connection" button verifies credentials before allowing Next.

### Step 2 — Files & Email
User selects the Excel file → app immediately shows recipient count.
User selects the Word template → app checks for `{{name}}` placeholder.
User types the email subject and body.
Next button only unlocks when all three sections are valid.

### Step 3 — Preview
Shows how the email will look for the first recipient with name filled in.
Confirms how many recipients will receive the email.
User confirms before anything is sent.

### Step 4 — Send & Track
Live table showing each recipient's status updating in real time.
Progress bar with count (e.g. "Sending 12 of 42...").
Stop button to abort mid-batch cleanly.
Export Log button (enabled after completion) saves CSV.

## What Success Looks Like
A HOD with zero technical knowledge opens DakBabu.exe, follows 4 steps,
and 50 personalized emails with PDF attachments are sent in under 10 minutes.
If anything goes wrong, they see a friendly message — not a crash.