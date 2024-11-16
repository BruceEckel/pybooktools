import argparse
import glob
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import List

from rich.console import Console
from rich.syntax import Syntax


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
        output = re.compile(r'(?<!=)"""|":\s(.+?)\n')
        script_content = self.script_path.read_text(encoding="utf-8")
        matches = output.findall(script_content)
        return matches

    def run_script(self) -> str:
        """
        Runs the script and captures its output.
        """
        result = subprocess.run(
            ["python", str(self.script_path)], capture_output=True, text=True
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
                    passed=expected == actual, expected=expected, actual=actual
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
                    updated_content = re.sub(
                        f"(?<=: ){re.escape(result.expected)}",
                        result.actual,
                        updated_content,
                        count=1,
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
