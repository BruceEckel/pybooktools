import sys
from dataclasses import dataclass
from io import StringIO
from pathlib import Path
from typing import Any, List

import libcst as cst


@dataclass
class Show:
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
        output_lines = output.split("\n")

        # Retrieve the caller's source file and verify or update output comment lines
        caller_frame = sys._getframe(1)
        caller_file = Path(caller_frame.f_code.co_filename)
        self._verify_or_update_comments(
            caller_file, caller_frame.f_lineno, output_lines
        )

    def _verify_or_update_comments(
        self, file_path: Path, call_line: int, output_lines: List[str]
    ) -> None:
        """
        Verify or update the output comment lines in the given source file.
        """
        source_code = file_path.read_text(encoding="utf-8")
        module = cst.parse_module(source_code)

        class ShowVisitor(cst.CSTVisitor):
            def __init__(self, target_line: int):
                self.target_line = target_line
                self.call_node = None

            def visit_Call(self, node: cst.Call) -> None:
                if node.lpar and node.lpar[0].whitespace_after:
                    line_number = node.lpar[0].whitespace_after.first_line
                    if line_number == self.target_line:
                        self.call_node = node

        visitor = ShowVisitor(call_line)
        module.visit(visitor)

        if not visitor.call_node:
            raise ValueError("Could not find the call to show() in the specified line.")

        # Find the indentation level of the call line
        lines = source_code.splitlines()
        call_line_content = lines[call_line - 1]
        indentation = len(call_line_content) - len(call_line_content.lstrip())
        indent_str = " " * indentation

        # Collect the current output comment lines (if any)
        comment_lines = []
        for i in range(call_line, len(lines)):
            line = lines[i]
            if line.lstrip().startswith("#:"):
                comment_lines.append(line.strip()[3:].strip())
            else:
                break

        # Compare current comments with the expected output lines
        if comment_lines != output_lines:
            # Update the source code with the correct output comment lines
            new_lines = (
                lines[:call_line]
                + [f"{indent_str}#: {line}" for line in output_lines]
                + lines[call_line + len(comment_lines) :]
            )

            # Write the updated source code back to the file
            file_path.write_text("\n".join(new_lines), encoding="utf-8")


# Example usage
if __name__ == "__main__":
    show = Show()
    show("example output")  #
    #: example output
