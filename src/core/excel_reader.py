"""Excel file reader for DakBabu.

Reads .xlsx files, validates required columns, detects duplicate emails,
skips empty rows, and returns a list of Recipient objects with a
ValidationResult summarizing any errors or warnings.

This module is pure business logic — no tkinter or UI imports.
"""

import re
from pathlib import Path

from openpyxl import load_workbook
from openpyxl.workbook import Workbook
from openpyxl.worksheet.worksheet import Worksheet

from src.core.models import Recipient, RecipientStatus, ValidationResult


# Basic email validation regex — intentionally permissive.
# Checks for: something @ something . something
_EMAIL_REGEX: re.Pattern[str] = re.compile(
    r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
)


def _is_valid_email(email: str) -> bool:
    """Check whether a string looks like a valid email address.

    Args:
        email: The string to validate.

    Returns:
        True if the string matches a basic email pattern, False otherwise.
    """
    return bool(_EMAIL_REGEX.match(email.strip()))


def _is_row_empty(row: tuple, col_count: int) -> bool:
    """Check whether an Excel row is entirely empty or whitespace.

    Args:
        row: A tuple of cell values from openpyxl.
        col_count: Number of header columns to check.

    Returns:
        True if every cell in the relevant range is None or blank.
    """
    for i in range(col_count):
        value = row[i].value if hasattr(row[i], "value") else row[i]
        if value is not None and str(value).strip() != "":
            return False
    return True


def read_recipients(
    file_path: Path,
) -> tuple[list[Recipient], ValidationResult]:
    """Read an Excel file and extract recipients with validation.

    Reads the first row as headers (case-insensitive). Requires an 'Email'
    column. All other columns become data fields on each Recipient.

    Args:
        file_path: Path to the .xlsx file to read.

    Returns:
        A tuple of (recipients list, ValidationResult).
        On critical failure (file not found, no Email column, etc.),
        returns an empty list with errors in the ValidationResult.
    """
    try:
        return _read_recipients_impl(file_path)
    except FileNotFoundError:
        return [], ValidationResult(
            is_valid=False,
            errors=[f"File not found: {file_path.name}"],
        )
    except PermissionError:
        return [], ValidationResult(
            is_valid=False,
            errors=[
                f"Cannot open '{file_path.name}' — it may be open in "
                f"another program. Please close it and try again."
            ],
        )
    except Exception as exc:
        return [], ValidationResult(
            is_valid=False,
            errors=[
                f"Could not read '{file_path.name}': {exc}"
            ],
        )


def _read_recipients_impl(
    file_path: Path,
) -> tuple[list[Recipient], ValidationResult]:
    """Internal implementation of read_recipients.

    Separated from the public function so that the try/except wrapper
    in read_recipients catches all exceptions uniformly.

    Args:
        file_path: Path to the .xlsx file.

    Returns:
        Tuple of (recipients list, ValidationResult).
    """
    errors: list[str] = []
    warnings: list[str] = []

    # --- Load workbook ---
    wb: Workbook = load_workbook(filename=str(file_path), read_only=True, data_only=True)
    ws: Worksheet = wb.active  # type: ignore[assignment]

    if ws is None:
        wb.close()
        return [], ValidationResult(
            is_valid=False,
            errors=["The Excel file has no active worksheet."],
        )

    # --- Read headers from first row ---
    header_row = next(ws.iter_rows(min_row=1, max_row=1), None)
    if header_row is None:
        wb.close()
        return [], ValidationResult(
            is_valid=False,
            errors=["The Excel file is empty — no header row found."],
        )

    # Map: column index → original header name (stripped)
    # Map: lowercase header → column index (for lookup)
    headers: dict[int, str] = {}
    header_lower_to_idx: dict[str, int] = {}

    for idx, cell in enumerate(header_row):
        value = cell.value
        if value is not None and str(value).strip() != "":
            header_name = str(value).strip()
            headers[idx] = header_name
            header_lower_to_idx[header_name.lower()] = idx

    if not headers:
        wb.close()
        return [], ValidationResult(
            is_valid=False,
            errors=["The first row is empty — no column headers found."],
        )

    # --- Find mandatory Email column ---
    email_col_idx: int | None = header_lower_to_idx.get("email")

    if email_col_idx is None:
        wb.close()
        found_cols = ", ".join(headers.values())
        return [], ValidationResult(
            is_valid=False,
            errors=[
                f"No 'Email' column found. Your Excel file must have a "
                f"column named 'Email'. Found columns: {found_cols}"
            ],
        )

    # --- Determine Name column (optional) ---
    name_col_idx: int | None = header_lower_to_idx.get("name")

    # --- Build list of data column indices (everything except Email) ---
    data_col_indices: list[int] = [
        idx for idx in headers if idx != email_col_idx
    ]

    col_count: int = len(headers)

    # --- Read data rows ---
    recipients: list[Recipient] = []
    seen_emails: dict[str, int] = {}  # lowercase email → first occurrence row
    invalid_email_count: int = 0
    skipped_empty: int = 0

    for row_num, row in enumerate(
        ws.iter_rows(min_row=2), start=2
    ):
        # Skip empty rows
        if _is_row_empty(row, max(headers.keys()) + 1 if headers else 0):
            skipped_empty += 1
            continue

        # Extract email
        email_cell = row[email_col_idx] if email_col_idx < len(row) else None
        raw_email = (
            str(email_cell.value).strip()
            if email_cell is not None and email_cell.value is not None
            else ""
        )

        if raw_email == "":
            skipped_empty += 1
            continue

        # Validate email format
        valid_email = _is_valid_email(raw_email)
        if not valid_email:
            invalid_email_count += 1

        # Track duplicates (by lowercase email)
        email_lower = raw_email.lower()
        if email_lower in seen_emails:
            seen_emails[email_lower] += 1
        else:
            seen_emails[email_lower] = 1

        # Extract name (optional)
        name_value = ""
        if name_col_idx is not None and name_col_idx < len(row):
            cell_val = row[name_col_idx].value
            if cell_val is not None:
                name_value = str(cell_val).strip()

        # Extract extra fields (all data columns except Name)
        extra_fields: dict[str, str] = {}
        for col_idx in data_col_indices:
            if col_idx == name_col_idx:
                continue  # Name is stored separately
            if col_idx < len(row):
                col_name_lower = headers[col_idx].lower()
                cell_val = row[col_idx].value
                extra_fields[col_name_lower] = (
                    str(cell_val).strip() if cell_val is not None else ""
                )

        # Determine initial status
        status = (
            RecipientStatus.PENDING
            if valid_email
            else RecipientStatus.FAILED
        )

        recipients.append(
            Recipient(
                name=name_value,
                email=raw_email,
                extra_fields=extra_fields,
                status=status,
            )
        )

    wb.close()

    # --- Build warnings ---
    # Duplicate emails
    duplicates = {
        email: count for email, count in seen_emails.items() if count > 1
    }
    total_dupes = sum(count - 1 for count in duplicates.values())
    if total_dupes > 0:
        warnings.append(
            f"Found {total_dupes} duplicate email(s). "
            f"{len(duplicates)} email address(es) appear more than once."
        )

    # Invalid emails
    if invalid_email_count > 0:
        warnings.append(
            f"{invalid_email_count} recipient(s) have invalid email "
            f"addresses and will be marked as Failed."
        )

    # Large recipient list
    if len(recipients) > 500:
        warnings.append(
            f"Your list has {len(recipients)} recipients. Gmail limits "
            f"sending to ~500 emails/day for regular accounts. Some "
            f"emails may fail due to provider limits."
        )

    # No valid recipients
    if len(recipients) == 0:
        errors.append(
            "No recipients found in the Excel file. Make sure your "
            "file has data rows below the header row."
        )

    is_valid = len(errors) == 0

    return recipients, ValidationResult(
        is_valid=is_valid,
        errors=errors,
        warnings=warnings,
    )


def get_column_names(file_path: Path) -> tuple[list[str], str | None]:
    """Read just the column headers from an Excel file.

    Useful for quick validation without reading all rows.

    Args:
        file_path: Path to the .xlsx file.

    Returns:
        A tuple of (list of column header names, error message or None).
        On failure, returns an empty list and an error string.
    """
    try:
        wb: Workbook = load_workbook(
            filename=str(file_path), read_only=True, data_only=True
        )
        ws: Worksheet = wb.active  # type: ignore[assignment]

        if ws is None:
            wb.close()
            return [], "The Excel file has no active worksheet."

        header_row = next(ws.iter_rows(min_row=1, max_row=1), None)
        if header_row is None:
            wb.close()
            return [], "The Excel file is empty — no header row found."

        columns: list[str] = []
        for cell in header_row:
            if cell.value is not None and str(cell.value).strip() != "":
                columns.append(str(cell.value).strip())

        wb.close()

        if not columns:
            return [], "The first row is empty — no column headers found."

        return columns, None

    except FileNotFoundError:
        return [], f"File not found: {file_path.name}"
    except PermissionError:
        return [], (
            f"Cannot open '{file_path.name}' — it may be open in "
            f"another program. Please close it and try again."
        )
    except Exception as exc:
        return [], f"Could not read '{file_path.name}': {exc}"


def get_duplicate_emails(
    recipients: list[Recipient],
) -> dict[str, int]:
    """Count duplicate email addresses in a recipient list.

    Args:
        recipients: List of Recipient objects to scan.

    Returns:
        A dict mapping each duplicated email (lowercase) to its count.
        Only emails appearing more than once are included.
    """
    counts: dict[str, int] = {}
    for r in recipients:
        key = r.email.lower()
        counts[key] = counts.get(key, 0) + 1

    return {email: count for email, count in counts.items() if count > 1}
