# add_ptags_2.py
"""
The argument to add_ptags is a string containing a valid Python script that may include print() statements.
Using an appropriate syntax manipulation tool, find all `print()` statements.

There may also be expressions involving indentation.

After each print() at the top level, or expressions at the top level with indentations and
containing a print() statement, add a "ptag".

A ptag is a `print()` with an argument of the form:
"_$_ptag_n"
Where n is an integer that is incremented for each ptag.
The `add_ptags` function returns the modified Python script.

The function will only add ptags to code at the top level (not inside a function).
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
"""

import ast
import astunparse


def add_ptags(python_example: str) -> str:
    """
    Given a Python script as a string, add ptag statements after each print() statement.

    Args:
        python_example (str): The input Python script.

    Returns:
        str: The modified Python script with ptag statements.
    """

    class PTagInserter(ast.NodeTransformer):
        def __init__(self):
            self.ptag_counter = 1

        def visit_Expr(self, node: ast.Expr) -> ast.AST:
            # Only process print() calls at the top level
            if (
                isinstance(node.value, ast.Call)
                and isinstance(node.value.func, ast.Name)
                and node.value.func.id == "print"
            ):
                # Create a new print() node for the ptag
                ptag_node = ast.Expr(
                    value=ast.Call(
                        func=ast.Name(id="print", ctx=ast.Load()),
                        args=[
                            ast.Constant(
                                value=f"_$_ptag_{self.ptag_counter}",
                                kind=None,
                            )
                        ],
                        keywords=[],
                    )
                )

                self.ptag_counter += 1

                # Attach the correct indentation to the new node
                ptag_node.col_offset = node.col_offset
                ptag_node.lineno = node.lineno + 1
                return [node, ptag_node]

            return node

        def generic_visit(self, node: ast.AST) -> ast.AST:
            # Avoid descending into function definitions
            if isinstance(node, ast.FunctionDef):
                return node
            return super().generic_visit(node)

    tree = ast.parse(python_example)
    transformer = PTagInserter()
    modified_tree = transformer.visit(tree)

    # Unparse the modified AST back to source code
    modified_code = astunparse.unparse(modified_tree)

    # Ensure all quotes are double quotes
    modified_code = modified_code.replace("'", '"')

    return modified_code.strip()


def check(ptagged: str, expected_output: str) -> None:
    if ptagged == expected_output:
        print("PASS")
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
    ptagged = add_ptags(input_code)
    check(ptagged, expected_output)

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
    ptagged = add_ptags(input_code)
    check(ptagged, expected_output)

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
    ptagged = add_ptags(input_code)
    check(ptagged, expected_output)

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
    ptagged = add_ptags(input_code)
    check(ptagged, expected_output)

    # Basic Test Cases:
    # Single print statement
    input_code = """print("Hello")""".strip()
    expected_output = """print("Hello")\nprint("_$_ptag_1")""".strip()
    ptagged = add_ptags(input_code)
    check(ptagged, expected_output)

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
    ptagged = add_ptags(input_code)
    check(ptagged, expected_output)

    # No print statements
    input_code = """
x = 10
y = 20
result = x + y
""".strip()
    expected_output = input_code
    ptagged = add_ptags(input_code)
    check(ptagged, expected_output)

    # Empty script
    input_code = """""".strip()
    expected_output = """""".strip()
    ptagged = add_ptags(input_code)
    check(ptagged, expected_output)

if __name__ == "__main__":
    test_add_ptags()
