# update_example_output.py
"""
Update embedded outputs in Python examples
"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Annotated, Optional, Iterable

from cyclopts import App, Parameter, Group, ValidationError
from cyclopts.types import ExistingDirectory
from rich.console import Console
from rich.panel import Panel

from pybooktools.find_files.find_file_types import python_files
from pybooktools.update_example_output.example_updater import ExampleUpdater
from pybooktools.util.python_example_validator import PyExample

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


def report(fname: str, files: list[Path], opts: OptFlags):
    global display
    r = f"{fname}:\n{files = }\n{opts = }"
    if display:
        print(r)
    return r


@dataclass
class Issues:
    path: Path = Path("issues.txt")
    issue_list: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Clear the issues.txt file on creation"""
        self.path.write_text("", encoding="utf-8")

    def add(self, line: str) -> None:
        """Appends non-empty strings to the file"""
        with self.path.open("a", encoding="utf-8") as f:
            if line.strip():
                f.write(f"{line.strip()}\n")
                self.issue_list.append(line)

    def display(self, item: str = "") -> None:
        if self.issue_list:
            console.print(f"[red]Issues found in {item}:[/red]")
            for issue in self.issue_list:
                console.print(issue)
            console.print(f"[red]See {self.path}[/red]")


issues = Issues()  # Clears issues.txt when this script is loaded


def process_example(example_path: Path, verbose=False, wrap: bool = True) -> str:
    """Process a single example"""
    if verbose:
        print(f"process({example_path}, verbose={verbose}, wrap={wrap}) ...")
    # if "# R:" in example_path.read_text():
    #     return f"Skipping {example_path.name} because it has '# R:' comments"
    return ExampleUpdater(example_path, verbose=verbose).update_output(wrap=wrap)


def process_example_list(example_paths: Iterable[Path], verbose=False, wrap: bool = True) -> None:
    """Process a list of examples"""
    for example_path in example_paths:
        result = process_example(example_path, verbose=verbose, wrap=wrap)
        if result:
            issues.add(result)


@app.command(name="-f", sort_key=1)
def update_examples(files: list[PyExample], *, opts: Optional[OptFlags] = None) -> None:
    """Files: Process one or more Python files provided as arguments"""
    opts = opts or OptFlags()
    if opts.verbose:
        report("process_files", files, opts=opts)
    process_example_list(files, opts.verbose, not opts.no_wrap)
    issues.display(f"{files}")


@app.command(name="-a", sort_key=2)
def update_all_examples_in_dir(
    target_dir: ExistingDirectory = Path("."),
    opts: Optional[OptFlags] = None
) -> None:
    """All: Update all Python examples in specified directory [.]"""
    opts = opts or OptFlags()
    # paths = [p for p in target_dir.glob("*.py") if p.name != "__init__.py"]
    paths = list(python_files("d", target_dir))
    if opts.verbose:
        report("all_files_in_dir", paths, opts=opts)
    process_example_list(paths, opts.verbose, not opts.no_wrap)
    issues.display(f"{target_dir}")


@app.command(name="-r", sort_key=3)
def recursive(target_dir: ExistingDirectory = Path("."), opts: Optional[OptFlags] = None) -> None:
    """Recursive: Update all Python examples in specified directory [.] AND subdirectories"""
    opts = opts or OptFlags()
    for p in python_files("r", target_dir):
        if opts.verbose:
            report("recursive", [p], opts=opts)
        process_example(p, opts.verbose, not opts.no_wrap)
        issues.display(f"{p}")


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

# @app.command(name="-x")
# def examples(example_text_path: ExistingFile = Path("bad_examples.txt"), retain: bool = False):
#     """Run examples"""
#     # Abandon CreateExamples and instead use simpler Pytest approach
#     # of creating a temporary cloned directory.
#     print("Abandon this approach")
#     return
# demo_files = CreateExamples.from_file("updater_examples", example_text_path)
# global display
# display = False
# for demo in demo_files:
#     run(["-f", str(demo.example_path), "-v", "-t", "-d"])
# run(["-a", "updater_examples", "-v", "-t", "-d"])
# run(["-r", "updater_examples", "-v", "-t", "-d"])
# if not retain:
#     demo_files.delete()
