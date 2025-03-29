# flags.py
from typing import Literal, Annotated

from cyclopts import App, Parameter

app = App()


@app.default
def main(
    flag: Annotated[Literal["-f", "-g", "-h"], Parameter(allow_leading_hyphen=True)],
    opt_flags: Annotated[list[Literal["-u", "-v", "-w"]], Parameter(allow_leading_hyphen=True)] = "-u",
    pyfiles: list[str] = None,
):
    print(f" {flag = } {pyfiles = } {opt_flags = }")


app()
