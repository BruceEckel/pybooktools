import argparse
import ast
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass
class TopLevelPrintFinder(ast.NodeVisitor):
    """
    Finds top-level print statements in a Python AST.
    """

    top_level_prints: List[int] = None

    def __post_init__(self):
        self.top_level_prints = []

    def visit_Expr(self, node: ast.Expr) -> None:
        if isinstance(node.value, ast.Call) and isinstance(
                node.value.func, ast.Name
        ):
            if node.value.func.id == "print":
                self.top_level_prints.append(node.lineno)
        self.generic_visit(node)


def add_output_comments(script_path: Path, modified_script_path: Path) -> None:
    """
    Reads a Python script, identifies top-level print statements, executes the script,
    and appends output comments after each print statement.

    :param script_path: Path to the original Python script.
    :param modified_script_path: Path to save the modified Python script.
    """
    # Read the original script
    script_code = script_path.read_text(encoding="utf-8")

    # Parse the script to find top-level print statements
    tree = ast.parse(script_code)
    finder = TopLevelPrintFinder()
    finder.visit(tree)

    # Execute the script and capture output
    process = subprocess.run(
        ["python", str(script_path)],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    output_lines = process.stdout.splitlines()

    # Add output comments after print statements
    lines = script_code.splitlines()
    for lineno in sorted(finder.top_level_prints, reverse=True):
        if lineno - 1 < len(lines):
            output_comment = (
                f"#| {output_lines.pop(0)}"
                if output_lines
                else "#| <no output>"
            )
            lines.insert(lineno, output_comment)

    # Write the modified script
    modified_script_path.write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(
        description="Generate a modified script with output comments for top-level print statements."
    )
    parser.add_argument(
        "script_path", type=Path, help="Path to the original Python script."
    )
    parser.add_argument(
        "output_path",
        type=Path,
        help="Path to save the modified Python script.",
    )
    args = parser.parse_args()

    add_output_comments(args.script_path, args.output_path)


if __name__ == "__main__":
    main()
