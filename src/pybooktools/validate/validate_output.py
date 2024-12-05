import sys
from io import StringIO
from pathlib import Path
from typing import Any, List

from icecream import ic

from pybooktools.util import panic


# ic.disable()


def show(*args: Any, **kwargs: Any) -> None:
    """
    Display the arguments using print() and capture the output to verify against output comment lines.
    """
    # Capture the output of print
    captured_output = StringIO()
    sys.stdout = captured_output
    print(*args, **kwargs)
    sys.stdout = sys.__stdout__

    # Get the printed output
    output = captured_output.getvalue().strip()
    output_lines = output.split("\n")

    # Retrieve the caller's source file and verify or update output comment lines
    caller_frame = sys._getframe(1)
    caller_filename = caller_frame.f_code.co_filename
    caller_file = Path(caller_filename)
    line_number = caller_frame.f_lineno
    ic(caller_file.name, line_number)
    if not _verify_comments(caller_file, line_number, output_lines):
        _update_comments(caller_file, line_number, output_lines)
        if not _verify_comments(caller_file, line_number, output_lines):
            ic()
            ic(output_lines)
            panic(f"Comments not corrected in {caller_file} line {line_number}")


def _verify_comments(
        file_path: Path, call_line: int, output_lines: List[str]
) -> bool:
    """
    Verify the output comment lines in the given source file.
    """
    ic()
    code_lines = file_path.read_text(encoding="utf-8").splitlines()

    # Collect the current output comment lines (if any)
    comment_lines = []
    for i in range(call_line, len(code_lines)):
        line = code_lines[i]
        if line.lstrip().startswith("#:"):
            comment_lines.append(line.strip()[3:].strip())
        else:
            break
    ic(comment_lines, output_lines, comment_lines == output_lines)

    # Compare current comments with the expected output lines
    return comment_lines == output_lines


def _update_comments(
        file_path: Path, call_line: int, output_lines: List[str]
) -> None:
    """
    Update the output comment lines in the given source file.
    """
    ic()
    code_lines = file_path.read_text(encoding="utf-8").splitlines()

    # Find the indentation level of the call line
    call_line_content = code_lines[call_line - 1]
    indentation = len(call_line_content) - len(call_line_content.lstrip())
    indent_str = " " * indentation

    # Collect the current output comment lines (if any)
    comment_lines = []
    for i in range(call_line, len(code_lines)):
        line = code_lines[i]
        if line.lstrip().startswith("#:"):
            comment_lines.append(line.strip()[3:].strip())
        else:
            break

    # Update the source code with the correct output comment lines
    new_lines = (
            code_lines[:call_line]
            + [f"{indent_str}#: {line}" for line in output_lines]
            + code_lines[call_line + len(comment_lines):]
    )

    # Write the updated source code back to the file
    file_path.write_text("\n".join(new_lines), encoding="utf-8")
