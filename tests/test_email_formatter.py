"""
Tests for the email formatter module.
"""

from src.core.email_formatter import TextSegment, format_email_html

def test_format_email_html_basic():
    """Test basic formatting without placeholders."""
    segments = [
        TextSegment(text="Hello ", bold=True),
        TextSegment(text="World", italic=True),
        TextSegment(text="!", underline=True),
    ]
    html_output = format_email_html(segments, {})
    assert html_output == "<strong>Hello </strong><em>World</em><u>!</u>"

def test_format_email_html_placeholders():
    """Test formatting with placeholders."""
    segments = [
        TextSegment(text="Dear {{name}},", bold=False),
        TextSegment(text="\nWelcome to ", bold=False),
        TextSegment(text="{{department}}", bold=True),
    ]
    placeholders = {"name": "Alice", "department": "CS"}
    html_output = format_email_html(segments, placeholders)
    expected = "Dear Alice,<br>Welcome to <strong>CS</strong>"
    assert html_output == expected

def test_format_email_html_escaping():
    """Test HTML escaping to prevent injection."""
    segments = [
        TextSegment(text="<script>alert('xss')</script>"),
    ]
    html_output = format_email_html(segments, {})
    assert "<script>" not in html_output
    assert "&lt;script&gt;" in html_output

def test_format_email_html_empty():
    """Test empty segments."""
    assert format_email_html([], {}) == ""
