import difflib
from pathlib import Path
from typing import LiteralString

import pytest

from pybooktools.update_markdown_code_listings import (
    MarkdownListing,
    find_python_files_and_listings,
    update_markdown_listings,
)


def test_post_init():
    slugname: LiteralString | None = "slugname"
    markdown_listing = "markdown_listing"
    source_file_path = Path("/src/pybooktools/update_markdown_code_listings.py")

    markdown_listing_obj = MarkdownListing(
        slugname,
        markdown_listing,
        source_file_path,
    )

    assert markdown_listing_obj.slugname == slugname
    assert markdown_listing_obj.markdown_listing == markdown_listing
    assert markdown_listing_obj.source_file_path == source_file_path
    assert markdown_listing_obj.source_file_contents.startswith("```python\n")
    assert markdown_listing_obj.source_file_contents.endswith("```")

    differ = difflib.Differ()
    diff_lines = list(
        differ.compare(
            markdown_listing_obj.markdown_listing.splitlines(keepends=True),
            markdown_listing_obj.source_file_contents.splitlines(keepends=True),
        )
    )
    diffs = "".join(diff_lines)
    assert markdown_listing_obj.diffs == diffs


def test_post_init_file_not_exist():
    slugname: LiteralString | None = "slugname"
    markdown_listing = "markdown_listing"
    source_file_path = Path("/non/existent/path.py")

    with pytest.raises(ValueError, match=r"source_file cannot be None"):
        MarkdownListing(
            slugname=slugname,
            markdown_listing=markdown_listing,
            source_file_path=source_file_path,
        )


def test_str_method():
    slugname: LiteralString | None = "slugname"
    markdown_listing = "markdown_listing"
    source_file_path = Path("/src/pybooktools/update_markdown_code_listings.py")

    markdown_listing_obj = MarkdownListing(
        slugname=slugname,
        markdown_listing=markdown_listing,
        source_file_path=source_file_path,
    )
    str_representation = str(markdown_listing_obj)

    assert "Filename from slugline: slugname" in str_representation
    assert (
            "Source File: /src/pybooktools/update_markdown_code_listings.py"
            in str_representation
    )
    assert "Markdown Code Listing" in str_representation
    assert markdown_listing in str_representation
    assert "Source File Code Listing" in str_representation
    assert markdown_listing_obj.source_file_contents in str_representation
    assert "diffs" in str_representation
    assert markdown_listing_obj.diffs in str_representation


def test_find_python_files_and_listings_abs_path():
    markdown_content = "#[code_location] /abs_path/ --></>"
    result = find_python_files_and_listings(markdown_content)
    assert isinstance(result, list)
    assert all(isinstance(k, MarkdownListing) for k in result)


def test_find_python_files_and_listings_rel_path():
    markdown_content = "#[code_location] rel_path --></>"
    result = find_python_files_and_listings(markdown_content)
    assert isinstance(result, list)
    assert all(isinstance(k, MarkdownListing) for k in result)


def test_find_python_files_and_listings_duplicate_names():
    markdown_content = "#[code_location] /dup_path/ --></>\n#[code_location] /dup_path2/ --></>"
    with pytest.raises(SystemExit):
        find_python_files_and_listings(markdown_content)


def test_find_python_files_and_listings_listing_content_and_name():
    markdown_content = "```python\n#: filename.py \nsome_code\n```"
    result = find_python_files_and_listings(markdown_content)
    assert isinstance(result, list)
    assert all(isinstance(k, MarkdownListing) for k in result)
    for k in result:
        assert k.slugname == "filename.py"
        assert (
                k.markdown_listing == "```python\n#: filename.py \nsome_code\n```"
        )


def test_update_markdown_listings_no_change():
    markdown_content = "Some content"
    listing = MarkdownListing("slugname1", False, "Listing1")
    updated_markdown = update_markdown_listings(markdown_content, [listing])
    assert updated_markdown == markdown_content


def test_update_markdown_listings_with_change():
    markdown_content = "Some content with Listing2"
    listing = MarkdownListing("slugname2", True, "Listing2")
    updated_markdown = update_markdown_listings(markdown_content, [listing])
    assert updated_markdown == "Some content with Contents2"


def test_update_markdown_listings_multi_listings():
    markdown_content = "Some content with Listing1 and Listing2"
    listing1 = MarkdownListing("slugname1", True, "Listing1")
    listing2 = MarkdownListing("slugname2", False, "Listing2")
    updated_markdown = update_markdown_listings(
        markdown_content, [listing1, listing2]
    )
    assert updated_markdown == "Some content with Contents1 and Listing2"
