from typing import Dict, List

from pybooktools.ptag import output_format


def ptags_to_dict(input_str: str) -> Dict[str, List[str]]:
    """
    Converts a string with _$_ptag_ markers into a dictionary.

    Args:
        input_str (str): The input string containing lines and _$_ptag_ markers.

    Returns:
        Dict[str, List[str]]: A dictionary where keys are ptag markers and values
                              are lists of lines preceding each marker.
    """
    result: Dict[str, List[str]] = {}
    lines = input_str.strip().split("\n")
    buffer: List[str] = []

    for line in lines:
        if "_$_ptag_" in line:
            result[line.strip()] = buffer
            buffer = []
        else:
            buffer.append(output_format(line))

    return result


def test_parse_to_dict():
    input_str = """
foo
_$_ptag_1
foo
bar
baz
_$_ptag_2
bar
_$_ptag_3
foo
bar
baz
bingo
_$_ptag_4
    """
    expected_result = {
        "_$_ptag_1": ["## foo"],
        "_$_ptag_2": ["## foo", "## bar", "## baz"],
        "_$_ptag_3": ["## bar"],
        "_$_ptag_4": ["## foo", "## bar", "## baz", "## bingo"],
    }
    parsed_dict = ptags_to_dict(input_str)
    print(parsed_dict)
    assert parsed_dict == expected_result

    # Additional test case: Single ptag at the beginning
    input_str_2 = """
_$_ptag_1
foo
bar
_$_ptag_2
baz
    """
    expected_result_2 = {"_$_ptag_1": [], "_$_ptag_2": ["## foo", "## bar"]}
    parsed_dict_2 = ptags_to_dict(input_str_2)
    print(parsed_dict_2)
    assert parsed_dict_2 == expected_result_2

    # Edge case: No ptags, just lines
    input_str_3 = """
foo
bar
baz
    """
    expected_result_3 = {}
    parsed_dict_3 = ptags_to_dict(input_str_3)
    print(parsed_dict_3)
    assert parsed_dict_3 == expected_result_3


if __name__ == "__main__":
    test_parse_to_dict()
