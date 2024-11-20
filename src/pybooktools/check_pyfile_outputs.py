#: check_pyfile_outputs.py
import argparse
import ast
import glob
from pathlib import Path
from typing import Final

validate_dir: Final[Path] = Path("_validate")
validate_dir.mkdir(exist_ok=True)


class PrintTransformer(ast.NodeTransformer):
    def visit_Call(self, node: ast.Call):
        # Replace print calls with track.print
        if isinstance(node.func, ast.Name) and node.func.id == "print":
            node.func = ast.Attribute(
                value=ast.Name(id="track", ctx=ast.Load()),
                attr="print",
                ctx=ast.Load(),
            )
        return self.generic_visit(node)


class UnassignedStringTransformer(ast.NodeTransformer):
    def visit_Expr(self, node: ast.Expr):
        if isinstance(node.value, ast.Constant) and isinstance(
                node.value.value, str
        ):
            # Surround unassigned strings with track.expected
            new_node = ast.Expr(
                value=ast.Call(
                    func=ast.Attribute(
                        value=ast.Name(id="track", ctx=ast.Load()),
                        attr="expected",
                        ctx=ast.Load(),
                    ),
                    args=[node.value],
                    keywords=[],
                )
            )
            return ast.copy_location(new_node, node)
        return node


def create_validation_pyfile(pyfile: Path) -> Path:
    validation_file_path = validate_dir / pyfile.with_name(
        f"{pyfile.stem}_validate{pyfile.suffix}"
    )
    output_file_path = pyfile.with_name(f"{pyfile.stem}_tracker.json")
    # Read the original Python file
    source_code = pyfile.read_text(encoding="utf-8")
    tree = ast.parse(source_code)

    # Add the necessary import and global Tracker instance
    import_node = ast.ImportFrom(
        module="pybooktools.tracker",
        names=[ast.alias(name="Tracker", asname=None)],
        level=0,
    )
    tracker_instance_node = ast.Assign(
        targets=[ast.Name(id="track", ctx=ast.Store())],
        value=ast.Call(
            func=ast.Name(id="Tracker", ctx=ast.Load()),
            args=[ast.Constant(value=str(output_file_path), kind=None)],
            keywords=[],
        ),
    )

    # Transform print calls and unassigned strings
    tree = PrintTransformer().visit(tree)
    tree = UnassignedStringTransformer().visit(tree)

    # Add the new import and tracker instance at the beginning
    tree.body.insert(0, tracker_instance_node)
    tree.body.insert(0, import_node)

    # Fix missing locations
    ast.fix_missing_locations(tree)

    # Write the transformed code to a new file
    transformed_code = ast.unparse(tree)
    validation_file_path.write_text(
        transformed_code + "\ntrack.compare()\ntrack.create_output_file()\n",
        encoding="utf-8",
    )
    return validation_file_path


def main():
    parser = argparse.ArgumentParser(
        description="Python Output Tester - Compare expected output comments with actual output."
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
    if not (args.file_pattern or args.store_true):
        parser.print_help()
        return

    scripts_to_test = glob.glob(args.file_pattern)
    if not scripts_to_test:
        print("No files matched the given file pattern.")
    else:
        for script in scripts_to_test:
            print(f"\nTesting script: {script}")
            val_file = create_validation_pyfile(Path(script))
            print(f"Created {val_file}")


if __name__ == "__main__":
    main()
