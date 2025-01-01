# valid_python_file.py
from pathlib import Path

from .display import error


def opt_msg(msg: str) -> str:
    return f"{msg}: " if msg else ""


def valid_python(pyfile: Path, msg: str = "") -> str:
    if not pyfile.exists():
        error(f"{opt_msg(msg)}{pyfile} doesn't exist")
    if not pyfile.is_file():
        error(f"{opt_msg(msg)}{pyfile} is not a file")
    if pyfile.suffix != ".py":
        error(f"{opt_msg(msg)}{pyfile} is not a Python file")
    return pyfile.read_text(encoding="utf-8")
