# path_utils.py
import shutil
from pathlib import Path


def cleaned_dir(dir_path: Path, prefix: str) -> Path:
    clean_dir = dir_path.parent / f"{prefix}{dir_path.stem}"
    if clean_dir.exists():
        shutil.rmtree(clean_dir)
    clean_dir.mkdir()
    return clean_dir


import re


def sanitize_title(title: str) -> str:
    """
    Sanitize a title string for safe filenames or identifiers.

    - Keep only alphanumeric characters, spaces, and colons.
    - Replace colons with spaces.
    - Remove all other characters.
    - Collapse multiple spaces into a single underscore.
    - Strip leading/trailing underscores.
    """
    # Replace colons with spaces
    title = title.replace(":", " ")
    # Remove unwanted characters (keep alphanumeric and spaces)
    cleaned = ''.join(ch for ch in title if ch.isalnum() or ch.isspace())
    # Collapse multiple spaces into a single underscore
    cleaned = re.sub(r'\s+', '_', cleaned)
    # Strip leading/trailing underscores
    cleaned = cleaned.strip('_')
    return cleaned
