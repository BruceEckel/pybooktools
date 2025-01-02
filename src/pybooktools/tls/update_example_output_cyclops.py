# update_example_output.py
"""
    pyfiles: The Python example file(s) (optional)

    Options:
      -a, --all              Process all Python examples in the current directory
      -r, --recurse          Find Python examples in subdirectories
      -v, --verbose          Trace info, save intermediate files, don't overwrite original file
      --nowrap               Do not wrap output lines
      -h, --help             Show this help message and exit
"""
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Optional, Annotated

import cyclopts
from cyclopts import Parameter

from pybooktools.tls.example_updater import ExampleUpdater
from pybooktools.util import console

app = cyclopts.App(name="px", help_format="rich")


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


@dataclass
class Args:
    pyfiles: Annotated[Optional[list[Path]], Parameter(negative="")] = None
    "The Python example file(s) (optional)"
    all_files: Annotated[Optional[Literal["-a", "--all"]], Parameter(negative="")] = None
    "Process all Python examples in the current directory"
    recurse: Annotated[Optional[Literal["-r", "--recurse"]], Parameter(negative="")] = None
    "Find Python examples in subdirectories"
    verbose: Annotated[Optional[Literal["-v", "--verbose"]], Parameter(negative="")] = None
    "Trace info, save intermediate files, don't overwrite original file"
    nowrap: Annotated[Optional[Literal["--nowrap"]], Parameter(negative="")] = None
    "Do not wrap output lines"


# def main(
#         pyfiles: Optional[list[Path]] = None,
#         all_files: Optional[Literal["-a", "--all"]] = None,
#         recurse: Optional[Literal["-r", "--recurse"]] = None,
#         verbose: Optional[Literal["-v", "--verbose"]] = None,
#         nowrap: Optional[Literal["--nowrap"]] = None,
# ):
# def px(a: Args = Args()):
@app.default
def main(
        pyfiles: Annotated[Optional[list[Path]], Parameter(help="The Python example file(s) (optional)")] = None,
        all_files: Annotated[Optional[Literal["-a", "--all"]], Parameter(
            help="Process all Python examples in the current directory")] = None,
        recurse: Annotated[
            Optional[Literal["-r", "--recurse"]], Parameter(help="Find Python examples in subdirectories")] = None,
        verbose: Annotated[Optional[Literal["-v", "--verbose"]], Parameter(
            help="Trace info, save intermediate files, don't overwrite original file")] = None,
        nowrap: Annotated[Optional[Literal["--nowrap"]], Parameter(help="Do not wrap output lines")] = None,
):
    """
    [green]Update embedded outputs in Python examples[/green]
    """
    if not pyfiles and not all_files and not recurse:
        app.help_print()
        console.print("\nError: No files specified and no mode selected (-a or -r)\n", style="bold red")
        sys.exit(1)

    wrap = not nowrap

    if pyfiles:
        process_files(
            [Path(file) for file in pyfiles],
            bool(verbose),
            wrap
        )
    else:
        process_files(
            collect_files(bool(recurse), bool(all_files)),
            bool(verbose),
            wrap
        )


if __name__ == "__main__":
    app()
