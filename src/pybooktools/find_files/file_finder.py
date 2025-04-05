# file_finder.py
from functools import partial
from pathlib import Path
from typing import Literal, Optional, Generator, Iterable, Callable


def file_finder(
    depth: Literal["directory", "recursive"] = "directory",
    start_search: Path = Path("."),
    extensions: Optional[Iterable[str]] = None,  # Include files with these extensions
    exclude_files: Optional[Iterable[str]] = None,
    exclude_dirs: Optional[Iterable[str]] = None,
) -> Generator[Path, None, None]:
    extensions = {ext.lower() for ext in extensions} if extensions else None
    exclude_dirs = set(exclude_dirs) if exclude_dirs else set()
    exclude_files = set(exclude_files) if exclude_files else set()

    def yield_this(path: Path) -> bool:
        if any(part in exclude_dirs for part in path.parts):
            return False
        if path.is_file():
            if path.name in exclude_files:
                return False
            if extensions and path.suffix.lower() not in extensions:
                return False
            return True
        return False

    iterator = start_search.iterdir() if depth == "directory" else start_search.rglob("*")

    for path in iterator:
        if yield_this(path):
            # print(path)
            yield path


def curry_file_finder(
    *,
    extensions: Optional[Iterable[str]] = None,
    exclude_files: Optional[set[str]] = None,
    exclude_dirs: Optional[set[str]] = None
) -> Callable[[Literal["directory", "recursive"], Path], Generator[Path, None, None]]:
    return partial(
        file_finder,
        extensions=extensions,
        exclude_files=exclude_files,
        exclude_dirs=exclude_dirs
    )
