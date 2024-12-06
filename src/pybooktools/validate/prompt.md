An "output comment line" (abbreviated as OCL) in a Python example file shows the output of the previous `print()` statement.
It has the following properties:

1. It follows a call to `print()` 
2. Each OCL is indented to the same level as its preceding `print()` and begins with `#: `
3. There is one OCL for each output line produced by `print()`.
   If the call to `print()` produces multiple output lines, each line is represented with its own `#: ` OCL.
4. Each correct OCL contains, after the `#: `, the corresponding output line from the preceding `print()`

For example, correct OCLs look like this:  

```python
print("example output")
#: example output


def f():
    print("one line\nanother line")
    #: one line
    #: another line


def g():
    print(
        """
    multiple lines
    of output
    using triple quotes
    """
    )
    #: multiple lines
    #: of output
    #: using triple quotes


if __name__ == "__main__":
    print("in main")
    #: in main
    f()
    g()
```

Please create a program that will create OCLs for Python examples.

We will need two dataclasses. Here are the starting points, and you may add fields and methods to them as necessary:

```python
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
        self.original_example = self.example_path.read_text(
            encoding="utf-8"
        )
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
```

To process a Python example file to include OCLs:

1. Create a global `eo = ExampleOutput(example_path)` at the top of the text of `self.ocl_stripped_example`
2. Using `libcst`, find all the `print()` statements in `self.ocl_stripped_example`.
3. For each `print()` statement in `self.ocl_stripped_example`, 
   add a `PrintStatment` object to `eo.print_statements`, and replace the `print()` with
   a call to that `PrintStatment` object's `run()`, passing the original `print()` arguments to the `run()`
4. Write the result of step 3 to `self.adapted_example`
5. `exec()` the `self.adapted_example` code to generate and capture the outputs for each `run()` call.
6. Add the outputs from each run after the `print()` statements in `self.example_with_updated_ocls`.
   Perform this from the end going backwards, so there will be no line-numbering problems


-------

Create a program ensure_output.py that uses argparse for the command line. 
The program searches the current directory and recursively into subdirectories.
If you give it a file name on the command line, it will only look for that file.
It looks for Python files that contain calls to `print()`.
For each python file containing `print()` calls:
