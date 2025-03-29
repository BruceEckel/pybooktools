# test_demo_dir.py
"""
pytest-based test suite for the `demo_dir.py` module. It tests various parts of the code
including parsing demo directory names, extracting paths, splitting directories vs. filenames,
parsing file blocks, creating `DemoDir` and `Example` objects, writing them to disk,
and re-loading them to verify round-trip integrity.

To run:
    pytest test_demo_dir.py
"""

from pathlib import Path

import pytest

from xperiments.pydemo import (
    DemoDir,
    Example,
)
from xperiments.pydemo.demo_dir import (
    parse_demo_dir_name,
    extract_path_part,
    split_directory_and_filename,
    parse_file_blocks,
)


@pytest.fixture
def sample_input_text() -> str:
    """
    Provide a reusable sample input text with multiple example blocks and directories.
    """
    return """[demo_dir_name]
---              # Create in demo_dir_name
print('Valid')
print('Example #1')
--- foo          # Create in demo_dir_name/foo
print('Another')
print('Valid')
print('Example #2')
--- bar          # Create in demo_dir_name/bar
print('Valid')
print('Example')
print('#3')
--- bar/baz      # Create in demo_dir_name/bar/baz
print('No slug line')
print('Example #4')
print('long enough')
--- baz/qux      # Create in demo_dir_name/baz/qux
print('For loop')
for i in range(5):
    print(f"{i = } Example #5")
--- baz/qux/zap  # Create in demo_dir_name/baz/qux/zap
print('While')
i = 0
while i < 5:
    i += 1
    print(f"{i = } Example #6")
--- named_file.py  # Create in demo_dir_name/named_file.py
print('Named file')
print('Example #7')
--- bun/another_named_file.py  # Create in demo_dir_name/bun/another_named_file.py
print('Another named file')
print('Example #8')
"""


def test_parse_demo_dir_name(sample_input_text: str) -> None:
    """
    Check that parse_demo_dir_name extracts the directory name and remaining lines properly.
    """
    lines = sample_input_text.splitlines()
    directory, remaining = parse_demo_dir_name(lines)
    assert directory.name == "demo_dir_name"
    # Ensure that the '---' lines remain in 'remaining'
    assert "---" in remaining[0]


def test_extract_path_part() -> None:
    """
    Test that extract_path_part correctly strips whitespace and comments after '#'.
    """
    line_with_comment = "---   foo/bar.py   # some comment"
    candidate = extract_path_part(line_with_comment)
    assert candidate == "foo/bar.py"

    line_empty = "--- # everything is comment"
    candidate = extract_path_part(line_empty)
    assert candidate == ""


@pytest.mark.parametrize(
    "candidate,expected_dir,expected_file",
    [
        ("", ".", None),
        ("foo.py", ".", "foo.py"),
        ("foo/bar.py", "foo", "bar.py"),
        ("some_dir", "some_dir", None),
        ("some/long/path.py", "some/long", "path.py"),
    ],
)
def test_split_directory_and_filename(
    candidate: str,
    expected_dir: str,
    expected_file: str | None,
    tmp_path: Path,
) -> None:
    """
    Test that split_directory_and_filename splits the path correctly into dir_path and filename.
    """
    root = tmp_path
    dir_path, filename = split_directory_and_filename(root, candidate)

    # Convert dir_path relative to root -> string
    relative_dir = str(dir_path.relative_to(root))

    # On Windows, this may contain backslashes, so we normalize to forward slashes.
    relative_dir = relative_dir.replace("\\", "/")

    assert relative_dir == expected_dir
    assert filename == expected_file


def test_parse_file_blocks(sample_input_text: str, tmp_path: Path) -> None:
    """
    Test parse_file_blocks to ensure it produces Example objects with correct directory/filename.
    """
    # 1. Extract the directory line
    lines = sample_input_text.splitlines()
    _, remaining_lines = parse_demo_dir_name(lines)

    # 2. Because parse_file_blocks calls Example(...) which expects
    #    Example.demo_dir_path to be set, we must set it here:
    Example.demo_dir_path = tmp_path

    # 3. Parse blocks
    examples = parse_file_blocks(remaining_lines, tmp_path)
    assert len(examples) == 8  # We have 8 blocks in sample_input_text

    # Spot-check some examples
    # The first block is '---              # Create in demo_dir_name'
    ex1 = examples[0]
    # It's auto-generated => example_1.py, relative to tmp_path
    assert ex1.filename is None
    assert "print('Valid')" in ex1.input_text
    assert ex1.dir_path == tmp_path

    # The last block is '--- bun/another_named_file.py'
    ex8 = examples[-1]
    # That has an explicit filename "another_named_file.py", subdir "bun"
    assert ex8.filename == "another_named_file.py"
    assert ex8.dir_path == tmp_path / "bun"


def test_example_class(tmp_path: Path) -> None:
    """
    Verify Example functionality: auto-generated filenames, slug insertion, writing to disk, etc.
    """
    # We must set the class variable so that Example.__post_init__ can compute relative paths
    Example.demo_dir_path = tmp_path
    Example.reset_counter()

    e = Example(
        dir_path=tmp_path,
        input_text="print('Hello, world!')",
    )
    # This should auto-generate example_1.py
    assert e._final_filename == "example_1.py"
    # Slug line should be inserted
    assert e.lines[0] == "# example_1.py"

    # Write to disk, ensure file is created
    e.write_to_disk()
    assert (tmp_path / "example_1.py").exists()
    written_content = (tmp_path / "example_1.py").read_text(encoding="utf-8").strip()
    # The first line in the file is slug line + the second line is print statement
    assert written_content.startswith("# example_1.py")
    assert "print('Hello, world!')" in written_content


def test_demo_dir_init(sample_input_text: str, tmp_path: Path) -> None:
    """
    Verify that DemoDir creates a directory with multiple examples as described.
    """
    d = DemoDir(sample_input_text)
    # Should create a folder named "demo_dir_name" in the current working directory
    assert d.dirpath.name == "demo_dir_name"

    # Should parse all examples
    assert len(d.examples) == 8

    # The directory should exist and contain subdirs/files
    assert d.dirpath.exists()
    for example in d.examples:
        # Each example file should be written
        assert example.file_path.exists()


def test_demo_dir_round_trip(sample_input_text: str, tmp_path: Path) -> None:
    """
    Test creating a DemoDir from text, then loading it back with from_directory, then from repr.
    """
    # 1) Create and write
    d1 = DemoDir(sample_input_text)
    assert len(d1.examples) == 8

    # 2) from_directory
    d2 = DemoDir.from_directory(d1.dirpath)
    assert len(d2.examples) == 8

    # 3) from repr => parse the text that d2.__repr__ produces
    d3 = DemoDir(repr(d2))
    assert len(d3.examples) == 8

    # Clean up
    d2.delete()
    assert not d1.dirpath.exists()
    assert not d2.dirpath.exists()
    assert not d3.dirpath.exists()


def test_demo_dir_from_file(tmp_path: Path) -> None:
    """
    Verify that DemoDir.from_file() works as intended.
    """
    content = """[temp_dir]
--- 
print('hello from file')
"""
    file_path = tmp_path / "demo_input.txt"
    file_path.write_text(content, encoding="utf-8")

    d = DemoDir.from_file(file_path)
    assert d.dirpath.name == "temp_dir"
    assert len(d.examples) == 1
    ex = d.examples[0]
    assert "hello from file" in ex.input_text

    # Check if file was physically created
    generated_path = d.dirpath / "example_1.py"
    assert generated_path.exists()

    # Clean up
    d.delete()
    assert not d.dirpath.exists()


def test_demo_dir_no_dir_raises() -> None:
    """
    If the input text does not contain [some_directory], we should get a ValueError.
    """
    bad_text = "--- foo.py\nprint('No dir line')"
    with pytest.raises(ValueError):
        _ = DemoDir(bad_text)


def test_delete_directory(sample_input_text: str) -> None:
    """
    Ensure that DemoDir.delete() removes the entire directory structure.
    """
    d = DemoDir(sample_input_text)
    # Directory should exist
    assert d.dirpath.exists()
    d.delete()
    # After delete, it should be gone
    assert not d.dirpath.exists()
