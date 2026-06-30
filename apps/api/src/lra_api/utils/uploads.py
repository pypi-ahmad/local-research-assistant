"""Upload validation helpers."""

from __future__ import annotations

from pathlib import Path

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".md",
    ".txt",
    ".csv",
    ".xlsx",
    ".xls",
    ".pptx",
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".bmp",
}

MAX_UPLOAD_BYTES = 50 * 1024 * 1024


def validate_upload(filename: str, content: bytes) -> None:
    """Validate file extension and size before ingestion."""
    suffix = Path(filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {suffix}")
    if len(content) > MAX_UPLOAD_BYTES:
        raise ValueError("File exceeds maximum size of 50 MB")
