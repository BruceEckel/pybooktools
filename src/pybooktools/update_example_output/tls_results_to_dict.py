# tls_results_to_dict.py
from typing import Dict, List

from pybooktools.update_example_output.output_formatter import output_format
from pybooktools.update_example_output.validate_transformer import validate_transformer, UseCase


def tls_tags_to_dict(input_str: str, wrap: bool = True) -> Dict[str, List[str]]:
    """
    Converts a string with __$n$_tls__ markers into a dictionary.

    Args:
        input_str (str): The input string containing lines and __$n$_tls__ markers.
        wrap (bool): Set to False prevents wrapping

    Returns:
        Dict[str, List[str]]: A dictionary where keys are update_example_output markers and values
                              are lists of lines preceding each marker.
    """
    result: Dict[str, List[str]] = {}
    lines = input_str.strip().split("\n")
    buffer: List[str] = []
    n = 0
    for line in lines:
        if "$_tls__" in line:
            n = int(line.split("$")[1])
            result[line.strip()] = buffer
            buffer = []
        else:
            buffer.extend(output_format(line, wrap=wrap))
    if buffer:
        result[f"__${n + 1}$_tls__"] = buffer

    return result


use_cases = [
    UseCase(
        1,
        """
foo
__$1$_tls__
foo
bar
baz
__$2$_tls__
bar
__$3$_tls__
foo
bar
baz
bingo
__$4$_tls__
    """,
        {
            "__$1$_tls__": ["## foo"],
            "__$2$_tls__": ["## foo", "## bar", "## baz"],
            "__$3$_tls__": ["## bar"],
            "__$4$_tls__": ["## foo", "## bar", "## baz", "## bingo"],
        },
    ),
    # Single update_example_output at the beginning
    UseCase(
        2,
        """
__$1$_tls__
foo
bar
__$2$_tls__
baz
    """,
        {
            "__$1$_tls__": [],
            "__$2$_tls__": ["## foo", "## bar"],
            "__$3$_tls__": ["## baz"],
        },
    ),
    # Edge case: No tls_tags, just lines
    UseCase(
        3,
        """
foo
bar
baz
    """,
        "{'__$1$_tls__': ['## foo', '## bar', '## baz']}",
    ),
]
if __name__ == "__main__":
    validate_transformer(tls_tags_to_dict, use_cases)

""" Output From: validate_transformer

================ Case 1 passed ================
================ Case 2 passed ================
================ Case 3 passed ================
"""
