# renumber_chapters.py
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

import typer

from pybooktools.diagnostics import trace
from pybooktools.util import display_function_name

chapter_pattern = r"^(\d+[a-zA-Z]?)\s+(.+)\.md$"

app = typer.Typer(
    context_settings={"help_option_names": ["-h", "--help"]},
    add_completion=False,
)


@dataclass(order=True)
class MarkdownChapter:
    path: Path
    file_name: str = field(init=False)
    file_name_title: str = field(init=False)
    markdown_title: str = field(init=False)
    title: str = field(init=False)
    number: str = field(init=False)
    content: list[str] = field(init=False)
    sort_index: int = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self.file_name = self.path.name
        match = re.match(chapter_pattern, self.file_name)
        if match:
            self.number, self.file_name_title = match.groups()
        else:
            raise ValueError(
                f"File name {self.file_name} does not match expected pattern"
            )
        self.sort_index = int(re.sub(r"\D", "", self.number))
        self.file_name_title = self.file_name_title.title()  # Title case

        self.content = self.path.read_text(encoding="utf-8").splitlines()
        if self.content and self.content[0].startswith("# "):
            self.markdown_title = self.content[0][2:].strip().title()

        self.title = self.markdown_title or self.file_name_title

        if not self.content or not self.content[0].startswith("# "):
            self.content.insert(0, f"# {self.title}")
        else:
            self.content[0] = f"# {self.title}"

    def update_chapter_number(self, new_number: str) -> None:
        self.number = new_number
        sanitized_title = re.sub(r"[^A-Za-z0-9 ]", "", self.title)
        new_name = f"{self.number} {sanitized_title}.md"
        self.path.rename(self.path.parent / new_name)
        self.path = self.path.parent / new_name
        self.path.write_text("\n".join(self.content) + "\n", encoding="utf-8")

    def __str__(self) -> str:
        return f"{self.number} {self.file_name_title}"


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

    def update_chapter_numbers(self) -> None:
        for i, chapter in enumerate(self.chapters, start=1):
            updated_number = f"{i:0{len(str(len(self.chapters)))}}"
            chapter.update_chapter_number(updated_number)

    def __str__(self) -> str:
        return "\n".join(str(chapter) for chapter in self.chapters)

    def display_chapters(self) -> None:
        for chapter in self.chapters:
            print(chapter.file_name)


@app.command()
def main(
        directory: str = typer.Argument(
            None,
            help="Directory containing Markdown chapters (default: current directory)",
        ),
        renumber: bool = typer.Option(
            False, "--renumber", "-r", help="Renumber the chapters in the directory"
        ),
        display: bool = typer.Option(
            False,
            "--display",
            "-d",
            help="Display the chapters in the directory without renumbering",
        ),
        trace_enabled: bool = typer.Option(
            False, "--trace", "-t", help="Enable tracing output"
        ),
) -> None:
    if trace_enabled:
        trace.enable()
        display_function_name()

    def help_error(msg: str) -> None:
        with typer.Context(typer.main.get_command(app)) as ctx:
            typer.echo(ctx.get_help())
        typer.secho(f"{msg}\n", fg="red")
        raise typer.Exit(code=1)

    if not (renumber or display):
        help_error("Specify either --renumber or --display")

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
        book.display_chapters()


if __name__ == "__main__":
    app()
