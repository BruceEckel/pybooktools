import tempfile
from pathlib import Path

from icecream import ic

from pybooktools.ocl import OCLContainer
from pybooktools.util import icc


def test_ocl_container_write_read():
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir) / "test_ocls.json"

        container = OCLContainer()
        container("1", "Test Arg 1", r'print("Test Arg 1")')
        container("2", [1, 2, 3], r"""print([1, 2, 3])""")
        container("3", {"key": "value"}, r"""print({"key": "value"})""")
        container(
            "4",
            "contains\na line break\n    and another",
            r"""print("contains\na line break\n    and another")""",
        )
        container(
            "5",
            """This is a triple-quoted string
that spans multiple lines
    with indentation""",
            r'''print("""This is a triple-quoted string
that spans multiple lines
    with indentation""")''',
        )
        container("6", OCLContainer, r"""print(OCLContainer)""")
        # Generator expressions cannot be pickled:
        # container("7", (x * 2 for x in range(3)))
        container("8", (1, 2, 3), r"""print((1, 2, 3))""")
        container("9", {1, 2, 3}, r"""print({1, 2, 3})""")
        container("10", "", r"""print("")""")
        container("11", {1: 2, 3: 4}, r"""print({1: 2, 3: 4})""")
        x, y = 1, 2
        container("12", f"{x = }, {y = }", r"""print(f"{x = }, {y = }")""")
        container("13", f"{x = },\n{y = }", r"""print(f"{x = },\n{y = }")""")
        container(
            "14",
            f"""
{x = },\n{y = }
""",
            r'''print(f"""
{x = },\n{y = }
""")''',
        )
        container(
            "15",
            'Special characters: \t tab, \n newline, " quotes',
            r"""print('Special characters: \t tab, \n newline, " quotes')""",
        )
        container("16", None, r"""print(None)""")
        container("17", 42, r"""print(42)""")
        container("18", 3.14, r"""print(3.14)""")
        container("19", True, r"""print(True)""")

        # ic("OCLContainer before writing to file", container)
        container.write(temp_path)

        read_container = OCLContainer.read(temp_path)
        # ic("read_container", read_container)

        # Assert that the written and read data are equivalent
        assert len(read_container.ocls) == len(container.ocls)
        icc(list(zip(container.ocls, read_container.ocls)))

        for original, read in zip(container.ocls, read_container.ocls):
            if original.arg != read.arg:
                ic("Not equal:", original.arg, read.arg)
                return
            if original.ident != read.ident:
                ic("Not equal:", original.ident, read.ident)
                return
            if original.result != read.result:
                ic("Not equal:", original.result, read.result)
                return
            if original.output_lines != read.output_lines:
                ic("Not equal:", original.output_lines, read.output_lines)
                return


if __name__ == "__main__":
    test_ocl_container_write_read()
    print("All tests passed.")
