# config.py
import re
from pathlib import Path
from re import Pattern
from typing import Final

LINE_LENGTH: Final[int] = 65
# 65 is for slide width

book_chapters = Path(r"C:\git\ThinkingInTypes.github.io\Chapters")

chapter_pattern: Final[str] = r"^[CZ](\d+)_.+\.md$"

repo_chapter_pattern: Final[str] = r"^[cz]\d+_[a-z_]+$"

code_location_pattern: Final[Pattern[str]] = re.compile(r"#\[code_location]\s*(.*)\s*-->")

listing_pattern: Final[Pattern[str]] = re.compile(r"```python\n(# (.*?)\n)?(.*?)```", re.DOTALL)

default_slug_line_pattern: Pattern[str] = re.compile(
    r"^\s*(?:#|//)\s*(\S+\.[a-zA-Z0-9_]+)"
)
