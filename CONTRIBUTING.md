# Contributing to DakBabu

## Development Setup

### Prerequisites
- Python 3.11 or later
- Microsoft Word (any version 2007+) — required for PDF conversion
- Windows OS (the app uses COM automation for Word)
- Git

### Initial Setup

```bash
# Clone the repository
git clone <repo-url>
cd DakBabu

# Activate the virtual environment
# On Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# On Windows (CMD):
.\.venv\Scripts\activate.bat

# Install dependencies
pip install -r requirements.txt
```

### Running the App

```bash
# Run from project root
python -m src.main
```

### Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run a specific test file
python -m pytest tests/test_excel_reader.py -v

# Run with coverage
python -m pytest tests/ --cov=src/core --cov-report=term-missing
```

### Building the .exe

```bash
pyinstaller build.spec
# Output: dist/DakBabu.exe
```

---

## Project Structure

```
src/
├── core/       # Pure business logic — NO tkinter imports
├── ui/         # All customtkinter code — NO business logic
│   ├── components/   # Reusable widgets
│   └── steps/        # One frame per wizard step
└── workers/    # Threading bridge between ui/ and core/
```

**Read `ARCHITECTURE.md` for the full explanation.**

---

## Coding Standards

### Python Style
- Follow PEP 8
- Maximum line length: 100 characters
- Use type hints for all function signatures
- Use docstrings for all public classes and functions (Google style)

### Naming Conventions
```python
# Files: snake_case
excel_reader.py
step1_credentials.py

# Classes: PascalCase
class ExcelReader:
class StepCredentials(ctk.CTkFrame):

# Functions/methods: snake_case
def read_recipients(file_path: Path) -> list[Recipient]:
def validate() -> bool:

# Constants: UPPER_SNAKE_CASE
PRIMARY_BLUE = "#2563EB"
MIN_WINDOW_WIDTH = 900

# Private methods: leading underscore
def _parse_headers(self) -> list[str]:
```

### Import Order
```python
# 1. Standard library
import re
import csv
from pathlib import Path
from dataclasses import dataclass

# 2. Third-party
import customtkinter as ctk
import openpyxl

# 3. Local
from src.core.models import Recipient
from src.ui.theme import PRIMARY_BLUE
```

### Path Handling
```python
# ALWAYS use pathlib.Path
from pathlib import Path

file_path = Path("data") / "recipients.xlsx"
temp_dir = Path(tempfile.mkdtemp())

# NEVER use os.path
# import os  # NO
# os.path.join(...)  # NO
```

### Error Handling
```python
# In core/ — raise descriptive exceptions
class ExcelValidationError(Exception):
    """Raised when the Excel file fails validation."""
    pass

def read_recipients(path: Path) -> list[Recipient]:
    if not path.exists():
        raise ExcelValidationError(f"File not found: {path.name}")
    # ...

# In ui/ — catch exceptions and show friendly dialogs
try:
    recipients = excel_reader.read_recipients(path)
except ExcelValidationError as e:
    self.show_error(str(e))
```

### Thread Safety
```python
# In workers/ — post to queue, never call tkinter
class SendWorker(threading.Thread):
    def __init__(self, queue: queue.Queue):
        self.queue = queue

    def run(self):
        # Do work...
        self.queue.put({"type": "status_update", "row": 5, "status": "Sent"})
        # NEVER do: self.some_label.configure(text="Done")  # WRONG

# In ui/ — poll queue from main thread
def poll_queue(self):
    while not self.queue.empty():
        msg = self.queue.get_nowait()
        # Update UI here (safe — we're in the main thread)
    self.after(100, self.poll_queue)
```

---

## Design Guidelines

### Use Theme Constants
```python
# CORRECT — import from theme
from src.ui.theme import PRIMARY_BLUE, FONT_BODY_MD, CARD_RADIUS

button = ctk.CTkButton(
    master=self,
    fg_color=PRIMARY_BLUE,
    corner_radius=PILL_RADIUS,
    font=FONT_BODY_MD,
)

# WRONG — hardcoded values
button = ctk.CTkButton(
    master=self,
    fg_color="#2563EB",     # Don't hardcode
    corner_radius=9999,     # Don't hardcode
    font=("Inter", 14),    # Don't hardcode
)
```

### Match the Stitch Reference
- Every screen has a reference design in `stitch_ui/stepN_*/screen.png`
- Match the layout, spacing, colors, and typography as closely as possible
- New UI elements (not in Stitch) must follow the same design language

---

## Architecture Rules

> These are non-negotiable. Read `CLAUDE.md` for the full rationale.

1. **`core/` never imports tkinter or customtkinter.**
2. **`ui/` never does file I/O, SMTP, Excel parsing, or Word operations.**
3. **`workers/` is the only bridge between ui/ and core/.**
4. **Workers never call tkinter methods.** They post to a `queue.Queue`.
5. **All colors/fonts/spacing come from `theme.py`.** No hardcoding.
6. **All paths use `pathlib.Path`.** Never `os.path`.
7. **The App Password is never written to disk.**

---

## Adding a New Feature

1. **Update `SPEC.md`** if the feature changes user-facing behavior
2. **Update `ARCHITECTURE.md`** if it affects the system design
3. **Write core logic first** in `src/core/` with unit tests
4. **Build the UI** in `src/ui/` using theme constants
5. **Wire them** through `src/workers/` if async work is needed
6. **Update `TODO.md`** to mark the task complete
7. **Test** with `python -m pytest tests/ -v`

---

## Commit Messages

Use clear, descriptive commit messages:

```
feat: add dynamic placeholder cross-validation
fix: handle empty rows in Excel without crashing
ui: match Step 2 file picker to Stitch design
refactor: extract SMTP config into separate module
test: add test for duplicate email detection
docs: update SPEC.md with retry-failed feature
```
