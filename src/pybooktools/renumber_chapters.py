import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List


@dataclass(order=True)
class MarkdownChapter:
    path: Path
    file_name: str = field(init=False)
    sort_index: int = field(init=False, repr=False)
    number: str = field(init=False)
    title: str = field(init=False)
    content: list[str] = field(init=False)

    def __post_init__(self) -> None:
        self.file_name = self.path.name
        match = re.match(r"^(\d+[a-zA-Z]?)\s+(.+)\.md$", self.file_name)
        if match:
            self.number, self.title = match.groups()
        else:
            raise ValueError(
                f"File name {self.file_name} does not match expected pattern"
            )
        self.sort_index = int(re.sub(r"\D", "", self.number))

        self.content = self.path.read_text(encoding="utf-8").splitlines()
        # Title at the beginning of the Markdown file takes precedence:
        if self.content and self.content[0].startswith("# "):
            self.title = self.content[0][2:].strip()
        # No title at the beginning of the Markdown file, use file name,
        # which has already been set to self.title, above.
        self.title = self.title.title()  # Force to title case
        if not self.content or not self.content[0].startswith("# "):
            self.content.insert(0, f"# {self.title}")
        # Rethink: if there's an existing title, replace it with the title-cased version.
        # If there's not an existing title, insert the generated title from the file name.
        # So: figure out what the title should be, then insert or replace the existing one.

    def update_chapter_number(self, new_number: str) -> None:
        # Only the number should be changed externally,
        # this object should manage the title by itself.
        self.number = new_number
        sanitized_title = re.sub(r"[^A-Za-z0-9 ]", "", self.title)
        new_name = f"{self.number} {sanitized_title}.md"
        self.path.rename(self.path.parent / new_name)
        self.path = self.path.parent / new_name
        # Ensure one and only one newline at the end of the file
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
            if f.is_file() and f.suffix == ".md"
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


def main() -> None:
    book = Book(Path(os.getcwd()))
    book.update_chapter_numbers()
    print(book)


if __name__ == "__main__":
    main()
