"""
Word Checker module.

Provides functionality to detect if Microsoft Word is installed on the user's
machine via COM automation. Used at app startup to ensure PDF conversion
will be possible.
"""

def check_word_installed() -> tuple[bool, str | None]:
    """
    Detects if Microsoft Word is installed via COM automation.
    
    Returns:
        tuple[bool, str | None]: A tuple containing:
            - is_available (bool): True if Word is successfully accessed.
            - version (str | None): The version string of Word, or None if failed.
    """
    try:
        import pythoncom
        import win32com.client
        
        # Initialize COM for the current thread
        pythoncom.CoInitialize()
        
        try:
            # Try to dispatch Word application
            word = win32com.client.Dispatch("Word.Application")
            version = str(word.Version)
            # Make sure to quit the application to not leave zombie processes
            word.Quit()
            return True, version
        finally:
            # Always uninitialize COM
            pythoncom.CoUninitialize()
            
    except ImportError:
        # pywin32 is not installed or we are not on Windows
        return False, None
    except Exception:
        # Catch all other COM errors or instantiation failures
        return False, None
