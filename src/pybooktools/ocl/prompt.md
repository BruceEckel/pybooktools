A top-level `print()` statement is one that is not inside a function or method; thus it is not indented.
The goal of this program is for each top-level `print()` statement in a Python script to be followed by the commented output of that `print()`.
These comments will start with `#| `.

To achieve this, we start with the `OCL` class:

```python
from dataclasses import dataclass, field
from pprint import pformat
from typing import Any, Optional


@dataclass
class OCL:
    arg: Any
    result: list[str] = field(default_factory=list)
    output_lines: list[str] = field(default_factory=list)
    output: Optional[str] = None

    def __init__(self):
        self.result = pformat(self.arg, width=47).splitlines()
        self.output_lines = ["#| " + line for line in self.result if line.strip()]
        self.output = "\n".join(self.output_lines)
```

Using `libcst`, find all top-level `print()` statements.
Create a new string `ocl_printer` that contains the program with each `print()` replaced by an `OCL` object that is passed the argument of that `print()`. 
Assign the resulting `OCL` to a variable that has a name starting with `o` followed by an incremented `int`.
For example:

```python
print("foo")
print("bar")
```

Produces an `ocl_printer`:

```python
o1 = OCL("foo")
o2 = OCL("bar")
```

Now `exec` the `ocl_printer` in the environment of the Python script.
Create a new string `ocl_result` where each `OCL` line is replaced by its original `print()` statement followed by the `output` of that `OCL`.
