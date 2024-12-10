#: produce_ocl.py
import ast
import re
from argparse import ArgumentParser
from pathlib import Path

import astor
from typing_extensions import override

from pybooktools.util import run_script


def main() -> None:
    parser = ArgumentParser(
        description="Process a Python file for OCL formatting."
    )
    parser.add_argument(
        "file", type=str, help="The path to the Python file to process."
    )
    args = parser.parse_args()

    example_path = Path(args.file)
    if not example_path.exists() or not example_path.is_file():
        raise FileNotFoundError(f"The file {example_path} does not exist.")

    source_code_1 = example_path.read_text(encoding="utf-8")
    # Remove comments starting with `#| `
    source_code_2 = re.sub(
        r"^\s*#\| .*$", "", source_code_1, flags=re.MULTILINE
    )

    # Parse the source code into an AST
    tree = ast.parse(source_code_2)

    class PrintTransformer(ast.NodeTransformer):
        @override
        def visit_Expr(self, node: ast.Expr) -> ast.AST:
            if isinstance(node.value, ast.Call) and isinstance(
                node.value.func, ast.Name
            ):
                if node.value.func.id == "print":
                    # Extract the argument for print()
                    if len(node.value.args) == 1:
                        arg = node.value.args[0]

                        # Create the ocl_format line
                        ocl_call = ast.Expr(
                            value=ast.Call(
                                func=ast.Name(id="ocl_format", ctx=ast.Load()),
                                args=[arg],
                                keywords=[],
                            )
                        )

                        # Add the new line after the print statement
                        return [node, ocl_call]
            return node

    # Transform the AST
    tree = PrintTransformer().visit(tree)
    ast.fix_missing_locations(tree)

    # Convert the AST back to source code
    source_code_2 = astor.to_source(tree)
    source_code_2a = re.sub(
        r"ocl_format\((.*?)\)", r"{ocl_format(\1)}", source_code_2
    )

    # Prepare source_code_3
    source_code_3 = f'''
from pybooktools.auto_ocl import ocl_format
from pathlib import Path

outfile = Path('.') / f"{example_path.stem}_ocl.py"
outfile.write_text(f"""
{source_code_2a}
""", encoding="utf-8")
    '''

    output_path = example_path.parent / f"{example_path.stem}_3.py"
    output_path.write_text(source_code_3, encoding="utf-8")

    run_script(output_path)


if __name__ == "__main__":
    main()
