# update_example_output.py
from pathlib import Path
from typing import Literal, Optional

import cyclopts

from pybooktools.util import console
from .example_updater import ExampleUpdater

app = cyclopts.App(help_format="rich")


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


@app.default
def main(
        pyfiles: Optional[list[Path]] = None,
        all_files: Optional[Literal["-a", "--all"]] = None,
        recurse: Optional[Literal["-r", "--recurse"]] = None,
        verbose: Optional[Literal["-v", "--verbose"]] = None,
        nowrap: Optional[Literal["--nowrap"]] = None,
):
    """
    Update embedded outputs in Python examples.

    usage: px [options] [pyfiles...]

    pyfiles: The Python example file(s) (optional)

    Options:
      -a, --all              Process all Python examples in the current directory
      -r, --recurse          Find Python examples in subdirectories
      -v, --verbose          Trace info, save intermediate files, don't overwrite original file
      --nowrap               Do not wrap output lines
      -h, --help             Show this help message and exit
    """
    if not pyfiles and not all_files and not recurse:
        console.print("\nError: No files specified and no mode selected (-a or -r)\n", style="bold red")
        exit(1)

    wrap = not nowrap

    if pyfiles:
        process_files([Path(file) for file in pyfiles], bool(verbose), wrap)
    else:
        process_files(collect_files(bool(recurse), bool(all_files)), bool(verbose), wrap)


if __name__ == "__main__":
    app()
