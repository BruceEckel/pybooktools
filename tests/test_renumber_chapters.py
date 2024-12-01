#: test_renumber_chapters.py
# This is still not testing differing file titles vs. Markdown titles

from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from pybooktools.renumber_chapters import MarkdownChapter, Book

# Centralized parameter data
chapter_data = [
    (0, "01", "Intro", "01", "Intro"),
    (1, "02", "Methods", "02", "Methods"),
    (2, "3A", "Additional Information", "03", "Additional Information"),
    (3, "04", "Data Analysis", "04", "Data Analysis"),
    (4, "05", "Custom", "05", "Custom"),
    (5, "06", "Results", "06", "Results"),
    (6, "07", "Conclusions", "07", "Conclusions"),
    (7, "08", "Review Of Literature", "08", "Review Of Literature"),
    (8, "09", "Future Work", "09", "Future Work"),
    (9, "10", "Recommendations", "10", "Recommendations"),
    (10, "11", "Appendix", "11", "Appendix"),
]


@pytest.fixture(scope="function")
def temp_book_directory():
    def create_chapter_file(path: Path, name: str, content: str = "") -> Path:
        file_path = path / name
        file_path.write_text(content, encoding="utf-8")
        return file_path

    with TemporaryDirectory() as tmpdir:
        temp_path = Path(tmpdir)
        # Create chapter files based on the centralized chapter_data
        for _, number, file_title, _, markdown_title in chapter_data:
            file_name = f"{number} {file_title}.md"
            create_chapter_file(
                temp_path, file_name, f"# {markdown_title}\nSome content here."
            )
        yield temp_path


@pytest.mark.parametrize(
    "chapter_index, initial_number, file_title, expected_number, markdown_title",
    chapter_data,
)
def test_book(
    temp_book_directory,
    chapter_index,
    initial_number,
    file_title,
    expected_number,
    markdown_title,
):
    book = Book(directory=temp_book_directory)
    book.update_chapter_numbers()
    expected_name = f"{expected_number} {markdown_title}.md"
    expected_content = f"{expected_number} {markdown_title}"

    assert len(book.chapters) == len(chapter_data)
    assert book.chapters[chapter_index].number == expected_number
    assert book.chapters[chapter_index].path.name == expected_name
    book_str = str(book)
    assert expected_content in book_str


@pytest.mark.parametrize(
    "chapter_index, initial_number, file_title, expected_number, markdown_title",
    chapter_data,
)
def test_book_initialization(
    temp_book_directory,
    chapter_index,
    initial_number,
    file_title,
    expected_number,
    markdown_title,
):
    book = Book(directory=temp_book_directory)
    print(book)
    assert len(book.chapters) == len(chapter_data)
    # Ensure numbering matches expected padded format:
    assert book.chapters[chapter_index].number == initial_number
    assert book.chapters[chapter_index].file_name_title == file_title
    assert book.chapters[chapter_index].markdown_title == markdown_title


@pytest.mark.parametrize(
    "chapter_index, expected_number",
    [(data[0], data[3]) for data in chapter_data],
)
def test_book_update_chapter_numbers(
    temp_book_directory, chapter_index, expected_number
):
    book = Book(directory=temp_book_directory)
    book.update_chapter_numbers()
    expected_name = (
        f"{expected_number} {book.chapters[chapter_index].markdown_title}.md"
    )

    assert len(book.chapters) == len(chapter_data)
    assert book.chapters[chapter_index].number == expected_number
    assert book.chapters[chapter_index].path.name == expected_name


@pytest.mark.skip(
    reason="Chapter might be not correcting for letters (doesn't work for point values either)"
)
@pytest.mark.parametrize(
    "expected_content", [f"{data[3]} {data[4]}" for data in chapter_data]
)
def test_book_str(temp_book_directory, expected_content):
    book = Book(directory=temp_book_directory)
    print(book)
    book_str = str(book)
    assert expected_content in book_str


def test_markdown_chapter_initialization(temp_book_directory):
    chapter_file = temp_book_directory / "01 Intro.md"
    chapter = MarkdownChapter(path=chapter_file)

    assert chapter.number == "01"
    assert chapter.file_name_title == "Intro"
    assert chapter.markdown_title == "Intro"
    assert chapter.title == "Intro"
    assert chapter.content[0] == "# Intro"
    assert chapter.sort_index == 1


def test_markdown_chapter_update_chapter_number(temp_book_directory):
    chapter_file = temp_book_directory / "01 Intro.md"
    chapter = MarkdownChapter(path=chapter_file)
    chapter.update_chapter_number("2")

    assert chapter.number == "2"
    assert chapter.path.name == "2 Intro.md"
    assert chapter.content[0] == "# Intro"
    assert chapter.path.read_text(encoding="utf-8").endswith("\n")


if __name__ == "__main__":
    pytest.main()
