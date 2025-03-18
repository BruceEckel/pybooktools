# renumber_chapters.py
"""
Renumbers Markdown chapters in a directory, and updates mkdocs.yml.

The Markdown chapters do not contain the chapter _number in the Markdown
title that begins the file and starts with a `#`. Thus the chapter _number
only exists at the beginning of the file name, and can be modified by
changing the file name alone.
"""
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Annotated, ClassVar

import typer

from pybooktools.util import HelpError
from pybooktools.util.config import chapter_pattern
from pybooktools.util.path_utils import sanitize_title

app = typer.Typer(
    context_settings={"help_option_names": ["--help", "-h"]},
    add_completion=False,
    rich_markup_mode="rich",
)


@dataclass
class MarkdownChapterID:
    path: Path
    _number: int = field(init=False)
    root_name: str = field(init=False)  # Does not include _number or '.md'
    appendix: bool = False
    number_width: ClassVar[int] = 2

    def __post_init__(self) -> None:
        assert self.path.is_file(), f"{self.path} is not a file."
        if not (match := re.match(chapter_pattern, self.path.name)):
            raise ValueError(f"{self.path.name} doesn't match pattern.")
        number_str = match.group(1)
        self.appendix = number_str.startswith('A')
        # Strip non-digit chars from number_str and convert it to an int:
        self._number = int(re.sub(r"\D", "", number_str))
        # self.id.root_name is single-# headline in markdown file
        with self.path.open(encoding="utf-8") as file:
            headline = file.readline()
        if headline.startswith("# "):
            self.root_name = sanitize_title(headline[2:].strip())
        else:
            raise ValueError(f"{self.path.name} must start with a single-# headline.")

    def file_name(self) -> str:
        _a = 'A' if self.appendix else ''
        return f"{_a}{self._number:0{self.number_width}d} {self.root_name}.md"

    @property
    def number(self) -> int:
        return self._number

    @number.setter
    def number(self, new_number: int) -> None:
        self._number = new_number
        self.path.rename(self.path.parent / self.file_name())


@dataclass
class Book:
    directory: Path
    chapters: List[MarkdownChapterID] = field(default_factory=list)

    def __post_init__(self) -> None:
        """
        Collect Markdown chapters/appendices from directory.
        """
        for f in self.directory.iterdir():
            if f.is_file() and re.match(chapter_pattern, f.name):
                self.chapters.append(MarkdownChapterID(path=f))

        # Non-appendices first, then appendices. If needed, sort by index second.
        self.chapters.sort(key=lambda ch: (ch.appendix, ch.index))

    def show_without_updating(self) -> None:
        for chapter in self.chapters:
            print(chapter)

    def renumber(self) -> None:
        for i, chapter in enumerate(self.chapters, start=1):
            chapter.number = i

    # def __str__(self) -> str:
    #     return "\n".join(str(chapter) for chapter in self.chapters)

    def update_nav(self) -> None:
        mdkocs_yml_path = self.directory.parent / "mkdocs.yml"
        if not mdkocs_yml_path.exists():
            print(f"mkdocs.yml not found in {self.directory.parent}")
            return
        mdkocs_yml = mdkocs_yml_path.read_text(encoding="utf-8")
        if "nav:" not in mdkocs_yml:
            print("'nav:' not found in mkdocs.yml")
            return
        # Assume nav section is at the end of the file.
        base = mdkocs_yml.rindex("nav:")
        print(mdkocs_yml[:base])
        updated_mkdocs_yml = mdkocs_yml[:base] + "nav:\n"
        for chapter in self.chapters:
            updated_mkdocs_yml += f"  - {chapter.file_name()}\n"
        print(updated_mkdocs_yml)
        # mdkocs_yml_path.write_text(updated_mkdocs_yml, encoding="utf-8")


@app.command()
def main(
    ctx: typer.Context,
    directory: Annotated[str, typer.Argument(
        help="Directory containing Markdown chapters (default: current directory)"
    )] = None,
    renumber: Annotated[bool, typer.Option(
        "--renumber", "-r", help="Renumber the chapters"
    )] = False,
    display: Annotated[bool, typer.Option(
        "--display",
        "-d",
        help="Display the existing chapters without renumbering",
    )] = False,
    test: Annotated[bool, typer.Option(
        "--test",
        "-t",
        help="Without making differences, show the renumbered chapters",
    )] = False,
) -> None:
    """[deep_sky_blue1]Renumbers Markdown chapters in a directory[/deep_sky_blue1]"""

    help_error = HelpError(ctx)

    if not (renumber or display or test):
        help_error("Specify either --renumber, --display, or --test")

    dir_path = Path(directory) if directory else Path.cwd()

    if not dir_path.is_dir():
        help_error(f"{dir_path} is not a valid directory path")

    book = Book(dir_path)
    if not book.chapters:
        help_error(f"No chapters found in {dir_path}")

    if renumber:
        book.renumber()
        print(book)
    elif display:
        print(book)
    elif test:
        book.show_without_updating()
        book.update_nav()


if __name__ == "__main__":
    app()
