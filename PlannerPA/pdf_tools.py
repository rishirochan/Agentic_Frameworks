"""PDF creation tool using weasyprint for markdown-to-PDF conversion."""

import os
import markdown
from weasyprint import HTML, CSS
from datetime import datetime
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field


# Output directory for PDFs
PDF_OUTPUT_DIR = "sandbox"

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_STYLES_PATH = os.path.join(SCRIPT_DIR, "pdf_styles.css")


class MarkdownToPDFInput(BaseModel):
    markdown_content: str = Field(description="The markdown text content to convert to PDF")
    filename: str = Field(description="Output filename (without .pdf extension)")
    title: str = Field(default=None, description="Optional title to add at the top of the PDF")


def _markdown_to_pdf(markdown_content: str, filename: str, title: str = None) -> str:
    """Convert markdown content to a PDF file."""
    try:
        # Ensure output directory exists
        os.makedirs(PDF_OUTPUT_DIR, exist_ok=True)
        
        # Clean filename
        safe_filename = "".join(c for c in filename if c.isalnum() or c in "._- ").strip()
        if not safe_filename:
            safe_filename = f"document_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        output_path = os.path.join(PDF_OUTPUT_DIR, f"{safe_filename}.pdf")
        
        # Add title if provided
        if title:
            markdown_content = f"# {title}\n\n{markdown_content}"
        
        # Convert markdown to HTML
        html_content = markdown.markdown(
            markdown_content,
            extensions=['tables', 'fenced_code', 'codehilite', 'toc']
        )
        
        # Wrap in full HTML document
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """
        
        # Generate PDF with external CSS
        html_doc = HTML(string=full_html)
        css = CSS(filename=PDF_STYLES_PATH)
        html_doc.write_pdf(output_path, stylesheets=[css])
        
        abs_path = os.path.abspath(output_path)
        return f"PDF created successfully: {abs_path}"
    
    except Exception as e:
        return f"Error creating PDF: {str(e)}"


def get_pdf_tools() -> list:
    """Returns list of PDF tools for LangChain integration."""
    return [
        StructuredTool.from_function(
            func=_markdown_to_pdf,
            name="create_pdf_from_markdown",
            description=(
                "Convert markdown text to a styled PDF document. "
                "Input: markdown_content (the text to convert), filename (output name without .pdf), "
                "and optionally title (adds a header). "
                "The PDF will be saved to the sandbox folder."
            ),
            args_schema=MarkdownToPDFInput
        ),
    ]
