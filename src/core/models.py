"""Data models for DakBabu.

Defines all shared dataclasses used across the application.
These are pure data containers — no business logic, no UI imports.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class RecipientStatus(Enum):
    """Possible states for a recipient during the send process."""

    PENDING = "Pending"
    SENDING = "Sending"
    SENT = "Sent"
    FAILED = "Failed"


@dataclass
class Recipient:
    """A single email recipient parsed from the Excel file.

    Attributes:
        name: Display name from the 'Name' column (empty string if absent).
        email: Email address from the mandatory 'Email' column.
        extra_fields: All other column values keyed by lowercase column name.
        status: Current send status, defaults to PENDING.
    """

    name: str
    email: str
    extra_fields: dict[str, str] = field(default_factory=dict)
    status: RecipientStatus = RecipientStatus.PENDING


@dataclass
class SendResult:
    """Outcome of sending a single email.

    Attributes:
        recipient: The recipient this result belongs to.
        success: Whether the email was sent successfully.
        error_message: Human-friendly error description if failed, empty if success.
        timestamp: When the send attempt completed.
    """

    recipient: Recipient
    success: bool
    error_message: str = ""
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class SmtpConfig:
    """SMTP server configuration for a given email provider.

    Attributes:
        host: SMTP server hostname (e.g. 'smtp.gmail.com').
        port: SMTP server port (e.g. 587 for STARTTLS).
        use_tls: Whether to use STARTTLS for the connection.
    """

    host: str
    port: int
    use_tls: bool = True


@dataclass
class EmailContent:
    """Composed email content ready for sending.

    Attributes:
        subject: Email subject line (may contain {{placeholders}}).
        body_html: Email body as HTML string (may contain {{placeholders}}).
        placeholders_used: Set of placeholder names found in subject + body
                           (lowercased, without curly braces).
    """

    subject: str
    body_html: str
    placeholders_used: set[str] = field(default_factory=set)


@dataclass
class ValidationResult:
    """Result of validating user input (Excel, Word template, etc.).

    Attributes:
        is_valid: True if validation passed with no blocking errors.
        errors: List of blocking error messages (user cannot proceed).
        warnings: List of non-blocking warnings (user may proceed).
    """

    is_valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
