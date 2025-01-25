# update_example_output.py
"""
Update embedded outputs in Python examples
"""
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated, Optional

from cyclopts import App, Parameter, Group, ValidationError
from cyclopts.types import ExistingDirectory
from rich.console import Console
from rich.panel import Panel

from pybooktools.util import PyExample, CreateExamples

console = Console()
app = App(
    version_flags=[],
    console=console,
    help_flags="-h",
    help_format="plaintext",
    help=__doc__,
    default_parameter=Parameter(negative=()),
)
optg = Group(
    "Option Flags (any combination)",
    default_parameter=Parameter(negative=""),  # Disable "--no-" flags
)
display = True


@dataclass
class OptFlags:
    no_wrap: Annotated[bool, Parameter(name="-nowrap", help="Do not wrap output", group=optg)] = False
    verbose: Annotated[bool, Parameter(name="-v", help="Verbose", group=optg)] = False
    trace: Annotated[bool, Parameter(name="-t", help="Trace", group=optg)] = False
    debug: Annotated[bool, Parameter(name="-d", help="Debug", group=optg)] = False


def report(fname: str, files: list[Path], opt_flags: OptFlags):
    global display
    r = f"{fname}:\n{files = }\n{opt_flags = }"
    if display:
        print(r)
    return r


def process(file_path: Path, verbose=False, wrap: bool = True) -> None:
    print(f"process({file_path}, verbose={verbose}, wrap={wrap}) ...")
    # ExampleUpdater(file_path, verbose=verbose).update_output(wrap=wrap)


@app.command(name="-f", sort_key=1)
def process_files(files: list[PyExample], *, opts: Optional[OptFlags] = None):
    """Files: Process one or more Python files provided as arguments"""
    opts = opts or OptFlags()
    for file in files:
        process(file, opts.verbose, not opts.no_wrap)
    return report("process_files", files, opt_flags=opts)


@app.command(name="-a", sort_key=2)
def all_files_in_dir(target_dir: ExistingDirectory = Path("."), opts: Optional[OptFlags] = None):
    """All: Process all Python examples in specified directory [.]"""
    opts = opts or OptFlags()
    # paths = list(valid_dir_path(target_dir).glob("*.py"))
    paths = list(target_dir.glob("*.py"))
    result = report("all_files_in_dir", paths, opt_flags=opts)
    process_files(paths, opts=opts)
    return result


@app.command(name="-r", sort_key=3)
def recursive(target_dir: ExistingDirectory = Path("."), opts: Optional[OptFlags] = None):
    """Recursive: Process all Python examples in specified directory [.] AND subdirectories"""
    opts = opts or OptFlags()
    # paths = list(valid_dir_path(target_dir).rglob("*.py"))
    paths = list(target_dir.rglob("*.py"))
    result = report("recursive", paths, opt_flags=opts)
    process_files(paths, opts=opts)
    return result


# Demo tests:

def run(arglist: list[str]):
    console.rule(str(arglist))
    try:
        console.print(
            Panel(
                f"[dark_goldenrod]{app(arglist, exit_on_error=False)}",
                title=f"[sea_green1]{str(arglist)}",
                style="blue",
                title_align="left"
            )
        )
    except (ValidationError, OSError):
        pass


@app.command(name="-x1")
def examples():
    """Run examples (1)"""

    demo_files = CreateExamples.from_file("updater_examples", "bad_examples.txt")
    global display
    display = False
    for demo in demo_files:
        run(["-f", str(demo.file_path), "-v", "-t", "-d"])
    run(["-a", "-v", "-t", "-d"])
    run(["-a", "updater_examples", "-v", "-t", "-d"])
    run(["-r", "-v", "-t", "-d"])
    run(["-r", "updater_examples", "-v", "-t", "-d"])
    run(["-a", "nonexistent_dir"])
    run(["-r", "nonexistent_dir"])
    demo_files.delete()


if __name__ == "__main__":
    app()
