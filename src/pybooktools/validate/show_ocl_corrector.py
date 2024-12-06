import argparse
import re
from dataclasses import dataclass, field
from pathlib import Path

from icecream import ic

from pybooktools.util import error


# Define the show() function which mimics the behavior of print(), but is used for OCL.
def show(*args, **kwargs):
    """
    A function similar to print() that outputs the provided arguments.
    This function is used to mark lines that should have corresponding Output Comment Lines (OCL).
    """
    print(*args, **kwargs)


@dataclass
class ShowCall:
    line_number: int
    content: str
    output_lines: list[str]

    def is_ocl_correct(self, ocl_lines: list[str]) -> bool:
        expected_ocl_lines = [f"#: {line}" for line in self.output_lines]
        length_equal: bool = len(expected_ocl_lines) == len(ocl_lines)
        ic(length_equal)
        return length_equal and all(
            ocl.strip() == expected_ocl.strip()
            for ocl, expected_ocl in zip(ocl_lines, expected_ocl_lines)
        )

    def correct_ocl(self, lines: list[str]) -> list[str]:
        corrected_lines = lines[: self.line_number + 1]
        corrected_lines += [f"#: {output}" for output in self.output_lines]
        corrected_lines += lines[
            self.line_number + 1 + len(self.output_lines) :
        ]
        return corrected_lines


@dataclass
class OCLCorrector:
    base_path: Path
    show_pattern = re.compile(r"^\s*show\((.*?)\)")
    lines: list[str] = field(default_factory=list)
    show_calls: list[ShowCall] = field(default_factory=list)

    def _find_show_calls(self) -> None:
        for idx, line in enumerate(self.lines):
            match = self.show_pattern.match(line)
            if match:
                ic(match)
                output_lines = parse_show_output(match.group(1))
                self.show_calls.append(
                    ShowCall(
                        line_number=idx, content=line, output_lines=output_lines
                    )
                )
        ic(self.show_calls)

    def correct_file(self, file_path: Path) -> bool:
        self.lines = file_path.read_text(encoding="utf-8").splitlines()
        self._find_show_calls()

        for show_call in self.show_calls:
            ocl_lines = find_ocl_lines(self.lines, show_call.line_number)
            if not show_call.is_ocl_correct(ocl_lines):
                corrected_lines = show_call.correct_ocl(self.lines)
                file_path.write_text(
                    "\n".join(corrected_lines), encoding="utf-8"
                )
                return True  # Correct only one and then restart the analysis.
        return False

    def correct_all(self):
        python_files = list(self.base_path.glob("**/*.py"))
        for python_file in python_files:
            while self.correct_file(python_file):
                pass


def parse_show_output(content: str) -> list[str]:
    # Evaluates the content inside a show() call and returns its output as a list of strings.
    # (Here you may improve how to handle expressions within show() like formatting.)
    return ic([str(eval(content))])


def find_ocl_lines(lines: list[str], start_idx: int) -> list[str]:
    ocl_lines = []
    for idx in range(start_idx + 1, len(lines)):
        if lines[idx].strip().startswith("#: "):
            ocl_lines.append(lines[idx])
        else:
            break
    return ocl_lines


def main():
    parser = argparse.ArgumentParser(
        description="Ensure output comment lines for show() calls in Python files."
    )
    parser.add_argument(
        "path",
        nargs="?",
        type=str,
        default=".",
        help="Path to the directory or file to process. Defaults to current directory.",
    )
    args = parser.parse_args()
    base_path = Path(args.path)
    ic(base_path)
    if not base_path.exists():
        error(f"{base_path} not found")

    corrector = OCLCorrector(base_path)
    ic(corrector)
    if base_path.is_file():
        corrector.correct_file(base_path)
    else:
        corrector.correct_all()


if __name__ == "__main__":
    main()
