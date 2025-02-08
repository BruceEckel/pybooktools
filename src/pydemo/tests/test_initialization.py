# test_initialization.py
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
