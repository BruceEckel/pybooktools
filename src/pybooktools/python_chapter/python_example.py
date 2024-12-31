import difflib
from dataclasses import dataclass, field
from pathlib import Path
from typing import LiteralString

from pybooktools.diagnostics import panic
from pybooktools.python_chapter import PythonChapter
from pybooktools.util import console


@dataclass
class PythonExample:
    in_python_chapter: "PythonChapter"
    markdown_example: str
    repo_example_path: Path | None
    slugname: LiteralString | None
    repo_example: str = field(init=False)
    differs: bool = field(init=False)
    diffs: str = field(init=False)

    def __post_init__(self):
        if self.repo_example_path is None:
            panic(f"repo_example_path cannot be None: {self.in_python_chapter}, {self.slugname}")
        if not self.repo_example_path.is_file():
            panic(f"repo_example_path is not a file: {self.repo_example_path}")
        if not self.repo_example_path.suffix == ".py":
            panic(f"repo_example_path is not a Python file: {self.repo_example_path}")
        self.repo_example = (
                "```python\n"
                + self.repo_example_path.read_text(encoding="utf-8").strip()
                + "\n```"
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

    def status(self) -> str:
        if self.differs:
            return (f"[bold red]{self.slugname}[/bold red]\n"
                    f"[bright_cyan]{self}[/bright_cyan]")
        else:
            return f"[bold green]{self.slugname}[/bold green]\n"

    def display(self) -> None:
        console.print(f"Filename from slugline: {self.slugname}")
        console.print(f"Source File: {self.repo_example_path.absolute() if self.repo_example_path else ""}")
        console.print(f"{self.differs = }")
        console.rule("[cyan]Markdown Code Listing")
        console.print(f"[chartreuse4]{self.markdown_example}[/chartreuse4]")
        console.rule("[cyan]Repo Code Listing")
        console.print(f"[chartreuse4]{self.repo_example}[/chartreuse4]")
        console.rule("[cyan]Diffs")
        console.print(f"[chartreuse4]{self.diffs}[/chartreuse4]")
        console.rule()
