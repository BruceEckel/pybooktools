from pathlib import Path
from pprint import pprint
from tempfile import TemporaryDirectory

import pytest

from pybooktools.renumber_chapters import MarkdownChapter, Book


@pytest.fixture(scope="module")
def temp_book_directory():
    with TemporaryDirectory() as tmpdir:
        temp_path = Path(tmpdir)
        create_chapter_file(
            temp_path, "1 Intro.md", "# Introduction\nSome content here."
        )
        create_chapter_file(
            temp_path, "2 Methodology.md", "# Methods\nSome content here."
        )
        create_chapter_file(
            temp_path, "4 Analysis.md", "# Analysis\nSome content here."
        )
        create_chapter_file(
            temp_path, "7 Conclusion.md", "# Conclusion\nSome content here."
        )
        create_chapter_file(
            temp_path,
            "3A Extra.md",
            "# Additional Information\nSome content here.",
        )
        create_chapter_file(
            temp_path, "10 Future Work.md", "# Future Scope\nSome content here."
        )
        create_chapter_file(
            temp_path,
            "11 Recommendations.md",
            "# Suggestions\nSome content here.",
        )
        create_chapter_file(
            temp_path, "5 Findings.md", "# Results\nSome content here."
        )
        create_chapter_file(
            temp_path, "8 Review.md", "# Literature Review\nSome content here."
        )
        create_chapter_file(
            temp_path,
            "12 Appendix.md",
            "# Supplementary Data\nSome content here.",
        )
        yield temp_path


def create_chapter_file(path: Path, name: str, content: str = "") -> Path:
    file_path = path / name
    file_path.write_text(content, encoding="utf-8")
    return file_path


def test_markdown_chapter_initialization(temp_book_directory):
    chapter_file = temp_book_directory / "1 Intro.md"
    chapter = MarkdownChapter(path=chapter_file)

    assert chapter.number == "1"
    assert chapter.file_name_title == "Intro"
    assert chapter.markdown_title == "Introduction"
    assert chapter.title == "Introduction"
    assert chapter.content[0] == "# Introduction"
    assert chapter.sort_index == 1


def test_markdown_chapter_update_chapter_number(temp_book_directory):
    chapter_file = temp_book_directory / "1 Intro.md"
    chapter = MarkdownChapter(path=chapter_file)
    chapter.update_chapter_number("2")

    assert chapter.number == "2"
    assert chapter.path.name == "2 Introduction.md"
    assert chapter.content[0] == "# Introduction"
    assert chapter.path.read_text(encoding="utf-8").endswith("\n")


def test_markdown_chapter_title_precedence(temp_book_directory):
    chapter_file = create_chapter_file(
        temp_book_directory, "4 Custom.md", "# Custom Title\nSome content here."
    )
    chapter = MarkdownChapter(path=chapter_file)

    assert chapter.title == "Custom Title"
    assert chapter.content[0] == "# Custom Title"


def test_book_initialization(temp_book_directory, capsys):
    book = Book(directory=temp_book_directory)
    with capsys.disabled():
        pprint([f.name for f in temp_book_directory.glob("*")])
        print(f"\n{book}")
    assert len(book.chapters) == 11
    # Before renumbering
    assert book.chapters[0].number == "2"
    assert book.chapters[1].number == "2"
    assert book.chapters[2].number == "3A"
    assert book.chapters[3].number == "4"
    assert book.chapters[4].number == "4"
    assert book.chapters[5].number == "5"
    assert book.chapters[6].number == "7"
    assert book.chapters[7].number == "8"
    assert book.chapters[8].number == "10"
    assert book.chapters[9].number == "11"
    assert book.chapters[10].number == "12"

    assert book.chapters[0].file_name_title == "Introduction"
    assert book.chapters[1].file_name_title == "Methodology"
    assert book.chapters[2].file_name_title == "Extra"
    assert book.chapters[3].file_name_title == "Analysis"
    assert book.chapters[4].file_name_title == "Custom"
    assert book.chapters[5].file_name_title == "Findings"
    assert book.chapters[6].file_name_title == "Conclusion"
    assert book.chapters[7].file_name_title == "Review"
    assert book.chapters[8].file_name_title == "Future Work"
    assert book.chapters[9].file_name_title == "Recommendations"
    assert book.chapters[10].file_name_title == "Appendix"


def test_book_update_chapter_numbers(temp_book_directory):
    book = Book(directory=temp_book_directory)
    book.update_chapter_numbers()

    assert len(book.chapters) == 11
    assert book.chapters[0].number == "01"
    assert book.chapters[1].number == "02"
    assert book.chapters[2].number == "03"
    assert book.chapters[3].number == "04"
    assert book.chapters[4].number == "05"
    assert book.chapters[5].number == "06"
    assert book.chapters[6].number == "07"
    assert book.chapters[7].number == "08"
    assert book.chapters[8].number == "09"
    assert book.chapters[9].number == "10"
    assert book.chapters[10].number == "11"

    assert book.chapters[0].path.name == "01 Introduction.md"
    assert book.chapters[1].path.name == "02 Methods.md"
    assert book.chapters[2].path.name == "03 Additional Information.md"
    assert book.chapters[3].path.name == "04 Analysis.md"
    assert book.chapters[4].path.name == "05 Custom Title.md"
    assert book.chapters[5].path.name == "06 Results.md"
    assert book.chapters[6].path.name == "07 Conclusion.md"
    assert book.chapters[7].path.name == "08 Literature Review.md"
    assert book.chapters[8].path.name == "09 Future Scope.md"
    assert book.chapters[9].path.name == "10 Suggestions.md"
    assert book.chapters[10].path.name == "11 Supplementary Data.md"


def test_book_str(temp_book_directory):
    book = Book(directory=temp_book_directory)
    book_str = str(book)
    assert "01 Introduction" in book_str
    assert "02 Methods" in book_str
    assert "03 Additional Information" in book_str
    assert "04 Analysis" in book_str
    assert "05 Custom Title" in book_str
    assert "06 Results" in book_str
    assert "07 Conclusion" in book_str
    assert "08 Literature Review" in book_str
    assert "09 Future Scope" in book_str
    assert "10 Suggestions" in book_str
    assert "11 Supplementary Data" in book_str


if __name__ == "__main__":
    pytest.main()
