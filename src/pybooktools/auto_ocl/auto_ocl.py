import argparse
import ast
from pathlib import Path

import astor


class OCLTransformer(ast.NodeTransformer):
    def __init__(self):
        super().__init__()
        self.counter = 0

    def visit_Expr(self, node: ast.Expr):
        if (
                isinstance(node.value, ast.Call)
                and isinstance(node.value.func, ast.Name)
                and node.value.func.id == "print"
        ):
            self.counter += 1
            arg = node.value.args[0] if node.value.args else None
            if arg is not None:
                ocl_assignment = ast.Assign(
                    targets=[ast.Name(id=f"_o{self.counter}", ctx=ast.Store())],
                    value=ast.Call(
                        func=ast.Name(id="ocl_format", ctx=ast.Load()),
                        args=[arg],
                        keywords=[],
                    ),
                )
                return [node, ocl_assignment]
        return node


def main():
    parser = argparse.ArgumentParser(
        description="Process a Python file with OCL formatting."
    )
    parser.add_argument(
        "filename", type=str, help="The name of the Python file to process."
    )
    args = parser.parse_args()

    example_path = Path(args.filename)
    if not example_path.exists():
        print(f"Error: {example_path} does not exist.")
        return

    source_code_1 = example_path.read_text(encoding="utf-8")

    # Parse source code and apply transformations
    tree = ast.parse(source_code_1)
    transformer = OCLTransformer()
    transformed_tree = transformer.visit(tree)
    ast.fix_missing_locations(transformed_tree)

    # Generate the transformed code
    updated_code = astor.to_source(transformed_tree)

    # Write the transformed code to a new file
    new_file = example_path.with_stem(example_path.stem + "_2")
    new_file.write_text(updated_code, encoding="utf-8")

    print(f"Processed file written to {new_file}")

    # Execute the new file
    import subprocess

    subprocess.run(["python", str(new_file)], check=True)


if __name__ == "__main__":
    main()
