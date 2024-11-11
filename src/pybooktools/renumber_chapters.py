import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List


@dataclass(order=True)
class Chapter:
    sort_index: int = field(init=False, repr=False)
    original_name: str
    number: str
    title: str
    path: Path

    def __post_init__(self) -> None:
        self.sort_index = int(re.sub(r"\D", "", self.number))

    def update_number_and_title(self, new_number: str, new_title: str) -> None:
        self.number = new_number
        self.title = new_title
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
            chapters, key=lambda ch: (ch.sort_index, ch.number)
        )

    def update_chapter_titles(self) -> None:
        for i, chapter in enumerate(self.chapters, start=1):
            updated_number = f"{i:0{len(str(len(self.chapters)))}}"
            updated_title = chapter.title.title()  # Use title case
            # splitlines() does not retain newlines at the end:
            content = chapter.path.read_text(encoding="utf-8").splitlines()

            if not content or not content[0].startswith("# "):
                content.insert(0, f"# {updated_title}")
            elif content[0] != f"# {updated_title}":
                content[0] = f"# {updated_title}"

            # Ensure one and only one newline at the end of the file
            chapter.path.write_text("\n".join(content) + "\n", encoding="utf-8")

            chapter.update_number_and_title(updated_number, updated_title)


def main() -> None:
    Book(Path(os.getcwd())).update_chapter_titles()


if __name__ == "__main__":
    main()
