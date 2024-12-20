# update_markdown_code_listings.py
"""
Looks in Markdown files for listings with sluglines,
and updates those listings from the source code repository.
You must provide the path to at least one source code repository,
as a Markdown comment in the form:
<!-- #[code_location] ./src/functional_error_handling -->
These can appear anywhere in the file.
The path can be relative or absolute.
If you provide more than one source code repository, you must ensure
there are no duplicate file names across those directories.
"""

import argparse
import collections
import difflib
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from pprint import pformat
from textwrap import dedent
from typing import LiteralString

from rich.console import Console

from pybooktools.diagnostics import trace
from pybooktools.util import display_function_name

centering_width = 65
console = Console()
python_files: list[Path] = []


@dataclass
class MarkdownListing:
    slugname: LiteralString | None
    markdown_listing: str
    source_file_path: Path | None
    # Exclude field from constructor arguments:
    source_file_contents: str = field(init=False)
    changed: bool = field(init=False)
    diffs: str = field(init=False)

    def __post_init__(self):
        if self.source_file_path is None:
            console.print(
                "[bold red] MarkdownListing: source_file_path is None"
                f" for slugname: {self.slugname}[/bold red]"
            )
            console.print(pformat(python_files))
            raise ValueError("source_file cannot be None")
        self.source_file_contents = (
                "```python\n"
                + self.source_file_path.read_text(encoding="utf-8")
                + "```"
        )
        self.changed = self.markdown_listing != self.source_file_contents
        if self.changed:
            # Compute the differences between markdown_listing and source_file_contents
            differ = difflib.Differ()
            diff_lines = list(
                differ.compare(
                    self.markdown_listing.splitlines(keepends=True),
                    self.source_file_contents.splitlines(keepends=True),
                )
            )
            # Format the differences for display
            self.diffs = "".join(diff_lines)

    def __str__(self):
        return dedent(
            f"""
        Filename from slugline: {self.slugname}
        Source File: {self.source_file_path.absolute() if self.source_file_path else ""}
        {self.changed = }
        {"  Markdown Code Listing  ".center(centering_width, "-")}[chartreuse4]
        {self.markdown_listing}[/chartreuse4]
        {"  Source File Code Listing  ".center(centering_width, "-")}[chartreuse4]
        {self.source_file_contents}[/chartreuse4]
        {"  diffs  ".center(centering_width, "v")}[chartreuse4]
        {self.diffs}[/chartreuse4]
        {'=' * centering_width}
        """
        )


def find_python_files_and_listings(
        markdown_content: str,
) -> list[MarkdownListing]:
    """
    Find all #[code_location] paths in the Markdown content and
    return associated Python files and listings.
    """
    global python_files
    listings: list[MarkdownListing] = []
    code_location_pattern = re.compile(r"#\[code_location]\s*(.*)\s*-->")
    # console.print(f"{markdown_content =}")

    for match in re.finditer(code_location_pattern, markdown_content):
        # console.print(f"[orange3]{match}, {match.group(1)}[/orange3]")
        code_location = Path(match.group(1).strip())
        # console.print(
        #     f"[orange3]{code_location}, {code_location.is_absolute()}[/orange3]"
        # )
        if code_location.is_absolute():
            # console.print(f"[blue]{code_location = }[/blue]")
            pyfiles = list(code_location.glob("*.py"))
            # console.print(f"[blue]{pyfiles = }[/blue]")
            python_files.extend(pyfiles)
            # console.print(f"[blue]{python_files = }[/blue]")
        else:  # Relative path:
            python_files.extend(
                list((Path.cwd() / code_location).resolve().glob("**/*.py"))
            )
    console.print(
        f"""[orange3]{"  Available Python Files  ".center(centering_width, "-")}[/orange3]"""
    )
    for pyfile in [pf.name for pf in python_files]:
        console.print(f"\t[sea_green2]{pyfile}[/sea_green2]")
    console.print(f"""[orange3]{"-" * centering_width}[/orange3]""")

    # Check for duplicate file names in python_files.
    # (Should python_files be a custom class?)
    # Map file names to their full paths:
    file_paths = collections.defaultdict(list)  # Values are lists
    for fpath in python_files:
        file_paths[fpath.name].append(fpath)

    # Discover duplicates
    duplicates = {
        file_name: paths
        for file_name, paths in file_paths.items()
        if len(paths) > 1
    }
    if duplicates:
        console.print(
            f"""[red]{"  Duplicate Python File Names  ".center(centering_width, "-")}[/red]"""
        )
        for name, pyfile in duplicates.items():
            console.print(f"\t[red]{name}: {pyfile}[/red]")
        console.print(f"""[red]{"-" * centering_width}[/red]""")
        sys.exit(1)

    # If slug line doesn't exist group(1) returns None:
    listing_pattern = re.compile(r"```python\n(# (.*?)\n)?(.*?)```", re.DOTALL)
    for match in re.finditer(listing_pattern, markdown_content):
        if match.group(1) is not None:
            listing_content = match.group(0)  # Include Markdown tags
            file_name = match.group(2).strip() if match.group(2) else None
            assert file_name, f"file_name not found in {match}"
            source_file = next(
                (file for file in python_files if file.name == file_name),
                None,
            )
            listings.append(
                MarkdownListing(file_name, listing_content, source_file)
            )
    return listings


def update_markdown_listings(
        markdown_content: str, listings: list[MarkdownListing]
) -> str:
    updated_markdown = markdown_content
    for listing in listings:
        if not listing.changed:
            console.print(f"[bold green]{listing.slugname}[/bold green]")
        if listing.changed:
            console.print(f"[bold red]{listing.slugname}[/bold red]")
            console.print(f"[bright_cyan]{listing}[/bright_cyan]")
            updated_markdown = updated_markdown.replace(
                listing.markdown_listing,
                listing.source_file_contents,
            )
    return updated_markdown


def main():
    parser = argparse.ArgumentParser(
        description="Update Python slugline-marked source-code listings within a markdown file."
    )
    parser.add_argument(
        "markdown_file",
        help="Path to the markdown file to be updated.",
    )
    parser.add_argument(
        "-t", "--trace", action="store_true", help="Enable tracing output"
    )
    args = parser.parse_args()

    if args.trace:
        trace.enable()
        display_function_name()

    markdown_file = Path(args.markdown_file)
    markdown_content = markdown_file.read_text(encoding="utf-8")
    listings = find_python_files_and_listings(markdown_content)
    changes = [True for listing in listings if listing.changed]
    if any(changes):
        updated_markdown = update_markdown_listings(markdown_content, listings)
        markdown_file.write_text(updated_markdown, encoding="utf-8")
    change_count = (
        f"  {changes.count(True)} changes made to {markdown_file}  ".center(
            centering_width, "-"
        )
    )
    console.print(f"\n[orange3]{change_count}[/orange3]")
    if any(changes):
        for change in [listing for listing in listings if listing.changed]:
            console.print(f"[bright_cyan]{change.slugname}[/bright_cyan]")


if __name__ == "__main__":
    main()
