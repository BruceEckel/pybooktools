from dataclasses import dataclass
from typing import Annotated

from cyclopts import App, Parameter
from rich.console import Console

console = Console()
app = App(
    version_flags=[],
    console=console,
)


@dataclass(frozen=True)
class Diagnostics:
    verbose: Annotated[bool, Parameter(name="-v", help="Verbose mode", group="Diagnostics")] = False
    trace: Annotated[bool, Parameter(name="-t", help="Trace mode", group="Diagnostics")] = False
    debug: Annotated[bool, Parameter(name="-d", help="Debug mode", group="Diagnostics")] = False
    DEFAULT = None
    NoParse = None


Diagnostics.DEFAULT = Diagnostics()
NoParse = Annotated[Diagnostics, Parameter(parse=False)]


@app.command(name="-f", help="It's foo")
def foo(val: int, *, diagnostics: Diagnostics.NoParse = Diagnostics.DEFAULT):
    console.print(f"FOO {val=}")
    console.print(f"{diagnostics=}")


@app.command(name="-b", help="It's bar")
def bar(flag: bool = False, *, diagnostics: Diagnostics.NoParse = Diagnostics.DEFAULT):
    console.print(f"BAR {flag=}")
    console.print(f"{diagnostics=}")


@app.command(name="-z", help="It's baz")
def baz(files: list[str], *, diagnostics: Diagnostics.NoParse = Diagnostics.DEFAULT):
    console.print(f"BAZ {files=}")
    console.print(f"{diagnostics=}")


@app.meta.default
def meta(
    *tokens: Annotated[str, Parameter(show=False, allow_leading_hyphen=True)],
    run_examples: Annotated[bool, Parameter(name="-x")] = False,
    diagnostics: Diagnostics = Diagnostics.DEFAULT,
):
    """
    Parameters
    ----------
    run_examples: bool
        Run CLI demo commands.
    diagnostics: Diagnostics
        Optional flags for "verbose", "trace", and "debug", any combination of "-v", "-t", and "-d"
    """
    if run_examples:
        return examples()

    additional_kwargs = {}
    command, bound, ignored = app.parse_args(tokens)
    console.print(f"command = {command.__name__}")
    console.print(f"{bound=}")
    console.print(f"{diagnostics=}")
    if "diagnostics" in ignored:
        additional_kwargs["diagnostics"] = diagnostics
    return command(*bound.args, **bound.kwargs, **additional_kwargs)


def examples():
    def run(arglist: list[str]):
        console.rule()
        app.meta(arglist)

    run(["-f", "42", "-v", "-t"])
    run(["-b", "0", "-v", "-d"])
    run(["-z", "one", "two", "three", "-v", "-d"])
    run(["-f", "42", "-d", "-v"])
    run(["-b", "0", "-v", "-t"])
    run(["-z", "one", "two", "three", "-t", "-d"])
    run(["-f", "42"])
    run(["-b", "0"])
    run(["-z", "one", "two", "three"])
    # Flag order doesn't matter(!):
    run(["-b", "0", "-v", "-d", "-t"])
    run(["-b", "0", "-d", "-v", "-t"])
    run(["-b", "0", "-d", "-t", "-v"])
    run(["-b", "0", "-t", "-v", "-d"])

    run(["-f", "-h"])
    run(["-h"])


if __name__ == "__main__":
    app.meta()
