# clean_example_repo.py
"""
Remove selected example repository elements.
Call before extracting code from markdown files.
"""
import re
from pathlib import Path

from cyclopts import App
from cyclopts.types import ResolvedExistingDirectory

from pybooktools.util.config import chapter_pattern

chapter_pattern
app = App(
    version_flags=[],
    # console=console,
    # help_format="plaintext",
    help=__doc__,
    # default_parameter=Parameter(negative=()),
)


@app.command(name="-d")
def display(path: ResolvedExistingDirectory = Path(".")):
    """Display the existing repo chapters"""
    print(path)
    for f in path.iterdir():
        if f.is_file() and re.match(chapter_pattern, f.name):
            print(f.name)
