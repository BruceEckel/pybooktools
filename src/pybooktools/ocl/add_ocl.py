#: add_ocl.py
"""
Take `python_source_code` and find every top-level (i.e., non-indented) `print(arg)` statement.
Add a line directly after it like this:

print(arg)
_on = ocl_format(arg)

Where the `n` in `_on` is an `int` that is incremented for each subsequent `print(arg)` that `add_ocl` modifies.

If a top-level `print()` has more than one argument, `add_ocl` issues a warning and ignores that `print()`.
Returns the modified `python_source_code` string.
"""

import re
from dataclasses import dataclass

import libcst as cst
import libcst.matchers as m

warn = print


@dataclass
class PrintTransformer(cst.CSTTransformer):
    counter: int = 0

    def leave_SimpleStatementLine(
        self,
        node: cst.SimpleStatementLine,
        updated_node: cst.SimpleStatementLine,
    ) -> cst.FlattenSentinel[cst.BaseStatement]:
        if m.matches(
            node,
            m.SimpleStatementLine(
                body=[m.Expr(value=m.Call(func=m.Name("print")))]
            ),
        ):
            call = node.body[0].value  # type: ignore
            if isinstance(call, cst.Call) and len(call.args) == 1:
                self.counter += 1
                ocl_assignment = cst.SimpleStatementLine(
                    body=[
                        cst.Assign(
                            targets=[
                                cst.AssignTarget(
                                    target=cst.Name(f"_o{self.counter}")
                                )
                            ],
                            value=cst.Call(
                                func=cst.Name("ocl_format"), args=call.args
                            ),
                        )
                    ]
                )
                return cst.FlattenSentinel([updated_node, ocl_assignment])
            else:
                warn(
                    f"Ignoring multi-argument or invalid print() statement: {node.code}"
                )
        return updated_node


def add_ocl(python_source_code: str) -> str:
    """
    Strips old OCL comments, then modifies the provided Python source code to add
    `_on = ocl_format(arg)` lines after each top-level print(arg).

    Args:
        python_source_code (str): The Python source code to modify.

    Returns:
        str: The modified Python source code.
    """
    # Remove comments starting with `#| `
    de_ocl_code = re.sub(
        r"^#\| .*$", "", python_source_code, flags=re.MULTILINE
    )

    tree = cst.parse_module(de_ocl_code)
    transformer = PrintTransformer()
    modified_tree = tree.visit(transformer)

    return modified_tree.code


def test_add_ocl():
    sample_code = """
def deposit(x, y):
  return 10.0
def withdraw(x, y):
  return 10.0
print(balance := deposit(100.0, 50.0))
print(withdraw(balance, 30.0))
"""
    print("\n--- sample_code ---\n", sample_code)
    modified_code = add_ocl(sample_code)
    print("\n--- modified_code ---\n", modified_code)


def main():
    test_add_ocl()
    # parser = argparse.ArgumentParser(
    #     description="Process a Python file with add_ocl."
    # )
    # parser.add_argument("file", type=str, help="The Python file to process.")
    # args = parser.parse_args()
    # file_path = Path(args.file)
    # if not file_path.exists():
    #     print(f"Error: The file {file_path} does not exist.")
    # else:
    #     source_code = file_path.read_text(encoding="utf-8")
    #     modified_code = add_ocl(source_code)
    #     print(modified_code)


if __name__ == "__main__":
    main()
