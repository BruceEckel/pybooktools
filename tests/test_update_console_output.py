#: test_update_console_output.py
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from unittest import mock

import pytest

from pybooktools.util import BoolStatus
from src.pybooktools.update_console_output import (
    main,
    debug,
    check_script,
    clear_script_output,
)


# -- Testing --
# def debug(
#     *msgs: str, title: str | None = None, debugging: BoolStatus = debug_status
# ) -> None:


def test_debug_messages(capsys):
    debug("Hello", "World", debugging=BoolStatus(True))
    captured = capsys.readouterr()
    assert captured.out == "Hello\nWorld\n"


def test_debug_no_messages(capsys):
    debug(debugging=BoolStatus(False))
    captured = capsys.readouterr()
    assert captured.out == ""


def test_debug_with_title(capsys):
    debug("Hello", "World", title="Debugging", debugging=BoolStatus(True))
    captured = capsys.readouterr()
    assert (" " + "Debugging" + " ").center(50, "-") in captured.out
    assert "Hello" in captured.out
    assert "World" in captured.out


# -- Testing --
# def check_script(script_path: Path) -> bool:


def test_check_script_success(mocker):
    mocker.patch.object(sys, "executable", return_value="/usr/bin/python3")
    mocker.patch.object(
        subprocess,
        "run",
        return_value=subprocess.CompletedProcess(args=[], returncode=0),
    )
    assert check_script(Path("mock_script_path.py")) is True


def test_check_script_failure(mocker):
    mocker.patch.object(sys, "executable", return_value="/usr/bin/python3")
    mocker.patch.object(
        subprocess,
        "run",
        return_value=subprocess.CompletedProcess(args=[], returncode=1),
    )
    assert check_script(Path("mock_script_path.py")) is False


# -- Testing --
# def clear_script_output(script_path: Path) -> None:


@dataclass
class TempFile:
    name: str
    content: str

    def create(self, base_path: Path) -> Path:
        file_path = base_path / self.name
        file_path.write_text(self.content, encoding="utf-8")
        return file_path


@pytest.fixture
def temp_files(tmp_path: Path) -> list[Path]:
    # Create TempFile instances with names and content
    files = [
        TempFile("file_0.py", "console == '''Hello, world!'''"),
        TempFile("file_1.py", 'console == """Goodbye, world!"""'),
        TempFile("file_2.py", "'This is a string, not a console message'"),
    ]
    return [file.create(tmp_path) for file in files]


@pytest.mark.parametrize("temp_file_index", range(3))
def test_clear_script_output_all_console_messages(
        temp_file_index: int, temp_files: list[Path]
):
    # `clear_script_output` must clear all "console" messages
    script = temp_files[temp_file_index]
    was_cleared = clear_script_output(script)
    cleared_script = script.read_text()
    if was_cleared:
        assert 'console == """"""' in cleared_script
    else:
        assert True


@pytest.mark.parametrize("temp_file_index", range(3))
def test_clear_script_output_no_console_message(
        temp_file_index: int, temp_files: list[Path]
):
    # `clear_script_output` must not clear strings that are not "console" messages
    script = temp_files[temp_file_index]
    original_script = script.read_text()
    clear_script_output(script)
    cleared_script = script.read_text()
    # If no console message, script should remain the same:
    if "console ==" not in original_script:
        assert cleared_script == original_script


# -- Testing --
# def capture_script_output(script_path: Path, temp_content: str) -> str:

# -- Testing --
# def update_script_with_output(script_path: Path, outputs: list[str]) -> bool:

# -- Testing --
# def update_console_output(file_args: list[str], clear: bool):

# -- Testing --
# def main():


def test_main_clear_debug_on(capsys):
    test_args = ["prog", "file1.py", "--clear", "--debug"]
    with mock.patch.object(sys, "argv", test_args):
        main()
        captured = capsys.readouterr()
        assert "Clearing all outputs" in captured.out
        assert "Debugging" in captured.out


def test_main_clear_on(capsys):
    test_args = ["prog", "file1.py", "--clear"]
    with mock.patch.object(sys, "argv", test_args):
        main()
        captured = capsys.readouterr()
        assert "Clearing all outputs" in captured.out


def test_main_debug_on(capsys):
    test_args = ["prog", "file1.py", "--debug"]
    with mock.patch.object(sys, "argv", test_args):
        main()
        captured = capsys.readouterr()
        assert "Debugging" in captured.out


def test_main_no_flags(capsys):
    test_args = ["prog", "file1.py"]
    with mock.patch.object(sys, "argv", test_args):
        main()
        # Add checks here for what should appear on stdout when no flags are present.
