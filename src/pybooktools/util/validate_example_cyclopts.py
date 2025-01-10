# validate_example_cyclopts.py
from pathlib import Path
from typing import Annotated

from cyclopts import Parameter

from pybooktools.util import is_slug


def python_example_validator(type_, pyfile: Path, main_allowed=False) -> None:
    def validate(assertion: bool, err_msg: str) -> None:
        if not assertion:
            msg = f"\npython_example_validator: {pyfile} {err_msg}"
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


PyExample = Annotated[Path, Parameter(validator=python_example_validator)]

### Test
if __name__ == "__main__":
    from cyclopts import App

    app = App()


    @app.default
    def main(_: PyExample):
        pass


    def demos() -> list[Path]:
        validate_demos = Path("validate_demos")
        validate_demos.mkdir(exist_ok=True)
        examples = {
            "valid_example.py": "# valid_example.py\nprint('Valid')\nprint('Example')",
            "empty_file.py": "",
            "short_example.py": "# short_example.py\nprint('Too short')",
            "missing_slug.py": "print('No slug line')\nprint('Example')\nprint('long enough')",
            "main_included.py": "# main_included.py\nif __name__ == '__main__':\n    print('Main block included')",
            "non_python.txt": "This is not a Python file.",
        }
        results: list[Path] = []
        for filename, content in examples.items():
            (validate_demos / filename).write_text(content, encoding="utf-8")
            results.append(validate_demos / filename)
        results.append(validate_demos / "nonexistent.py")
        return results


    for demo in demos():
        print(f"arg: {demo}")
        try:
            # Note brackets around argument:
            app([str(demo)], exit_on_error=False)
        except Exception:
            pass
