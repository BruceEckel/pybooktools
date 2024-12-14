# slug_line.py
import argparse
import re
from pathlib import Path

from rich.console import Console

from pybooktools.trace import trace
from pybooktools.util import display_function_name

console = Console()


def ensure_slug_line(pycode: str, file_path: Path) -> str:
    """
    Ensure slug line at the top of pycode based on file_path
    """
    lines = pycode.splitlines(True)
    slug_line = f"# {file_path.name}\n"

    # Check if the first line is a slug line
    if lines and re.match(r"^#\s*(?::\s+)?\w+\.py$", lines[0]):
        # Slug line exists, replace it:
        lines[0] = slug_line
    else:
        # Slug line doesn't exist, insert at top of file
        lines.insert(0, slug_line)
    return "".join(lines)


def main():
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
        display_function_name()

    if args.files:  # Multiple files on command line
        code_files: list[Path] = [Path(file) for file in args.files]
    elif args.recursive:
        code_files: list[Path] = [
            file
            for file in Path("../ptag").rglob("*.py")
            # Exclude directories starting with '.' or '_':
            if not any(
                (part.startswith(".") or part.startswith("_"))
                for part in file.parts
            )
        ]
    else:  # No flags == find all files in the current directory:
        code_files: list[Path] = list(Path("../ptag").glob("*.py"))

    if not code_files:
        console.print("No Python files found")
        return

    changes = 0
    for path in code_files:
        pycode = path.read_text(encoding="utf-8")
        slugged = ensure_slug_line(pycode, path)
        if slugged == pycode:
            console.print(f"[bold green]{path.name}[/bold green]")
        else:
            console.print(f"[red]{path.name}[/red]")
            changes += 1
        path.write_text(slugged, encoding="utf-8")
    console.print(f"[bold blue]Number of changes[/bold blue]: {changes}")


if __name__ == "__main__":
    main()
