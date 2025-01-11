# slug_line_pycharm_watcher.py
# File Watcher Configuration for Pycharm:
# 1. Program: `python.exe`
# 2. Arguments: `slug_line_pycharm_watcher.py $FilePath$`
# 3. Working Directory: `$FileDir$`
import re
import sys
from pathlib import Path
from typing import Final

slug_pattern: Final[str] = r"^#\s+\w+\.py$"

if __name__ == "__main__":
    pyfile = Path(sys.argv[1])
    lines = pyfile.read_text(encoding="utf-8").splitlines(True)
    slug_line = f"# {pyfile.name}\n"

    if lines and re.match(slug_pattern, lines[0]):
        lines[0] = slug_line  # Replace existing slug line
    else:
        lines.insert(0, slug_line)  # Insert new slug line

    pyfile.write_text("".join(lines), encoding="utf-8")
