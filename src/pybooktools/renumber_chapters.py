# renumber_chapters.py
"""
Renumbers Markdown chapters in a directory, and updates mkdocs.yml.
"""
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, ClassVar, Annotated

from cyclopts import App, Parameter, Group
from cyclopts.types import ExistingDirectory
from rich.console import Console

from pybooktools.util.config import chapter_pattern
from pybooktools.util.path_utils import sanitize_title

console = Console()
app = App(
    version_flags=[],
    console=console,
    help_flags="-h",
    help_format="plaintext",
    help=__doc__,
    default_parameter=Parameter(negative=()),
)
optg = Group(
    "Option Flags (any combination)",
    default_parameter=Parameter(negative=""),  # Disable "--no-" flags
)


@dataclass(order=True)
class MarkdownChapterID:
    path: Path
    _number: int = field(init=False)
    root_name: str = field(init=False)  # Does not include _number or '.md'
    appendix: bool = False
    chapternum_width: ClassVar[int] = 2
    appendixnum_width: ClassVar[int] = 1

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
        if self.appendix:
            return f"A{self._number:0{self.appendixnum_width}d} {self.root_name}.md"
        else:
            return f"{self._number:0{self.chapternum_width}d} {self.root_name}.md"

    @property
    def number(self) -> int:
        return self._number

    @number.setter
    def number(self, new_number: int) -> None:
        self._number = new_number

    def update_file_name(self) -> None:
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

        if not self.chapters:
            raise ValueError(f"No chapters found in {self.directory}")

        # Non-appendices first, then appendices. If needed, sort by number second.
        self.chapters.sort(key=lambda ch: (ch.appendix, ch.number))

    def __str__(self) -> str:
        return "\n".join([c.file_name() for c in self.chapters])

    def renumber(self) -> None:
        appendix_count = 1
        for i, chapter in enumerate(self.chapters, start=1):
            if not chapter.appendix:
                chapter.number = i
            else:
                chapter.number = appendix_count
                appendix_count += 1

    def update_file_names(self) -> None:
        for chapter in self.chapters:
            chapter.update_file_name()

    def updated_mkdocs_yml(self) -> (Path, str):
        mdkocs_yml_path = self.directory.parent / "mkdocs.yml"
        if not mdkocs_yml_path.exists():
            raise ValueError(f"mkdocs.yml not found in {self.directory.parent}")
        mdkocs_yml = mdkocs_yml_path.read_text(encoding="utf-8")
        if "nav:" not in mdkocs_yml:
            raise ValueError("'nav:' not found in mkdocs.yml")
        # Assume nav section is at the end of the file.
        base = mdkocs_yml.rindex("nav:")
        updated_mkdocs_yml = mdkocs_yml[:base] + "nav:\n"
        for chapter in self.chapters:
            updated_mkdocs_yml += f"  - {chapter.file_name()}\n"
        return mdkocs_yml_path, updated_mkdocs_yml

    def update_nav(self) -> None:
        mdkocs_yml_path, updated_mkdocs_yml = self.updated_mkdocs_yml()
        mdkocs_yml_path.write_text(updated_mkdocs_yml, encoding="utf-8")


@app.command(name="-r")
def renumber(path: Annotated[Path, Parameter(validator=ExistingDirectory())]):
    """Renumber the chapters, update mkdocs.yml"""
    book = Book(path)
    book.renumber()
    book.update_file_names()
    book.update_nav()
    print(book)


@app.command(name="-d")
def display(path: Annotated[Path, Parameter(validator=ExistingDirectory())]):
    """Display the existing chapters without renumbering"""
    book = Book(path)
    print(book)


@app.command(name="-t")
def test(path: Annotated[Path, Parameter(validator=ExistingDirectory())]):
    """Test info, no changes"""
    book = Book(path)
    print(" Renumbered ".center(60, "-"))
    book.renumber()
    print(book)
    print(" updated_mkdocs_yml ".center(60, "-"))
    mdkocs_yml_path, updated_mkdocs_yml = book.updated_mkdocs_yml()
    print(f"{mdkocs_yml_path = }")
    print(updated_mkdocs_yml)


app()

# def main(
#     ctx: typer.Context,
#     directory: Annotated[str, typer.Argument(
#         help="Directory containing Markdown chapters (default: current directory)"
#     )] = None,
#     renumber: Annotated[bool, typer.Option(
#         "--renumber", "-r", help="Renumber the chapters"
#     )] = False,
#     display: Annotated[bool, typer.Option(
#         "--display",
#         "-d",
#         help="Display the existing chapters without renumbering",
#     )] = False,
#     test: Annotated[bool, typer.Option(
#         "--test",
#         "-t",
#         help="Without making differences, show the renumbered chapters",
#     )] = False,
# ) -> None:
#     """[deep_sky_blue1]Renumbers Markdown chapters in a directory[/deep_sky_blue1]"""
#
#     help_error = HelpError(ctx)
#
#     if not (renumber or display or test):
#         help_error("Specify either --renumber, --display, or --test")
#
#     dir_path = Path(directory) if directory else Path.cwd()
#
#     if not dir_path.is_dir():
#         help_error(f"{dir_path} is not a valid directory path")
#
#     book = Book(dir_path)
#     if renumber:
#         book.renumber()
#         book.update_file_names()
#         book.update_nav()
#         print(book)
#     elif display:
#         print(book)
#     elif test:
#         print(" Renumbered ".center(60, "-"))
#         book.renumber()
#         print(book)
#         print(" updated_mkdocs_yml ".center(60, "-"))
#         mdkocs_yml_path, updated_mkdocs_yml = book.updated_mkdocs_yml()
#         print(f"{mdkocs_yml_path = }")
#         print(updated_mkdocs_yml)
