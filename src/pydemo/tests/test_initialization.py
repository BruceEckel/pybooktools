# test_initialization.py
import os
from pathlib import Path

import pytest

from pydemo import DemoDir

test_input_text = """[test_dir]\n---\nprint('Hello, World!')"""


@pytest.fixture
def demo_dir_instance(tmp_path: Path) -> DemoDir:
    """Creates a DemoDir instance with temporary path."""
    test_path = tmp_path / "test_dir"
    return DemoDir(input_text=test_input_text.replace("test_dir", str(test_path)))


def test_demo_dir_initialization(demo_dir_instance: DemoDir):
    """Test that DemoDir is initialized correctly."""
    assert demo_dir_instance.dirpath.name == "test_dir"
    assert len(demo_dir_instance.examples) == 1
    assert demo_dir_instance.examples[0].example_text == "# example_1.py\nprint('Hello, World!')"


def test_demo_dir_directory_preparation(demo_dir_instance: DemoDir):
    """Test that DemoDir creates the correct directory."""
    assert demo_dir_instance.dirpath.exists()
    assert demo_dir_instance.dirpath.is_dir()


def test_demo_dir_example_files_written(demo_dir_instance: DemoDir):
    """Test that examples are written to disk properly."""
    example_file = demo_dir_instance.examples[0].file_path
    assert example_file.exists()
    assert example_file.read_text(encoding="utf-8").strip() == "# example_1.py\nprint('Hello, World!')"


def test_demo_dir_cleanup(demo_dir_instance: DemoDir):
    """Test that DemoDir cleanup removes the directory."""
    demo_dir_instance.delete()
    assert not demo_dir_instance.dirpath.exists()


def test_absolute_relative_path_handling(tmp_path: Path):
    """Test handling of absolute and relative paths."""
    rel_path = Path("relative/test/dir")
    abs_path = tmp_path / "absolute/test/dir"

    # Test relative path
    rel_input = f"[{rel_path}]\n---\nprint('test')"
    rel_demo = DemoDir(input_text=rel_input)
    assert rel_demo.dirpath.is_absolute()

    # Test absolute path
    abs_input = f"[{abs_path}]\n---\nprint('test')"
    abs_demo = DemoDir(input_text=abs_input)
    assert abs_demo.dirpath.is_absolute()


def test_path_separator_handling(tmp_path: Path):
    """Test handling of different path separators."""
    # Create path with forward slashes
    forward_path = tmp_path / "forward/slash/path"
    forward_input = f"[{forward_path}]\n---\nprint('test')"
    forward_demo = DemoDir(input_text=forward_input)
    assert forward_demo.dirpath.exists()

    # Create path with backslashes (Windows-style)
    back_path = str(tmp_path / "back\\slash\\path").replace('/', '\\')
    back_input = f"[{back_path}]\n---\nprint('test')"
    back_demo = DemoDir(input_text=back_input)
    assert back_demo.dirpath.exists()


def test_reuse_existing_directory(tmp_path: Path):
    """Test reusing an existing directory."""
    test_path = tmp_path / "reuse_dir"
    input_text = f"[{test_path}]\n---\nprint('test1')"

    # Create first instance
    demo1 = DemoDir(input_text=input_text)
    assert demo1.dirpath.exists()

    # Create second instance with same directory
    input_text2 = f"[{test_path}]\n---\nprint('test2')"
    demo2 = DemoDir(input_text=input_text2)
    assert demo2.dirpath.exists()

    # Verify content was updated
    assert "test2" in demo2.examples[0].example_text

