import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List


@dataclass
class Chapter:
    original_name: str
    number: str
    title: str
    path: Path

    def update_number(self, new_number: str) -> None:
        self.number = new_number
        self._rename_file()

    def update_title(self, new_title: str) -> None:
        self.title = new_title
        self._rename_file()

    def _rename_file(self) -> None:
        new_name = f"{self.number} {self.title}.md"
        self.path.rename(self.path.parent / new_name)
        self.path = self.path.parent / new_name

    def __str__(self) -> str:
        return f"{self.number} {self.title}"


@dataclass
class Book:
    directory: Path
    chapters: List[Chapter] = field(init=False)

    def __post_init__(self) -> None:
        chapter_files = [
            f
            for f in self.directory.iterdir()
            if f.is_file() and f.suffix == ".md"
        ]
        chapters = []

        for file in chapter_files:
            match = re.match(r"^(\d+[a-zA-Z]?)\s+(.+)\.md$", file.name)
            if match:
                number, title = match.groups()
                chapters.append(
                    Chapter(
                        original_name=file.name,
                        number=number,
                        title=title,
                        path=file,
                    )
                )

        self.chapters = sorted(
            chapters,
            key=lambda ch: (int(re.sub(r"\D", "", ch.number)), ch.number),
        )

    def ensure_chapter_titles(self) -> None:
        for i, chapter in enumerate(self.chapters, start=1):
            updated_number = f"{i:0{len(str(len(self.chapters)))}}"
            updated_title = chapter.title.title()  # Use title case

            content = chapter.path.read_text(encoding="utf-8").splitlines()

            if not content or not content[0].startswith("# "):
                content.insert(0, f"# {updated_title}")
            elif content[0] != f"# {updated_title}":
                content[0] = f"# {updated_title}"

            chapter.path.write_text("\n".join(content), encoding="utf-8")

            chapter.update_number(updated_number)
            chapter.update_title(updated_title)


def main() -> None:
    current_directory = Path(os.getcwd())
    book = Book(directory=current_directory)
    book.ensure_chapter_titles()


if __name__ == "__main__":
    main()
