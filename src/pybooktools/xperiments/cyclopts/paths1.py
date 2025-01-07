# paths.py
from itertools import product
from pathlib import Path

from cyclopts import App
from cyclopts.types import File, ExistingFile, ResolvedFile, ResolvedExistingFile
from rich.console import Console
from rich.panel import Panel

console = Console()

app = App(
    version_flags=[],
    console=console,
    help_flags="-h",
)

display = True


def result(files: list[Path]):
    global display
    r = f"result: {files}"
    if display:
        print(f"result: {files}")
    return str(files)


@app.command
def f1(files: list[File]):
    """cyclopts.types.File"""
    return result(files)


@app.command
def f2(files: list[ExistingFile]):
    """cyclopts.types.ExistingFile"""
    return result(files)


@app.command
def f3(files: list[ResolvedFile]):
    """cyclopts.types.ResolvedFile"""
    return result(files)


@app.command
def f4(files: list[ResolvedExistingFile]):
    """cyclopts.types.ResolvedExistingFile"""
    return result(files)


@app.command(name="-x")
def examples():
    """Run examples"""
    all_combinations = product(
        ["f1", "f2", "f3", "f4"],
        [
            ["paths.py"],
            ["paths.py", "paths.py"],
            ["paths.py", "paths.py", "paths.py"],
            ["paths.py", "nonexistent.py"],
            ["nonexistent.py", "paths.py"],
            ["paths.py", "nonexistent1.py", "nonexistent2.py"],
            ["paths.py", "paths.py", "nonexistent3.py", "nonexistent4.py"],
        ]
    )
    global display
    display = False
    for cmdlist in [[command] + args for command, args in all_combinations]:
        console.print(
            Panel(
                f"[dark_goldenrod]{app(cmdlist)}",
                title=f"[sea_green1]{str(cmdlist)}",
                style="blue",
                title_align="left"
            )
        )


if __name__ == "__main__":
    app()
