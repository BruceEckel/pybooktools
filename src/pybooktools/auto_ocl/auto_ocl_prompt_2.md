In a canvas, create the program produce_ocl.py as follows.
The program takes a name of a Python file from the command line using argparse.
It turns that name into a Path called `example_path`.

Read the contents of `example_path` into `source_code_1` and make a copy into `source_code_2`.

Modify `source_code_2`:
1. Remove all comments that start with `#| `.
2. Using an appropriate syntax tree modification library, find all `print()` statements.
3. After each `print(arg)`, add a line
    `{ocl_format(arg)}`
   where `arg` is the argument of the `print()` statement.

Create `source_code_3` containing:

```python
from pybooktools.auto_ocl import ocl_format
from pathlib import Path

outfile = Path(.) / f"{example_path.stem}_ocl.py" 
outfile.write_text(
    f"""
{source_code_2}
""",
    encoding="utf-8",
)
```


For example:

```python
import math

print(1)
print("foo")
print("A really long line that just keeps going am I finished yet? Yes!")
print({1: 2, 3: 4})
print({"a", "b", "c"})
print(3.14159)
print(f"The value of pi is {math.pi}. Of course that has been rounded off")
```

Is read into `source_code_1`.

`source_code_3` becomes:

```python
from pybooktools.auto_ocl import ocl_format
from pathlib import Path

outfile = Path(.) / f"{example_path.stem}_ocl.py"

import math

outfile.write_text(f"""
import math

print(1)
{ocl_format(1)}
print("foo")
{ocl_format("foo")}
print("A really long line that just keeps going am I finished yet? Yes!")
{ocl_format("A really long line that just keeps going am I finished yet? Yes!")}
print({1: 2, 3: 4})
{ocl_format({1: 2, 3: 4})}
print({"a", "b", "c"})
{ocl_format({"a", "b", "c"})}
print(3.14159)
{ocl_format(3.14159)}
print(f"The value of pi is {math.pi}. Of course that has been rounded off")
{ocl_format(f"The value of pi is {math.pi}. Of course that has been rounded off")}
""",
    encoding="utf-8",
)
```

Store `source_code_3` a file with the name of the original script followed by a `_3.py`.
Run Python on that file.
