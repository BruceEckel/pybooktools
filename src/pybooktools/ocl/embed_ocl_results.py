#: embed_ocl_results.py
import re


def embed_ocl_results(with_ocls: str) -> str:
    """
    Converts lines containing `_on = ocl_format(arg)` to `{_on}` format and leaves all other Python code as is.

    Args:
        with_ocls (str): The Python source code containing `_on = ocl_format(...)` lines.

    Returns:
        str: The modified Python source code with embedded OCL results.
    """
    # Regular expression to match `_on = ocl_format(...)` lines
    pattern = r"^(_o\d+)\s*=\s*ocl_format\((.+)\)"

    def replacer(match: re.Match) -> str:
        variable = match.group(1)
        return f"{{{variable}}}"

    # Apply the transformation
    return re.sub(pattern, replacer, with_ocls, flags=re.MULTILINE)


def test_embed_ocl_results():
    sample_code = """
_o1 = ocl_format(1)
_o2 = ocl_format("foo")
_o3 = ocl_format("A really long line that just keeps going am I finished yet? Yes!")
_o4 = ocl_format({1: 2, 3: 4})
_o5 = ocl_format({"a", "b", "c"})
_o6 = ocl_format(3.14159)
_o7 = ocl_format(f"The value of pi is {a_6}. Of course that has been rounded off")
_o8 = ocl_format(balance)
_o9 = ocl_format(withdraw(balance, 30.0))
"""
    print(embed_ocl_results(sample_code))


if __name__ == "__main__":
    test_embed_ocl_results()
