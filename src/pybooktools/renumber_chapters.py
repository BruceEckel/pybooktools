#: renumber_chapters.py
import os
import re
from argparse import ArgumentParser
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

from pybooktools.util import display

chapter_pattern = r"^(\d+[a-zA-Z]?)\s+(.+)\.md$"


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

        # Extract Markdown file's version of title if there is one:
        self.content = self.path.read_text(encoding="utf-8").splitlines()
        if self.content and self.content[0].startswith("# "):
            self.markdown_title = self.content[0][2:].strip().title()

        # Title at the beginning of the Markdown file takes precedence
        # No title at the beginning of the Markdown file, use file_name_title
        self.title = self.markdown_title or self.file_name_title

        # If there's not an existing title, insert the generated title from the file name.
        if not self.content or not self.content[0].startswith("# "):
            self.content.insert(0, f"# {self.title}")
        else:
            # If there's an existing title, replace it with the title-cased version.
            self.content[0] = f"# {self.title}"

    def update_chapter_number(self, new_number: str) -> None:
        self.number = new_number
        sanitized_title = re.sub(r"[^A-Za-z0-9 ]", "", self.title)
        new_name = f"{self.number} {sanitized_title}.md"
        self.path.rename(self.path.parent / new_name)
        self.path = self.path.parent / new_name
        # Ensure one and only one newline at the end of the file
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


def main() -> None:
    display(f"{Path(__file__).name}")
    parser = ArgumentParser(description="Manage chapters in a Markdown book")
    parser.add_argument(
        "directory",
        type=str,
        nargs="?",
        default=None,
        help="Directory containing Markdown chapters (default: current directory)",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-r",
        "--renumber",
        action="store_true",
        help="Renumber the chapters in the directory",
    )
    group.add_argument(
        "-d",
        "--display",
        action="store_true",
        help="Display the chapters in the directory without renumbering",
    )
    args = parser.parse_args()

    if not (args.renumber or args.display):
        parser.print_help()
        return

    directory = Path(args.directory) if args.directory else Path(os.getcwd())
    book = Book(directory)

    if args.renumber:
        book.update_chapter_numbers()
        print(book)
    elif args.display:
        book.display_chapters()


if __name__ == "__main__":
    main()
