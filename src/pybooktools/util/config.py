import re
from re import Pattern
from typing import Final

# slug_pattern: Final[str] = r"^#\s*(?::\s+)?\w+\.py$"
slug_pattern: Final[str] = r"^#\s+\w+\.py$"

chapter_pattern: Final[str] = r"^(\d+[a-zA-Z]?)\s+(.+)\.md$"

code_location_pattern: Final[Pattern[str]] = re.compile(r"#\[code_location]\s*(.*)\s*-->")

listing_pattern: Final[Pattern[str]] = re.compile(r"```python\n(# (.*?)\n)?(.*?)```", re.DOTALL)
