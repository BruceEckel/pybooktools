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
            r'(^""":\n([\s\S]*?)\n""")|(^":\s*([^\n"]*?)")', re.MULTILINE
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
            lines = script_content.splitlines()

            updated_lines = []
            result_idx = 0

            for line in lines:
                updated_lines.append(line)
                if "print(" in line and result_idx < len(results):
                    # Process single-line expected output
                    result = results[result_idx]
                    result_idx += 1

                    # Update or append the expected output
                    if not result.passed:
                        if result.expected == "(No expected output)":
                            updated_lines.append(f'": {result.actual}"')
                        else:
                            # Update existing single-line expected output
                            if len(updated_lines) > 1 and updated_lines[
                                -2
                            ].startswith('": '):
                                updated_lines[-1] = f'": {result.actual}"'

                elif line.startswith('"""') and result_idx < len(results):
                    # Process multi-line expected outputs
                    result = results[result_idx]
                    result_idx += 1

                    # Update multi-line block if mismatched
                    if not result.passed:
                        updated_lines.append(result.actual)

            # Add any remaining results as expected outputs
            while result_idx < len(results):
                result = results[result_idx]
                result_idx += 1
                if result.expected == "(No expected output)":
                    updated_lines.append(f'": {result.actual}"')
                elif result.actual == "(No actual output)":
                    updated_lines.append(f'": {result.expected}"')

            self.script_path.write_text(
                "\n".join(updated_lines), encoding="utf-8"
            )
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
