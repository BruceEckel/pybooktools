from pathlib import Path
from typing import Annotated

from cyclopts import Parameter

from pybooktools.util import is_slug


def python_example_validator(type_, pyfile: Path, main_allowed=False) -> None:
    def fail(assertion: bool, err_msg: str) -> None:
        if not assertion:
            print(f"{pyfile} {err_msg}")
            # raise ValueError(f"{pyfile} {err_msg}")

    print(f"python_example_validator: {pyfile=}")

    fail(pyfile.exists(), "doesn't exist")
    fail(pyfile.is_file(), "is not a file")
    fail(pyfile.suffix == ".py", "is not a Python file")
    example = pyfile.read_text(encoding="utf-8")
    example_lines = example.splitlines()
    fail(bool(example), "is empty")
    fail(len(example_lines) > 2, "is too short")
    fail(is_slug(example_lines[0]), "has no slug line")
    fail("__main__" not in example and not main_allowed, "contains __main__")


PyExample = Annotated[Path, Parameter(validator=python_example_validator)]
