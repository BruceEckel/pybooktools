"""
insert_top_level_separators(script: str) -> str

Takes a string containing a Python script and divides it into top-level statements.
It doesn't change any of the original code, but inserts lines containing:

print("__$n$_tls__")

(where n is an incremented int) after each top level statement.
The function returns the resulting string.
"""

import ast

from check_utils import UseCase, check_operation


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
                        child, "lineno"
                ):  # Ensure it's a statement with a line number
                    self.insertions.append(
                        (child.lineno, f'print("__${self.counter}$_tls__")\n')
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
        1,
        """
x = 42
def greet():
    print("Hello, world!")

if x > 10:
    greet()
else:
    print("Goodbye!")
        """,
        """
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

        """,
    )
]

if __name__ == "__main__":
    check_operation(insert_top_level_separators, use_cases)

""" Output From check_operation:

================ Case 1 failed ================
--- Expected ---

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

        
--- Actual ---

x = 42
print("__$1$_tls__")
def greet():
print("__$2$_tls__")
    print("Hello, world!")

if x > 10:
print("__$3$_tls__")
    greet()
else:
    print("Goodbye!")
        

"""
