from dataclasses import dataclass
from typing import Annotated

from cyclopts import App, Parameter

app = App(version_flags=[])


@dataclass(frozen=True)
class Diagnostics:
    verbose: Annotated[bool, Parameter(name="-v", help="Verbose mode")] = False
    trace: Annotated[bool, Parameter(name="-t", help="Trace mode")] = False
    debug: Annotated[bool, Parameter(name="-d", help="Debug mode")] = False

    # Default instance
    DEFAULT = None


# Define DEFAULT after the class is fully initialized
Diagnostics.DEFAULT = Diagnostics()


@app.command(name="-f", help="It's foo")
def foo(val: int, diagnostics: Diagnostics = Diagnostics.DEFAULT):
    print(f"FOO {val=}")
    print(f"{diagnostics=}")
    print()


@app.command(name="-b", help="It's bar")
def bar(flag: bool = False, diagnostics: Diagnostics = Diagnostics.DEFAULT):
    print(f"BAR {flag=}")
    print(f"{diagnostics=}")
    print()


@app.command(name="-z", help="It's baz")
def baz(files: list[str], diagnostics: Diagnostics = Diagnostics.DEFAULT):
    print(f"BAZ {files=}")
    print(f"{diagnostics=}")
    print()


if __name__ == "__main__":
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
