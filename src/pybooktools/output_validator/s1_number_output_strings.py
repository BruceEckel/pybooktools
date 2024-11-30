#: s1_number_output_strings.py
# Step 1
import argparse
from dataclasses import dataclass, field
from pathlib import Path
from typing import override

import libcst as cst

from pybooktools.tracing import trace
from pybooktools.util import (
    valid_python_file,
    artifact_path,
    trace_function_name,
)


@dataclass
class StringNumberingTransformer(cst.CSTTransformer):
    count: int = 0
    modified_strings: list[str] = field(default_factory=list)

    @override
    def leave_SimpleString(
            self, original_node: cst.SimpleString, updated_node: cst.SimpleString
    ) -> cst.CSTNode:
        value: str = original_node.value
        if value.startswith('""":'):
            # Handle triple-quoted strings that start with ':'
            stripped_value = value[4:-3]  # Remove the `""":` prefix
            self.count += 1
            numbered_string = f"{self.count}:{stripped_value}"
            new_value = f'"""{numbered_string}"""'
            self.modified_strings.append(new_value)
            return updated_node.with_changes(value=new_value)
        elif value.startswith('":'):
            # Handle single-quoted strings that start with ':'
            stripped_value = value[2:-1]  # Remove the `":` prefix
            self.count += 1
            numbered_string = f"{self.count}:{stripped_value}"
            new_value = f'"{numbered_string}"'
            self.modified_strings.append(new_value)
            return updated_node.with_changes(value=new_value)
        return updated_node


def number_output_strings(example_path: Path) -> Path:
    valid_python_file(example_path)
    example_code = example_path.read_text(encoding="utf-8")
    parsed_module = cst.parse_module(example_code)

    transformer = StringNumberingTransformer()
    modified_tree = parsed_module.visit(transformer)
    output_path = artifact_path(
        example_path, "s1_numbered", "number_output_strings"
    )
    output_path.write_text(modified_tree.code, encoding="utf-8")
    trace(f"Numbered file saved to {output_path}")
    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Adds numbers to output strings starting with ':'"
    )
    parser.add_argument(
        "file_pattern",
        type=str,
        help="File or pattern to match Python scripts to test.",
    )
    parser.add_argument(
        "-t", "--trace", action="store_true", help="Enable tracing"
    )
    args = parser.parse_args()

    if args.trace:
        trace.enable()

    if not args.file_pattern:
        parser.print_help()
        return

    trace_function_name(f"{Path(__file__).name}")
    scripts_to_number = list(Path(".").glob(args.file_pattern))
    if not scripts_to_number:
        print("No files matched the given file pattern.")
    else:
        for original_script in scripts_to_number:
            print(f"\nNumbered script: {original_script}")
            numbered_py_path = number_output_strings(original_script)
            print(f"Wrote {numbered_py_path}")


if __name__ == "__main__":
    main()
