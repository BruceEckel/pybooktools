# slug_line_pycharm_watcher.py
# File Watcher Configuration for Pycharm:
# 0. Install https://plugins.jetbrains.com/plugin/7177-file-watchers
# Go to Settings | Tools | Actions on Save, Click on "Configure File Watcher", then '+'
# 1. Program: `python.exe`
# 2. Arguments: `C:\git\pybooktools\src\pybooktools\util\slug_line_pycharm_watcher.py $FilePath$`
# 3. Working Directory: `$FileDir$`
# 4. Uncheck all Advanced Options to prevent infinite looping
import re
import sys
from pathlib import Path
from typing import Final

slug_pattern: Final[str] = r"^#\s+\w+\.py$"

if __name__ == "__main__":
    pyfile = Path(sys.argv[1])
    slug_line = f"# {pyfile.name}\n"
    lines = pyfile.read_text(encoding="utf-8").splitlines(True)

    if lines and re.match(slug_pattern, lines[0]):
        lines[0] = slug_line  # Replace existing slug line
    else:
        lines.insert(0, slug_line)  # Insert new slug line

    pyfile.write_text("".join(lines), encoding="utf-8")
