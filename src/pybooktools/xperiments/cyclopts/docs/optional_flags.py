import sys
from dataclasses import dataclass
from typing import Annotated

from cyclopts import App, Parameter
from rich.console import Console
from rich.panel import Panel

console = Console()
app = App()


@dataclass(frozen=True)
class Diagnostics:
    verbose: Annotated[bool, Parameter(name="-v", help="Verbose", group="Diagnostics")] = False
    trace: Annotated[bool, Parameter(name="-t", help="Trace", group="Diagnostics")] = False
    debug: Annotated[bool, Parameter(name="-d", help="Debug", group="Diagnostics")] = False


@app.command
def alpha(val: int, diagnostics=Diagnostics()):
    """Perform alpha on a single integer"""
    console.print(f"alpha {val = }\n{diagnostics = }")


@app.command
def beta(flag: bool = False, diagnostics=Diagnostics()):
    """Perform beta on a boolean flag"""
    console.print(f"beta {flag = }\n{diagnostics = }")


@app.command
def gamma(files: list[str], diagnostics=Diagnostics()):
    """Perform gamma on a list of strings"""
    console.print(f"gamma {files = }\n{diagnostics = }")


examples = [
    ["alpha", "42"],
    ["alpha", "42", "-v", "-t"],
    ["alpha", "42", "-d", "-v"],
    ["beta", "0"],
    ["beta", "0", "-v", "-d"],
    ["beta", "0", "-v", "-t"],
    ["gamma", "one", "two", "three"],
    ["gamma", "one", "two", "three", "-v", "-d"],
    ["gamma", "one", "two", "three", "-t", "-d"],
    # Flag order doesn't matter:
    ["beta", "1", "-v", "-d", "-t"],
    ["beta", "1", "-d", "-v", "-t"],
    ["beta", "1", "-d", "-t", "-v"],
    ["beta", "1", "-t", "-v", "-d"],
    # Invoke help:
    ["alpha", "-h"],
    ["beta", "-h"],
    ["gamma", "-h"],
    ["-h"]
]


def run(arglist: list[str]):
    console.print(Panel(
        f"Testing: [dark_khaki]{arglist}[/dark_khaki]",
        style="green",
    ))
    app(arglist)


if __name__ == "__main__":
    if "-x" in sys.argv:
        for example in examples:
            run(example)
    else:
        app()
