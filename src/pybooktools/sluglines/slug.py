# slug.py
import re
from pathlib import Path
from typing import Final

slug_pattern: Final[str] = r"^#\s+\w+\.py$"


def is_slug(line: str) -> bool:
    return re.match(slug_pattern, line) is not None


def ensure_slug_line(pycode: str, file_path: Path) -> str:
    """
    Ensure slug line at the top of pycode based on example_path
    """
    lines = pycode.splitlines(True)
    slug_line = f"# {file_path.name}\n"

    # Check if the first line is a slug line
    if lines and is_slug(lines[0]):
        # Slug line exists, replace it:
        lines[0] = slug_line
    else:
        # Slug line doesn't exist, insert at top of file
        lines.insert(0, slug_line)
    return "".join(lines)
