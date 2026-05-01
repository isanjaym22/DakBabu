"""
Email sending module.

Handles SMTP connections, connection testing, and sending MIME multipart
emails with HTML bodies and PDF attachments. 
Ensures all errors are caught and returned as friendly messages.
"""

import smtplib
from email.message import EmailMessage
from pathlib import Path
from datetime import datetime
import socket

from src.core.models import SmtpConfig, Recipient, SendResult


def test_connection(email: str, password: str, config: SmtpConfig) -> tuple[bool, str]:
    """
    Test the SMTP connection and authentication credentials.
    
    Args:
        email (str): The sender's email address.
        password (str): The sender's app password.
        config (SmtpConfig): The SMTP server configuration to use.
        
    Returns:
        tuple[bool, str]: A tuple containing a success boolean and an error message (if any).
    """
    try:
        # Establish connection
        with smtplib.SMTP(config.host, config.port, timeout=15) as server:
            if config.use_tls:
                server.ehlo()
                server.starttls()
                server.ehlo()
            
            # Attempt login
            server.login(email, password)
            return True, ""
            
    except smtplib.SMTPAuthenticationError:
        return False, "Could not connect. Please check your email and App Password are correct."
    except (socket.gaierror, socket.timeout, ConnectionRefusedError, smtplib.SMTPConnectError):
        return False, "Network error. Please check your internet connection and try again."
    except Exception as e:
        return False, f"An unexpected error occurred during connection: {str(e)}"


def send_email(
    email: str, 
    password: str, 
    config: SmtpConfig, 
    recipient: Recipient, 
    subject: str, 
    body_html: str, 
    pdf_path: Path
) -> SendResult:
    """
    Send a personalized email with a PDF attachment to a recipient.
    
    Args:
        email (str): The sender's email address.
        password (str): The sender's app password.
        config (SmtpConfig): The SMTP server configuration.
        recipient (Recipient): The recipient's details.
        subject (str): The email subject.
        body_html (str): The HTML email body.
        pdf_path (Path): Path to the PDF attachment to include.
        
    Returns:
        SendResult: The outcome of the send attempt.
    """
    try:
        # Construct the email message
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = email
        msg['To'] = recipient.email
        
        # Add HTML body
        msg.set_content("This email requires an HTML-capable email client.")
        msg.add_alternative(body_html, subtype='html')
        
        # Read and attach the PDF file
        try:
            pdf_data = pdf_path.read_bytes()
        except FileNotFoundError:
            return SendResult(
                recipient=recipient,
                success=False,
                error_message=f"Attachment not found: {pdf_path.name}",
                timestamp=datetime.now()
            )
        except Exception as e:
            return SendResult(
                recipient=recipient,
                success=False,
                error_message=f"Could not read attachment: {str(e)}",
                timestamp=datetime.now()
            )
            
        msg.add_attachment(
            pdf_data,
            maintype='application',
            subtype='pdf',
            filename=pdf_path.name
        )
        
        # Send the email
        with smtplib.SMTP(config.host, config.port, timeout=30) as server:
            if config.use_tls:
                server.ehlo()
                server.starttls()
                server.ehlo()
            
            server.login(email, password)
            server.send_message(msg)
            
        return SendResult(
            recipient=recipient,
            success=True,
            error_message="",
            timestamp=datetime.now()
        )
        
    except smtplib.SMTPAuthenticationError:
        return SendResult(
            recipient=recipient,
            success=False,
            error_message="Authentication failed. Please check your App Password.",
            timestamp=datetime.now()
        )
    except (socket.gaierror, socket.timeout, ConnectionRefusedError, smtplib.SMTPException) as e:
        return SendResult(
            recipient=recipient,
            success=False,
            error_message=f"Network/SMTP error: {str(e)}",
            timestamp=datetime.now()
        )
    except Exception as e:
        return SendResult(
            recipient=recipient,
            success=False,
            error_message=f"Failed to send email: {str(e)}",
            timestamp=datetime.now()
        )
