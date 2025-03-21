# validate.py
"""Perform multiple validation tests on Markdown files."""
import re
from typing import Callable, List

from cyclopts import App
from cyclopts.types import ResolvedExistingFile, ResolvedExistingDirectory

# slug_line_pattern = re.compile(r"^\s*(?:#|//)\s*(\S+\.[a-zA-Z0-9_]+)")
slug_line_pattern = re.compile(r"^\s*(?:#|//)\s*(\S+\.(?:py|pyi|cpp|java))")


def check_duplicate_slug_lines(markdown_content: str) -> List[str]:
    """Checks for duplicate slug lines (lines starting with '#: ') in a Markdown file."""
    lines = markdown_content.splitlines()
    seen = set()
    duplicates = []

    for line in lines:
        if slug_line_pattern.match(line):
            if line in seen:
                duplicates.append(f"Duplicate slug line found: {line}")
            seen.add(line)

    return duplicates


# Define and populate the list of test functions
tests: List[Callable[[str], List[str]]] = [
    check_duplicate_slug_lines,
    # Add more test functions here as needed
]

app = App(
    version_flags=[],
    help_flags="-h",
    help=__doc__,
    # default_parameter=Parameter(negative=()),
)


@app.command(name="-v")
def validate_markdown_file(markdown_file: ResolvedExistingFile):
    """Validate a single Markdown file."""
    content = markdown_file.read_text(encoding="utf-8")
    issues: List[str] = []
    for test in tests:
        issues.extend(test(content))
    if issues:
        for issue in issues:
            print(f"- {issue}")


@app.command(name="-d")
def validate_markdown_directory(markdown_dir: ResolvedExistingDirectory):
    """Validate all Markdown files in a directory."""
    markdown_files = list(markdown_dir.glob("*.md"))
    for markdown_file in markdown_files:
        print(f"Validating {markdown_file}")
        validate_markdown_file(markdown_file)
