# path_utils.py
import shutil
from pathlib import Path


def cleaned_dir(dir_path: Path, prefix: str) -> Path:
    clean_dir = dir_path.parent / f"{prefix}{dir_path.stem}"
    if clean_dir.exists():
        shutil.rmtree(clean_dir)
    clean_dir.mkdir()
    return clean_dir
