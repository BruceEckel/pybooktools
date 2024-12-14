# add_ptags_3.py
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

import libcst as cst


def add_ptags(python_example: str) -> str:
    """
    Given a Python script as a string, add ptag statements after each print() statement.

    Args:
        python_example (str): The input Python script.

    Returns:
        str: The modified Python script with ptag statements.
    """

    class PTagTransformer(cst.CSTTransformer):
        def __init__(self):
            super().__init__()
            self.ptag_counter = 1

        def leave_Module(self, original_node: cst.Module, updated_node: cst.Module) -> cst.Module:
            """
            Process the top-level statements in the module and append ptag statements
            after top-level prints or blocks containing prints.
            """
            new_body = []
            for stmt in original_node.body:
                new_body.append(stmt)
                if self._is_top_level_print(stmt) or self._contains_print(stmt):
                    new_body.append(self._create_ptag())
            return updated_node.with_changes(body=new_body)

        def _is_top_level_print(self, stmt: cst.CSTNode) -> bool:
            """Check if the statement is a top-level print statement."""
            return (
                    isinstance(stmt, cst.SimpleStatementLine)
                    and any(
                isinstance(expr, cst.Call)
                and isinstance(expr.func, cst.Name)
                and expr.func.value == "print"
                for expr in stmt.body
            )
            )

        def _contains_print(self, stmt: cst.CSTNode) -> bool:
            """Recursively check if a block contains a print statement."""
            if isinstance(stmt, (cst.If, cst.For, cst.While)):
                # Check main body
                for substmt in stmt.body.body:
                    if self._is_top_level_print(substmt) or self._contains_print(substmt):
                        return True
                # Check else/orelse body if applicable
                if stmt.orelse:
                    for substmt in stmt.orelse.body:
                        if self._is_top_level_print(substmt) or self._contains_print(substmt):
                            return True
            return False

        def _create_ptag(self) -> cst.SimpleStatementLine:
            """Create a print statement for the ptag."""
            ptag_code = f'print("_$_ptag_{self.ptag_counter}")'
            self.ptag_counter += 1
            return cst.parse_statement(ptag_code)

    tree = cst.parse_module(python_example)
    transformer = PTagTransformer()
    modified_tree = tree.visit(transformer)
    return modified_tree.code


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
