import argparse
import glob
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import List

from rich.console import Console
from rich.syntax import Syntax

from pybooktools.util import get_virtual_env_python


@dataclass
class TestResult:
    passed: bool
    expected: str
    actual: str


@dataclass
class PythonOutputTester:
    script_path: Path

    def extract_expected_output(self) -> List[str]:
        """
        Extracts expected output lines from the Python script.
        Any unassigned string starting with ': ' is considered expected output.
        """
        output_pattern = re.compile(
            r'(^"{3}:\s*([\s\S]+?)"{3})|(^":\s*(.*?))("{1})', re.MULTILINE
        )
        script_content = self.script_path.read_text(encoding="utf-8")
        matches = output_pattern.findall(script_content)
        # Flatten matches and remove empty strings
        extracted = [
            match[1] or match[3]
            for match in matches
            if match[1] or match[3] is not None
        ]
        # Split multiline matches into separate lines
        expected_lines = []
        for match in extracted:
            expected_lines.extend(match.strip().splitlines())
        return expected_lines

    def run_script(self) -> str:
        """
        Runs the script and captures its output.
        """
        result = subprocess.run(
            [get_virtual_env_python(), str(self.script_path)],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            console = Console()
            console.print(
                f"[bold red]Error running script {self.script_path}:[/bold red]"
            )
            syntax = Syntax(
                self.script_path.read_text(encoding="utf-8"),
                "python",
                theme="monokai",
                line_numbers=True,
            )
            console.print(syntax)
            console.print(
                f"[bold red]Error Message:[/bold red] {result.stderr}"
            )
        return result.stdout.strip()

    def compare_output(self) -> List[TestResult]:
        """
        Compares the extracted expected output with the actual output from running the script.
        """
        expected_output = self.extract_expected_output()
        actual_output = self.run_script().splitlines()

        results = []
        for expected, actual in zip(expected_output, actual_output):
            results.append(
                TestResult(
                    passed=expected.strip() == actual.strip(),
                    expected=expected,
                    actual=actual,
                )
            )

        # Handle cases where actual output has more lines than expected output
        if len(actual_output) > len(expected_output):
            for extra_actual in actual_output[len(expected_output):]:
                results.append(
                    TestResult(
                        passed=False,
                        expected="(No expected output)",
                        actual=extra_actual,
                    )
                )

        # Handle cases where expected output has more lines than actual output
        if len(expected_output) > len(actual_output):
            for extra_expected in expected_output[len(actual_output):]:
                results.append(
                    TestResult(
                        passed=False,
                        expected=extra_expected,
                        actual="(No actual output)",
                    )
                )

        return results

    def run_tests(self, update: bool = False) -> None:
        """
        Runs the tests and prints the results. If 'update' is True, update the script with actual output.
        """
        results = self.compare_output()
        if update:
            script_content = self.script_path.read_text(encoding="utf-8")
            updated_content = script_content
            for result in results:
                if not result.passed:
                    if result.expected == "(No expected output)":
                        # Add expected output where none existed before
                        updated_content = re.sub(
                            r"(print\(.*\))",
                            f'\1\n": {result.actual}"',
                            updated_content,
                            count=1,
                        )
                    elif result.actual != "(No actual output)":
                        # Update existing expected output and ensure it is properly quoted
                        updated_content = re.sub(
                            f"(?<=: ){re.escape(result.expected)}(?=\n|$)",
                            result.actual,
                            updated_content,
                            count=1,
                        )
            # Ensure all added or updated lines have proper closing quotes and are valid
            updated_content = re.sub(
                r'(": [^\"]*)$', r'\1"', updated_content, flags=re.MULTILINE
            )
            self.script_path.write_text(updated_content, encoding="utf-8")
            print(f"Corrected the expected output in {self.script_path}")
        else:
            for idx, result in enumerate(results, start=1):
                if result.passed:
                    print(f"Test {idx}: PASSED")
                else:
                    print(f"Test {idx}: FAILED")
                    print(f"  Expected: {result.expected}")
                    print(f"  Actual:   {result.actual}")


def main():
    parser = argparse.ArgumentParser(
        description="Python Output Tester - Compare expected output comments in scripts with actual output."
    )
    parser.add_argument(
        "file_pattern",
        type=str,
        help="File or pattern to match Python scripts to test.",
    )
    parser.add_argument(
        "-u",
        "--update",
        action="store_true",
        help="Update the expected output to match the actual output.",
    )
    args = parser.parse_args()

    scripts_to_test = glob.glob(args.file_pattern)
    if not scripts_to_test:
        print("No files matched the given file pattern.")
    else:
        for script in scripts_to_test:
            print(f"\nTesting script: {script}")
            tester = PythonOutputTester(Path(script))
            tester.run_tests(update=args.update)


if __name__ == "__main__":
    main()
