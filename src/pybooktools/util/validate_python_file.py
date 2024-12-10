from pathlib import Path

from pybooktools.util import error


def optional_message(msg: str) -> str:
    return f"{msg}: " if msg else ""


def valid_python(pyfile: Path, msg: str = "") -> str:
    if not pyfile.exists():
        error(f"{optional_message(msg)}{pyfile} doesn't exist")
    if not pyfile.is_file():
        error(f"{optional_message(msg)}{pyfile} is not a file")
    if pyfile.suffix != ".py":
        error(f"{optional_message(msg)}{pyfile} is not a Python file")
    return pyfile.read_text(encoding="utf-8")
