# test_examples.py
from pathlib import Path

import pytest

from pydemo import DemoDir


@pytest.fixture
def example_input() -> str:
    return """[example_test_dir]
    --- foo.py
    print('Example test file 1')
    --- bar.py
    print('Example test file 2')"""


@pytest.fixture
def demo_dir_with_examples(tmp_path: Path, example_input: str) -> DemoDir:
    test_path = tmp_path / "example_test_dir"
    return DemoDir(input_text=example_input.replace("example_test_dir", str(test_path)))


def test_example_count(demo_dir_with_examples: DemoDir):
    """Test that the correct number of examples are created."""
    assert len(demo_dir_with_examples.examples) == 2


def test_example_file_paths(demo_dir_with_examples: DemoDir):
    """Test that each example has the correct file path."""
    expected_paths = {"foo.py", "bar.py"}
    actual_paths = {example.file_path.name for example in demo_dir_with_examples.examples}
    assert actual_paths == expected_paths


def test_example_file_content(demo_dir_with_examples: DemoDir):
    """Test that example files have the correct content."""
    contents = [
        example.file_path.read_text(encoding="utf-8").strip() for example in demo_dir_with_examples.examples
    ]
    assert contents == [
        "# example_1.py\nprint('Example test file 1')",
        "# example_2.py\nprint('Example test file 2')"
    ]


def test_example_filename_generation(demo_dir_with_examples: DemoDir):
    """Test that filenames are generated correctly."""
    assert demo_dir_with_examples.examples[0].filename == "example_1.py"
    assert demo_dir_with_examples.examples[1].filename == "example_2.py"
