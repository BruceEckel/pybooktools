# meta_app.py
"""
Create or Update the embedded output in Python examples. The embedded output is
everything output to the console after each Top-Level Statement (TLS). For example:
```python
print("foo")
## foo
for i in range(3):  # Entire `for` is a TLS
    print(i)
## 0
## 1
## 2
```
"""
from typing import Annotated

from cyclopts import App, Parameter

from pybooktools.util import error

app = App(
    name="px",
    help_format="markdown",
    version_flags=[],
    help=__doc__,
    usage="\nUsage: [green]px [-f FILES] [-a] [-r][/green]"
)


@app.command(name=("-f", "--files"), sort_key=1)
def foo(pyfiles: tuple[str, ...]):
    """Process each file provided after -f"""
    for f in pyfiles:
        print(f"Processing {f}")


@app.command(name=("-a", "--all"), sort_key=2)
def current_dir():
    """Find and process each file in the current directory"""
    for f in ["a.py", "b.py", "c.py"]:
        print(f"Processing {f}")


@app.command(name=("-r", "--recurse"), sort_key=3)
def recurse_dirs():
    """Recursively find and process all files in the current directory and subdirectories"""
    for f in ["foo/a.py", "bar/b.py", "baz/c.py"]:
        print(f"Processing {f}")


@app.meta.default
def launcher(
    *args: Annotated[
        str, Parameter(show=True, allow_leading_hyphen=True, help="After -f, Python file(s) to process")]
):
    print(f"{args!r}\n{type(args)=}")
    if not args or args[0] not in ("-f", "--files", "-a", "--all", "-r", "--recurse"):
        app.help_print()
        h = "green"
        error(f"First element on command line must be [{h}]-f[/{h}], [{h}]-a[/{h}], or [{h}]-r[/{h}]")
    app(args)


def main():
    app.meta()


if __name__ == "__main__":
    main()
