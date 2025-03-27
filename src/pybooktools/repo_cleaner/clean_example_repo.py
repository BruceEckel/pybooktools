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

repo_chapter_pattern: Final[str] = r"^[a]?\d+_[a-z_]+$"

app = App(
    version_flags=[],
    help=__doc__,
)


def chapter_dirs(root: Path) -> list[Path]:
    """
    Directories from the given root that match `repo_chapter_pattern`.
    """
    return [
        chapter for chapter in root.iterdir()
        if chapter.is_dir()
           and re.match(repo_chapter_pattern, chapter.name)
    ]


@app.command(name="-d")
def display(path: ResolvedExistingDirectory = Path(".")):
    """Display the existing repo chapters"""
    for f in chapter_dirs(path):
        print(f.name)


@app.command(name="-c")
def remove_chapters(path: ResolvedExistingDirectory = Path(".")):
    """Remove numbered repo chapters"""
    for chapter in chapter_dirs(path):
        print(f"removing: {chapter.name}")
        shutil.rmtree(chapter)


@app.command(name="-a")
def remove_all(path: ResolvedExistingDirectory = Path(".")) -> None:
    """Remove repo chapters AND 'util' subdirectory"""
    for chapter in chapter_dirs(path) + [path / "util"]:
        print(f"removing: {chapter.name}")
        shutil.rmtree(chapter)
