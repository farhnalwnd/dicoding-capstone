"""
File upload validation utilities.
Validates file type, size, and sanitizes filenames for CV/resume uploads.
"""

import os
import re

# ====================================
# Constants
# ====================================

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc"}
ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/msword",
}


def sanitize_filename(filename: str) -> str:
    """Remove path traversal characters and sanitize the filename."""
    # Take only the basename (strip directory components)
    name = os.path.basename(filename)
    # Remove any characters that aren't alphanumeric, dots, hyphens, underscores, or spaces
    name = re.sub(r"[^\w\s\-\.]", "", name)
    return name or "unknown_file"


def validate_upload_file(filename: str, file_bytes: bytes) -> None:
    """
    Validate an uploaded file for type and size.
    Raises ValueError with a descriptive message on validation failure.
    """
    if not filename:
        raise ValueError("No filename provided.")

    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(
            f"Invalid file type '{ext}'. Allowed types: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )

    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        max_mb = MAX_FILE_SIZE_BYTES / (1024 * 1024)
        raise ValueError(f"File size exceeds maximum limit of {max_mb:.0f} MB.")

    if len(file_bytes) == 0:
        raise ValueError("Uploaded file is empty.")
