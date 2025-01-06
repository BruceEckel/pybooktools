# update_example_output_cyclops2.py
from pathlib import Path
from typing import Optional, Annotated

import cyclopts
from cyclopts import Parameter

from pybooktools.tls.example_updater import ExampleUpdater
from pybooktools.util import console

app = cyclopts.App(name="px", help_format="rich", help="[green]Update embedded outputs in Python examples[/green]")


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


@app.command
def files(
        pyfiles: Annotated[Optional[list[Path]], Parameter(help="The Python example file(s) (optional)")],
        verbose: Annotated[bool, Parameter(name=["--verbose", "-v"],
                                           help="Trace info, save intermediate files, don't overwrite original file")] = False,
        nowrap: Annotated[bool, Parameter(name=["--nowrap"], help="Do not wrap output lines")] = False,
):
    """
    Provide one or more Python files to update
    """
    # if not pyfiles and not all_files and not recurse:
    #     app.help_print()
    #     console.print("\nError: No files specified and no mode selected (-a or -r)\n", style="bold red")
    #     sys.exit(1)

    wrap = not nowrap

    process_files(
        [Path(file) for file in pyfiles],
        bool(verbose),
        wrap
    )


@app.command
def star(
        verbose: Annotated[bool, Parameter(name=["--verbose", "-v"],
                                           help="Trace info, save intermediate files, don't overwrite original file")] = False,
        nowrap: Annotated[bool, Parameter(name=["--nowrap"], help="Do not wrap output lines")] = False,
):
    """
    Update all files in current directory
    """
    # if not pyfiles and not all_files and not recurse:
    #     app.help_print()
    #     console.print("\nError: No files specified and no mode selected (-a or -r)\n", style="bold red")
    #     sys.exit(1)

    wrap = not nowrap

    process_files(
        collect_files(recurse=False, all_files=True),
        bool(verbose),
        wrap
    )


@app.command
def recurse(
        verbose: Annotated[bool, Parameter(name=["--verbose", "-v"]),
        Parameter(help="Trace info, save intermediate files, don't overwrite original file")] = False,
        nowrap: Annotated[bool, Parameter(name=["--nowrap"], help="Do not wrap output lines")] = False,
):
    """
    Recursively update all files in current directory and subdirectories
    """
    wrap = not nowrap
    process_files(
        collect_files(recurse=True, all_files=False),
        bool(verbose),
        wrap
    )


if __name__ == "__main__":
    app()
