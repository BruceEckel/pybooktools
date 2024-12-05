import argparse
import re
from dataclasses import dataclass
from pathlib import Path


# Define the show() function which mimics the behavior of print(), but is used for OCL purposes.
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


class ShowOCLCorrector:
    show_pattern = re.compile(r"^\s*show\((.*?)\)")

    def __init__(self, base_path: Path):
        self.base_path = base_path

    def _parse_show_output(self, content: str) -> list[str]:
        # Evaluates the content inside a show() call and returns its output as a list of strings.
        # (Here you may improve how to handle expressions within show() like formatting.)
        return [str(eval(content))]

    def _find_show_calls(self, lines: list[str]) -> list[ShowCall]:
        show_calls = []
        for idx, line in enumerate(lines):
            match = self.show_pattern.match(line)
            if match:
                output_lines = self._parse_show_output(match.group(1))
                show_calls.append(
                    ShowCall(
                        line_number=idx, content=line, output_lines=output_lines
                    )
                )
        return show_calls

    def _find_ocl_lines(self, lines: list[str], start_idx: int) -> list[str]:
        ocl_lines = []
        for idx in range(start_idx + 1, len(lines)):
            if lines[idx].strip().startswith("#: "):
                ocl_lines.append(lines[idx])
            else:
                break
        return ocl_lines

    def _is_ocl_correct(
            self, show_call: ShowCall, ocl_lines: list[str]
    ) -> bool:
        expected_ocl_lines = [f"#: {line}" for line in show_call.output_lines]
        return len(expected_ocl_lines) == len(ocl_lines) and all(
            ocl.strip() == expected_ocl.strip()
            for ocl, expected_ocl in zip(ocl_lines, expected_ocl_lines)
        )

    def _correct_ocl(self, lines: list[str], show_call: ShowCall) -> list[str]:
        corrected_lines = lines[: show_call.line_number + 1]
        corrected_lines += [f"#: {output}" for output in show_call.output_lines]
        corrected_lines += lines[
                           show_call.line_number + 1 + len(show_call.output_lines):
                           ]
        return corrected_lines

    def correct_file(self, file_path: Path) -> bool:
        lines = file_path.read_text(encoding="utf-8").splitlines()
        show_calls = self._find_show_calls(lines)

        for show_call in show_calls:
            ocl_lines = self._find_ocl_lines(lines, show_call.line_number)
            if not self._is_ocl_correct(show_call, ocl_lines):
                corrected_lines = self._correct_ocl(lines, show_call)
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

    if base_path.is_file():
        corrector = ShowOCLCorrector(base_path.parent)
        corrector.correct_file(base_path)
    else:
        corrector = ShowOCLCorrector(base_path)
        corrector.correct_all()


if __name__ == "__main__":
    main()
