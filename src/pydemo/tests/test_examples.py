# test_examples.py
import threading
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


def test_concurrent_access(tmp_path: Path):
    """Test concurrent access to the same directory."""
    input_text = f"""[{tmp_path / "concurrent_dir"}]
    ---
    print('test')"""

    demo_dirs = []
    def create_demo_dir():
        demo_dirs.append(DemoDir(input_text=input_text))

    threads = [threading.Thread(target=create_demo_dir) for _ in range(3)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(demo_dirs) == 3
    assert all(d.dirpath.exists() for d in demo_dirs)


def test_empty_lines_handling(tmp_path: Path):
    """Test that empty lines are preserved in examples."""
    input_text = f"""[{tmp_path / "empty_lines_dir"}]
    ---
    print('line1')

    print('line2')

    print('line3')"""
    demo_dir = DemoDir(input_text=input_text)
    content = demo_dir.examples[0].file_path.read_text(encoding="utf-8")
    assert content.count('\n') == 5  # Including the slug line


def test_whitespace_preservation(tmp_path: Path):
    """Test that significant whitespace is preserved."""
    input_text = f"""[{tmp_path / "whitespace_dir"}]
    ---
    def example():
        print('indented')
            print('double indented')"""
    demo_dir = DemoDir(input_text=input_text)
    content = demo_dir.examples[0].file_path.read_text(encoding="utf-8")
    assert "    print('indented')" in content
    assert "        print('double indented')" in content

