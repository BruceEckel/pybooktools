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
