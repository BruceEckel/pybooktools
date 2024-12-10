#: test_update_markdown_code_listings.py
from pathlib import Path

import pytest

from pybooktools.update_markdown_code_listings import MarkdownListing


@pytest.fixture
def markdown_file(tmp_path: Path) -> Path:
    # Automatically erased at the end of test
    file_path = tmp_path / "markdown_file.md"
    file_path.write_text("```\nprint('Hello, World!')\n```", encoding="utf-8")
    return file_path


def test_markdown_listing_initialization(markdown_file):
    # TODO output looks wrong here
    markdown_listing = MarkdownListing(
        "slugname", "```print('Hello, World!')```", markdown_file
    )

    assert markdown_listing.slugname == "slugname"
    assert markdown_listing.markdown_listing == "```print('Hello, World!')```"
    assert markdown_listing.source_file_path == markdown_file
    assert (
            markdown_listing.source_file_contents
            == "```python\n```\nprint('Hello, World!')\n``````"
    )
    assert markdown_listing.changed
    # assert markdown_listing.diffs == ""
    print(markdown_listing)
    print(markdown_listing.diffs)


def test_markdown_listing_init_with_non_existent_file():
    with pytest.raises(ValueError, match="source_file cannot be None"):
        MarkdownListing("slugname", "```print('Hello, World!')```", None)


def test_markdown_listing_change_detection():
    # create a temporary file with some python code for testing
    source_file = Path("./source_file.py")
    source_file.write_text("```\nprint('Hello, World!')\n```", encoding="utf-8")

    # source file and markdown_listing are different
    markdown_listing = MarkdownListing(
        "slugname", "```print('Hi, World!')```", source_file
    )

    assert markdown_listing.changed
    assert markdown_listing.diffs != ""


def test_markdown_listing_str_representation():
    # create a temporary file with some python code for testing
    source_file = Path("./source_file.py")
    source_file.write_text("```\nprint('Hello, World!')\n```", encoding="utf-8")

    markdown_listing = MarkdownListing(
        "slugname", "```print('Hello, World!')```", source_file
    )
    str_representation = str(markdown_listing)

    # we can just check if all the necessary information is included in the str representation
    assert "slugname" in str_representation
    assert "source_file.py" in str_representation
    assert "```print('Hello, World!')```" in str_representation

    # cleanup - delete the temporary file
    if source_file.exists():
        source_file.unlink()
