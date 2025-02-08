# test_corner_cases.py
from pathlib import Path

import pytest

from pydemo import DemoDir


@pytest.mark.parametrize("input_text, expected_error", [
    ("", ValueError),  # No directory name
    ("---\nprint('No directory name')", ValueError),  # No valid directory header
    ("[valid_dir]\n---", ValueError),  # No content after separator
])
def test_invalid_input(input_text: str, expected_error: type[Exception]):
    """Test that invalid inputs raise the appropriate exceptions."""
    with pytest.raises(expected_error):
        DemoDir(input_text)


@pytest.fixture
def demo_dir_empty(tmp_path: Path) -> DemoDir:
    """Creates a DemoDir instance with no example content."""
    input_text = "[empty_test_dir]"
    return DemoDir(input_text=input_text)


def test_no_examples(demo_dir_empty: DemoDir):
    """Test that DemoDir handles cases with no examples correctly."""
    assert demo_dir_empty.examples == []
    assert demo_dir_empty.dirpath.exists()


@pytest.fixture
def demo_dir_large_example(tmp_path: Path) -> DemoDir:
    """Creates a DemoDir instance with a large example."""
    large_content = "\n".join(["print('Line {0}')".format(i) for i in range(1000)])
    input_text = f"[large_example_dir]\n---\n{large_content}"
    return DemoDir(input_text=input_text.replace("large_example_dir", str(tmp_path / "large_example_dir")))


def test_large_example_file(demo_dir_large_example: DemoDir):
    """Test that large examples are handled correctly."""
    assert len(demo_dir_large_example.examples) == 1
    example = demo_dir_large_example.examples[0]
    assert example.file_path.exists()
    assert len(example.file_path.read_text(encoding="utf-8").splitlines()) == 1001  # Including the slug line


def test_special_characters_in_directory(tmp_path: Path):
    """Test that directories with special characters are handled correctly."""
    input_text = """[special_@_dir]\n---\nspecial_chars_test = 'Handled'"""
    demo_dir = DemoDir(input_text=input_text.replace("special_@_dir", str(tmp_path / "special_@_dir")))
    assert demo_dir.dirpath.exists()
    assert demo_dir.examples[0].example_text == "# example_1.py\nspecial_chars_test = 'Handled'"
