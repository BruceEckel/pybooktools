#: slug_line.py
import argparse
import re
from pathlib import Path

from rich.console import Console

from pybooktools.tracing import trace
from pybooktools.util import FileChanged, display_function_name

console = Console()


def ensure_slug_line(file_path: Path) -> FileChanged:
    """
    Create or update the slug line in the Python file: file_path
    """
    changed = FileChanged(file_path.name)
    lines = file_path.read_text(encoding="utf-8").splitlines(True)
    correct_slug_line = f"#: {file_path.name}\n"

    # Check if the first line is a slug line
    if lines and re.match(r"^#:\s\w+\.py\n$", lines[0]):
        # Slug line exists, verify and correct if necessary
        if lines[0] != correct_slug_line:
            lines[0] = correct_slug_line
            file_path.write_text("".join(lines), encoding="utf-8")
            return changed.true()
        return changed.false()
    else:
        # Slug line doesn't exist, insert at top of file
        lines.insert(0, correct_slug_line)
        file_path.write_text("".join(lines), encoding="utf-8")
        return changed.true()


def main():
    display_function_name()
    parser = argparse.ArgumentParser(
        description="Create or update slug lines (commented file name at top) in Python files"
    )
    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="Recursively search for Python files in subdirectories (that don't start with '.' or '_')",
    )
    parser.add_argument(
        "-f",
        "--files",
        nargs="+",
        help="Specify one or more files to process",
    )
    parser.add_argument(
        "-t", "--trace", action="store_true", help="Enable tracing"
    )
    args = parser.parse_args()

    if args.trace:
        trace.enable()

    if args.files:
        # code_files = [Path(file) for file in args.files]
        code_files = map(Path, args.files)
    elif args.recursive:
        code_files = [
            file
            for file in Path(".").rglob(
                "*.py"
            )  # Exclude directories starting with '.' or '_':
            if not any(
                (part.startswith(".") or part.startswith("_"))
                for part in file.parts
            )
        ]
    else:  # No flags == find all files in the current directory:
        code_files = list(Path(".").glob("*.py"))

    if not code_files:
        console.print("No Python files found")
        return

    results = [ensure_slug_line(listing) for listing in code_files]
    for r in results:
        console.print(r.report())
    console.print(
        f"[bold blue]Number of changes[/bold blue]: {sum(r.modified for r in results)}"
    )


if __name__ == "__main__":
    main()
