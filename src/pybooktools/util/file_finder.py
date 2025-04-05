# file_finder.py
from functools import partial
from pathlib import Path
from typing import Literal, Optional, Generator, Iterable, Callable

# Directories to exclude from python_files().
EXCLUDED_DIRS = {"venv", ".venv", "__pycache__", ".git", "python", "invoke_tasks"}
EXCLUDED_FILES = {"__init__.py", "tasks.py", "bootstrap.py"}


def uff(
    depth: Literal["d", "r"] = "d",  # d is current dir, r is recursive
    directory: Path = Path("."),  # Where to start search
    extensions: Optional[Iterable[str]] = None,  # Only include files with these extensions
    exclude_files: Optional[set[str]] = None,  # Files to skip
    exclude_dirs: Optional[set[str]] = None,  # Directories to skip
) -> Generator[Path, None, None]:
    if exclude_dirs is None:
        exclude_dirs = set()
    if exclude_files is None:
        exclude_files = set()
    if extensions is not None:
        extensions = {ext.lower() for ext in extensions}

    def is_valid_file(path: Path) -> bool:
        if path.name in exclude_files:
            return False
        if extensions is not None and path.suffix.lower() not in extensions:
            return False
        return True

    if depth == "d":
        for entry in directory.iterdir():
            if entry.is_dir():
                if entry.name not in exclude_dirs:
                    continue  # Skip directories in current dir mode
            elif is_valid_file(entry):
                yield entry

    elif depth == "r":
        for path in directory.rglob("*"):
            if path.is_dir() and path.name in exclude_dirs:
                continue
            if path.is_file() and is_valid_file(path):
                yield path


def curry_uff(
    *,
    extensions: Optional[Iterable[str]] = None,
    exclude_files: Optional[set[str]] = None,
    exclude_dirs: Optional[set[str]] = None
) -> Callable[[Literal["d", "r"], Path], Generator[Path, None, None]]:
    return partial(
        uff,
        extensions=extensions,
        exclude_files=exclude_files,
        exclude_dirs=exclude_dirs
    )


python_files = curry_uff(extensions={".py"}, exclude_files=EXCLUDED_FILES, exclude_dirs=EXCLUDED_DIRS)
