"""
Email formatter module.

This module converts structured rich-text segments into clean HTML for email bodies.
It replaces placeholders and handles basic formatting (bold, italic, underline).
"""

import html
import re
from dataclasses import dataclass
from typing import List, Dict

from src.core.template_engine import replace_placeholders


@dataclass
class TextSegment:
    """Represents a segment of text with its formatting metadata.
    
    Attributes:
        text (str): The raw text content.
        bold (bool): Whether the text is bold.
        italic (bool): Whether the text is italic.
        underline (bool): Whether the text is underlined.
    """
    text: str
    bold: bool = False
    italic: bool = False
    underline: bool = False


def format_email_html(segments: List[TextSegment], placeholders: Dict[str, str]) -> str:
    """
    Converts a list of formatted text segments into an HTML string,
    replacing placeholders with their corresponding values.
    
    Args:
        segments (List[TextSegment]): The structured text segments.
        placeholders (Dict[str, str]): A dictionary of lowercase placeholder names and their replacement values.
        
    Returns:
        str: The final HTML string with formatting and replaced placeholders.
    """
    html_parts = []
    
    for segment in segments:
        # Escape HTML special characters to prevent injection
        safe_text = html.escape(segment.text)
        
        # Convert newlines to HTML line breaks
        safe_text = safe_text.replace("\n", "<br>")
        
        # Apply formatting
        if segment.bold:
            safe_text = f"<strong>{safe_text}</strong>"
        if segment.italic:
            safe_text = f"<em>{safe_text}</em>"
        if segment.underline:
            safe_text = f"<u>{safe_text}</u>"
            
        html_parts.append(safe_text)
        
    full_html = "".join(html_parts)
    
    # Replace placeholders
    if placeholders:
        full_html = replace_placeholders(full_html, placeholders)
        
    return full_html
