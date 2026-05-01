"""Template engine for DakBabu.

Scans Word documents (.docx) and plain text for {{placeholder}} markers,
cross-validates them against Excel column names, and generates personalized
copies with all placeholders replaced.

Handles the python-docx "split runs" problem where a single placeholder
like {{name}} may be split across multiple runs due to Word formatting.

This module is pure business logic — no tkinter or UI imports.
"""

import copy
import re
from pathlib import Path
from typing import IO

from docx import Document
from docx.opc.exceptions import PackageNotFoundError

from src.core.models import Recipient, ValidationResult


# Regex pattern to match {{placeholder}} markers.
# Captures the name inside the braces (without the braces themselves).
# Example: "{{Name}}" → captures "Name"
_PLACEHOLDER_PATTERN: re.Pattern[str] = re.compile(
    r"\{\{([^}]+)\}\}"
)


def scan_placeholders(text: str) -> set[str]:
    """Find all {{placeholder}} markers in a text string.

    Placeholder names are returned lowercased for case-insensitive matching.

    Args:
        text: The text to scan for placeholders.

    Returns:
        A set of placeholder names (lowercased, without braces).
        Example: {"name", "department"} for text containing
        "Dear {{Name}}, from {{Department}}".
    """
    matches = _PLACEHOLDER_PATTERN.findall(text)
    return {m.strip().lower() for m in matches}


def cross_validate_placeholders(
    placeholders: set[str],
    column_names: set[str],
) -> ValidationResult:
    """Check that every placeholder has a matching Excel column.

    The 'email' column is excluded from available placeholders since it
    is the send target, not a data placeholder.

    Unused columns (present in Excel but not in placeholders) are silently
    ignored — no warning is raised.

    Args:
        placeholders: Set of placeholder names (lowercased) found in the
            document or email.
        column_names: Set of Excel column names (lowercased) available
            for substitution.

    Returns:
        A ValidationResult. is_valid is False if any placeholder has no
        matching column, with human-friendly error messages listing each
        missing column.
    """
    # Email is the send target, not available as a placeholder
    available_columns = {c for c in column_names if c != "email"}

    missing = placeholders - available_columns
    errors: list[str] = []

    if missing:
        for name in sorted(missing):
            errors.append(
                f"Placeholder '{{{{{name}}}}}' found in document but no "
                f"'{name.title()}' column exists in your Excel file."
            )

    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
    )


def replace_placeholders(text: str, data: dict[str, str]) -> str:
    """Replace all {{placeholder}} markers in text with values from data.

    Matching is case-insensitive: {{Name}}, {{name}}, and {{NAME}} all
    match a key "name" in the data dict. All occurrences are replaced,
    not just the first.

    Args:
        text: The text containing {{placeholder}} markers.
        data: A dict mapping lowercase placeholder names to their
            replacement values.

    Returns:
        The text with all matched placeholders replaced.
        Unmatched placeholders are left as-is.
    """
    def _replacer(match: re.Match) -> str:
        """Replace a single placeholder match with its value.

        Args:
            match: The regex match object for a {{placeholder}}.

        Returns:
            The replacement value, or the original match if not found.
        """
        key = match.group(1).strip().lower()
        return data.get(key, match.group(0))

    return _PLACEHOLDER_PATTERN.sub(_replacer, text)


def scan_docx_placeholders(file_path: Path) -> tuple[set[str], str | None]:
    """Scan a Word document for all {{placeholder}} markers.

    Reads all paragraphs (including those inside tables) and scans
    each for placeholder patterns. Handles placeholders that are split
    across multiple runs by concatenating run texts before scanning.

    Args:
        file_path: Path to the .docx file.

    Returns:
        A tuple of (set of placeholder names lowercased, error or None).
        On failure, returns an empty set and an error message.
    """
    try:
        doc = Document(str(file_path))
    except PackageNotFoundError:
        return set(), (
            f"'{file_path.name}' is not a valid Word document (.docx). "
            f"Please select a .docx file."
        )
    except PermissionError:
        return set(), (
            f"Cannot open '{file_path.name}' — it may be open in "
            f"another program. Please close it and try again."
        )
    except Exception as exc:
        return set(), f"Could not read '{file_path.name}': {exc}"

    placeholders: set[str] = set()

    # Scan all paragraphs in the document body
    for paragraph in doc.paragraphs:
        full_text = _get_paragraph_text(paragraph)
        placeholders.update(scan_placeholders(full_text))

    # Scan all paragraphs inside tables
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    full_text = _get_paragraph_text(paragraph)
                    placeholders.update(scan_placeholders(full_text))

    return placeholders, None


def _get_paragraph_text(paragraph) -> str:
    """Get the full text of a paragraph by concatenating all runs.

    This handles the python-docx problem where a single placeholder
    like {{name}} may be split across multiple runs due to formatting.

    Args:
        paragraph: A python-docx Paragraph object.

    Returns:
        The concatenated text of all runs in the paragraph.
    """
    return "".join(run.text for run in paragraph.runs)


def generate_personalized_docx(
    template_path: Path,
    recipient: Recipient,
    output_path: Path,
) -> tuple[bool, str]:
    """Create a personalized copy of a Word template for a recipient.

    Opens the template, replaces all {{placeholder}} markers with the
    recipient's data, and saves the result to output_path.

    Handles placeholders split across multiple Word runs by
    reconstructing run text after replacement.

    Args:
        template_path: Path to the original .docx template.
        recipient: The Recipient whose data is used for replacement.
        output_path: Path where the personalized .docx is saved.

    Returns:
        A tuple of (success: bool, error_message: str).
        On success, error_message is empty.
    """
    try:
        return _generate_personalized_docx_impl(
            template_path, recipient, output_path
        )
    except PackageNotFoundError:
        return False, (
            f"'{template_path.name}' is not a valid Word document (.docx)."
        )
    except PermissionError:
        return False, (
            f"Cannot access '{template_path.name}' — it may be open "
            f"in another program."
        )
    except Exception as exc:
        return False, f"Failed to personalize document: {exc}"


def _generate_personalized_docx_impl(
    template_path: Path,
    recipient: Recipient,
    output_path: Path,
) -> tuple[bool, str]:
    """Internal implementation of generate_personalized_docx.

    Args:
        template_path: Path to the .docx template.
        recipient: Recipient data for placeholder replacement.
        output_path: Where to save the personalized document.

    Returns:
        Tuple of (success, error_message).
    """
    doc = Document(str(template_path))

    # Build the replacement data dict (all keys lowercased)
    data = _build_replacement_data(recipient)

    # Replace placeholders in all body paragraphs
    for paragraph in doc.paragraphs:
        _replace_in_paragraph(paragraph, data)

    # Replace placeholders in all table cells
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    _replace_in_paragraph(paragraph, data)

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    doc.save(str(output_path))
    return True, ""


def _build_replacement_data(recipient: Recipient) -> dict[str, str]:
    """Build a flat dict of placeholder name → value from a Recipient.

    Includes the 'name' field and all extra_fields. Keys are lowercased.
    The 'email' key is excluded since it's the send target, not a
    placeholder (though it won't cause harm if present).

    Args:
        recipient: The Recipient to extract data from.

    Returns:
        A dict mapping lowercase placeholder names to string values.
    """
    data: dict[str, str] = {}

    # Add name if present
    if recipient.name:
        data["name"] = recipient.name

    # Add all extra fields (already keyed by lowercase name)
    data.update(recipient.extra_fields)

    return data


def _replace_in_paragraph(paragraph, data: dict[str, str]) -> None:
    """Replace all {{placeholder}} markers in a paragraph's runs.

    Handles the python-docx "split runs" problem. The strategy:
    1. Concatenate all run texts to get the full paragraph text.
    2. Check if the paragraph contains any placeholders.
    3. If yes, perform replacement on the full text, then redistribute
       the replaced text back into the runs (preserving the first run's
       formatting for the entire result, since placeholder replacement
       shouldn't change formatting).

    Args:
        paragraph: A python-docx Paragraph object.
        data: Dict mapping lowercase placeholder names to values.
    """
    runs = paragraph.runs
    if not runs:
        return

    # Get full paragraph text by joining all runs
    full_text = "".join(run.text for run in runs)

    # Quick check: does this paragraph even contain placeholders?
    if "{{" not in full_text:
        return

    # Perform the replacement on the full text
    replaced_text = replace_placeholders(full_text, data)

    # If nothing changed, no need to update runs
    if replaced_text == full_text:
        return

    # Redistribute the replaced text back into runs.
    # Strategy: put all text into the first run, clear the rest.
    # This preserves the first run's formatting for the replaced text.
    # While not perfect for mixed formatting within a placeholder,
    # it correctly handles the most common case where the placeholder
    # itself is uniformly formatted.
    runs[0].text = replaced_text
    for run in runs[1:]:
        run.text = ""
