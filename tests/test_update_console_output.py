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
    capture_script_output,
    update_script_with_output,
    ScriptExecutionError,
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

original_content = "print('Hello world!')"


@pytest.fixture
def script_file(tmp_path: Path) -> Path:
    """Erases itself after the test"""
    file_path = tmp_path / "testfile.py"
    file_path.write_text(original_content)
    return file_path


def test_capture_script_output_success(script_file):
    test_content = "print('Test content')\nprint('Additional content')"
    expected_output = "Test content\nAdditional content\n"
    assert capture_script_output(script_file, test_content) == expected_output
    assert script_file.read_text() == original_content


def test_capture_script_output_fail(script_file):
    test_content = "exit(1)"  # Simulate a script that fails
    with pytest.raises(SystemExit) as excinfo:
        capture_script_output(script_file, test_content)
    assert excinfo.value.code == 1
    assert script_file.read_text() == original_content


# -- Testing --
# def update_script_with_output(script_path: Path, outputs: list[str]) -> bool:


@pytest.fixture
def tmp_script(tmp_path: Path) -> Path:
    script_path = tmp_path / "test_script.py"
    return script_path


@pytest.mark.parametrize(
    "initial_content, outputs, expected_modified, expected_content",
    [
        # Test case 1: No change needed
        (
                'print("Hello World!")',
                ["Hello World!"],
                False,
                'print("Hello World!")',
        ),
        # Test case 2: Single change in the script
        # (
        #     r'print("Hello World!")\nconsole = """',
        #     ["Hello World!"],
        #     True,
        #     'print("Hello World!")\nconsole = """\nHello World!\n"""',
        # ),
        # # Test case 3: Multiple outputs requiring modification
        # (
        #     'print("Hello World!")\nconsole = ""\nprint("Goodbye cruel world!")\nconsole = ""',
        #     ["Hello World!", "Goodbye cruel world!"],
        #     True,
        #     'print("Hello World!")\nconsole = """\nHello World!\n"""\nprint("Goodbye cruel world!")\nconsole = """\nGoodbye cruel world!\n"""',
        # ),
    ],
)
def test_update_script_with_output(
        tmp_script, initial_content, outputs, expected_modified, expected_content
):
    tmp_script.write_text(initial_content)

    try:
        assert (
                update_script_with_output(tmp_script, outputs) == expected_modified
        )
        assert tmp_script.read_text() == expected_content
    except ScriptExecutionError as e:
        pytest.fail(f"Script execution failed: {e}")


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
