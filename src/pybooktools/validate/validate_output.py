import sys
from dataclasses import dataclass, field
from io import StringIO
from pathlib import Path
from typing import Any, List, Optional

import libcst as cst
from icecream import ic
from libcst.metadata import ParentNodeProvider

from pybooktools.util import panic


# ic.disable()


@dataclass
class Show:
    output_lines: list[str] = field(default_factory=list)
    caller_file: Optional[Path] = None
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

        # Retrieve the caller's source file
        self._retrieve_caller_info()

        # Find and fix the first incorrect comment using libcst
        if self._fix_first_incorrect_show():
            # Re-run verification after updating comments
            if not self._verify_comments():
                ic()
                ic(self.output_lines)
                panic(f"Comments not corrected in {self.caller_file}")

    def _retrieve_caller_info(self) -> None:
        """
        Retrieve the caller's source file and store it.
        """
        self.caller_frame = sys._getframe(2)
        caller_filename = self.caller_frame.f_code.co_filename
        self.caller_file = Path(caller_filename)
        ic(self.caller_file.name)

    def _fix_first_incorrect_show(self) -> bool:
        """
        Find and fix the first incorrect show() call using libcst.
        """
        source_code = self.caller_file.read_text(encoding="utf-8")
        tree = cst.parse_module(source_code)
        wrapper = cst.metadata.MetadataWrapper(tree)
        transformer = ShowTransformer(self.output_lines)
        modified_tree = wrapper.visit(transformer)

        if transformer.found_incorrect:
            self.caller_file.write_text(modified_tree.code, encoding="utf-8")
            return True
        return False

    def _verify_comments(self) -> bool:
        """
        Verify the output comment lines in the given source file.
        """
        ic()
        source_code = self.caller_file.read_text(encoding="utf-8")
        tree = cst.parse_module(source_code)
        wrapper = cst.metadata.MetadataWrapper(tree)
        verifier = ShowVerifier(self.output_lines)
        wrapper.visit(verifier)
        return verifier.is_correct


class ShowTransformer(cst.CSTTransformer):
    METADATA_DEPENDENCIES = (ParentNodeProvider,)

    def __init__(self, output_lines: List[str]):
        super().__init__()
        self.output_lines = output_lines
        self.found_incorrect = False

    def leave_Call(
            self, original_node: cst.Call, updated_node: cst.Call
    ) -> cst.CSTNode:
        # Check if this is a `show()` call
        if (
                isinstance(original_node.func, cst.Name)
                and original_node.func.value == "show"
        ):
            # Find existing comments after the `show()` call
            parent = self.get_metadata(ParentNodeProvider, original_node)
            if isinstance(parent, cst.SimpleStatementLine):
                # Extract trailing comments if present
                comments = []
                if parent.trailing_whitespace.comment:
                    comments.append(
                        parent.trailing_whitespace.comment.value.strip()
                    )

                # Check if comments match expected output
                if comments != self.output_lines:
                    self.found_incorrect = True
                    # Update comments
                    new_comments = "\n".join(
                        [f"#: {line}" for line in self.output_lines]
                    )
                    updated_statement = parent.with_changes(
                        trailing_whitespace=cst.TrailingWhitespace(
                            whitespace=parent.trailing_whitespace.whitespace,
                            comment=cst.Comment(new_comments),
                            newline=cst.Newline(),
                        )
                    )
                    return updated_statement

        return updated_node


class ShowVerifier(cst.CSTVisitor):
    METADATA_DEPENDENCIES = (ParentNodeProvider,)

    def __init__(self, output_lines: List[str]):
        super().__init__()
        self.output_lines = output_lines
        self.is_correct = True

    def visit_Call(self, node: cst.Call) -> None:
        if isinstance(node.func, cst.Name) and node.func.value == "show":
            parent = self.get_metadata(ParentNodeProvider, node)
            if isinstance(parent, cst.SimpleStatementLine):
                # Extract trailing comments if present
                comments = []
                if parent.trailing_whitespace.comment:
                    comments.append(
                        parent.trailing_whitespace.comment.value.strip()
                    )

                if comments != self.output_lines:
                    self.is_correct = False
