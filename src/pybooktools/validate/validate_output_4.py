import sys
from dataclasses import dataclass, field
from io import StringIO
from pathlib import Path
from typing import Any

from icecream import ic

from pybooktools.util import panic


# ic.disable()


@dataclass
class Show:
    output_lines: list[str] = field(default_factory=list)
    line_number: int = 0
    caller_file: Path = None
    caller_frame: Any = None

    def __call__(self, *args: Any, **kwargs: Any) -> None:
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
        self.output_lines = output.split("\n")

        # Retrieve the caller's source file and line number
        self._retrieve_caller_info()

        # Find and fix the first incorrect comment
        if self._find_first_incorrect_show():
            self._update_comments()
            # Recalculate line_number after updating comments
            self.line_number = self._get_updated_line_number()
            if not self._verify_comments():
                ic()
                ic(self.output_lines)
                panic(
                    f"Comments not corrected in {self.caller_file} line {self.line_number}"
                )

    def _retrieve_caller_info(self) -> None:
        """
        Retrieve the caller's source file and line number.
        """
        self.caller_frame = sys._getframe(2)
        caller_filename = self.caller_frame.f_code.co_filename
        self.caller_file = Path(caller_filename)
        self.line_number = self.caller_frame.f_lineno
        ic(self.caller_file.name, self.line_number)

    def _find_first_incorrect_show(self) -> bool:
        """
        Find the first show() call that has incorrect or nonexistent output comment lines.
        """
        code_lines = self.caller_file.read_text(encoding="utf-8").splitlines()
        for i, line in enumerate(code_lines):
            if "show(" in line:
                self.line_number = i + 1
                if not self._verify_comments():
                    return True
        return False

    def _get_updated_line_number(self) -> int:
        """
        Recalculate the line number of the show() call after updating the comments.
        """
        code_lines = self.caller_file.read_text(encoding="utf-8").splitlines()
        search_text = "show("
        for i in range(self.line_number - 1, len(code_lines)):
            if search_text in code_lines[i]:
                return i + 1

        # If not found after the original line, try scanning backwards to handle edge cases
        for i in range(self.line_number - 2, -1, -1):
            if search_text in code_lines[i]:
                return i + 1

        # Default to original line if no better match is found
        return self.line_number

    @staticmethod
    def _output_comment_lines(
        call_line: int, code_lines: list[str]
    ) -> list[str]:
        comment_lines = []
        for i in range(call_line, len(code_lines)):
            line = code_lines[i]
            ic(i, line)
            if line.lstrip().startswith("#:"):
                comment_lines.append(line.strip()[3:].strip())
            else:
                break
        return comment_lines

    def _verify_comments(self) -> bool:
        """
        Verify the output comment lines in the given source file.
        """
        ic()
        code_lines = self.caller_file.read_text(encoding="utf-8").splitlines()

        # Collect the current output comment lines (if any)
        comment_lines = self._output_comment_lines(self.line_number, code_lines)
        ic(comment_lines, self.output_lines, comment_lines == self.output_lines)

        # Compare current comments with the expected output lines
        return comment_lines == self.output_lines

    def _update_comments(self) -> None:
        """
        Update the output comment lines in the given source file.
        """
        ic()
        code_lines = self.caller_file.read_text(encoding="utf-8").splitlines()

        # Find the indentation level of the call line
        call_line_content = code_lines[self.line_number - 1]
        indentation = len(call_line_content) - len(call_line_content.lstrip())
        indent_str = " " * indentation

        # Collect the current output comment lines (if any)
        comment_lines = self._output_comment_lines(self.line_number, code_lines)

        # Update the source code with the correct output comment lines
        new_comment_lines = [
            f"{indent_str}#: {line}" for line in self.output_lines
        ]
        new_lines = (
            code_lines[: self.line_number]
            + new_comment_lines
            + code_lines[self.line_number + len(comment_lines) :]
        )

        # Write the updated source code back to the file
        self.caller_file.write_text("\n".join(new_lines), encoding="utf-8")
