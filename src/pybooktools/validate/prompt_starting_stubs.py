import sys
from dataclasses import dataclass, field
from io import StringIO
from pathlib import Path
from typing import Optional

from pybooktools.util import error


@dataclass
class PrintStatement:
    # The text of the original `print()` in the Python example file:
    source: str
    line_number: int  # The starting line number of the original `print()` in the Python example file.
    number_of_lines: int  # The number of lines occupied by the original `print()` in the Python example file.
    output: list[str] = ""  # The captured output

    def run(self, *args, **kwargs) -> None:
        captured_output = StringIO()
        sys.stdout = captured_output
        print(*args, **kwargs)
        sys.stdout = sys.__stdout__

        # Get the printed output
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
        if self.example_path.suffix != "py":
            error(f"{self.example_path} is not Python file")
        self.original_example = self.example_path.read_text(encoding="utf-8")
        self.adapted_example = self.original_example
        self.ocl_stripped_example = self._strip_ocls(self.original_example)
        self.example_with_updated_ocls = self.ocl_stripped_example

    @staticmethod
    def _strip_ocls(code: str) -> str:
        pass  # Add code here

    def write(self, output_path: Path = None):
        if not output_path:
            output_path = self.example_path
        output_path.write_text(self.example_with_updated_ocls, encoding="utf-8")
