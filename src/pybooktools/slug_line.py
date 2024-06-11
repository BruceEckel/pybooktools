#: slug_line.py
import argparse
import re
from dataclasses import dataclass, field
from pathlib import Path

from rich.console import Console

console = Console()


@dataclass
class Changed:
    file_name: str
    # Set to False and exclude field from constructor arguments
    modified: bool = field(default=False, init=False)

    def true(self) -> "Changed":
        self.modified = True
        return self

    def false(self) -> "Changed":
        self.modified = False
        return self

    def report(self) -> str:
        if self.modified:
            return f"[bold red]{self.file_name}[/bold red]"
        return f"[bold green]{self.file_name}[/bold green]"


def ensure_slug_line(file_path: Path) -> Changed:
    """
    Create or update the slug line in the Python file: file_path
    """
    changed = Changed(file_path.name)
    lines = file_path.read_text(encoding="utf-8").splitlines(True)
    correct_slug_line = f"#: {file_path.name}\n"

    # Check if the first line is a slug line
    if lines and re.match(r"^#\:\s\w+\.py\n$", lines[0]):
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
    parser = argparse.ArgumentParser(
        description="Create or update slug lines (commented file name at top) in Python files"
    )
    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="Recursively search for Python files in subdirectories (that don't start with '.')",
    )
    parser.add_argument(
        "-f",
        "--files",
        nargs="+",
        help="Specify one or more files to process",
    )
    args = parser.parse_args()

    if args.files:
        code_files = [Path(file) for file in args.files]
    elif args.recursive:
        code_files = [
            file
            for file in Path(".").rglob("*.py")
            if not any(part.startswith(".") for part in file.parts)
        ]
    else:  # No flags == find all files in current directory:
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
