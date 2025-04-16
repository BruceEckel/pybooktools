# config.py
import re
from re import Pattern
from typing import Final

chapter_pattern: Final[str] = r"^C\d+_.+\.md$"

code_location_pattern: Final[Pattern[str]] = re.compile(r"#\[code_location]\s*(.*)\s*-->")

listing_pattern: Final[Pattern[str]] = re.compile(r"```python\n(# (.*?)\n)?(.*?)```", re.DOTALL)
