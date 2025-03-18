# path_utils.py
import shutil
from pathlib import Path


def cleaned_dir(dir_path: Path, prefix: str) -> Path:
    clean_dir = dir_path.parent / f"{prefix}{dir_path.stem}"
    if clean_dir.exists():
        shutil.rmtree(clean_dir)
    clean_dir.mkdir()
    return clean_dir


def sanitize_title(title: str) -> str:
    """
    Keep only alphanumeric characters and spaces; replace spaces with underscores.
    """
    cleaned = ''.join(ch for ch in title if ch.isalnum() or ch.isspace())
    return cleaned.replace(" ", "_")
