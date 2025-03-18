# renumber_chapters.py
"""
Renumbers Markdown chapters in a directory, and updates mkdocs.yml.

The Markdown chapters do not contain the chapter number in the Markdown
title that begins the file and starts with a `#`. Thus the chapter number
only exists at the beginning of the file name, and can be modified by
changing the file name alone.
"""
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Annotated, Iterator, Tuple, ClassVar

import typer

from pybooktools.util import HelpError
from pybooktools.util.config import chapter_pattern

app = typer.Typer(
    context_settings={"help_option_names": ["--help", "-h"]},
    add_completion=False,
    rich_markup_mode="rich",
)


def sanitize_title(title: str) -> str:
    """
    Keep only alphanumeric characters and spaces; replace spaces with underscores.
    """
    cleaned = ''.join(ch for ch in title if ch.isalnum() or ch.isspace())
    return cleaned.replace(" ", "_")


@dataclass
class ChapterID:
    file_name: str
    number: int = field(init=False)
    root_name: str = field(init=False)  # Does not include number or '.md'
    appendix: bool = False
    number_width: ClassVar[int] = 2

    def __post_init__(self) -> None:
        if not (match := re.match(chapter_pattern, self.file_name)):
            raise ValueError(f"File name {self.file_name} does not match the pattern.")
        number_str, self.root_name = match.group
        self.root_name = sanitize_title(self.root_name)
        self.appendix = number_str.startswith('A')
        # Strip non-digit chars from number_str and convert it to an int:
        self.number = int(re.sub(r"\D", "", number_str))

    def __increment__(self) -> "ChapterID":
        self.number += 1
        return self

    def __str__(self) -> str:
        _a = 'A' if self.appendix else ''
        return f"{_a}{self.number:0{self.number_width}d} {self.root_name}.md"


@dataclass(order=True)
class MarkdownChapter:
    path: Path
    id: ChapterID = field(init=False)
    index: int = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self.id = ChapterID(self.path.name)
        self.index = self.id.number
        # Update self.id.root_name to match single-# headline in markdown file
        with self.path.open(encoding="utf-8") as file:
            headline = file.readline().rstrip("\n")
        if headline.startswith("# "):
            self.id.root_name = sanitize_title(headline[2:].strip())
        else:
            raise ValueError(f"File {self.path} does not start with a single-# headline.")

    def __str__(self) -> str:
        return f"{self.id}"


@dataclass(order=True)
class MarkdownChapterX:
    path: Path
    file_name: str = field(init=False)
    title: str = field(init=False)
    number: str = field(init=False)
    appendix: bool = False
    sort_index: int = field(init=False, repr=False)

    def __post_init__(self) -> None:
        """
        Identify number, detect appendix if it starts with 'A',
        and compute sorting index so chapters can be ordered correctly.
        """
        self.file_name = self.path.name
        if not (match := re.match(chapter_pattern, self.file_name)):
            raise ValueError(f"File name {self.file_name} does not match the pattern.")

        raw_num, raw_title = match.groups()
        self.appendix = raw_num.startswith('A')
        # Convert 'A12' -> '12' or '10' -> '10'
        numeric_part = re.sub(r"\D", "", raw_num)
        self.number = f"{int(numeric_part):02d}"
        self.sort_index = int(numeric_part)

        # Use either the matched title or (optionally) a title from file contents.
        self.title = raw_title

    def new_name(self, new_number: str) -> str:
        self.number = new_number
        sanitized_title = re.sub(r"[^A-Za-z0-9 ]", "", self.title)
        return f"{self.number} {sanitized_title}.md"

    def update_chapter_number(self, new_number: str) -> None:
        new_name = self.new_name(new_number)
        self.path.rename(self.path.parent / new_name)
        self.path = self.path.parent / new_name

    def __str__(self) -> str:
        return f"{'A' if self.appendix else ''}{self.number} {self.title}"


@dataclass
class Book:
    directory: Path
    chapters: List[MarkdownChapter] = field(default_factory=list)

    def __post_init__(self) -> None:
        """
        Gather all Markdown chapters/appendices in one list
        and sort them so appendices appear at the end.
        """
        for f in self.directory.iterdir():
            if f.is_file() and re.match(chapter_pattern, f.name):
                self.chapters.append(MarkdownChapter(path=f))

        # Non-appendices first, then appendices. If needed, sort by index second.
        self.chapters.sort(key=lambda ch: (ch.appendix, ch.index))

    def __iter__(self) -> Iterator[Tuple[int, str, MarkdownChapter]]:
        for i, chapter in enumerate(self.chapters, start=1):
            formatted_updated_number = f"{i:0{len(str(len(self.chapters)))}}"
            yield i, formatted_updated_number, chapter

    def show_without_updating(self) -> None:
        for chapter in self.chapters:
            print(chapter)

    def renumber(self) -> None:
        for i, fmt_num, chapter in self:
            chapter.update_chapter_number(fmt_num)

    def __str__(self) -> str:
        return "\n".join(str(chapter) for chapter in self.chapters)

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
            updated_mkdocs_yml += f"  - {chapter.id}\n"
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
