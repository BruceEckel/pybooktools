# clean_example_repo.py
"""
Remove selected example repository elements.
Call before extracting code from markdown files.
"""
import re
from pathlib import Path
from typing import Final

from cyclopts import App
from cyclopts.types import ResolvedExistingDirectory

repo_chapter_pattern: Final[str] = r"^[a]?\d+_[a-z_]+$"

app = App(
    version_flags=[],
    # console=console,
    # help_format="plaintext",
    help=__doc__,
    # default_parameter=Parameter(negative=()),
)


def is_valid_path(f: Path, util_dirs: bool = False) -> bool:
    print(f" {f.name} ".center(60, "-"))
    if re.match(repo_chapter_pattern, f.name):
        print(f"pattern match {f.name}")
        return True
    if util_dirs:
        print(f"all match {f.name}")
        if f.is_dir() and f.suffix == "" and f.name[:1].isalnum():
            print(f"other directory match {f.name}")
            return True
    return False


@app.command(name="-d")
def display(path: ResolvedExistingDirectory = Path(".")):
    """Display the existing repo chapters"""
    for f in path.iterdir():
        print(f"{f.name} {f.is_dir() = }".center(60, "-"))
        print(f"{re.match(repo_chapter_pattern, f.name) = }")
        if f.is_dir() and re.match(repo_chapter_pattern, f.name):
            print(f"matched: {f.name}")


@app.command(name="-r")
def remove_chapters(path: ResolvedExistingDirectory = Path(".")):
    """Remove numbered repo chapters"""
    for f in path.iterdir():
        if f.is_dir() and re.match(repo_chapter_pattern, f.name):
            print(f"removing: {f.name}")


@app.command(name="-a")
def remove_all(path: ResolvedExistingDirectory = Path(".")):
    """Remove repo chapters AND other subdirectories"""

    for f in filter(is_valid_path, path.iterdir()):
        print(f"removing: {f.name}")
