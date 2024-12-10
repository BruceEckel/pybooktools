In a canvas, create the program auto_ocl.py as follows.
The program takes a name of a Python file from the command line using argparse.
It turns that name into a Path called `example_path`.

Read the contents of `example_path` into `source_code_1` and `source_code_2`.

Modify `source_code_2`:
    1. Remove all lines that start with `#| `.
    2. Using `libcst`, find all `print()` statements.
    3. After each `print()`, add a line
        `_0n = ocl_format(arg)`
       where `n` is incremented for each `ocl_format` call, and `arg` is the argument of the `print()` statement.

For example:

```python
print(1)
print("foo")
print("A really long line that just keeps going am I finished yet? Yes!")
print({1: 2, 3: 4})
print({"a", "b", "c"})
print(3.14159)
print(f"The value of pi is {a_6}. Of course that has been rounded off")
```

Is read into `source_code_1`.

`source_code_2` becomes:

```python
from pybooktools.auto_ocl import ocl_format # Inserted by the program
from pathlib import Path # Inserted by the program

outfile = Path(.) / f"{example_path.stem}_ocl.py" # Inserted by the program

print(1)
_o1 = ocl_format(1)
print("foo")
_o2 = ocl_format("foo")
print("A really long line that just keeps going am I finished yet? Yes!")
_o3 = ocl_format("A really long line that just keeps going am I finished yet? Yes!")
print({1: 2, 3: 4})
_o4 = ocl_format({1: 2, 3: 4})
print({"a", "b", "c"})
_o5 = ocl_format({"a", "b", "c"})
print(3.14159)
_o6 = ocl_format(3.14159)
print(f"The value of pi is {a_6}. Of course that has been rounded off")
_o7 = ocl_format(f"The value of pi is {a_6}. Of course that has been rounded off")

outfile.write_text(f"""
print(1)
{_o1}
print("foo")
{_o2}
print("A really long line that just keeps going am I finished yet? Yes!")
{_o3}
print({1: 2, 3: 4})
{_o4}
print({"a", "b", "c"})
{_o5}
print(3.14159)
{_o6}
print(f"The value of pi is {a_6}. Of course that has been rounded off")
{_o7}
""")
```

Store `source_code_2` a file with the name of the original script followed by a `_2.py`.
Run Python on that file.
