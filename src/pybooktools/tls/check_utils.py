# check_utils.py
import difflib
import inspect
from dataclasses import dataclass
from pathlib import Path

OUTPUT_TAG = '\n""" Output From check_operation:'
DIVIDER = "****"


@dataclass
class UseCase:
    case_id: int
    script: str
    expected_output: str

    def __post_init__(self):
        self.script = self.script.strip() + "\n"
        self.expected_output = self.expected_output.strip() + "\n"

    def __iter__(self):
        return iter((self.case_id, self.script, self.expected_output))


def report(test: bool, case_id: int) -> str:
    if test:
        return f" Case {case_id} passed ".center(47, "=")
    else:
        return f" Case {case_id} failed ".center(47, "=")


passed = lambda case_id: report(True, case_id)
failed = lambda case_id: report(False, case_id)


def check_string_transformer(
        string_transformer: callable, use_cases: list[UseCase]
) -> None:
    results = []
    for case_id, script, expected_output in use_cases:
        actual_output = string_transformer(script).strip() + "\n"
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

    if OUTPUT_TAG in this_file:
        this_file = this_file[: this_file.index(OUTPUT_TAG)]
    this_file_path.write_text(
        this_file + f'{OUTPUT_TAG}\n{"".join(results)}\n"""\n',
        encoding="utf-8",
    )


if __name__ == "__main__":
    print("start")
    check_string_transformer(
        lambda script: script + " bar",
        [
            UseCase(1, "foo", "foo bar"),
            UseCase(2, "x", "foo x"),
            UseCase(3, "x", "x bar"),
        ],
    )
    print("end")

""" Output From check_operation:
================ Case 1 passed ================
================ Case 2 failed ================
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
"""
