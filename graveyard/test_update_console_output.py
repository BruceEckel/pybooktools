import os
import tempfile
from pathlib import Path

import pytest
from update_console_output import (
    capture_script_output,
    clear_script_output,
    update_console_output,
    update_script_with_output,
)


# Helper function to create a temporary Python script
def create_temp_script(content: str, suffix: str = ".py") -> Path:
    temp_dir = tempfile.TemporaryDirectory()
    script_path = Path(temp_dir.name) / f"temp_script{suffix}"
    script_path.write_text(content)
    return script_path, temp_dir


def test_clear_script_output():
    script_content = '''
from validate_output import console
console == """Hello, World!"""
print("Hello, World!")
'''
    script_path, temp_dir = create_temp_script(script_content)
    clear_script_output(script_path)
    expected_content = '''
from validate_output import console
console == """"""
print("Hello, World!")
'''
    assert script_path.read_text() == expected_content
    temp_dir.cleanup()


def test_capture_script_output():
    script_content = """
print("Captured output")
"""
    script_path, temp_dir = create_temp_script(script_content)
    temp_content = """
print("END_OF_CONSOLE_OUTPUT_SECTION")
print("Captured output")
"""
    output = capture_script_output(script_path, temp_content)
    assert "Captured output" in output
    temp_dir.cleanup()


def test_update_script_with_output():
    script_content = '''
from validate_output import console
console == """"""
print("Updated output")
'''
    script_path, temp_dir = create_temp_script(script_content)
    temp_content = """
from validate_output import console
print("END_OF_CONSOLE_OUTPUT_SECTION")
print("Updated output")
"""
    output = capture_script_output(script_path, temp_content)
    update_script_with_output(script_path, [output])
    expected_content = '''
from validate_output import console
console == """
Updated output
"""
print("Updated output")
'''
    assert script_path.read_text().strip() == expected_content.strip()
    temp_dir.cleanup()


def test_update_console_output():
    script_content = '''
from validate_output import console
console == """"""
print("Test output")
'''
    script_path, temp_dir = create_temp_script(script_content)
    # Change the working directory to the temp directory to use relative paths
    original_cwd = Path.cwd()
    try:
        os.chdir(temp_dir.name)  # Corrected to use os.chdir()
        relative_script_path = script_path.relative_to(temp_dir.name)
        update_console_output([str(relative_script_path)], clear=False)
        expected_content = '''
from validate_output import console
console == """
Test output
"""
print("Test output")
'''
        assert script_path.read_text().strip() == expected_content.strip()
    finally:
        os.chdir(original_cwd)  # Corrected to use os.chdir()
    temp_dir.cleanup()


if __name__ == "__main__":
    pytest.main()
