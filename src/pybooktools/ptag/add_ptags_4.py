# add_ptags_4.py
"""
The argument to add_ptags is a string containing a valid Python script that may include print() statements.
Using an appropriate syntax manipulation tool, find all `print()` statements.

There may also be top-level expressions involving indentation.

After each print() at the top level, or expressions at the top level with indentations and
containing a print() statement, add a "ptag".

A ptag is a `print()` with an argument of the form:
"_$_ptag_n"
Where n is an integer that is incremented for each ptag.
The `add_ptags` function returns the modified Python script.

The function will only add ptags to code at the top level (not inside a function or within an indented top-level expression).
So ptags are never indented.
If the code being tagged involves indentation, the ptag will be added after all the indentation, for example:

```python
if True:
    print("Hello")
print("_$_ptag_1")
```

and:

```python
for i in range(3):
    print(f"Loop {i}")
print("_$_ptag_1")
```

See the examples in test_add_ptags() for more details.

DO NOT modify test_add_ptags(), but only modify add_ptags() so that the `expected_output`s are correctly produced.
"""


def add_ptags(python_example: str) -> str:
    """
    Given a Python script as a string, add ptag statements after each print() statement.

    Args:
        python_example (str): The input Python script.

    Returns:
        str: The modified Python script with ptag statements.
    """
    lines = python_example.split("\n")
    result = []
    ptag_counter = 1

    def get_indent(line: str) -> str:
        """Get the leading whitespace of a line."""
        return line[: len(line) - len(line.lstrip())]

    def is_print_statement(line: str) -> bool:
        """Check if a line is a print statement."""
        stripped = line.strip()
        return stripped.startswith("print(") and stripped.endswith(")")

    indent_stack = []  # Track the active blocks by indentation levels

    for i, line in enumerate(lines):
        stripped = line.strip()
        current_indent = get_indent(line)

        # Close blocks if indentation decreases
        while indent_stack and current_indent < indent_stack[-1]:
            indent_stack.pop()
            result.append(f'{current_indent}print("_$_ptag_{ptag_counter}")')
            ptag_counter += 1

        result.append(line)

        # If it's a print statement, add a ptag only after the block ends
        if is_print_statement(line):
            if not indent_stack:
                result.append(
                    f'{current_indent}print("_$_ptag_{ptag_counter}")'
                )
                ptag_counter += 1

        # If it's a block opener, track its indentation
        elif stripped.endswith(":"):
            indent_stack.append(current_indent)

    # Close any remaining open blocks
    while indent_stack:
        indent_stack.pop()
        result.append(f'print("_$_ptag_{ptag_counter}")')
        ptag_counter += 1

    return "\n".join(result)


def check(input_code: str, expected_output: str) -> None:
    ptagged = add_ptags(input_code)
    if ptagged == expected_output:
        print(" PASS ".center(40, "*"))
    else:
        print(" FAIL ".center(40, "*"))
        print(f"--- Expected ---\n{expected_output}")
        print(f"--- Actual ---\n{ptagged}")


def test_add_ptags() -> None:
    """Test the add_ptags function with various cases."""
    # New Test Cases:
    input_code = """
if True:
    print("Inside if")
""".strip()

    expected_output = """
if True:
    print("Inside if")
print("_$_ptag_1")
""".strip()
    check(input_code, expected_output)

    input_code = """
if True:
    if True:
        print("Deeply nested")
""".strip()

    expected_output = """
if True:
    if True:
        print("Deeply nested")
print("_$_ptag_1")
""".strip()
    check(input_code, expected_output)

    input_code = """
print("Start")
for i in range(3):
    print(f"Loop {i}")
print("End")
""".strip()
    expected_output = """
print("Start")
print("_$_ptag_1")
for i in range(3):
    print(f"Loop {i}")
print("_$_ptag_2")
print("End")
print("_$_ptag_3")
""".strip()
    check(input_code, expected_output)

    input_code = """
print("Normal")
if True:
    print("Nested")
""".strip()

    expected_output = """
print("Normal")
print("_$_ptag_1")
if True:
    print("Nested")
print("_$_ptag_2")
""".strip()
    check(input_code, expected_output)

    # Basic Test Cases:
    # Single print statement
    input_code = """print("Hello")""".strip()
    expected_output = """print("Hello")\nprint("_$_ptag_1")""".strip()
    check(input_code, expected_output)

    # Multiple print statements
    input_code = """
print("Hello")
x = 42
print("World")
""".strip()

    expected_output = """
print("Hello")
print("_$_ptag_1")
x = 42
print("World")
print("_$_ptag_2")
""".strip()
    check(input_code, expected_output)

    # No print statements
    input_code = """
x = 10
y = 20
result = x + y
""".strip()
    expected_output = input_code
    check(input_code, expected_output)

    # Empty script
    input_code = """""".strip()
    expected_output = """""".strip()
    check(input_code, expected_output)

    # print("All tests passed")


if __name__ == "__main__":
    test_add_ptags()
