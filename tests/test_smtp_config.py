"""
Tests for the SMTP Configuration module.
"""

from src.core.smtp_config import get_smtp_config

def test_gmail_domain():
    """Test that gmail.com resolves to the correct config."""
    config = get_smtp_config("user@gmail.com")
    assert config is not None
    assert config.host == "smtp.gmail.com"
    assert config.port == 587
    assert config.use_tls is True

def test_outlook_domain():
    """Test that outlook.com resolves to the correct config."""
    config = get_smtp_config("user@outlook.com")
    assert config is not None
    assert config.host == "smtp.office365.com"
    assert config.port == 587
    assert config.use_tls is True

def test_yahoo_domain():
    """Test that yahoo.com resolves to the correct config."""
    config = get_smtp_config("user@yahoo.com")
    assert config is not None
    assert config.host == "smtp.mail.yahoo.com"
    assert config.port == 587
    assert config.use_tls is True

def test_unknown_domain():
    """Test that an unknown domain returns None (fallback)."""
    config = get_smtp_config("user@unknown-domain.xyz")
    assert config is None

def test_invalid_email():
    """Test that invalid email strings return None."""
    assert get_smtp_config("not-an-email") is None
    assert get_smtp_config("") is None
