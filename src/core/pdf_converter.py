"""
PDF Converter module.

Handles the conversion of Word documents (.docx) to PDF format using docx2pdf.
Manages temporary files safely and ensures all conversion errors are
caught and handled gracefully.
"""

import tempfile
from pathlib import Path
from contextlib import contextmanager
from typing import Generator

def convert_docx_to_pdf_in_dir(docx_path: Path, output_dir: Path) -> tuple[bool, str, Path | None]:
    """
    Converts a .docx file to a .pdf file inside the specified output directory.
    
    Args:
        docx_path (Path): Path to the source .docx file.
        output_dir (Path): Path to the directory where the PDF should be saved.
        
    Returns:
        tuple[bool, str, Path | None]: Success flag, error message if any, and the path to the PDF.
    """
    try:
        from docx2pdf import convert
        
        if not docx_path.exists():
            return False, f"Source document not found: {docx_path.name}", None
            
        pdf_name = docx_path.stem + ".pdf"
        pdf_path = output_dir / pdf_name
        
        # docx2pdf.convert(input_path, output_path)
        convert(str(docx_path), str(pdf_path))
        
        if not pdf_path.exists():
            return False, "Conversion completed but PDF file was not created.", None
            
        return True, "", pdf_path
        
    except Exception as e:
        return False, f"Failed to convert document to PDF: {str(e)}", None


@contextmanager
def managed_pdf_conversion(docx_path: Path) -> Generator[tuple[bool, str, Path | None], None, None]:
    """
    Context manager that converts a .docx file to a .pdf in a temporary directory,
    yielding the result. Once the context is exited, the temporary directory
    (and the PDF inside it) is automatically deleted.
    
    Args:
        docx_path (Path): Path to the source .docx file.
        
    Yields:
        tuple[bool, str, Path | None]: Success flag, error message, and PDF path.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)
        success, error, pdf_path = convert_docx_to_pdf_in_dir(docx_path, temp_dir_path)
        yield success, error, pdf_path
