from pathlib import Path
from typing import Optional, Annotated

import cyclopts
from cyclopts import Parameter

app = cyclopts.App(
    name="px",
    help_format="rich",
    help="[green]Update embedded outputs in Python examples[/green]",
    version_flags=[],
)
app["--help"].group = "Help"


# app["--version"].group = "Info"


@app.command(group="Arguments")
def files(
    pyfiles: Annotated[Optional[list[Path]], Parameter(help="The Python example file(s) (optional)")] = None,
    verbose: Annotated[bool, Parameter(name=["--verbose", "-v"],
                                       help="Trace info, save intermediate files, don't overwrite original file")] = False,
    nowrap: Annotated[bool, Parameter(name=["--nowrap"], help="Do not wrap output lines")] = False,
):
    """
    Provide one or more Python files to update [blue]OR[/blue]
    """
    print(pyfiles, verbose, nowrap)


@app.command(name=("--all", "-a"), group="Arguments")
def star(
    verbose: Annotated[bool, Parameter(name=["--verbose", "-v"],
                                       help="Trace info, save intermediate files, don't overwrite original file")] = False,
    nowrap: Annotated[bool, Parameter(name=["--nowrap"], help="Do not wrap output lines")] = False,
):
    """
    Update all files in current directory [blue]OR[/blue]
    """
    print(verbose, nowrap)


@app.command(name=("--recurse", "-r"), group="Arguments")
def recurse(
    verbose: Annotated[
        bool, Parameter(name=["--verbose", "-v"],
                        help="Trace info, save intermediate files, don't overwrite original file")] = False,
    nowrap: Annotated[bool, Parameter(name=["--nowrap"], help="Do not wrap output lines")] = False,
    foo: Annotated[str, Parameter(name=["-f", "--foo"], help="Foo")] = "",
):
    """
    Recursively update all files in current directory and subdirectories
    """
    print(verbose, nowrap, foo)


if __name__ == "__main__":
    app()
