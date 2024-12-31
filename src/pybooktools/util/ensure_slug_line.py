# ensure_slug_line.py
import re
from pathlib import Path


def ensure_slug_line(pycode: str, file_path: Path) -> str:
    """
    Ensure slug line at the top of pycode based on file_path
    """
    lines = pycode.splitlines(True)
    slug_line = f"# {file_path.name}\n"

    # Check if the first line is a slug line
    if lines and re.match(r"^#\s*(?::\s+)?\w+\.py$", lines[0]):
        # Slug line exists, replace it:
        lines[0] = slug_line
    else:
        # Slug line doesn't exist, insert at top of file
        lines.insert(0, slug_line)
    return "".join(lines)
