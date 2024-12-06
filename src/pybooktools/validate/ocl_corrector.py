import argparse
import re
from dataclasses import dataclass, field
from pathlib import Path

from icecream import ic

from pybooktools.util import error


@dataclass
class PrintCall:
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
                           self.line_number + 1 + len(self.output_lines):
                           ]
        return corrected_lines


@dataclass
class OCLCorrector:
    base_path: Path
    lines: list[str] = field(default_factory=list)
    print_calls: list[PrintCall] = field(default_factory=list)
    print_pattern = re.compile(r"^\s*print\((.*?)\)")

    def _find_print_calls(self) -> None:
        for idx, line in enumerate(self.lines):
            match = self.print_pattern.match(line)
            if match:
                ic(match)
                output_lines = parse_print_output(match.group(1))
                self.print_calls.append(
                    PrintCall(
                        line_number=idx, content=line, output_lines=output_lines
                    )
                )
        ic("After _find_print_calls", self)

    def correct_file(self, file_path: Path) -> bool:
        self.lines = file_path.read_text(encoding="utf-8").splitlines()
        self._find_print_calls()

        for print_call in self.print_calls:
            ocl_lines = find_ocl_lines(self.lines, print_call.line_number)
            if not print_call.is_ocl_correct(ocl_lines):
                corrected_lines = print_call.correct_ocl(self.lines)
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


def parse_print_output(content: str) -> list[str]:
    # Evaluates the content inside a print() call and returns its output as a list of strings.
    # (Here you may improve how to handle expressions within print() like formatting.)
    ic()
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
        description="Ensure output comment lines for print() calls in Python files."
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
