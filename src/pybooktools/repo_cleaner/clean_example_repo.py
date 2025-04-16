# clean_example_repo.py
"""
Remove selected example repository elements.
Call before extracting code from markdown files.
"""
import re
import shutil
from pathlib import Path
from typing import Final

from cyclopts import App
from cyclopts.types import ResolvedExistingDirectory

# Extra directories to be removed by `remove_all`:
additional_dirs = [
    "book_utils",
    "book_util",
    "butil",
    "util"
]

repo_chapter_pattern: Final[str] = r"^c\d+_[a-z_]+$"  # TODO: Unify in config.py

app = App(
    version_flags=[],
    help=__doc__,
)


def chapter_dirs(root: Path) -> list[Path]:
    """Directories from the given root that match `repo_chapter_pattern`."""
    return [
        p for p in root.iterdir()
        if p.is_dir() and re.match(repo_chapter_pattern, p.name)
    ]


def remove_dirs(dirs: list[Path]) -> None:
    """Print and remove the specified directories."""
    for d in dirs:
        if d.exists():
            print(f"removing: {d.name}")
            shutil.rmtree(d)


@app.command(name="-d")
def display(path: ResolvedExistingDirectory = Path(".")) -> None:
    """Display the existing example_repo chapters."""
    for d in chapter_dirs(path):
        print(d.name)


@app.command(name="-c")
def remove_chapters(path: ResolvedExistingDirectory = Path(".")) -> None:
    """Remove numbered example_repo chapters."""
    remove_dirs(chapter_dirs(path))


@app.command(name="-a")
def remove_all(path: ResolvedExistingDirectory = Path(".")) -> None:
    """Remove example_repo chapters AND additional specified directories."""
    remove_dirs([
        *chapter_dirs(path),
        *(d for name in additional_dirs if (d := path / name).exists())
    ])
