# add_ptags.py
"""
The argument to add_ptags is a string containing a valid Python script that may include print() statements.
Using libcst, find all `print()` statements and add a print() statement right after it, at the same indent level.
This added print() statement will be called a `ptag`.
The argument to the ptag is a simple string of the form:
"_ptag_{n}"
Where n is an integer that is incremented for each ptag.
The `add_ptags` function returns the modified Python script.
"""
from typing import Union

import libcst as cst
from libcst import matchers as m


class AddPTagsTransformer(cst.CSTTransformer):
    def __init__(self) -> None:
        super().__init__()
        self.ptag_counter = 0

    def leave_SimpleStatementLine(
            self,
            original_node: cst.SimpleStatementLine,
            updated_node: cst.SimpleStatementLine,
    ) -> Union[cst.BaseStatement, cst.RemovalSentinel]:
        # Check if the line contains a print() statement
        if any(
                m.matches(child, m.Expr(m.Call(func=m.Name("print"))))
                for child in original_node.body
        ):
            # Increment ptag counter
            self.ptag_counter += 1
            # Create a ptag statement with the same indentation as the original
            ptag_statement = cst.SimpleStatementLine(
                [
                    cst.Expr(
                        cst.Call(
                            func=cst.Name("print"),
                            args=[
                                cst.Arg(
                                    value=cst.SimpleString(
                                        f'"_ptag_{self.ptag_counter}"'
                                    )
                                )
                            ],
                        )
                    )
                ]
            )
            # Return original statement plus the new ptag statement
            return cst.FlattenSentinel([updated_node, ptag_statement])
        return updated_node


def add_ptags(python_example: str) -> str:
    """
    Given a Python script as a string, add ptag statements after each print() statement.

    Args:
        python_example (str): The input Python script.

    Returns:
        str: The modified Python script with ptag statements.
    """
    # Parse the input Python script
    tree = cst.parse_module(python_example)
    # Apply the transformer
    modified_tree = tree.visit(AddPTagsTransformer())
    # Return the modified code as a string
    return modified_tree.code


def test_add_ptags() -> None:
    """Test the add_ptags function with various cases."""
    # Test case 1: Single print statement
    input_code = """print("Hello")"""
    expected_output = """print("Hello")\nprint("_ptag_1")"""
    assert add_ptags(input_code) == expected_output

    # Test case 2: Multiple print statements
    input_code = """
print("Hello")
x = 42
print("World")
"""
    expected_output = """
print("Hello")
print("_ptag_1")
x = 42
print("World")
print("_ptag_2")
"""
    assert add_ptags(input_code) == expected_output

    # Test case 3: Nested print statement
    input_code = """
if True:
    print("Inside if")
"""
    expected_output = """
if True:
    print("Inside if")
    print("_ptag_1")
"""
    assert add_ptags(input_code) == expected_output

    # Test case 4: No print statements
    input_code = """
x = 10
y = 20
result = x + y
"""
    expected_output = input_code
    assert add_ptags(input_code) == expected_output

    # Test case 5: Mixed content
    input_code = """
print("Start")
for i in range(3):
    print(f"Loop {i}")
print("End")
"""
    expected_output = """
print("Start")
print("_ptag_1")
for i in range(3):
    print(f"Loop {i}")
    print("_ptag_2")
print("End")
print("_ptag_3")
"""
    assert add_ptags(input_code) == expected_output

    # Test case 6: Empty script
    input_code = """"""
    expected_output = """"""
    assert add_ptags(input_code) == expected_output

    # Test case 7: Indentation edge case
    input_code = """
def example():
    print("Indented")
    if True:
        print("Nested")
"""
    expected_output = """
def example():
    print("Indented")
    print("_ptag_1")
    if True:
        print("Nested")
        print("_ptag_2")
"""
    assert add_ptags(input_code) == expected_output

    # Test case 8: Deeply nested print statements
    input_code = """
if True:
    if True:
        print("Deeply nested")
"""
    expected_output = """
if True:
    if True:
        print("Deeply nested")
        print("_ptag_1")
"""
    assert add_ptags(input_code) == expected_output

    print("All tests passed.")


if __name__ == "__main__":
    test_add_ptags()
