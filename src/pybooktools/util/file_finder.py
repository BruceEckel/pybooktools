# file_finder.py
from functools import partial
from pathlib import Path
from typing import Literal, Optional, Generator, Iterable, Callable

# Exclude these directories from python_files().
EXCLUDE_DIRS = {"venv", ".venv", "__pycache__", ".git", "python", "invoke_tasks"}
# Exclude these files from python_files().
EXCLUDE_FILES = {"__init__.py", "tasks.py", "bootstrap.py"}


def file_finder(
    depth: Literal["d", "r"] = "d",  # d is current dir, r is recursive
    directory: Path = Path("."),  # Where to start search
    extensions: Optional[Iterable[str]] = None,  # Only include files with these extensions
    exclude_files: Optional[Iterable[str]] = None,  # Files to skip
    exclude_dirs: Optional[Iterable[str]] = None,  # Directories to skip
) -> Generator[Path, None, None]:
    extensions = {ext.lower() for ext in extensions} if extensions else None
    exclude_dirs = set(exclude_dirs) if exclude_dirs else set()
    exclude_files = set(exclude_files) if exclude_files else set()

    def should_yield(path: Path) -> bool:
        if any(part in exclude_dirs for part in path.parts):
            return False
        if path.is_file():
            if path.name in exclude_files:
                return False
            if extensions and path.suffix.lower() not in extensions:
                return False
            return True
        return False

    iterator = directory.iterdir() if depth == "d" else directory.rglob("*")

    for path in iterator:
        if should_yield(path):
            # print(path)
            yield path


def curry_file_finder(
    *,
    extensions: Optional[Iterable[str]] = None,
    exclude_files: Optional[set[str]] = None,
    exclude_dirs: Optional[set[str]] = None
) -> Callable[[Literal["d", "r"], Path], Generator[Path, None, None]]:
    return partial(
        file_finder,
        extensions=extensions,
        exclude_files=exclude_files,
        exclude_dirs=exclude_dirs
    )


python_files = curry_file_finder(extensions={".py"}, exclude_files=EXCLUDE_FILES, exclude_dirs=EXCLUDE_DIRS)
