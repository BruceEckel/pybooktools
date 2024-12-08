"""
Using `libcst`, find all top-level (i.e., non-indented) `print()` statements.
Ensure that those top-level `print()` statements contain only a single argument.
Create a new string `ocl_printer` that contains the program with each `print()` replaced 
by a call to `oclgen()` that is passed, as its second argument, the argument of that `print()`.
The first argument to `oclgen()` is an incremented `int`.
For example:

```python
print("foo")
print("bar")
```

Becomes:

```python
oclgen("1", "foo")
oclgen("2", "bar")
```

Create a new directory beneath the directory of the file being tested.
Give that directory the name of the original script followed by `_check`.
Store all the following files in that directory.

Store `ocl_printer` in a file with the name of the original script followed by a `_1.py`.
Add imports and command at the end store the JSON data in a file with the name of the original script followed by `_3.json`.
Store that new thing  in a file with the name of the original script followed by a `_2.py`.
Run that file.
Read the JSON file into xxx and replace the oclgen calls in `_1.py` with the original print + the output lines.
Store that in a file with the name of the original script followed by a `_4.py`.
"""
