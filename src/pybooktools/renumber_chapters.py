# renumber_chapters.py
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Annotated

import typer

from pybooktools.util import HelpError
from pybooktools.util.config import chapter_pattern

app = typer.Typer(
    context_settings={"help_option_names": ["--help", "-h"]},
    add_completion=False,
    rich_markup_mode="rich",
)


@dataclass(order=True)
class MarkdownChapter:
    path: Path
    file_name: str = field(init=False)
    file_name_title: str = field(init=False)
    markdown_title: str | None = field(init=False)
    title: str = field(init=False)
    number: str = field(init=False)
    content: list[str] = field(init=False)
    sort_index: int = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self.file_name = self.path.name
        match = re.match(chapter_pattern, self.file_name)
        if match:
            self.number, self.file_name_title = match.groups()
            print(f"{self.number = }, {self.file_name_title = }")
        else:
            raise ValueError(
                f"File name {self.file_name} does not match expected pattern"
            )
        self.sort_index = int(re.sub(r"\D", "", self.number))
        self.file_name_title = self.file_name_title.title()  # Title case

        self.content = self.path.read_text(encoding="utf-8").splitlines()
        if self.content and self.content[0].startswith("# "):
            self.markdown_title = self.content[0][2:].strip().title()
        else:
            self.markdown_title = None

        self.title = self.markdown_title or self.file_name_title

        if not self.content or not self.content[0].startswith("# "):
            self.content.insert(0, f"# {self.title}")
        else:
            self.content[0] = f"# {self.title}"

    def new_name(self, new_number: str) -> str:
        self.number = new_number
        sanitized_title = re.sub(r"[^A-Za-z0-9 ]", "", self.title)
        return f"{self.number} {sanitized_title}.md"

    def update_chapter_number(self, new_number: str) -> None:
        new_name = self.new_name(new_number)
        self.path.rename(self.path.parent / new_name)
        self.path = self.path.parent / new_name
        self.path.write_text("\n".join(self.content) + "\n", encoding="utf-8")

    def __str__(self) -> str:
        return f"{self.number} {self.title}"


@dataclass
class Book:
    directory: Path
    chapters: List[MarkdownChapter] = field(init=False)

    def __post_init__(self) -> None:
        chapter_files = [
            f
            for f in self.directory.iterdir()
            if f.is_file() and re.match(chapter_pattern, f.name)
        ]
        chapters = [MarkdownChapter(path=file) for file in chapter_files]
        self.chapters = sorted(
            chapters, key=lambda ch: (ch.sort_index, ch.number)
        )

    def show_without_updating(self) -> None:
        for i, chapter in enumerate(self.chapters, start=1):
            updated_number = f"{i:0{len(str(len(self.chapters)))}}"
            print(chapter.new_name(updated_number))

    def update_chapter_numbers(self) -> None:
        for i, chapter in enumerate(self.chapters, start=1):
            updated_number = f"{i:0{len(str(len(self.chapters)))}}"
            chapter.update_chapter_number(updated_number)

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
            updated_mkdocs_yml += f"  - {chapter.new_name(chapter.number)}\n"
        print(updated_mkdocs_yml)
        # mdkocs_yml_path.write_text(updated_mkdocs_yml, encoding="utf-8")

    # def display_chapters(self) -> None:
    #     for chapter in self.chapters:
    #         print(chapter.file_name)


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
        book.update_chapter_numbers()
        print(book)
    elif display:
        print(book)
    elif test:
        book.show_without_updating()
        book.update_nav()


if __name__ == "__main__":
    app()
