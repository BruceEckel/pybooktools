# validate_transformer.py
import difflib
import inspect
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pybooktools.util import config


@dataclass
class UseCase:
    case_id: int
    script: str
    expected_output: Any

    def __post_init__(self):
        # self.script = self.script.strip() + "\n"
        self.expected_output = str(self.expected_output).strip() + "\n"

    def __iter__(self):
        return iter((self.case_id, self.script, self.expected_output))


def validate_transformer(
    transformer: callable, use_cases: list[UseCase]
) -> None:
    results = []
    for case_id, script, expected_output in use_cases:
        actual_output = str(transformer(script)).strip() + "\n"
        if actual_output == expected_output:
            results.append(passed(case_id))
        else:
            diff = "\n".join(
                difflib.unified_diff(
                    actual_output.splitlines(),
                    expected_output.splitlines(),
                    lineterm="",
                    fromfile="Actual",
                    tofile="Expected",
                )
            )
            fail_message = f"""
{failed(case_id)}
{DIVIDER} Script {DIVIDER}
_______________________________
{script}
_______________________________
{DIVIDER} Actual {DIVIDER}
_______________________________
{actual_output}
_______________________________
{DIVIDER} Expected {DIVIDER}
_______________________________
{expected_output}
_______________________________
{DIVIDER} Differences {DIVIDER}
{diff}
"""
            print(fail_message)
            results.append(fail_message)

    # Discover file from which check_operation is called:
    caller_frame = inspect.stack()[1]
    caller_file = Path(caller_frame.filename)
    this_file_path = caller_file
    this_file = this_file_path.read_text(encoding="utf-8")

    if OUTPUT_MARKER in this_file:
        this_file = this_file[: this_file.index(OUTPUT_MARKER)]
    this_file_path.write_text(
        this_file
        + f'{output_from_marker("validate_transformer")}\n{"".join(results)}\n"""\n',
        encoding="utf-8",
    )


if __name__ == "__main__":
    validate_transformer(
        lambda script: script + " bar",
        [
            UseCase(1, "foo", "foo bar"),
            UseCase(2, "x", "foo x"),
            UseCase(3, "x", "x bar"),
            UseCase(4, "baz", "baz bar"),
        ],
    )

""" Output From validate_string_transformer:

================ Case 1 passed ================
================ Case 2 failed ================
**** Script ****
_______________________________
x
_______________________________
**** Actual ****
_______________________________
x bar

_______________________________
**** Expected ****
_______________________________
foo x

_______________________________
**** Differences ****
--- Actual
+++ Expected
@@ -1 +1 @@
-x bar
+foo x

================ Case 3 passed ================
================ Case 4 passed ================
"""
OUTPUT_MARKER = '\n""" Output From:'


def output_from_marker(function_name: str) -> str:
    return f"{OUTPUT_MARKER} {function_name}"


DIVIDER = "****"


def report(test: bool, case_id: int) -> str:
    if test:
        return "\n" + f" Case {case_id} passed ".center(config.LINE_LENGTH, "=")
    else:
        return f" Case {case_id} failed ".center(config.LINE_LENGTH, "=")


passed = lambda case_id: report(True, case_id)
failed = lambda case_id: report(False, case_id)
