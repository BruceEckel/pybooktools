import re
import subprocess
from pathlib import Path

from pyparsing import nestedExpr, Literal, CharsNotIn, ParseException

from pybooktools.util import get_virtual_env_python


def create_temp_script(original_script: str) -> Path:
    temp_script: list[str] = [
        "from output_tracer import Tracer\n\ntracer = Tracer()\n"
    ]

    # Define a grammar to match the print statements
    open_paren = Literal("(")
    close_paren = Literal(")")
    content = CharsNotIn("()") | nestedExpr("(", ")")
    print_stmt = Literal("print") + open_paren + content + close_paren

    original_lines = original_script.splitlines()

    for line in original_lines:
        stripped_line = line.strip()

        if stripped_line.startswith("print("):
            try:
                # Parse and modify the print statement
                parsed_result = print_stmt.parseString(stripped_line)
                parsed_content = "".join(parsed_result[2:-1])
                modified_print = f"print({parsed_content}, file=tracer)"
                temp_script.append(modified_print)
            except ParseException:
                # If parsing fails, append the line as is
                temp_script.append(line)
        else:
            temp_script.append(line)

    # Handle the case where parentheses are not correctly detected by modifying the line manually
    temp_script = [
        (
            re.sub(r"print\((.*)\)$", r"print(\1, file=tracer)", line)
            if line.strip().startswith("print(") and ", file=tracer" not in line
            else line
        )
        for line in temp_script
    ]
    temp_script += ["print(tracer)"]

    # temp_script_path = Path(
    #     tempfile.NamedTemporaryFile(delete=False, suffix="_tmp.py").name
    # )
    temp_script_path = Path("test_temp_a.py")
    temp_script_path.write_text("\n".join(temp_script), encoding="utf-8")
    return temp_script_path


def run_temp_script(script_path: Path) -> list[str]:
    result = subprocess.run(
        [get_virtual_env_python(), script_path], capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"Script execution failed with error:\n{result.stderr}"
        )

    # Extract tracer outputs
    tracer_outputs = []
    exec_globals = {}
    script_content = script_path.read_text(encoding="utf-8")
    exec(script_content, exec_globals)
    tracer = exec_globals.get("tracer")
    if tracer:
        tracer_outputs = [output.strip() for output in tracer.outputs]

    return tracer_outputs


def verify_tracer_output(
        original_script: str, tracer_outputs: list[str]
) -> bool:
    expected_outputs = []
    in_multiline_comment = False

    for line in original_script.splitlines():
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
    expected_outputs = [output.strip('"').strip() for output in expected_outputs if output]

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
    temp_script_path = create_temp_script(original_script_content)
    try:
        tracer_outputs = run_temp_script(temp_script_path)
        is_verified = verify_tracer_output(
            original_script_content, tracer_outputs
        )
        if is_verified:
            print("Tracer output verified successfully.")
        else:
            print("Tracer output verification failed.")
    finally:
        print(f"Cleaning up {temp_script_path}")
        # temp_script_path.unlink()  # Clean up the temporary script file
