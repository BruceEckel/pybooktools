# prototype.py
"""
Update embedded outputs in Python examples
"""
from dataclasses import dataclass
from itertools import product, chain
from pathlib import Path
from typing import Annotated

from cyclopts import App, Parameter, Group
from rich.console import Console
from rich.panel import Panel

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


@app.command(name="-f", sort_key=1)
def process_files(files: list[PyExample], *, opt_flags=OptFlags.DEFAULT):
    """Files: Process one or more Python files provided as arguments"""
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
    flags = [
        ["-nowrap", "-v", "-t", "-d"],
        ["-nowrap", "-v", "-t"],
        ["-nowrap", "-v"],
        ["-nowrap"],
    ]
    combinations_f = product(
        ["-f"],
        [
            ["prototype.py"],
            ["prototype.py", "prototype.py"],
            ["prototype.py", "prototype.py", "prototype.py"],
            ["prototype.py", "nonexistent.py"],
            ["nonexistent.py", "prototype.py"],
            ["prototype.py", "nonexistent1.py", "nonexistent2.py"],
            ["prototype.py", "prototype.py", "nonexistent3.py", "nonexistent4.py"],
        ],
        flags,
    )
    # Flatten:
    all_combinations = \
        [list(chain([a], b, c)) for a, b, c in combinations_f] + \
        [list(chain([a], b)) for a, b in product(["-a"], flags)] + \
        [list(chain([a], b)) for a, b in product(["-r"], flags)]
    global display
    display = False
    for cmdlist in all_combinations:
        console.print(
            Panel(
                f"[dark_goldenrod]{app(cmdlist)}",
                title=f"[sea_green1]{str(cmdlist)}",
                style="blue",
                title_align="left"
            )
        )


# @app.meta.default
# def meta(
#     *tokens: Annotated[str, Parameter(show=False, allow_leading_hyphen=True)],
#     run_examples: Annotated[bool, Parameter(name="-x")] = False,
#     opts: OptFlags = OptFlags.DEFAULT,
# ):
#     """
#     Parameters
#     ----------
#     run_examples: bool
#         Run example commands
#     opts: OptFlags
#         Optional flags for "verbose", "trace", "debug" and "no wrap";
#         any combination of "-v", "-t", "-d", and "--nowrap"
#     """
#     if run_examples:
#         return examples()
#
#     additional_kwargs = {}
#     command, bound, ignored = app.parse_args(tokens)
#     if "opts" in ignored:
#         additional_kwargs["opts"] = opts
#     if opts.debug:
#         display_function_name()
#         console.print(f"command = {command.__name__}")
#         console.print(f"{bound=}")
#         console.print(f"{opts=}")
#         console.print(f"{additional_kwargs=}")
#
#     return command(*bound.args, **bound.kwargs, **additional_kwargs)

if __name__ == "__main__":
    app()
