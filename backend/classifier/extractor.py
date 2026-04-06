"""
extractor.py — PDF Text Extraction
Pulls raw text from uploaded PDF files using pdfplumber (primary)
with PyPDF2 as fallback if pdfplumber fails.

Why two libraries?
- pdfplumber is better at complex layouts, tables, multi-column docs
- PyPDF2 is faster and works when pdfplumber struggles
"""

import pdfplumber
import PyPDF2
import os
from backend.core.logger import logger
from backend.core.exceptions import ClassificationException


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract all text from a PDF file.
    Tries pdfplumber first, falls back to PyPDF2.
    Returns cleaned raw text string.
    """
    if not os.path.exists(file_path):
        raise ClassificationException(f"File not found: {file_path}")

    # Primary: pdfplumber — handles complex layouts better
    try:
        text = _extract_with_pdfplumber(file_path)
        if text and len(text.strip()) > 50:
            logger.info(f"Extracted {len(text)} chars via pdfplumber: {os.path.basename(file_path)}")
            return text
    except Exception as e:
        logger.warning(f"pdfplumber failed: {e} — trying PyPDF2")

    # Fallback: PyPDF2
    try:
        text = _extract_with_pypdf2(file_path)
        if text and len(text.strip()) > 50:
            logger.info(f"Extracted {len(text)} chars via PyPDF2: {os.path.basename(file_path)}")
            return text
    except Exception as e:
        logger.error(f"PyPDF2 also failed: {e}")

    raise ClassificationException("Could not extract text from PDF — file may be scanned/image-only")


def _extract_with_pdfplumber(file_path: str) -> str:
    """Extract text page by page using pdfplumber."""
    pages = []
    with pdfplumber.open(file_path) as pdf:
        for i, page in enumerate(pdf.pages):
            page_text = page.extract_text()
            if page_text:
                pages.append(f"[Page {i+1}]\n{page_text}")
    return "\n\n".join(pages)


def _extract_with_pypdf2(file_path: str) -> str:
    """Extract text page by page using PyPDF2."""
    pages = []
    with open(file_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                pages.append(f"[Page {i+1}]\n{page_text}")
    return "\n\n".join(pages)


def get_page_count(file_path: str) -> int:
    """Return number of pages in PDF."""
    try:
        with pdfplumber.open(file_path) as pdf:
            return len(pdf.pages)
    except Exception:
        return 0
