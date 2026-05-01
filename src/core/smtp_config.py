"""
SMTP Configuration module.

Provides a lookup mechanism to determine the correct SMTP server details
(host, port, and TLS usage) based on the sender's email domain.
Supports common providers like Gmail, Outlook, and Yahoo.
"""

from src.core.models import SmtpConfig


def get_smtp_config(email_address: str) -> SmtpConfig | None:
    """
    Determine the SMTP configuration based on the provided email address domain.
    
    Args:
        email_address (str): The email address to parse the domain from.
        
    Returns:
        SmtpConfig | None: The configuration if the domain is recognized,
                           otherwise None to indicate a fallback is needed.
    """
    if not email_address or "@" not in email_address:
        return None
        
    domain = email_address.split("@")[-1].lower().strip()
    
    # Gmail
    if domain == "gmail.com":
        return SmtpConfig(host="smtp.gmail.com", port=587, use_tls=True)
        
    # Outlook / Hotmail
    if domain in ["outlook.com", "hotmail.com", "live.com", "msn.com"]:
        return SmtpConfig(host="smtp.office365.com", port=587, use_tls=True)
        
    # Yahoo
    if domain in ["yahoo.com", "ymail.com", "rocketmail.com", "yahoo.in", "yahoo.co.in", "yahoo.co.uk"]:
        return SmtpConfig(host="smtp.mail.yahoo.com", port=587, use_tls=True)
        
    return None
