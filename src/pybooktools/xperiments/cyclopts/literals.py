from pathlib import Path
from typing import Literal, Optional, Annotated

import cyclopts
from cyclopts import Parameter

app = cyclopts.App(name="px", help_format="rich", version_flags=[])


@app.default
def main(
    operation: Annotated[Literal["-f", "-a", "-r"], Parameter(allow_leading_hyphen=True)] = "-f",
    pyfiles: Optional[list[Path]] = None,
):
    """
    f: Provide python files
    a: Update all files in current directory
    r: Recursively update all files in current directory and subdirectories
    """
    print(f"{pyfiles= }, {operation= }")


app()
