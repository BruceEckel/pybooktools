#: remove_validation_dir.py
import argparse
from pathlib import Path
from shutil import rmtree

from rich.console import Console
from rich.panel import Panel

from pybooktools.trace import trace
from pybooktools.util import display_function_name

console = Console()


def main():
    parser = argparse.ArgumentParser(
        description="Recursively remove '_validation' directories"
    )
    parser.add_argument(
        "-n",
        "--no_recurse",
        action="store_true",
        help="Only look in local directory",
    )
    parser.add_argument(
        "-t", "--trace", action="store_true", help="Enable tracing"
    )
    args = parser.parse_args()

    if args.trace:
        trace.enable()
        display_function_name()

    if args.no_recurse:
        validation_dirs = Path(".") / "_validation"
    else:
        validation_dirs = [
            dir_path
            for dir_path in Path(".").rglob("_validation")
            if dir_path.is_dir()
        ]
    if not validation_dirs:
        console.print(
            Panel(
                f"[dark_slate_gray2]No _validation dirs found[/dark_slate_gray2]",
                border_style="light_green",
            )
        )
    else:
        for val_dir in validation_dirs:
            rmtree(val_dir)
            console.print(
                Panel(
                    f"[dark_slate_gray2]{val_dir}[/dark_slate_gray2]",
                    title="[bold light_green]Removed[/bold light_green]",
                    title_align="left",
                    border_style="light_green",
                )
            )


if __name__ == "__main__":
    main()
