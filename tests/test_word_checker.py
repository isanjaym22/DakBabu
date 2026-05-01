"""
Tests for the Word Checker module.
"""

import sys
from unittest.mock import MagicMock, patch
from src.core.word_checker import check_word_installed

def test_check_word_installed_success():
    """Test successful detection of MS Word."""
    mock_pythoncom = MagicMock()
    mock_win32com = MagicMock()
    mock_client = MagicMock()
    mock_word = MagicMock()
    
    mock_word.Version = "16.0"
    mock_client.Dispatch.return_value = mock_word
    mock_win32com.client = mock_client
    
    with patch.dict(sys.modules, {'pythoncom': mock_pythoncom, 'win32com': mock_win32com, 'win32com.client': mock_client}):
        success, version = check_word_installed()
        
        assert success is True
        assert version == "16.0"
        mock_word.Quit.assert_called_once()
        mock_pythoncom.CoInitialize.assert_called_once()
        mock_pythoncom.CoUninitialize.assert_called_once()

def test_check_word_installed_dispatch_failure():
    """Test when MS Word is not installed (Dispatch fails)."""
    mock_pythoncom = MagicMock()
    mock_win32com = MagicMock()
    mock_client = MagicMock()
    
    mock_client.Dispatch.side_effect = Exception("Class not registered")
    mock_win32com.client = mock_client
    
    with patch.dict(sys.modules, {'pythoncom': mock_pythoncom, 'win32com': mock_win32com, 'win32com.client': mock_client}):
        success, version = check_word_installed()
        
        assert success is False
        assert version is None

def test_check_word_installed_import_error():
    """Test when pywin32 is not installed (e.g. running on Linux without mock)."""
    # Force ImportError by removing from sys.modules if it exists and patching __import__
    with patch("builtins.__import__", side_effect=ImportError("No module named win32com")):
        success, version = check_word_installed()
        
        assert success is False
        assert version is None
