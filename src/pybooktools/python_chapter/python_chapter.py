import difflib
import re
from dataclasses import dataclass, field
from pathlib import Path
from re import Pattern
from typing import LiteralString, Final

from pybooktools.diagnostics import panic
from pybooktools.display.report import display_available_python_files, find_duplicate_python_files, \
    display_listing_status


@dataclass
class PythonExample:
    from_python_chapter: "PythonChapter"
    markdown_example: str
    repo_example_path: Path | None
    slugname: LiteralString | None
    # Exclude field from constructor arguments:
    repo_example: str = field(init=False)
    differs: bool = field(init=False)
    diffs: str = field(init=False)

    def __post_init__(self):
        if self.repo_example_path is None:
            panic(f"repo_example_path cannot be None: {self.from_python_chapter}, {self.slugname}")
        if not self.repo_example_path.is_file():
            panic(f"repo_example_path is not a file: {self.repo_example_path}")
        if not self.repo_example_path.suffix == ".py":
            panic(f"repo_example_path is not a Python file: {self.repo_example_path}")
        self.repo_example = (
                "```python\n"
                + self.repo_example_path.read_text(encoding="utf-8")
                + "```"
        )
        self.differs = self.markdown_example != self.repo_example
        if self.differs:
            differ = difflib.Differ()
            diff_lines = list(
                differ.compare(
                    self.markdown_example.splitlines(keepends=True),
                    self.repo_example.splitlines(keepends=True),
                )
            )
            # Format the differences for display
            self.diffs = "".join(diff_lines)


@dataclass
class PythonChapter:
    markdown_path: Path
    markdown_text: str = field(init=False)
    repo_paths: list[Path] = field(default_factory=list, init=False)
    python_repo_examples: list[Path] = field(default_factory=list, init=False)
    python_examples: list[PythonExample] = field(default_factory=list, init=False)
    updated_markdown: str = field(init=False)
    differences: int = 0
    code_location_pattern: Final[Pattern[str]] = re.compile(r"#\[code_location]\s*(.*)\s*-->")
    listing_pattern: Final[Pattern[str]] = re.compile(r"```python\n(# (.*?)\n)?(.*?)```", re.DOTALL)

    def __post_init__(self) -> None:
        if not (self.markdown_path.is_file() and self.markdown_path.suffix == ".md"):
            panic(f"{self.markdown_path} is not a Markdown file")
        self.markdown_text = self.markdown_path.read_text(encoding="utf-8")
        self.extract_repo_paths()
        self.find_python_examples_in_repo()
        self.find_python_examples_in_markdown()
        self.differences = len([True for example in self.python_examples if example.differs])

    def extract_repo_paths(self) -> None:
        """
        Extract all #[code_location] paths from the markdown content.
        """
        location_list = [
            Path(match.group(1).strip())
            for match in re.finditer(self.code_location_pattern, self.markdown_text)
        ]
        for location in location_list:
            if location.is_absolute():
                self.repo_paths.append(location)
            else:
                self.repo_paths.append(Path.cwd() / location)

    def find_python_examples_in_repo(self) -> None:
        """
        Find Python files and listings in `repo_paths`
        """
        assert self.repo_paths, "No repo_paths found"

        for code_location in self.repo_paths:
            self.python_repo_examples.extend(list(code_location.glob("*.py")))
        display_available_python_files(self.python_repo_examples)
        find_duplicate_python_files(self.python_repo_examples)

    def find_python_examples_in_markdown(self):
        # Find python examples in Markdown chapter:
        for match in re.finditer(self.listing_pattern, self.markdown_text):
            # If slug line doesn't exist group(1) returns None:
            if match.group(1) is not None:
                markdown_python_example = match.group(0)  # Include Markdown tags
                slugname = match.group(2).strip() if match.group(2) else None
                assert slugname, f"slugname not found in {match}"
                repo_example_path = next(
                    (file for file in self.python_repo_examples if file.name == slugname),
                    None,
                )
                self.python_examples.append(
                    PythonExample(self, markdown_python_example, repo_example_path, slugname)
                )

    def update_markdown_listings(self) -> None:
        self.updated_markdown = self.markdown_text
        for listing in self.python_examples:
            display_listing_status(listing)
            if listing.differs:
                self.updated_markdown = self.updated_markdown.replace(listing.markdown_example, listing.repo_example)

    def write_updated_chapter(self) -> None:
        self.markdown_path.write_text(self.updated_markdown, encoding="utf-8")
