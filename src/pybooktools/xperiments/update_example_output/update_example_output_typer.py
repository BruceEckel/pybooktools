# update_example_output_typer.py
from pathlib import Path

import typer
from pybooktools.update_example_output.example_updater import ExampleUpdater
from pybooktools.util import console, HelpError

app = typer.Typer()


def process_files(file_paths: list[Path], verbose: bool, wrap: bool) -> None:
    """Process multiple Python files."""
    for file_path in file_paths:
        if file_path.is_file() and file_path.suffix == ".py":
            ExampleUpdater(file_path, verbose=verbose).update_output(wrap=wrap)
        else:
            console.print(f"Error: Invalid file: {file_path}", style="bold red")


def collect_files(recurse: bool, all_files: bool) -> list[Path]:
    """Collect files based on the provided options."""
    if all_files:
        return [file for file in Path.cwd().glob("*.py") if not file.name.startswith("_")]
    if recurse:
        return list(Path.cwd().rglob("*.py"))
    return []


@app.command()
def main(
    ctx: typer.Context,
    pyfiles: list[Path] = typer.Argument(
        None, help="The Python example file(s)", show_default=False
    ),
    verbose: bool = typer.Option(
        False, "-v", "--verbose", help="Trace info, save intermediate files, don't overwrite original file"
    ),
    nowrap: bool = typer.Option(
        False, "--nowrap", help="Do not wrap output lines"
    ),
    recurse: bool = typer.Option(
        False, "-r", "--recurse", help="Find Python examples in subdirectories"
    ),
    all_files: bool = typer.Option(
        False, "-a", "--all", help="Process all Python examples in the current directory"
    )
):
    """Update embedded outputs in Python examples."""
    if not pyfiles and not all_files and not recurse:
        HelpError(ctx)("No files specified and no mode selected (-a or -r)")

    wrap = not nowrap

    if pyfiles:
        process_files(pyfiles, verbose, wrap)
    else:
        process_files(collect_files(recurse, all_files), verbose, wrap)


if __name__ == "__main__":
    app()
