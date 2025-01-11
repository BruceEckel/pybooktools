# update_example_output.py
"""
Update embedded outputs in Python examples
"""
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated

from cyclopts import App, Parameter, Group
from rich.console import Console
from rich.panel import Panel

from pybooktools.tls import ExampleUpdater
from pybooktools.util import PyExample, create_demo_files

console = Console()
app = App(
    version_flags=[],
    console=console,
    help_flags="-h",
    help_format="plaintext",
    help=__doc__,
    default_parameter=Parameter(negative=()),
)
opts = Group(
    "Option Flags (any combination)",
    default_parameter=Parameter(negative=""),  # Disable "--no-" flags
)
display = True


@dataclass(frozen=True)
class OptFlags:
    no_wrap: Annotated[bool, Parameter(name="-nowrap", help="Do not wrap output", group=opts)] = False
    verbose: Annotated[bool, Parameter(name="-v", help="Verbose", group=opts)] = False
    trace: Annotated[bool, Parameter(name="-t", help="Trace", group=opts)] = False
    debug: Annotated[bool, Parameter(name="-d", help="Debug", group=opts)] = False
    DEFAULT = None
    NoParse = None


OptFlags.DEFAULT = OptFlags()
NoParse = Annotated[OptFlags, Parameter(parse=False)]


def report(fname: str, files: list[Path], opt_flags: OptFlags):
    global display
    r = f"{fname}:\n{files = }\n{opt_flags = }"
    if display:
        print(r)
    return r


def process(file_path: Path, verbose=False, wrap: bool = True) -> None:
    ExampleUpdater(file_path, verbose=verbose).update_output(wrap=wrap)


@app.command(name="-f", sort_key=1)
def process_files(files: list[PyExample], *, opt_flags=OptFlags.DEFAULT):
    """Files: Process one or more Python files provided as arguments"""
    for file in files:
        process(file, opt_flags.verbose, not opt_flags.no_wrap)
    result = report("process_files", files, opt_flags=opt_flags)
    return result


@app.command(name="-a", sort_key=2)
def all_files_in_current_dir(opt_flags=OptFlags.DEFAULT):
    """All: Process all Python examples in the current directory"""
    paths = list(Path(".").glob("*.py"))
    result = report("all_files_in_current_dir", paths, opt_flags=opt_flags)
    process_files(paths, opt_flags=opt_flags)
    return result


@app.command(name="-r", sort_key=3)
def recursive(opt_flags=OptFlags.DEFAULT):
    """Recursive: Process all Python examples in current directory AND subdirectories"""
    paths = list(Path(".").rglob("*.py"))
    result = report("recursive", paths, opt_flags=opt_flags)
    process_files(paths, opt_flags=opt_flags)
    return result


@app.command(name="-x")
def examples():
    """Run examples"""
    demo_dir = "updater_demos"
    examples: dict[str, str] = {
        "valid_example.py": "# valid_example.py\nprint('Valid')\nprint('Example')",
        "empty_file.py": "",
        "short_example.py": "# short_example.py\nprint('Too short')",
        "missing_slug.py": "print('No slug line')\nprint('Example')\nprint('long enough')",
        "main_included.py": "# main_included.py\nif __name__ == '__main__':\n    print('Main block included')",
        "non_python.txt": "This is not a Python file.",
    }
    create_demo_files(demo_dir, examples)
    global display
    display = False
    for cmdlist in all_combinations:
        console.print(
            Panel(
                f"[dark_goldenrod]{app(cmdlist, exit_on_error=False)}",
                title=f"[sea_green1]{str(cmdlist)}",
                style="blue",
                title_align="left"
            )
        )
    Path(demo_dir).rmdir()


if __name__ == "__main__":
    app()
