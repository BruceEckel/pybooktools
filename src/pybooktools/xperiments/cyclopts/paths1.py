# paths.py
from itertools import product

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


@app.command
def f1(files: list[File]):
    print(f"f1: {files}")
    return f"f1: {files}"


@app.command
def f2(files: list[ExistingFile]):
    print(f"f2: {files}")
    return f"f2: {files}"


@app.command
def f3(files: list[ResolvedFile]):
    print(f"f3: {files}")
    return f"f3: {files}"


@app.command
def f4(files: ResolvedExistingFile):
    print(f"f4: {files}")
    return f"f4: {files}"


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

    for cmdlist in [[command] + args for command, args in all_combinations]:
        console.print(Panel(app(cmdlist), title=str(cmdlist), style="bold"))


if __name__ == "__main__":
    app()
