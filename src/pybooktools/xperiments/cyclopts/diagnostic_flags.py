import sys
from dataclasses import dataclass
from typing import Annotated

from cyclopts import App, Parameter

app = App(version_flags=[], help="Usage: diagnostic_flags.py [CMD] [ARGS] [DIAGNOSTIC FLAGS]", help_flags=["-h"])


@dataclass(frozen=True)
class Diagnostics:
    verbose: Annotated[bool, Parameter(name="-v", help="Verbose mode", group="diagnostic flags")] = False
    trace: Annotated[bool, Parameter(name="-t", help="Trace mode", group="diagnostic flags")] = False
    debug: Annotated[bool, Parameter(name="-d", help="Debug mode", group="diagnostic flags")] = False
    DEFAULT = None


Diagnostics.DEFAULT = Diagnostics()


@app.command(name="--help", help="Show this help message")
def helper(diagnostics=Diagnostics.DEFAULT):
    """helper doc string"""
    print(diagnostics)
    app.help_print()


@app.command(name="-f", help="It's foo")
def foo(val: int, diagnostics=Diagnostics.DEFAULT):
    print(f"FOO {val=}")
    print(f"{diagnostics=}")


@app.command(name="-b", help="It's bar")
def bar(flag: bool = False, diagnostics=Diagnostics.DEFAULT):
    print(f"BAR {flag=}")
    print(f"{diagnostics=}")


@app.command(name="-z", help="It's baz")
def baz(files: list[str], diagnostics=Diagnostics.DEFAULT):
    print(f"BAZ {files=}")
    print(f"{diagnostics=}")


def examples():
    app(["-f", "42", "-v", "-t"])
    app(["-b", "0", "-v", "-d"])
    app(["-z", "one", "two", "three", "-v", "-d"])
    app(["-f", "42", "-d", "-v"])
    app(["-b", "0", "-v", "-t"])
    app(["-z", "one", "two", "three", "-t", "-d"])
    app(["-f", "42"])
    app(["-b", "0"])
    app(["-z", "one", "two", "three"])
    # Flag order doesn't matter(!):
    app(["-b", "0", "-v", "-d", "-t"])
    app(["-b", "0", "-d", "-v", "-t"])
    app(["-b", "0", "-d", "-t", "-v"])
    app(["-b", "0", "-t", "-v", "-d"])

    app(["-h"])
    app(["-f", "-h"])
    app.help_print("--help")


if __name__ == "__main__":
    if "-x" in sys.argv:
        examples()
    else:
        app()
