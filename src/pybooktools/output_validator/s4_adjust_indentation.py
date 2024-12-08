#: s4_adjust_indentation.py
# Step 4
import argparse
import re
from pathlib import Path

from pybooktools.tracing import trace
from pybooktools.util import get_artifact, artifact_path, display_function_name


def adjust_multiline_strings_indent(code: str) -> str:
    """
    Adjust the indentation of multiline string literals that start with ':'
    """

    def adjust_indent(match: re.Match) -> str:
        multiline_string = match.group(0)
        trace("multiline_string:", multiline_string)
        # Find the indentation level by inspecting the preceding line
        preceding_whitespace = match.group(1)
        trace(f"preceding_whitespace: [{preceding_whitespace}]")
        # Adjust each line after the first with the correct indentation level
        lines = multiline_string.splitlines()
        trace("lines:", lines)
        if len(lines) > 1:
            lines = [lines[0]] + [
                f"{preceding_whitespace}{line.strip()}" for line in lines[1:]
            ]
            trace("lines:", lines)
        result = "\n".join(lines)
        trace("result:", result)
        return result

    # Regular expression to find multiline strings starting with '""": '
    pattern = re.compile(r'\n([ \t]*)""":\n((?:.*\n?)+?)"""', re.MULTILINE)
    modified_code = re.sub(pattern, adjust_indent, code)

    return modified_code


def main():
    parser = argparse.ArgumentParser(
        description='Updates Python examples containing output strings that begin with ": or """:'
    )
    parser.add_argument(
        "file_pattern",
        type=str,
        help="File or pattern to match Python scripts to test",
    )
    parser.add_argument(
        "-t", "--trace", action="store_true", help="Enable tracing output"
    )
    args = parser.parse_args()

    if args.trace:
        trace.enable()
        display_function_name()

    if not args.file_pattern:
        parser.print_help()
        return

    scripts_to_update = list(Path(".").glob(args.file_pattern))
    if not scripts_to_update:
        print("No files matched the given file pattern.")
    else:
        for original_script in scripts_to_update:
            print(f"\nAdjusting indentation for {original_script}")
            incorporated_py_path = get_artifact(
                original_script, "s3_incorporated"
            )
            adjusted: str = adjust_multiline_strings_indent(
                incorporated_py_path.read_text(encoding="utf-8")
            )
            trace("adjusted:", adjusted)
            adjusted_py: Path = artifact_path(original_script, "adjusted")
            adjusted_py.write_text(adjusted, encoding="utf-8")
            print(f"Indented version saved: {adjusted_py}")


if __name__ == "__main__":
    main()
