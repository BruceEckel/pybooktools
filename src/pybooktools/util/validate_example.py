# validate_example.py
"""
Contains everything that determines a valid book example
"""
from pathlib import Path
from typing import Annotated

from cyclopts import Parameter

from pybooktools.util import is_slug


def invalid_example(pyfile: Path, msg: str = "", main_allowed=False) -> str | None:
    def descr(err_msg: str) -> str:
        opt_msg = f"{msg}: " if msg else ""
        return f"{opt_msg}{pyfile} {err_msg}"

    if not pyfile.exists():
        return descr("doesn't exist")
    if not pyfile.is_file():
        return descr("is not a file")
    if pyfile.suffix != ".py":
        return descr("is not a Python file")
    example = pyfile.read_text(encoding="utf-8")
    example_lines = example.splitlines()
    if not example:
        return descr("is empty")
    if not is_slug(example_lines[0]):
        return descr("has no slug line")
    if len(example_lines) < 3:
        return descr("is too short")
    if "__main__" in example and not main_allowed:
        return descr("contains __main__")
    return None


def python_example_validator(type_, pyfile: Path, main_allowed=False) -> None:
    def fail(err_msg: str) -> str:
        raise ValueError(f"{pyfile} {err_msg}")

    print(f"python_example_validator: {pyfile=}")

    if not pyfile.exists():
        fail("doesn't exist")
    if not pyfile.is_file():
        fail("is not a file")
    if pyfile.suffix != ".py":
        fail("is not a Python file")
    example = pyfile.read_text(encoding="utf-8")
    example_lines = example.splitlines()
    if not example:
        fail("is empty")
    if not is_slug(example_lines[0]):
        fail("has no slug line")
    if len(example_lines) < 3:
        fail("is too short")
    if "__main__" in example and not main_allowed:
        fail("contains __main__")


PyExample = Annotated[Path, Parameter(validator=python_example_validator)]
