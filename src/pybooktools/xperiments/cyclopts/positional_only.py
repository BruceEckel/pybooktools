from pathlib import Path
from typing import Literal

from cyclopts import App

app = App()


@app.default
def main(srcs: list[Path], flag: Literal['-f', '-g', '-h']):  # "/" makes all prior parameters POSITIONAL_ONLY
    print(f"Processing files {srcs!r} to {flag!r}.")


app()
