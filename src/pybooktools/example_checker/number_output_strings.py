#: number_output_strings.py
import argparse
from dataclasses import dataclass, field
from pathlib import Path
from typing import override

import libcst as cst

from pybooktools.util import valid_python_file


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


def number_output_strings(example_path: Path) -> None:
    valid_python_file(example_path)
    validate_dir = example_path.parent / "_validate"
    validate_dir.mkdir(exist_ok=True)

    example_code = example_path.read_text(encoding="utf-8")
    parsed_module = cst.parse_module(example_code)

    transformer = StringNumberingTransformer()
    modified_tree = parsed_module.visit(transformer)

    output_path = validate_dir / f"{example_path.stem}_numbered.py"
    output_path.write_text(modified_tree.code, encoding="utf-8")
    print(f"Modified file saved to {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Adds numbers to output strings starting with ':'"
    )
    parser.add_argument(
        "file_pattern",
        type=str,
        help="File or pattern to match Python scripts to test.",
    )
    args = parser.parse_args()
    if not args.file_pattern:
        parser.print_help()
        return

    scripts_to_number = list(Path(".").glob(args.file_pattern))
    if not scripts_to_number:
        print("No files matched the given file pattern.")
    else:
        for original_script in scripts_to_number:
            print(f"\nNumbering script: {original_script}")
            number_output_strings(original_script)


if __name__ == "__main__":
    main()
