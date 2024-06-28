import tempfile
from pathlib import Path

import pytest
from slug_line import FileChanged, ensure_slug_line


@pytest.fixture
def temp_file():
    temp_dir = tempfile.mkdtemp()
    temp_file = Path(temp_dir) / "test_file.py"
    temp_file.write_text("")

    yield temp_file

    temp_file.unlink()


def test_existing_correct_slug_line(temp_file):
    temp_file.write_text("#: test_file.py\n")
    result = ensure_slug_line(temp_file)
    assert isinstance(result, FileChanged)
    assert not result.modified
    assert temp_file.read_text() == "#: test_file.py\n"


def test_existing_incorrect_slug_line(temp_file):
    temp_file.write_text("#: wrong_file_name.py\n")
    result = ensure_slug_line(temp_file)
    assert isinstance(result, FileChanged)
    assert result.modified
    assert temp_file.read_text() == "#: test_file.py\n"


def test_no_existing_slug_line(temp_file):
    result = ensure_slug_line(temp_file)
    assert isinstance(result, FileChanged)
    assert result.modified
    assert temp_file.read_text() == "#: test_file.py\n"


def test_empty_file():
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir) / "tempfile.py"
        temp_path.touch()  # Create an empty file
        result = ensure_slug_line(temp_path)
        assert isinstance(result, FileChanged)
        assert result.modified
        assert temp_path.read_text() == f"#: {temp_path.name}\n"


# Add more tests as needed for edge cases, encoding, etc.
