#: update_console_output.py
"""
Update 'console ==' expressions in scripts.
Update all python scripts:
python update_console_output.py *
Update foo.py and bar.py:
python update_console_output.py foo.py bar.py

Note that this works only on the Python files, and not
the examples embedded in Markdown documents. To update those after
you've run this program, use:
`update_markdown_code_listings.py`.
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

from pybooktools.util import BoolStatus

console_pattern = re.compile(r'console\s*==\s*"""[\s\S]*?"""')
console_import_line = "from validate_output import console"
output_section_delimiter = "END_OF_CONSOLE_OUTPUT_SECTION"

debug_status = BoolStatus(False)


def debug(
        *msgs: str, title: str | None = None, debugging: BoolStatus = debug_status
) -> None:
    if debugging:
        if title is not None:
            print((" " + title + " ").center(50, "-"))
        for msg in msgs:
            print(msg)


def check_script(script_path: Path) -> bool:
    """Check to see if script runs"""
    print(f"Checking: {script_path} ", end="")
    result = subprocess.run(
        [sys.executable, str(script_path)], capture_output=True, text=True
    )
    if result.returncode != 0:
        print(" ... failed")
        return False
    else:
        print(" ... passed")
        return True


def clear_script_output(script_path: Path) -> bool:
    cleared = False
    debug(title=f"Clearing {script_path}")
    original_script = script_path.read_text()
    cleared_script = original_script
    matches = list(console_pattern.finditer(original_script))
    for match in matches:
        debug(f"{match.group(0) = }")
        cleared_script = cleared_script.replace(
            match.group(0), 'console == """"""', 1
        )
        script_path.write_text(cleared_script)
        cleared = True
    if cleared:
        debug(f"Cleared {script_path}")
        return True
    else:
        debug(f"Not cleared {script_path}")
        return False


def capture_script_output(script_path: Path, temp_content: str) -> str:
    """
    1. Temporarily rewrite the script for output capture
    2. Run it
    3. Restore original
    """
    original_content = script_path.read_text()
    script_path.write_text(
        temp_content
    )  # temp_content does not redirect output

    try:
        result = subprocess.run(
            [sys.executable, str(script_path)], capture_output=True, text=True
        )
        # Check if the script ran successfully
        if result.returncode != 0:
            print(" Temporary script failed ".center(50, "-"))
            print(temp_content)
            sys.exit(result.returncode)
        return result.stdout
    finally:  # Always restore original
        script_path.write_text(original_content)


def update_script_with_output(script_path: Path, outputs: list[str]) -> bool:
    """Update 'console ==' lines with the new outputs"""
    original_script = script_path.read_text()
    modified_script = original_script
    matches = list(console_pattern.finditer(original_script))
    # Replace the console placeholders with delimiter prints in the temp script
    for match in matches:
        debug(f"{match.group(0) = }")
        modified_script = modified_script.replace(
            match.group(0), f'print("{output_section_delimiter}")', 1
        )
    debug(modified_script, title="modified_script")
    if debug_status:
        modified_script_path = script_path.with_name(
            script_path.stem + "_modified.py"
        )
        print(f"{modified_script_path = }")
        modified_script_path.write_text(modified_script)

    # Capture output using the modified script
    output = capture_script_output(script_path, modified_script)
    debug(output, title="output")
    output_sections = output.split(output_section_delimiter)
    for output_section in output_sections:
        debug(f"{output_section = }")

    # Update original script with new outputs
    modified_script = original_script
    for match, new_output in zip(matches, output_sections):
        debug(f"{match.group(0) = }\n\t{new_output = }")
        modified_script = modified_script.replace(
            match.group(0), f'console == """\n{new_output.strip()}\n"""', 1
        )
    debug(modified_script, title="modified_script")

    if modified_script != original_script:
        script_path.write_text(modified_script)
        return True  # Changes made
    return False  # No changes made


def update_console_output(file_args: list[str], clear: bool):
    this_script_name = Path(__file__).name
    for file_pattern in file_args:
        for file in Path(".").glob(file_pattern):
            if file.name.endswith(".py") and file.name != this_script_name:
                content = file.read_text()
                if console_import_line in content:
                    if clear:
                        clear_script_output(file)
                        continue  # Do not process this file
                    if not check_script(file):
                        temp_content = content.replace(
                            console_import_line, "console = ''"
                        )
                        output = capture_script_output(file, temp_content)
                        outputs = [
                            out.strip()
                            for out in output.split("\n")
                            if out.strip()
                        ]
                        if update_script_with_output(file, outputs):
                            print(f"\t{file} updated with console outputs.")
                        else:
                            print(f"\t(No changes to {file})")


def main():
    parser = argparse.ArgumentParser(
        description="Update or clear 'console ==' output sections in Python scripts"
    )
    parser.add_argument(
        "files", nargs="+", help="File names or patterns to process"
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear outputs instead of updating them",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Turn on debugging",
    )
    args = parser.parse_args()
    if args.clear:
        print("Clearing all outputs")
    if args.debug:
        global debug_status
        debug_status = BoolStatus(True)
        print("Debugging")
    update_console_output(args.files, args.clear)


if __name__ == "__main__":
    main()
