"""
Take `python_source_code` and find every top-level (i.e., non-indented) `print(arg)` statement.
To avoid problems with the `arg` containing multiple lines and/or parentheses, use an appropriate syntax manipulation library.
Add a line directly after it like this:

print(arg)
_on = ocl_format(arg)

Where the `n` in `_on` is an `int` that is incremented for each subsequent `print(arg)` that `add_ocl` modifies.

If a top-level `print()` has more than one argument, `add_ocl` a warning and ignores that `print()`.
Returns the modified `python_source_code` string.
"""

import argparse
import ast
import re
from dataclasses import dataclass
from pathlib import Path

import astor

from pybooktools.util import warn


@dataclass
class PrintTransformer(ast.NodeTransformer):
    counter: int = 0

    def visit_Expr(self, node: ast.Expr) -> ast.AST:
        # Check if this is a `print()` call
        if isinstance(node.value, ast.Call) and isinstance(
                node.value.func, ast.Name
        ):
            if node.value.func.id == "print":
                args = node.value.args

                if (
                        len(args) == 1
                ):  # Handle only single-argument `print()` calls
                    self.counter += 1
                    ocl_line = ast.Expr(
                        value=ast.Call(
                            func=ast.Name(id="ocl_format", ctx=ast.Load()),
                            args=[args[0]],
                            keywords=[],
                        )
                    )

                    # Insert new `_on = _ocl_format(arg)` line
                    assignment = ast.Assign(
                        targets=[
                            ast.Name(id=f"_o{self.counter}", ctx=ast.Store())
                        ],
                        value=ocl_line.value,
                    )
                    return [node, assignment]
                else:
                    warn(
                        f"Args: {[astor.to_source(arg).strip() for arg in args]}",
                        "Ignoring multi-argument print()",
                    )

        return node


def add_ocl(python_source_code: str) -> str:
    """
    Strips old OCL comments.
    Modifies the provided Python source code to add `_on = ocl_format(arg)` lines after each top-level print(arg).

    Args:
        python_source_code (str): The Python source code to modify.

    Returns:
        str: The modified Python source code.
    """
    # Remove comments starting with `#| `
    de_ocl_code = re.sub(
        r"^#\| .*$", "", python_source_code, flags=re.MULTILINE
    )
    # Parse the Python source code
    tree = ast.parse(de_ocl_code)

    # Apply transformations
    transformer = PrintTransformer()
    modified_tree = transformer.visit(tree)

    # Ensure the tree is consistent
    ast.fix_missing_locations(modified_tree)

    # Convert the modified AST back to source code
    modified_source = astor.to_source(modified_tree)

    return modified_source


def test_add_ocl():
    sample_code = """
print("Hello")
#| Bob's yer
x = 10
print(x)
#| Uncle
print("This will be ignored", x)
"""
    modified_code = add_ocl(sample_code)
    print(modified_code)


def main():
    parser = argparse.ArgumentParser(
        description="Process a Python file with add_ocl."
    )
    parser.add_argument("file", type=str, help="The Python file to process.")
    args = parser.parse_args()
    file_path = Path(args.file)
    if not file_path.exists():
        print(f"Error: The file {file_path} does not exist.")
    else:
        source_code = file_path.read_text(encoding="utf-8")
        modified_code = add_ocl(source_code)
        print(modified_code)


if __name__ == "__main__":
    main()
