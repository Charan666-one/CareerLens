"""
Resume text extraction.

Supports PDF (via PyMuPDF/fitz), DOCX (via python-docx), and plain text.
Skill extraction from the resulting text lives in skill_normalizer.py -
this module is only responsible for turning uploaded file bytes into text.

All failures callers are expected to handle derive from ResumeParseError,
so a route can catch that one base class and return 400 rather than
leaking a library-specific exception (fitz.FzErrorFormat,
zipfile.BadZipFile, ...) as an unhandled 500.
"""
import io

import fitz  # PyMuPDF
from docx import Document

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt"}


class ResumeParseError(ValueError):
    """Base for every "we can't read this upload" condition."""


class UnsupportedFileTypeError(ResumeParseError):
    """The file extension isn't one we know how to read."""


class CorruptFileError(ResumeParseError):
    """The extension is supported but the bytes don't parse as that format -
    a truncated/encrypted PDF, a .doc renamed to .docx, an HTML error page
    saved as a resume, etc."""


def _extract_pdf_text(file_bytes: bytes) -> str:
    try:
        with fitz.open(stream=file_bytes, filetype="pdf") as doc:
            return "\n".join(page.get_text() for page in doc)
    except Exception as exc:  # fitz raises its own error hierarchy
        raise CorruptFileError(
            "That PDF couldn't be read - it may be corrupt, encrypted, or not "
            "actually a PDF. Try re-exporting it."
        ) from exc


def _extract_docx_text(file_bytes: bytes) -> str:
    try:
        document = Document(io.BytesIO(file_bytes))
        return "\n".join(paragraph.text for paragraph in document.paragraphs)
    except Exception as exc:  # python-docx surfaces zipfile/XML errors
        raise CorruptFileError(
            "That DOCX couldn't be read - it may be corrupt, or it may be an "
            "older .doc file renamed to .docx. Try re-saving it as .docx."
        ) from exc


def _extract_txt_text(file_bytes: bytes) -> str:
    return file_bytes.decode("utf-8", errors="ignore")


def extract_text(filename: str, file_bytes: bytes) -> str:
    """
    Extract raw text from an uploaded resume file. Dispatches on file
    extension. Raises UnsupportedFileTypeError for an unknown extension and
    CorruptFileError when a supported extension fails to parse - both are
    ResumeParseError, which callers should catch.
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
