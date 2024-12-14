from dataclasses import dataclass
from pathlib import Path

OUTPUT_TAG = '\n""" Output From check_operation:'


@dataclass
class UseCase:
    case_id: int
    script: str
    expected_output: str

    def __iter__(self):
        return iter((self.case_id, self.script, self.expected_output))


def report(test: bool, case_id: int) -> str:
    if test:
        return f" Case {case_id} passed ".center(47, "=")
    else:
        return f" Case {case_id} failed ".center(47, "=")


passed = lambda case_id: report(True, case_id)
failed = lambda case_id: report(False, case_id)


def check_operation(operation: callable, use_cases: list[UseCase]) -> None:
    results = []
    for case_id, script, expected_output in use_cases:
        actual_output = operation(script)
        if actual_output == expected_output:
            results.append(passed(case_id))
        else:
            results.append(
                f"""
{failed(case_id)}
--- Expected ---
{expected_output}
--- Actual ---
{actual_output}
"""
            )
    this_file_path = Path(__file__.replace("\\", "/"))
    this_file = this_file_path.read_text(encoding="utf-8")

    if OUTPUT_TAG in this_file:
        this_file = this_file[: this_file.index(OUTPUT_TAG)]
    this_file_path.write_text(
        this_file + f'{OUTPUT_TAG}\n{"".join(results)}\n"""\n',
        encoding="utf-8",
    )


if __name__ == "__main__":
    check_operation(
        lambda script: script + " bar",
        [
            UseCase(1, "foo", "foo bar"),
            UseCase(2, "x", "foo x"),
            UseCase(3, "x", "x bar"),
        ],
    )

""" Output From check_operation:
================ Case 1 passed ================
================ Case 2 failed ================
--- Expected ---
foo x
--- Actual ---
x bar
================ Case 3 passed ================
"""
