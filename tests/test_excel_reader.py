"""Tests for src.core.excel_reader.

Covers column validation, email format checking, duplicate detection,
empty row skipping, case-insensitive header matching, and extra column
preservation.
"""

import pytest
from pathlib import Path
from openpyxl import Workbook

from src.core.excel_reader import (
    read_recipients,
    get_column_names,
    get_duplicate_emails,
)
from src.core.models import RecipientStatus


@pytest.fixture
def tmp_xlsx(tmp_path: Path):
    """Factory fixture that creates a .xlsx file from rows.

    Usage:
        path = tmp_xlsx([["Email", "Name"], ["a@b.com", "Alice"]])
    """

    def _create(rows: list[list]) -> Path:
        """Write rows to a temporary .xlsx file and return its path.

        Args:
            rows: List of lists, where the first list is the header row.

        Returns:
            Path to the created .xlsx file.
        """
        wb = Workbook()
        ws = wb.active
        for row in rows:
            ws.append(row)
        file_path = tmp_path / "test_recipients.xlsx"
        wb.save(str(file_path))
        wb.close()
        return file_path

    return _create


class TestReadRecipients:
    """Tests for the read_recipients function."""

    def test_valid_file_with_name_and_email(self, tmp_xlsx) -> None:
        """Valid file with Name + Email columns returns recipients."""
        path = tmp_xlsx([
            ["Email", "Name"],
            ["alice@example.com", "Alice"],
            ["bob@example.com", "Bob"],
        ])

        recipients, result = read_recipients(path)

        assert result.is_valid is True
        assert len(result.errors) == 0
        assert len(recipients) == 2
        assert recipients[0].email == "alice@example.com"
        assert recipients[0].name == "Alice"
        assert recipients[1].email == "bob@example.com"
        assert recipients[1].name == "Bob"

    def test_missing_email_column_returns_error(self, tmp_xlsx) -> None:
        """File without an Email column produces a validation error."""
        path = tmp_xlsx([
            ["Name", "Department"],
            ["Alice", "CS"],
        ])

        recipients, result = read_recipients(path)

        assert result.is_valid is False
        assert len(recipients) == 0
        assert any("Email" in e for e in result.errors)

    def test_invalid_email_format_marked_failed(self, tmp_xlsx) -> None:
        """Rows with invalid email formats are marked as Failed."""
        path = tmp_xlsx([
            ["Email", "Name"],
            ["valid@example.com", "Valid"],
            ["not-an-email", "Invalid"],
            ["also@bad", "AlsoBad"],
        ])

        recipients, result = read_recipients(path)

        assert result.is_valid is True
        assert recipients[0].status == RecipientStatus.PENDING
        assert recipients[1].status == RecipientStatus.FAILED
        assert recipients[2].status == RecipientStatus.FAILED
        assert any("invalid email" in w.lower() for w in result.warnings)

    def test_duplicate_emails_warning_with_count(self, tmp_xlsx) -> None:
        """Duplicate emails produce a warning with the count."""
        path = tmp_xlsx([
            ["Email", "Name"],
            ["alice@example.com", "Alice1"],
            ["alice@example.com", "Alice2"],
            ["bob@example.com", "Bob"],
            ["bob@example.com", "Bob2"],
            ["bob@example.com", "Bob3"],
        ])

        recipients, result = read_recipients(path)

        assert result.is_valid is True
        assert len(recipients) == 5
        assert any("duplicate" in w.lower() for w in result.warnings)

    def test_empty_rows_skipped(self, tmp_xlsx) -> None:
        """Empty rows between data are silently skipped."""
        path = tmp_xlsx([
            ["Email", "Name"],
            ["alice@example.com", "Alice"],
            [None, None],
            ["", ""],
            ["bob@example.com", "Bob"],
        ])

        recipients, result = read_recipients(path)

        assert result.is_valid is True
        assert len(recipients) == 2

    def test_case_insensitive_header_matching(self, tmp_xlsx) -> None:
        """Headers like EMAIL, email, Email are all recognized."""
        path = tmp_xlsx([
            ["EMAIL", "NAME"],
            ["test@example.com", "Test"],
        ])

        recipients, result = read_recipients(path)

        assert result.is_valid is True
        assert len(recipients) == 1
        assert recipients[0].email == "test@example.com"
        assert recipients[0].name == "Test"

    def test_extra_columns_preserved_in_extra_fields(self, tmp_xlsx) -> None:
        """Extra columns are stored in Recipient.extra_fields."""
        path = tmp_xlsx([
            ["Email", "Name", "Department", "Roll_No"],
            ["a@b.com", "Alice", "Computer Science", "CS001"],
        ])

        recipients, result = read_recipients(path)

        assert result.is_valid is True
        assert len(recipients) == 1
        assert recipients[0].extra_fields["department"] == "Computer Science"
        assert recipients[0].extra_fields["roll_no"] == "CS001"

    def test_file_not_found_returns_error(self) -> None:
        """Nonexistent file produces a clear error."""
        fake_path = Path("/nonexistent/file.xlsx")

        recipients, result = read_recipients(fake_path)

        assert result.is_valid is False
        assert len(recipients) == 0
        assert any("not found" in e.lower() for e in result.errors)

    def test_empty_file_returns_error(self, tmp_xlsx) -> None:
        """Excel file with no data rows returns an error."""
        path = tmp_xlsx([
            ["Email", "Name"],
        ])

        recipients, result = read_recipients(path)

        assert result.is_valid is False
        assert any("no recipients" in e.lower() for e in result.errors)

    def test_large_recipient_list_warning(self, tmp_xlsx) -> None:
        """More than 500 recipients triggers a warning."""
        rows = [["Email", "Name"]]
        for i in range(501):
            rows.append([f"user{i}@example.com", f"User{i}"])

        path = tmp_xlsx(rows)

        recipients, result = read_recipients(path)

        assert result.is_valid is True
        assert len(recipients) == 501
        assert any("500" in w for w in result.warnings)

    def test_mixed_case_email_column(self, tmp_xlsx) -> None:
        """'eMaIl' header variant is still recognized."""
        path = tmp_xlsx([
            ["eMaIl", "Name"],
            ["x@y.com", "X"],
        ])

        recipients, result = read_recipients(path)

        assert result.is_valid is True
        assert len(recipients) == 1


class TestGetColumnNames:
    """Tests for the get_column_names function."""

    def test_returns_column_names(self, tmp_xlsx) -> None:
        """Returns list of header names from first row."""
        path = tmp_xlsx([
            ["Email", "Name", "Department"],
            ["a@b.com", "A", "CS"],
        ])

        columns, error = get_column_names(path)

        assert error is None
        assert columns == ["Email", "Name", "Department"]

    def test_missing_file_returns_error(self) -> None:
        """Nonexistent file returns an error string."""
        columns, error = get_column_names(Path("/no/such/file.xlsx"))

        assert len(columns) == 0
        assert error is not None
        assert "not found" in error.lower()


class TestGetDuplicateEmails:
    """Tests for the get_duplicate_emails function."""

    def test_no_duplicates(self) -> None:
        """No duplicates returns empty dict."""
        from src.core.models import Recipient

        recipients = [
            Recipient(name="A", email="a@b.com"),
            Recipient(name="B", email="c@d.com"),
        ]

        result = get_duplicate_emails(recipients)
        assert result == {}

    def test_detects_duplicates_case_insensitive(self) -> None:
        """Duplicates detected case-insensitively."""
        from src.core.models import Recipient

        recipients = [
            Recipient(name="A", email="Alice@Example.com"),
            Recipient(name="B", email="alice@example.com"),
            Recipient(name="C", email="unique@test.com"),
        ]

        result = get_duplicate_emails(recipients)
        assert "alice@example.com" in result
        assert result["alice@example.com"] == 2
        assert "unique@test.com" not in result
