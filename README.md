# DakBabu 📬

> Named after the Indian postal worker — reliable, personal, built for everyone.

A desktop app for sending personalized bulk emails with PDF attachments.
Built for non-technical college staff who need to send acknowledgement 
letters to seminar attendees.

## What It Does
- Reads recipients from an Excel file
- Personalizes a Word document for each person → converts to PDF
- Sends each person a customized email with their PDF attached
- Tracks live send status per recipient
- Exports a send log as CSV

## Built With
- Python 3.11+
- customtkinter (GUI)
- python-docx + docx2pdf (Word/PDF)
- smtplib (Email)
- PyInstaller (.exe packaging)

## Status
🚧 Active development — Phase 2 (Core Logic)

## Setup (for developers)
```bash
git clone https://github.com/yourusername/dakbabu.git
cd dakbabu
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m src.main
```

## Requirements
- Windows 10/11
- Microsoft Word installed (for PDF conversion)
- Python 3.11+ (for development only)
