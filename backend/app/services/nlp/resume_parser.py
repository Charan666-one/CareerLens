"""
Resume text extraction.

Supports PDF (via PyMuPDF/fitz), DOCX (via python-docx), and plain text.
Skill extraction from the resulting text lives in skill_normalizer.py -
this module is only responsible for turning uploaded file bytes into text.
"""
import io

import fitz  # PyMuPDF
from docx import Document

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt"}


class UnsupportedFileTypeError(ValueError):
    pass


def _extract_pdf_text(file_bytes: bytes) -> str:
    with fitz.open(stream=file_bytes, filetype="pdf") as doc:
        return "\n".join(page.get_text() for page in doc)


def _extract_docx_text(file_bytes: bytes) -> str:
    document = Document(io.BytesIO(file_bytes))
    return "\n".join(paragraph.text for paragraph in document.paragraphs)


def _extract_txt_text(file_bytes: bytes) -> str:
    return file_bytes.decode("utf-8", errors="ignore")


def extract_text(filename: str, file_bytes: bytes) -> str:
    """
    Extract raw text from an uploaded resume file. Dispatches on file
    extension. Raises UnsupportedFileTypeError for anything else.
    """
    lowered = filename.lower()

    if lowered.endswith(".pdf"):
        text = _extract_pdf_text(file_bytes)
    elif lowered.endswith(".docx"):
        text = _extract_docx_text(file_bytes)
    elif lowered.endswith(".txt"):
        text = _extract_txt_text(file_bytes)
    else:
        raise UnsupportedFileTypeError(
            f"Unsupported file type for '{filename}'. "
            f"Supported types: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )

    return text.strip()