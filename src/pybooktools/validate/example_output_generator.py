import sys
from dataclasses import dataclass, field
from io import StringIO
from pathlib import Path
from typing import Optional

import libcst as cst
import libcst.matchers as m

from pybooktools.util import error

eo: Optional["ExampleOutput"] = None


@dataclass
class PrintStatement:
    source: str
    line_number: int
    number_of_lines: int
    output: list[str] = field(default_factory=list)

    def run(self, *args, **kwargs) -> None:
        """
        Executes the original print statement and captures the output.
        """
        captured_output = StringIO()
        sys.stdout = captured_output
        try:
            # Execute print with the provided arguments
            print(*args, **kwargs)
        finally:
            sys.stdout = sys.__stdout__

        # Capture the printed output
        output = captured_output.getvalue().strip()
        self.output = output.split("\n")


@dataclass
class ExampleOutput:
    example_path: Path
    original_example: Optional[str] = None
    print_statements: list[PrintStatement] = field(default_factory=list)
    ocl_stripped_example: Optional[str] = None
    adapted_example: Optional[str] = None
    example_with_updated_ocls: Optional[str] = None

    def __post_init__(self):
        if not self.example_path.exists():
            error(f"{self.example_path} does not exist")
        if not self.example_path.is_file():
            error(f"{self.example_path} is not a file")
        if self.example_path.suffix != ".py":
            error(f"{self.example_path} is not a Python file")
        self.original_example = self.example_path.read_text(encoding="utf-8")
        self.ocl_stripped_example = self._strip_ocls(self.original_example)
        self.adapted_example = self.ocl_stripped_example
        self.example_with_updated_ocls = self.ocl_stripped_example

    @staticmethod
    def _strip_ocls(code: str) -> str:
        """
        Strips all output comment lines (OCLs) from the given code.
        """
        stripped_lines = []
        for line in code.splitlines():
            if not line.strip().startswith("#:"):
                stripped_lines.append(line)
        return "\n".join(stripped_lines)

    def process_print_statements(self):
        """
        Finds all print statements and replaces them with calls to PrintStatement.run().
        """

        class PrintTransformer(cst.CSTTransformer):
            def __init__(self):
                super().__init__()
                self.current_line = 0

            def on_leave(self, original_node, updated_node):
                self.current_line += len(original_node.leading_lines)
                return updated_node

            def leave_Call(
                    self, original_node: cst.Call, updated_node: cst.Call
            ) -> cst.BaseExpression:
                if m.matches(original_node.func, m.Name("print")):
                    line_number = self.current_line
                    source = cst.Module([]).code_for_node(updated_node)
                    number_of_lines = len(source.splitlines())
                    print_statement = PrintStatement(
                        source, line_number, number_of_lines
                    )
                    eo.print_statements.append(print_statement)
                    return updated_node.with_changes(
                        func=cst.Name("print_statement.run")
                    )
                return updated_node

        # Parse the original code into an AST and transform print statements
        module = cst.parse_module(self.ocl_stripped_example)
        transformed_module = module.visit(PrintTransformer())
        self.adapted_example = transformed_module.code

    def execute_adapted_example(self):
        """
        Executes the adapted example to capture outputs for each print statement.
        """
        global_vars = {"print_statement": PrintStatement}
        exec(self.adapted_example, global_vars)
        # Update print_statements with captured outputs
        for print_statement in self.print_statements:
            print_statement.run()

    def insert_ocls(self):
        """
        Inserts output comment lines after each print statement in the code.
        """
        lines = self.ocl_stripped_example.splitlines()
        for ps in reversed(self.print_statements):
            insert_idx = ps.line_number + ps.number_of_lines
            ocl_lines = [
                f"{'    ' * ps.line_number}#: {line}" for line in ps.output
            ]
            lines[insert_idx:insert_idx] = ocl_lines
        self.example_with_updated_ocls = "\n".join(lines)

    def write(self, output_path: Path = None):
        if not output_path:
            output_path = self.example_path
        output_path.write_text(self.example_with_updated_ocls, encoding="utf-8")


if __name__ == "__main__":
    example_path = Path("test_ocl_corrector.py")
    eo = ExampleOutput(example_path)
    eo.process_print_statements()
    eo.execute_adapted_example()
    eo.insert_ocls()
    eo.write()
