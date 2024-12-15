# tls_results_to_dict.py
from typing import Dict, List

from pybooktools.tls import output_format
from pybooktools.validate import UseCase, validate_transformer


def tls_tags_to_dict(input_str: str) -> Dict[str, List[str]]:
    """
    Converts a string with __$n$_tls__ markers into a dictionary.

    Args:
        input_str (str): The input string containing lines and __$n$_tls__ markers.

    Returns:
        Dict[str, List[str]]: A dictionary where keys are tls markers and values
                              are lists of lines preceding each marker.
    """
    result: Dict[str, List[str]] = {}
    lines = input_str.strip().split("\n")
    buffer: List[str] = []

    for line in lines:
        if "$_tls__" in line:
            result[line.strip()] = buffer
            buffer = []
        else:
            buffer.extend(output_format(line))

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
    # Single tls at the beginning
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
        "{}",
    ),
]
if __name__ == "__main__":
    validate_transformer(tls_tags_to_dict, use_cases)

""" Output From: validate_transformer

================ Case 1 passed ================
================ Case 2 passed ================
================ Case 3 passed ================
"""
