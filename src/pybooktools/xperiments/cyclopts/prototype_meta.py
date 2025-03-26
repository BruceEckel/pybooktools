# prototype_meta.py
"""
pyfiles: The Python example file(s) (optional)

Options:
  -f python_file(s)      Process one or more Python files provided as arguments
  -a                     Process all Python examples in the current directory
  -r                     Find Python examples in subdirectories
  -v                     Trace info, save intermediate files, don't overwrite original file
  --nowrap               Do not wrap output lines
  -h                     Show this help message and exit
"""
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated

from cyclopts import App, Parameter, Group
from rich.console import Console

from pybooktools.util.display import display_function_name

console = Console()
app = App(
    version_flags=[],
    console=console,
    help_flags="-h",
    help_format="plaintext",
    help=__doc__,
)

opts = Group(
    "Option Flags (any combination)",
    default_parameter=Parameter(negative=""),  # Disable "--no-" flags
)


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


@app.command(name="-f", sort_key=1)
def process_file_arguments(files: list[Path], *, opt_flags=OptFlags.DEFAULT):
    """Process one or more Python files provided as arguments"""
    console.print(f"process_file_arguments {opt_flags=}")
    if opt_flags.debug:
        display_function_name()
        console.print(f"{files=}")
        console.print(f"{opt_flags=}")


@app.command(name="-a", sort_key=2)
def all_files_in_current_dir(opt_flags=OptFlags.DEFAULT):
    """Process all Python examples in the current directory"""
    if opt_flags.debug:
        display_function_name()
        console.print(f"{opt_flags=}")


@app.command(name="-r", sort_key=3)
def foo(opt_flags=OptFlags.DEFAULT):
    """Process all Python examples in current directory AND subdirectories"""
    if opt_flags.debug:
        display_function_name()
        console.print(f"{opt_flags=}")


@app.meta.default
def meta(
    *tokens: Annotated[str, Parameter(show=False, allow_leading_hyphen=True)],
    run_examples: Annotated[bool, Parameter(name="-x")] = False,
    opt_flags: OptFlags = OptFlags.DEFAULT,
):
    """
    Parameters
    ----------
    run_examples: bool
        Run example commands
    opt_flags: OptFlags
        Optional flags for "verbose", "trace", "debug" and "no wrap"; any combination of "-v", "-t", "-d", and "--nowrap"
    """
    if run_examples:
        return examples()

    additional_kwargs = {}
    command, bound, ignored = app.parse_args(tokens)
    if "opts" in ignored:
        additional_kwargs["opts"] = opt_flags
    if opt_flags.debug:
        display_function_name()
        console.print(f"command = {command.__name__}")
        console.print(f"{bound=}")
        console.print(f"{opt_flags=}")
        console.print(f"{additional_kwargs=}")

    return command(*bound.args, **bound.kwargs, **additional_kwargs)


def examples():
    def run(arglist: list[str]):
        console.rule()
        app.meta(arglist)

    run(["-f", "one", "two", "three"])
    run(["-f", "one", "two", "three", "-v", "-d"])
    run(["-f", "one", "two", "three", "-t", "-d"])
    run(["-a", "-v", "-d"])
    run(["-a", "-v", "-t"])
    run(["-a"])
    run(["-r"])
    run(["-r", "-v", "-t"])
    run(["-r", "-d", "-v"])
    # Flag order doesn't matter(!):
    run(["-a", "-v", "-d", "-t"])
    run(["-a", "-d", "-v", "-t"])
    run(["-a", "-d", "-t", "-v"])
    run(["-a", "-t", "-v", "-d"])

    run(["-h"])
    run(["-f", "-h"])


if __name__ == "__main__":
    app.meta()
