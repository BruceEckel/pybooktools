# clean_example_repo.py
"""
Remove selected example repository elements.
Call before extracting code from markdown files.
"""
import re
from pathlib import Path
from typing import Final, Iterator

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


def repo_dirs(root: Path, util_dirs: bool = False) -> Iterator[Path]:
    """
    Lazily yields directories from the given root that match one of the following:

    - The directory name matches `repo_chapter_pattern`.
    - If `util_dirs` is True: there's no suffix and the name starts with an alphanumeric character.
    """
    for path in root.iterdir():
        if not path.is_dir():
            continue

        print(f" {path.name} ".center(60, "-"))

        if re.match(repo_chapter_pattern, path.name):
            print(f"pattern match {path.name}")
            yield path
        elif util_dirs and path.suffix == "" and path.name[:1].isalnum():
            print(f"util dirs: {path.name}")
            print(f"util dir match {path.name}")
            yield path


@app.command(name="-d")
def display(path: ResolvedExistingDirectory = Path(".")):
    """Display the existing repo chapters"""
    for f in repo_dirs(path, util_dirs=True):
        print(f"{f.name} {f.is_dir() = }".center(60, "-"))
        print(f"{re.match(repo_chapter_pattern, f.name) = }")
        if f.is_dir() and re.match(repo_chapter_pattern, f.name):
            print(f"matched: {f.name}")


@app.command(name="-c")
def remove_chapters(path: ResolvedExistingDirectory = Path(".")):
    """Remove numbered repo chapters"""
    for f in repo_dirs(path):
        print(f"removing: {f.name}")


@app.command(name="-a")
def remove_all(path: ResolvedExistingDirectory = Path(".")):
    """Remove repo chapters AND other subdirectories"""
    for f in repo_dirs(path, util_dirs=True):
        print(f"removing: {f.name}")
