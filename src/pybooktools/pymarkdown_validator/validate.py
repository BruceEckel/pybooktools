# validate.py
"""Perform multiple validation tests on Markdown files."""
import re
from typing import Callable, List

from cyclopts import App
from cyclopts.types import ResolvedExistingFile, ResolvedExistingDirectory

slug_line_pattern = re.compile(r"^\s*(?:#|//)\s*(\S+\.(?:py|pyi|cpp|java))")


def check_for_duplicate_slug_lines(markdown_content: str) -> List[str]:
    """Checks for duplicate slug lines in a Markdown file."""
    lines = markdown_content.splitlines()
    seen = set()
    duplicates = []

    for line in lines:
        if slug_line_pattern.match(line):
            if line in seen:
                duplicates.append(f"Duplicate slug line found: {line}")
            seen.add(line)

    return duplicates


def check_for_missing_slug_lines(markdown_content: str) -> List[str]:
    """Checks for missing slug lines in a Markdown file"""
    missing: List[str] = []
    code_block_pattern = re.compile(
        r"```(?P<lang>python|cpp|java)\s*\n(?P<code>.*?)\n```",
        re.DOTALL
    )

    comment_markers = {
        "python": "#",
        "cpp": "//",
        "java": "//",
    }

    for match in code_block_pattern.finditer(markdown_content):
        lines = match.group("code").strip().splitlines()
        # Get the line number in the document where the code block starts
        start_index = match.start()
        line_number = markdown_content[:start_index].count("\n") + 1

        expected_marker = comment_markers[match.group("lang")]
        if not lines or not re.match(rf"{re.escape(expected_marker)}\s*\S+\.(py|pyi|cpp|java)", lines[0]):
            missing.append(f"Missing slug line at line {line_number}")

    return missing


def check_for_main(markdown_content: str) -> List[str]:
    """Checks for __main__ in a Markdown file."""
    mains = []
    for n, line in enumerate(markdown_content.splitlines()):
        if "__main__" in line:
            mains.append(f"__main__ found on line {n + 1}")
    return mains


# Define and populate the list of test functions
validation_checks: List[Callable[[str], List[str]]] = [
    check_for_missing_slug_lines,
    check_for_duplicate_slug_lines,
    check_for_main,
    # Add more test functions here as needed
]

app = App(
    version_flags=[],
    help_flags="-h",
    help=__doc__,
    # default_parameter=Parameter(negative=()),
)


def check_markdown_file(markdown_file: ResolvedExistingFile) -> List[str]:
    """Validate a single Markdown file."""
    content = markdown_file.read_text(encoding="utf-8")
    issues: List[str] = []
    for check in validation_checks:
        issues.extend(check(content))
    return issues


@app.command(name="-v")
def validate_markdown_file(markdown_file: ResolvedExistingFile):
    """Validate a single Markdown file."""
    for issue in check_markdown_file(markdown_file):
        print(f"- {issue}")


@app.command(name="-d")
def validate_markdown_directory(markdown_dir: ResolvedExistingDirectory):
    """Validate all Markdown files in a directory."""
    for markdown_file in list(markdown_dir.glob("*.md")):
        issues = check_markdown_file(markdown_file)
        if issues:
            print(markdown_file.name.center(70, "-"))
            for issue in issues:
                print(f"- {issue}")
    print("check complete")
