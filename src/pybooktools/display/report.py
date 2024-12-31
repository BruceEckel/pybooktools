import collections
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel

from pybooktools.python_chapter.python_chapter import PythonExample, PythonChapter

console = Console(width=65)


def report(
        msg: str,
        title: str,
        msg_color: str = "orange3",
        title_color: str = "bold red",
        style="bold red",
) -> None:
    panel = Panel(
        f"[{msg_color}]{msg}[/{msg_color}]",
        title=f"[{title_color}]{title}[/{title_color}]",
        title_align="left",
        style=style,
    )
    console.print(panel)


def display_available_python_files(python_files: list[Path]) -> None:
    console.rule("[orange3]Available Python Files")
    # console.print(
    #     f"""[orange3]{"  Available Python Files  ".center(centering_width, "-")}[/orange3]"""
    # )
    for pyfile in [pf.name for pf in python_files]:
        console.print(f"\t[sea_green2]{pyfile}[/sea_green2]")
    console.rule("[orange3]Available Python Files")
    # console.print(f"""[orange3]{"-" * centering_width}[/orange3]""")


def find_duplicate_python_files(python_files: list[Path]) -> None:
    # Check for duplicate file names in `python_repo_examples`.
    # (Should python_repo_examples be a custom class?)
    # Map file names to their full paths:
    file_paths = collections.defaultdict(list)  # Values are lists
    for fpath in python_files:
        file_paths[fpath.name].append(fpath)

    # Discover duplicates
    duplicates = {
        file_name: paths
        for file_name, paths in file_paths.items()
        if len(paths) > 1
    }
    if duplicates:
        console.rule("[red]Duplicate Python File Names")
        # console.print(
        #     f"""[red]{"  Duplicate Python File Names  ".center(centering_width, "-")}[/red]"""
        # )
        for name, pyfile in duplicates.items():
            console.print(f"\t[red]{name}: {pyfile}[/red]")
        # console.print(f"""[red]{"-" * centering_width}[/red]""")
        console.rule("[red]")
        sys.exit(1)


def display_listing_status(listing: PythonExample) -> None:
    if listing.differs:
        console.print(f"[bold red]{listing.slugname}[/bold red]")
        console.print(f"[bright_cyan]{listing}[/bright_cyan]")
    else:
        console.print(f"[bold green]{listing.slugname}[/bold green]")


def display_python_example(pyexample: PythonExample) -> None:
    console.print(f"Filename from slugline: {pyexample.slugname}")
    console.print(f"Source File: {pyexample.repo_example_path.absolute() if pyexample.repo_example_path else ""}")
    console.print(f"{pyexample.differs = }")
    console.rule("[cyan]Markdown Code Listing")
    console.print(f"[chartreuse4]{pyexample.markdown_example}[/chartreuse4]")
    console.rule("[cyan]Repo Code Listing")
    console.print(f"[chartreuse4]{pyexample.repo_example}[/chartreuse4]")
    console.rule("[cyan]Diffs")
    console.print(f"[chartreuse4]{pyexample.diffs}[/chartreuse4]")
    console.rule("[cyan]")


def python_chapter_change_report(pychapter: PythonChapter) -> None:
    console.rule(f"[orange3]{pychapter.differences} Python Chapter Differences")
    for python_example in [python_example for python_example in pychapter.python_examples if python_example.differs]:
        console.print(f"[bright_cyan]{python_example.slugname}[/bright_cyan]")
