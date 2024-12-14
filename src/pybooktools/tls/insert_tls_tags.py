# insert_tls_tags.py
"""
insert_top_level_separators(script: str) -> str

Takes a string containing a Python script and divides it into top-level statements.
It doesn't change any of the original code, but inserts lines containing:

print("__$n$_tls__")

(where n is an incremented int) after each top level statement.
The function returns the resulting string.
"""

import ast

from pybooktools.validate import UseCase, validate_transformer


def insert_top_level_separators(script: str) -> str:
    """
    Inserts `print("__$n$_tls__")` between top-level statements in a Python script.

    Args:
        script: A string containing the Python script.

    Returns:
        A string with a special `print` statement inserted after each top-level statement.
    """

    class TopLevelInserter(ast.NodeVisitor):
        def __init__(self):
            self.lines = script.splitlines(keepends=True)
            self.insertions = []
            self.counter = 1

        def visit_Module(self, node: ast.Module) -> None:
            # Collect top-level statements
            for child in node.body:
                if hasattr(
                        child, "end_lineno"
                ):  # Ensure it's a statement with an end line number
                    self.insertions.append(
                        (
                            child.end_lineno,
                            f'print("__${self.counter}$_tls__")\n',
                        )
                    )
                    self.counter += 1

        def apply_insertions(self) -> str:
            # Insert lines in reverse to maintain line number integrity
            for lineno, print_statement in reversed(self.insertions):
                self.lines.insert(lineno, print_statement)
            return "".join(self.lines)

    # Parse the script into an AST
    tree = ast.parse(script)

    # Traverse and collect top-level statements
    inserter = TopLevelInserter()
    inserter.visit(tree)

    # Apply the collected insertions and return the modified script
    return inserter.apply_insertions()


use_cases = [
    UseCase(
        case_id=1,
        script="""
x = 42
def greet():
    print("Hello, world!")

if x > 10:
    greet()
else:
    print("Goodbye!")

while True:
    print("Hello, world!")
    break
        """,
        expected_output="""
x = 42
print("__$1$_tls__")
def greet():
    print("Hello, world!")
print("__$2$_tls__")

if x > 10:
    greet()
else:
    print("Goodbye!")
print("__$3$_tls__")

while True:
    print("Hello, world!")
    break
print("__$4$_tls__")
        """,
    ),
    UseCase(
        case_id=2,
        script="""
class Example:
    def method(self):
        pass

example = Example()
example.method()
        """,
        expected_output="""
class Example:
    def method(self):
        pass
print("__$1$_tls__")

example = Example()
print("__$2$_tls__")
example.method()
print("__$3$_tls__")
        """,
    ),
    UseCase(
        case_id=3,
        script="""
def outer():
    def inner():
        print("Inner")
    inner()

outer()
        """,
        expected_output="""
def outer():
    def inner():
        print("Inner")
    inner()
print("__$1$_tls__")

outer()
print("__$2$_tls__")
        """,
    ),
    UseCase(
        case_id=4,
        script="""
for i in range(3):
    print(i)
        """,
        expected_output="""
for i in range(3):
    print(i)
print("__$1$_tls__")
        """,
    ),
    UseCase(
        case_id=5,
        script="""
x = 10
if x > 5:
    print("x is greater than 5")
        """,
        expected_output="""
x = 10
print("__$1$_tls__")
if x > 5:
    print("x is greater than 5")
print("__$2$_tls__")
        """,
    ),
]

if __name__ == "__main__":
    validate_transformer(insert_top_level_separators, use_cases)

""" Output From: validate_string_transformer

================ Case 1 passed ================
================ Case 2 passed ================
================ Case 3 passed ================
================ Case 4 passed ================
================ Case 5 passed ================
"""
