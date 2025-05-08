# config.py
import re
from re import Pattern
from typing import Final

chapter_pattern: Final[str] = r"^[CZ](\d+)_.+\.md$"

repo_chapter_pattern: Final[str] = r"^[cz]\d+_[a-z_]+$"

code_location_pattern: Final[Pattern[str]] = re.compile(r"#\[code_location]\s*(.*)\s*-->")

listing_pattern: Final[Pattern[str]] = re.compile(r"```python\n(# (.*?)\n)?(.*?)```", re.DOTALL)

default_slug_line_pattern: Pattern[str] = re.compile(
    r"^\s*(?:#|//)\s*(\S+\.[a-zA-Z0-9_]+)"
)
