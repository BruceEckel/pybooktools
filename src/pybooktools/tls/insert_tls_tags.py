"""
insert_top_level_separators(script: str) -> str

Takes a string containing a Python script and divides it into top-level statements.
It doesn't change any of the original code, but inserts lines containing:

print("__$n$tls__")

(where n is an incremented int) after each top level statement.
The function returns the resulting string.
"""

import ast
from pathlib import Path


def insert_top_level_separators(script: str) -> str:
    """
    Inserts `print("__$n$tls__")` between top-level statements in a Python script.

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
                        (child.lineno, f'print("__${self.counter}$tls$__")\n')
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


use_cases = {
    1: [
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
print("__$1$tls$__")

def greet():
    print("Hello, world!")
print("__$2$tls$__")

if x > 10:
    greet()
else:
    print("Goodbye!")
print("__$3$tls$__")

""",
    ],
}


def test_insert_top_level_separators() -> None:
    results = []
    for case_id, (script, expected_output) in use_cases.items():
        actual_output = insert_top_level_separators(script)
        if actual_output == expected_output:
            results.append(f"Case {case_id} passed")
        else:
            results.append(
                f"""Case {case_id} failed
--- Expected ---\n{expected_output}
--- Actual ---\n{actual_output}
"""
            )
    this_file_path = Path(__file__.replace("\\", "/"))
    this_file = this_file_path.read_text(encoding="utf-8")
    output_tag = '\n"""Output:'
    if output_tag in this_file:
        this_file = this_file[: this_file.index(output_tag)]
    this_file_path.write_text(
        this_file + "\n" + f'"""Output:\n{"".join(results)}\n"""',
        encoding="utf-8",
    )


if __name__ == "__main__":
    test_insert_top_level_separators()
