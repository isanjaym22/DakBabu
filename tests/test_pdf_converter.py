"""
Tests for the PDF Converter module.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch
from src.core.pdf_converter import convert_docx_to_pdf_in_dir, managed_pdf_conversion

def get_mocked_docx2pdf(tmp_path=None, success=True):
    mock_docx2pdf = MagicMock()
    if success:
        def fake_convert(in_path, out_path):
            Path(out_path).touch()
        mock_docx2pdf.convert.side_effect = fake_convert
    else:
        def fake_convert_fail(in_path, out_path):
            pass # Do not create file
        mock_docx2pdf.convert.side_effect = fake_convert_fail
    return mock_docx2pdf

def test_convert_docx_to_pdf_success(tmp_path: Path):
    """Test successful conversion of docx to pdf."""
    docx_path = tmp_path / "test.docx"
    docx_path.touch()
    
    mock_docx2pdf = get_mocked_docx2pdf(success=True)
    
    with patch.dict(sys.modules, {'docx2pdf': mock_docx2pdf}):
        success, error, pdf_path = convert_docx_to_pdf_in_dir(docx_path, tmp_path)
        
        assert success is True
        assert error == ""
        assert pdf_path.exists()
        assert pdf_path.name == "test.pdf"

def test_convert_docx_to_pdf_missing_file(tmp_path: Path):
    """Test behavior when the input docx file is missing."""
    docx_path = tmp_path / "missing.docx"
    
    # Even without mocking, it should fail early
    mock_docx2pdf = get_mocked_docx2pdf(success=True)
    with patch.dict(sys.modules, {'docx2pdf': mock_docx2pdf}):
        success, error, pdf_path = convert_docx_to_pdf_in_dir(docx_path, tmp_path)
        
        assert success is False
        assert "not found" in error
        assert pdf_path is None

def test_convert_docx_to_pdf_conversion_failure(tmp_path: Path):
    """Test when docx2pdf fails to create the PDF."""
    docx_path = tmp_path / "test.docx"
    docx_path.touch()
    
    mock_docx2pdf = get_mocked_docx2pdf(success=False)
    
    with patch.dict(sys.modules, {'docx2pdf': mock_docx2pdf}):
        success, error, pdf_path = convert_docx_to_pdf_in_dir(docx_path, tmp_path)
        
        assert success is False
        assert "PDF file was not created" in error

def test_managed_pdf_conversion(tmp_path: Path):
    """Test the context manager handles temp dir creation and cleanup."""
    docx_path = tmp_path / "test.docx"
    docx_path.touch()
    
    mock_docx2pdf = get_mocked_docx2pdf(success=True)
    
    with patch.dict(sys.modules, {'docx2pdf': mock_docx2pdf}):
        saved_dir = None
        with managed_pdf_conversion(docx_path) as (success, error, pdf_path):
            assert success is True
            assert pdf_path.exists()
            assert pdf_path.name == "test.pdf"
            
            # The pdf should be in a temporary directory, not in tmp_path
            assert pdf_path.parent != tmp_path
            saved_dir = pdf_path.parent
            assert saved_dir.exists()
            
        # After exiting context, the temp directory and its contents should be deleted
        assert not saved_dir.exists()
