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

result = ""


@app.command(name="-f1")
def process_files(files: list[File]):
    global result
    result += f"-f1: process_files\n{files}"


@app.command(name="-f2")
def process_existing_files(files: list[ExistingFile]):
    global result
    result += f"-f2: process_existing_files\n{files}"


@app.command(name="-f3")
def process_resolved_files(files: list[ResolvedFile]):
    global result
    result += f"-f3: process_resolved_files\n{files}"


@app.command(name="-f4")
def process_resolved_existing_files(files: list[ResolvedExistingFile]):
    global result
    result += f"-f4: process_resolved_existing_files\n{files}"


@app.command(name="-x")
def examples():
    """Run examples"""
    global result
    all_combinations = product(
        ["-f1", "-f2", "-f3", "-f4"],
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
        result = ""
        app(cmdlist)
        console.print(Panel(result, title=str(cmdlist), style="bold"))


if __name__ == "__main__":
    app()
