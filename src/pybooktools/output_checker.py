#: output_checker.py
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

from pyparsing import nestedExpr, Literal, CharsNotIn, ParseException

from pybooktools.util import get_virtual_env_python


@dataclass
class OutputChecker:
    script_path: Path
    script: str = field(init=False)
    temp_script: List[str] = field(default_factory=list)
    temp_script_path: Path = None

    def __post_init__(self):
        self.script = self.script_path.read_text(encoding="utf-8")
        self.temp_script = [
            "from output_tracer import Tracer\n\ntracer = Tracer()\n"
        ]
        self.temp_script_path = Path("test_temp_a.py")

    def create_temp_script(self) -> None:
        # Define a grammar to match the print statements
        open_paren = Literal("(")
        close_paren = Literal(")")
        content = CharsNotIn("()") | nestedExpr("(", ")")
        print_stmt = Literal("print") + open_paren + content + close_paren

        original_lines = self.script.splitlines()

        for line in original_lines:
            stripped_line = line.strip()

            if stripped_line.startswith("print("):
                try:
                    # Parse and modify the print statement
                    parsed_result = print_stmt.parseString(stripped_line)
                    parsed_content = "".join(parsed_result[2:-1])
                    # Ensure 'file=tracer' is not added redundantly
                    if "file=tracer" not in stripped_line:
                        modified_print = f"print({parsed_content}, file=tracer)"
                    else:
                        modified_print = stripped_line
                    self.temp_script.append(modified_print)
                except ParseException:
                    # If parsing fails, append the line as is
                    self.temp_script.append(line)
            else:
                self.temp_script.append(line)

        # Deduplicate lines, preserving order
        seen_lines = set()
        deduplicated_script = []
        for line in self.temp_script:
            if line not in seen_lines:
                deduplicated_script.append(line)
                seen_lines.add(line)

        # Append tracer output printing
        deduplicated_script.append("print(tracer)")
        self.temp_script = deduplicated_script

    def save_temp_script(self) -> Path:
        self.temp_script_path.write_text(
            "\n".join(self.temp_script), encoding="utf-8"
        )
        return self.temp_script_path

    def run_temp_script(self) -> List[str]:
        result = subprocess.run(
            [get_virtual_env_python(), self.temp_script_path],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"Script execution failed with error:\n{result.stderr}"
            )

        # Extract tracer outputs
        tracer_outputs = []
        exec_globals = {}
        script_content = self.temp_script_path.read_text(encoding="utf-8")
        exec(script_content, exec_globals)
        tracer = exec_globals.get("tracer")
        if tracer:
            tracer_outputs = [output.strip() for output in tracer.outputs]

        return tracer_outputs

    def verify_tracer_output(self, tracer_outputs: List[str]) -> bool:
        expected_outputs = []
        in_multiline_comment = False

        for line in self.script.splitlines():
            stripped_line = line.strip()

            if stripped_line.startswith('":'):
                # Single-line expected output
                expected_outputs.append(stripped_line[2:].strip())
            elif stripped_line.startswith('""":'):
                # Toggle the multiline comment state
                in_multiline_comment = not in_multiline_comment
            elif in_multiline_comment:
                # Inside multiline comment, add expected output if the line is not empty
                if stripped_line:
                    expected_outputs.append(stripped_line)

        # Clean up any extraneous quotes or whitespace from the expected outputs
        expected_outputs = [
            output.strip('"').strip() for output in expected_outputs if output
        ]

        # Debugging: Print both expected and actual outputs for comparison
        print(f"Expected Outputs: {expected_outputs}")
        print(f"Tracer Outputs: {tracer_outputs}")

        return tracer_outputs == expected_outputs


# Example usage
if __name__ == "__main__":
    print("starting output checker")
    original_script_content = '''#: test.py
print("test1")
":test1"

print("test2")
print("test3")
""":
test2
test3
"""
'''
    checker = OutputChecker(script_path=Path("test_temp_a.py"))
    checker.create_temp_script()
    temp_script_path = checker.save_temp_script()
    try:
        tracer_outputs = checker.run_temp_script()
        is_verified = checker.verify_tracer_output(tracer_outputs)
        if is_verified:
            print("Tracer output verified successfully.")
        else:
            print("Tracer output verification failed.")
    finally:
        print(f"Cleaning up {temp_script_path}")
        # temp_script_path.unlink()  # Clean up the temporary script file
