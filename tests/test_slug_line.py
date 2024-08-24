import argparse
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from pybooktools.slug_line import ensure_slug_line, FileChanged, main


# from src.pybooktools.slug_line import main


@pytest.fixture
def test_file():
    file_path = Path("testfile.py")
    yield file_path
    # Teardown
    if file_path.exists():
        file_path.unlink()


def test_ensure_slug_line_existing_correct(test_file):
    test_file.write_text("#: testfile.py\nprint('Hello, world!')")
    result = ensure_slug_line(test_file)
    assert isinstance(result, FileChanged)
    assert not result.modified
    assert test_file.read_text() == "#: testfile.py\nprint('Hello, world!')"


def test_ensure_slug_line_existing_incorrect(test_file):
    test_file.write_text("#: wrong_name.py\nprint('Hello, world!')")
    result = ensure_slug_line(test_file)
    assert isinstance(result, FileChanged)
    assert result.modified
    assert test_file.read_text() == "#: testfile.py\nprint('Hello, world!')"


def test_ensure_slug_line_missing(test_file):
    test_file.write_text("print('Hello, world!')")
    result = ensure_slug_line(test_file)
    assert isinstance(result, FileChanged)
    assert result.modified
    assert test_file.read_text() == "#: testfile.py\nprint('Hello, world!')"


def test_ensure_slug_line_empty_file(test_file):
    test_file.write_text("")
    result = ensure_slug_line(test_file)
    assert isinstance(result, FileChanged)
    assert result.modified
    assert test_file.read_text() == "#: testfile.py\n"


# -- Test --
# main()


@patch("argparse.ArgumentParser.parse_args")
@patch("src.pybooktools.slug_line.console.print")
def test_main_no_files_found(mock_console, mock_args):
    mock_args.return_value = argparse.Namespace(files=None, recursive=False)
    main()
    mock_console.assert_called_once_with("No Python files found")


@patch("argparse.ArgumentParser.parse_args")
@patch("src.pybooktools.slug_line.console.print")
def test_main_files_provided(mock_console, mock_args):
    mock_args.return_value = argparse.Namespace(
        files=["test.py"], recursive=False
    )
    mock_path = MagicMock()
    mock_path.parts = [".", "directory", "child", "file.py"]
    with patch.object(Path, "__iter__", return_value=iter([mock_path])):
        main()

    mock_console.assert_any_call("No Python files found")


@patch("argparse.ArgumentParser.parse_args")
@patch("src.pybooktools.slug_line.console.print")
def test_main_recursive(mock_console, mock_args):
    mock_args.return_value = argparse.Namespace(files=None, recursive=True)
    mock_path = MagicMock()
    mock_path.parts = [".", "directory", "child", "file.py"]
    with patch.object(Path, "rglob", return_value=iter([mock_path])):
        main()

    # assert the call contains the expected string
    assert mock_console.call_args[0][0].startswith(
        "[bold blue]Number of changes[/bold blue]"
    )
