# slug_line.py
from pathlib import Path
from typing import Annotated

import typer

from pybooktools.sluglines.slug import ensure_slug_line
from pybooktools.util.console import console
from pybooktools.util.display import display_function_name
from pybooktools.util.typer_help_error import HelpError

app = typer.Typer(
    context_settings={"help_option_names": ["--help", "-h"]},
    add_completion=False,
    rich_markup_mode="rich",
)


@app.command()
def main(
    ctx: typer.Context,
    recursive: Annotated[bool, typer.Option(
        "--recursive", "-r",
        help="Recursively search for Python files in subdirectories (that don't start with '.' or '_')"
    )] = False,
    files: Annotated[list[Path], typer.Option(
        "--files", "-f", help="Specify one or more files to process"
    )] = None,
    trace_flag: Annotated[bool, typer.Option(
        "--trace", "-t", help="Enable tracing"
    )] = False,
) -> None:
    """Create or update slug lines (commented file name at top) in Python files"""
    help_error = HelpError(ctx)

    if trace_flag:
        display_function_name()

    if files:  # Multiple files on command line
        code_files: list[Path] = files
    elif recursive:
        code_files: list[Path] = list(Path.cwd().rglob("*.py"))
    else:  # No flags == find all files in the current directory:
        code_files: list[Path] = list(Path.cwd().glob("*.py"))

    # Exclude directories starting with '.' or '_':
    code_files = [cf for cf in code_files if not any(
        (part.startswith(".") or part.startswith("_"))
        for part in cf.parts
    )]

    if not code_files:
        help_error("No Python files found")

    changes = 0
    result = ""
    for path in code_files:
        pycode = path.read_text(encoding="utf-8")
        slugged = ensure_slug_line(pycode, path)
        if slugged == pycode:
            result += f"[bold green]{path.name}[/bold green]\n"
        else:
            result += f"[red]{path.name}[/red]\n"
            changes += 1
        path.write_text(slugged, encoding="utf-8")
    console.rule(f"[bold blue]{changes} changes")
    console.print(result)


if __name__ == "__main__":
    app()
