# test_corner_cases.py
from pathlib import Path
import shutil
import pytest
from hypothesis import given, strategies as st

from pydemo import DemoDir


@pytest.mark.parametrize("input_text, expected_error", [
    ("", ValueError),  # No directory name
    ("---\nprint('No directory name')", ValueError),  # No valid directory header
    ("[valid_dir]\n---", ValueError),  # No content after separator
    ("[valid_dir]\n--- ###", ValueError),  # Invalid filename
])
def test_invalid_input(input_text: str, expected_error: type[Exception]):
    """Test that invalid inputs raise the appropriate exceptions."""
    with pytest.raises(expected_error):
        DemoDir(input_text)


@pytest.fixture
def demo_dir_empty(tmp_path: Path) -> DemoDir:
    """Creates a DemoDir instance with no example content."""
    input_text = f"[{tmp_path / 'empty_test_dir'}]"
    return DemoDir(input_text=input_text)


def test_no_examples(demo_dir_empty: DemoDir):
    """Test that DemoDir handles cases with no examples correctly."""
    assert demo_dir_empty.examples == []
    assert demo_dir_empty.dirpath.exists()


@pytest.fixture
def demo_dir_large_example(tmp_path: Path) -> DemoDir:
    """Creates a DemoDir instance with a large example."""
    large_content = "\n".join(["print('Line {0}')".format(i) for i in range(1000)])
    input_text = f"[{tmp_path / 'large_example_dir'}]\n---\n{large_content}"
    return DemoDir(input_text=input_text)


def test_large_example_file(demo_dir_large_example: DemoDir):
    """Test that large examples are handled correctly."""
    assert len(demo_dir_large_example.examples) == 1
    example = demo_dir_large_example.examples[0]
    assert example.file_path.exists()
    assert len(example.file_path.read_text(encoding="utf-8").splitlines()) == 1001  # Including the slug line


def test_special_characters_in_directory(tmp_path: Path):
    """Test that directories with special characters are handled correctly."""
    special_dir = tmp_path / "special_@_dir"
    input_text = f"[{special_dir}]\n---\nspecial_chars_test = 'Handled'"
    demo_dir = DemoDir(input_text=input_text)
    assert demo_dir.dirpath.exists()
    assert demo_dir.examples[0].example_text == "# example_1.py\nspecial_chars_test = 'Handled'"


def test_unicode_content(tmp_path: Path):
    """Test handling of Unicode content in examples."""
    input_text = f"""[{tmp_path / "unicode_dir"}]
    ---
    print('Hello, 世界!')"""
    demo_dir = DemoDir(input_text=input_text)
    assert demo_dir.examples[0].example_text == "# example_1.py\nprint('Hello, 世界!')"


def test_path_normalization(tmp_path: Path):
    """Test path normalization across different formats."""
    mixed_path = tmp_path / "path/../path/./demo"
    input_text = f"""[{mixed_path}]
    ---
    print('test')"""
    demo_dir = DemoDir(input_text=input_text)
    assert demo_dir.dirpath == (tmp_path / "path/demo").resolve()


@given(st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_categories=('Cs',))))
def test_property_example_content(tmp_path: Path, content: str):
    """Test that any valid content is preserved in examples."""
    input_text = f"""[{tmp_path / "prop_test_dir"}]
    ---
    {content}"""
    try:
        demo_dir = DemoDir(input_text=input_text)
        assert content.strip() in demo_dir.examples[0].example_text
    except ValueError:
        pytest.skip("Invalid input for DemoDir")
    finally:
        if (tmp_path / "prop_test_dir").exists():
            shutil.rmtree(tmp_path / "prop_test_dir")

