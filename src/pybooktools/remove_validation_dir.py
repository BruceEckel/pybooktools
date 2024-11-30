# TODO: Add recursive removal
from pathlib import Path
from shutil import rmtree

from rich.console import Console
from rich.panel import Panel

from pybooktools.util import panic, trace_function_name

console = Console()


def main():
    trace_function_name(f"{Path(__file__).name}")
    validation_dir = Path(".") / "_validation"
    if not validation_dir.exists():
        panic(f"Does not exist: {validation_dir}")
    if not validation_dir.is_dir():
        panic(f"Is not a directory: {validation_dir}")

    # Use rmtree to remove the directory and its contents
    rmtree(validation_dir)
    console.print(
        Panel(
            f"[dark_slate_gray2]{validation_dir}[/dark_slate_gray2]",
            title="[bold light_green]Removed[/bold light_green]",
            title_align="left",
            border_style="light_green",
        )
    )


if __name__ == "__main__":
    main()
