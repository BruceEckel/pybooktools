# meta_app.py
from typing import Annotated

from cyclopts import App, Parameter
from rich.syntax import Syntax

from pybooktools.util import error

doc = f"""[cyan1]\
Create or Update the embedded output in Python examples. The embedded output is 
everything output to the console after each Top-Level Statement. For example:

{Syntax(
    '''print("foo")
    ## foo
    for i in range(3):
        print(i)
    ## 0
    ## 1
    ## 2''', "python", theme="monokai", line_numbers=True)}
[/cyan1]"""

app = App(name="px", help_format="rich", version_flags=[], help=doc)


@app.command(name=("-f", "--files"), sort_key=1)
def foo(pyfiles: tuple[str, ...]):
    """Process each file provided after -f"""
    for f in pyfiles:
        print(f"Processing {f}")


@app.command(name=("-a", "--all"), sort_key=2)
def current_dir():
    """
from rich.syntax import Syntax

Find and process each file in the current directory"""
    for f in ["a.py", "b.py", "c.py"]:
        print(f"Processing {f}")


@app.command(name=("-r", "--recurse"), sort_key=3)
def recurse_dirs():
    """Recursively find and process all files in the current directory and subdirectories"""
    for f in ["foo/a.py", "bar/b.py", "baz/c.py"]:
        print(f"Processing {f}")


@app.meta.default
def launcher(
    *pyfiles: Annotated[
        str, Parameter(show=True, allow_leading_hyphen=True, help="After -f, Python file(s) to process")]
):
    if pyfiles[0] not in ("-f", "-a", "-r"):
        app.help_print()
        h = "green"
        error(f"First element on command line must be [{h}]-f[/{h}], [{h}]-a[/{h}], or [{h}]-r[/{h}]")
    app(pyfiles)


def main():
    app.meta()


if __name__ == "__main__":
    main()
