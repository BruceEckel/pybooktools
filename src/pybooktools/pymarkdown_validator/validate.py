# validate.py
"""Perform multiple validation tests on Markdown files."""
import re
from typing import Callable, List, NamedTuple

from cyclopts import App
from cyclopts.types import ResolvedExistingFile, ResolvedExistingDirectory
from rich.console import Console, Group
from rich.panel import Panel

from pybooktools.md_examples import examples_without_sluglines

slug_line_pattern = re.compile(r"^\s*(?:#|//)\s*(\S+\.(?:py|pyi|cpp|java))")


class Issue(NamedTuple):
    """A validation issue."""
    problem: str
    text: str


# TODO: use md_examples util here:
def check_for_duplicate_slug_lines(markdown_content: str) -> list[Issue]:
    """Checks for duplicate slug lines in a Markdown file."""
    lines = markdown_content.splitlines()
    seen = set()
    duplicates: list[Issue] = []

    for line in lines:
        if slug_line_pattern.match(line):
            if line in seen:
                duplicates.append(Issue(f"Duplicate slug line", line))
            seen.add(line)

    return duplicates


def check_for_missing_slug_lines(markdown_content: str) -> list[Issue]:
    """Checks for missing slug lines in a Markdown file"""
    missing_line_issues: list[Issue] = []
    for slugless in examples_without_sluglines(markdown_content):
        if not slugless.strip().startswith("```python"):
            continue
        missing_line_issues.append(Issue("Missing Slug Line", slugless))
    return missing_line_issues


# TODO: use md_examples util here:
def check_for_main(markdown_content: str) -> list[Issue]:
    """Checks for '__main__' inside fenced code blocks in a Markdown file."""
    mains: list[Issue] = []
    in_code_block = False
    lines = markdown_content.splitlines()

    for i, line in enumerate(lines):
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block and "__main__" in line:
            mains.append(Issue("__main__ found", f"line {i + 1}"))

    return mains


# Define and populate the list of test functions
validation_checks: List[Callable[[str], list[Issue]]] = [
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


def check_markdown_file(markdown_file: ResolvedExistingFile) -> list[Issue]:
    """Validate a single Markdown file."""
    content = markdown_file.read_text(encoding="utf-8")
    issues: list[Issue] = []
    for check in validation_checks:
        issues.extend(check(content))
    return issues


def display_issues(issues: list[Issue], markdown_file: ResolvedExistingFile):
    """Display issues in a human-readable format using rich panels."""
    if not issues:
        return

    console = Console()
    sub_panels = [Panel(issue.text, title=issue.problem) for i, issue in enumerate(issues)]
    grouped = Group(*sub_panels)
    main_panel = Panel(grouped, title=str(markdown_file.name), border_style="red")
    console.print(main_panel)


@app.command(name="-f")
def validate_markdown_file(markdown_file: ResolvedExistingFile):
    """Validate a single Markdown file."""
    issues = check_markdown_file(markdown_file)
    display_issues(issues, markdown_file)


@app.command(name="-d")
def validate_markdown_directory(markdown_dir: ResolvedExistingDirectory):
    """Validate all Markdown files in a directory."""
    for markdown_file in list(markdown_dir.glob("*.md")):
        validate_markdown_file(markdown_file)
