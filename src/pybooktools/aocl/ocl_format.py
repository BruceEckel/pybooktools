import textwrap
from typing import Any


def ocl_format(arg: Any) -> str:
    """
    Formats the given argument such that the output:
    - Starts with '#| '
    - Ensures each resulting line is no wider than 47 characters.

    Args:
        arg (Any): The input argument to format.

    Returns:
        str: The formatted string.
    """
    formatted = str(arg)
    wrapped_lines = textwrap.wrap(formatted, width=47)
    # Prepend '#| ' to each line
    result = "\n".join(f"#| {line}" for line in wrapped_lines)
    return result


def test_ocl_format():
    # Test examples
    a_1 = 1
    a_2 = "foo"
    a_3 = "A really long line that just keeps going am I finished yet? Yes!"
    a_4 = {1: 2, 3: 4}
    a_5 = {"a", "b", "c"}
    a_6 = 3.14159
    a_7 = f"The value of pi is {a_6}. Of course that has been rounded off"

    # Basic tests
    print(ocl_format(a_1))
    print(ocl_format(a_2))
    print(ocl_format(a_3))
    print(ocl_format(a_4))
    print(ocl_format(a_5))
    print(ocl_format(a_6))
    print(ocl_format(a_7))

    # Additional tests
    # Empty string
    print(ocl_format(""))

    # Multiline string
    multiline = "This is a test of multiline wrapping.\nHere is another line to ensure we handle them."
    print(ocl_format(multiline))

    # Very long single word
    long_word = "supercalifragilisticexpialidocious" * 2
    print(ocl_format(long_word))

    # Nested structures
    nested = [{"key1": [1, 2, 3]}, {"key2": (4, 5, 6)}]
    print(ocl_format(nested))

    # Boolean values
    print(ocl_format(True))
    print(ocl_format(False))

    # None value
    print(ocl_format(None))

    # Complex number
    complex_num = 3 + 4j
    print(ocl_format(complex_num))

    # Large integer
    large_int = 10 ** 100
    print(ocl_format(large_int))

    # Bytes
    byte_data = b"This is a byte string."
    print(ocl_format(byte_data))

    # Escape characters
    escape_str = "Line1\nLine2\tTabbed"
    print(ocl_format(escape_str))


if __name__ == "__main__":
    test_ocl_format()
