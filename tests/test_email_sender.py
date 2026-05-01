"""
Tests for the email sender module.
"""

import smtplib
import socket
from unittest.mock import MagicMock, patch
from pathlib import Path

from src.core.email_sender import test_connection as check_connection, send_email
from src.core.models import SmtpConfig, Recipient


def test_test_connection_success():
    """Test successful SMTP connection and login."""
    config = SmtpConfig("smtp.test.com", 587, use_tls=True)
    
    with patch("src.core.email_sender.smtplib.SMTP") as mock_smtp:
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        success, error = check_connection("test@test.com", "password", config)
        
        assert success is True
        assert error == ""
        mock_server.ehlo.assert_called()
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with("test@test.com", "password")


def test_test_connection_auth_failure():
    """Test authentication failure during connection test."""
    config = SmtpConfig("smtp.test.com", 587, use_tls=True)
    
    with patch("src.core.email_sender.smtplib.SMTP") as mock_smtp:
        mock_server = MagicMock()
        # Raise SMTPAuthenticationError when login is called
        mock_server.login.side_effect = smtplib.SMTPAuthenticationError(535, b"Auth failed")
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        success, error = check_connection("test@test.com", "wrong_pass", config)
        
        assert success is False
        assert "App Password" in error


def test_test_connection_network_error():
    """Test network error during connection test."""
    config = SmtpConfig("smtp.test.com", 587, use_tls=True)
    
    with patch("src.core.email_sender.smtplib.SMTP") as mock_smtp:
        # Raise gaierror when trying to connect
        mock_smtp.side_effect = socket.gaierror("Name or service not known")
        
        success, error = check_connection("test@test.com", "password", config)
        
        assert success is False
        assert "Network error" in error


def test_send_email_success(tmp_path: Path):
    """Test successful email sending with attachment."""
    config = SmtpConfig("smtp.test.com", 587, use_tls=True)
    recipient = Recipient(name="Alice", email="alice@test.com")
    
    # Create a dummy PDF file
    pdf_path = tmp_path / "test.pdf"
    pdf_path.write_bytes(b"%PDF-1.4 mock pdf content")
    
    with patch("src.core.email_sender.smtplib.SMTP") as mock_smtp:
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        result = send_email(
            "sender@test.com", 
            "password", 
            config, 
            recipient, 
            "Test Subject", 
            "<p>Test Body</p>", 
            pdf_path
        )
        
        assert result.success is True
        assert result.error_message == ""
        assert result.recipient == recipient
        mock_server.send_message.assert_called_once()


def test_send_email_missing_attachment():
    """Test sending an email when the attachment is missing."""
    config = SmtpConfig("smtp.test.com", 587, use_tls=True)
    recipient = Recipient(name="Alice", email="alice@test.com")
    
    pdf_path = Path("/nonexistent/file.pdf")
    
    result = send_email(
        "sender@test.com", 
        "password", 
        config, 
        recipient, 
        "Test Subject", 
        "<p>Test Body</p>", 
        pdf_path
    )
    
    assert result.success is False
    assert "Attachment not found" in result.error_message


def test_send_email_auth_failure(tmp_path: Path):
    """Test sending an email with an authentication failure."""
    config = SmtpConfig("smtp.test.com", 587, use_tls=True)
    recipient = Recipient(name="Alice", email="alice@test.com")
    
    pdf_path = tmp_path / "test.pdf"
    pdf_path.write_bytes(b"content")
    
    with patch("src.core.email_sender.smtplib.SMTP") as mock_smtp:
        mock_server = MagicMock()
        mock_server.login.side_effect = smtplib.SMTPAuthenticationError(535, b"Auth failed")
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        result = send_email(
            "sender@test.com", 
            "password", 
            config, 
            recipient, 
            "Test Subject", 
            "<p>Test Body</p>", 
            pdf_path
        )
        
        assert result.success is False
        assert "Authentication failed" in result.error_message
