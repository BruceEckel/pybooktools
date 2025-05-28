# output_formatter.py
import textwrap
from typing import Any

from pybooktools.util import config


def output_format(arg: Any, wrap: bool = True) -> list[str]:
    arg = str(arg)
    if wrap:
        lines: list[str] = textwrap.wrap(arg, width=config.LINE_LENGTH)
    else:
        lines = [arg]
    # Prepend '## ' to each line
    result = [f"## {line}".strip() for line in lines]
    return result


def test_output_format():
    # Test examples
    a_1 = 1
    a_2 = "foo"
    a_3 = "A really long line that just keeps going am I finished yet? Yes!"
    a_4 = {1: 2, 3: 4}
    a_5 = {"a", "b", "c"}
    a_6 = 3.14159
    a_7 = f"The value of pi is {a_6}. Of course that has been rounded off"

    # Basic tests
    print(output_format(a_1))
    print(output_format(a_2))
    print(output_format(a_3))
    print(output_format(a_4))
    print(output_format(a_5))
    print(output_format(a_6))
    print(output_format(a_7))

    # Empty string
    print(output_format(""))

    # Multiline string
    multiline = "This is a test of multiline wrapping.\nHere is another line to ensure we handle them."
    print(output_format(multiline))

    # Very long single word
    long_word = "supercalifragilisticexpialidocious" * 2
    print(output_format(long_word))

    # Nested structures
    nested = [{"key1": [1, 2, 3]}, {"key2": (4, 5, 6)}]
    print(output_format(nested))

    # Boolean values
    print(output_format(True))
    print(output_format(False))

    # None value
    print(output_format(None))

    # Complex number
    complex_num = 3 + 4j
    print(output_format(complex_num))

    # Large integer
    large_int = 10 ** 100
    print(output_format(large_int))

    # Bytes
    byte_data = b"This is a byte string."
    print(output_format(byte_data))

    # Escape characters
    escape_str = "Line1\nLine2\tTabbed"
    print(output_format(escape_str))


if __name__ == "__main__":
    test_output_format()
