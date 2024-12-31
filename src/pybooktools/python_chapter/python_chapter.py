# python_chapter.py
import collections
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from re import Pattern
from typing import Final

from pybooktools.util import display_dict, display_path_list, console, error
from .python_example import PythonExample


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
            error(f"{self.markdown_path} is not a Markdown file")
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
        display_path_list("Available Repo Examples", self.python_repo_examples)
        self.find_duplicate_python_repo_examples()

    def find_duplicate_python_repo_examples(self) -> None:
        # Check for duplicate file names in `paths`.
        # Map file names to their full paths:
        file_paths = collections.defaultdict(list)  # Values are lists
        for fpath in self.python_repo_examples:
            file_paths[fpath.name].append(fpath)
        duplicates = {
            file_name: paths
            for file_name, paths in file_paths.items()
            if len(paths) > 1
        }
        if duplicates:
            display_dict("Duplicate Python File Names", duplicates)
            sys.exit(1)

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

    def update_markdown_examples(self) -> None:
        self.updated_markdown = self.markdown_text
        for example in self.python_examples:
            console.print(example.status())
            if example.differs:
                self.updated_markdown = self.updated_markdown.replace(example.markdown_example, example.repo_example)

    def write_updated_chapter(self) -> None:
        self.markdown_path.write_text(self.updated_markdown, encoding="utf-8")

    def change_report(self) -> None:
        console.rule(f"[orange3]{self.markdown_path.name} differences: {self.differences}")
        for python_example in [python_example for python_example in self.python_examples if
                               python_example.differs]:
            console.print(f"[bright_cyan]{python_example.slugname}[/bright_cyan]")
        console.rule()
