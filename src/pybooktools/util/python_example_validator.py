# python_example_validator.py
"""
Single point of truth to determine a valid book example.
"""
from pathlib import Path
from typing import Annotated

from cyclopts import Parameter

from pybooktools.sluglines.slug import is_slug
from pybooktools.util.create_demo_files import create_demo_files


def python_example_validator(pyfile: Path, main_allowed=False) -> None:
    def validate(assertion: bool, err_msg: str) -> None:
        if not assertion:
            msg = f"\n{pyfile} {err_msg}"
            raise ValueError(msg)

    validate(pyfile.exists(), "doesn't exist")
    validate(pyfile.is_file(), "is not a file")
    validate(pyfile.suffix == ".py", "is not a Python file")
    example = pyfile.read_text(encoding="utf-8")
    example_lines = example.splitlines()
    validate(len(example) > 0, "is empty")
    validate(len(example_lines) > 2, "is too short")
    validate(is_slug(example_lines[0]), "has no slug line")
    validate("__main__" not in example and not main_allowed, "contains __main__")


def cyclopts_python_example_validator(type_, pyfile: Path, main_allowed=False) -> None:  # noqa
    python_example_validator(pyfile, main_allowed=main_allowed)


PyExample = Annotated[Path, Parameter(validator=cyclopts_python_example_validator)]

### Test ###

demo_dir = "validate_demos"

if __name__ == "__main__":
    from cyclopts import App

    app = App()


    @app.default
    def main(_: PyExample):
        pass


    examples: dict[str, str] = {
        "valid_example.py": "# valid_example.py\nprint('Valid')\nprint('Example')",
        "empty_file.py": "",
        "short_example.py": "# short_example.py\nprint('Too short')",
        "missing_slug.py": "print('No slug line')\nprint('Example')\nprint('long enough')",
        "main_included.py": "# main_included.py\nif __name__ == '__main__':\n    print('Main block included')",
        "non_python.txt": "This is not a Python file.",
    }

    for demo in create_demo_files(demo_dir, examples):
        print(f"arg: {demo}")
        try:
            # Note brackets around argument:
            app([str(demo)], exit_on_error=False)
        except Exception:  # noqa pylint: disable=broad-except
            pass

    Path(demo_dir).rmdir()
