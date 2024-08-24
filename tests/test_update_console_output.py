import subprocess
import sys
from pathlib import Path
from unittest import mock

import pytest

from src.pybooktools.update_console_output import (
    main,
    debug,
    BoolStatus,
    check_script,
    clear_script_output,
)


# Testing: def debug(
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


# Testing: def check_script(script_path: Path) -> bool:


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


# Testing: def clear_script_output(script_path: Path) -> None:


def write_script_file(text: str) -> Path:
    # Helper to generate script file
    script_path = Path("test_script.py")
    with script_path.open("w") as f:
        f.write(text)
        print(f"{text = }")
    return script_path


@pytest.fixture
def set_up_script_files():
    # Create a setup for each test case
    # These are dummy scripts with some console messages
    yield [
        write_script_file('console == """Hello, world!"""'),
        write_script_file('console == """Goodbye, world!"""'),
        write_script_file("'This is a string, not a console message'"),
    ]


def test_clear_script_output_all_console_messages(set_up_script_files):
    # Test that `clear_script_output` clears all "console" messages
    for script in set_up_script_files:
        # print(f"{script = }")
        was_cleared = clear_script_output(script)
        cleared_script = script.read_text()
        # print(f"{cleared_script = }")
        # Assert that all cleared scripts should now have 'console == """"""'
        if was_cleared:
            assert 'console == """"""' in cleared_script
        else:
            assert True


def test_clear_script_output_no_console_message(set_up_script_files):
    # Test that `clear_script_output` doesn't clear strings that are not "console" messages
    for script in set_up_script_files:
        original_script = script.read_text()
        clear_script_output(script)
        cleared_script = script.read_text()
        # Assert that if no console message, then the script should remain the same
        if "console ==" not in original_script:
            assert cleared_script == original_script


# Testing: def main():


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
