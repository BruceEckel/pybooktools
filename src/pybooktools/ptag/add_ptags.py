#: add_ptags.py
"""
The argument to add_ptags is a string containing a valid Python script that may include print() statements.
Using libcst, find all `print()` statements and add a print() statement right after it, at the same indent level.
This added print() statement will be called a `ptag`.
The argument to the ptag is a simple string of the form:
f"_ptag_{n}"
Where n is an integer that is incremented for each ptag.
add_ptags returns the modified Python script.
"""
def add_ptags(python_example: str) -> str:
    pass