# file: show.py
import sys
from io import StringIO
from typing import List

import libcst as cst


class Show:
    def __call__(self, *args, **kwargs):
        """
        Call method to mimic print functionality, capture the output, and compare or update
        the output comments in the source file.
        """
        # Capture printed output
        captured_output = self._capture_output(args, kwargs)

        # Get source file of the call
        caller_frame = sys._getframe(1)
        caller_file = caller_frame.f_code.co_filename
        caller_lineno = caller_frame.f_lineno

        # Parse and modify the source file
        self._process_source_file(caller_file, caller_lineno, captured_output)

    def _capture_output(self, args, kwargs) -> List[str]:
        """
        Capture the printed output of the call.
        """
        buffer = StringIO()
        original_stdout = sys.stdout
        sys.stdout = buffer
        try:
            print(*args, **kwargs)
        finally:
            sys.stdout = original_stdout
        return buffer.getvalue().strip().split("\n")

    def _process_source_file(self, filename: str, lineno: int, output_lines: List[str]):
        """
        Process the source file to add or update output comment lines.
        """
        with open(filename, "r") as f:
            source_code = f.read()

        module = cst.parse_module(source_code)

        class UpdateCommentsVisitor(cst.CSTTransformer):
            def __init__(self, target_lineno: int, output_lines: List[str]):
                self.target_lineno = target_lineno
                self.output_lines = output_lines
                self.updated = False

            def leave_SimpleStatementLine(
                self,
                original_node: cst.SimpleStatementLine,
                updated_node: cst.SimpleStatementLine,
            ) -> cst.SimpleStatementLine:
                """
                Locate the target call line and update its comments if needed.

                Overrides the leave_SimpleStatementLine method from CSTTransformer.
                """
                if original_node.start.line == self.target_lineno:
                    # Check if there are output comments and compare them
                    comments_to_add = [
                        cst.Comment(f"#: {line}") for line in self.output_lines
                    ]
                    existing_comments = [
                        trailing.comment.value
                        for trailing in updated_node.trailing_whitespace.trailing
                        if trailing.comment
                    ]

                    if existing_comments == [
                        f"#: {line}" for line in self.output_lines
                    ]:
                        self.updated = True  # Comments already correct
                        return updated_node

                    # Update or add comments
                    updated_trailing_whitespace = (
                        updated_node.trailing_whitespace.with_changes(
                            trailing=[
                                cst.TrailingWhitespace(comment=c)
                                for c in comments_to_add
                            ]
                        )
                    )
                    self.updated = True
                    return updated_node.with_changes(
                        trailing_whitespace=updated_trailing_whitespace
                    )
                return updated_node

        visitor = UpdateCommentsVisitor(lineno, output_lines)
        updated_module = module.visit(visitor)

        if visitor.updated:
            # Write updated code back to the file
            with open(filename, "w") as f:
                f.write(updated_module.code)


def demo():
    show = Show()
    show("example output")  # Call show to test functionality


if __name__ == "__main__":
    demo()
