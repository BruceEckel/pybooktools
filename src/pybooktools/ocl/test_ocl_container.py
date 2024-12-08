import tempfile
from pathlib import Path

from icecream import ic

from ocl_container_pickle import OCLContainer
from pybooktools.util import icc

ic.enable()


def test_ocl_container_write_read():
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir) / "test_ocls.json"

        container = OCLContainer()
        container("1", "Test Arg 1")
        container("2", [1, 2, 3])
        container("3", {"key": "value"})
        container("4", "contains\na line break\n    and another")
        container(
            "5",
            """This is a triple-quoted string
that spans multiple lines
    with indentation""",
        )
        container("6", OCLContainer)
        # Generator expressions cannot be pickled:
        # container("7", (x * 2 for x in range(3)))
        container("8", (1, 2, 3))  # A tuple
        container("9", {1, 2, 3})  # A set
        container("10", "")
        container("11", {1: 2, 3: 4})
        x, y = 1, 2
        container("12", f"{x = }, {y = }")
        container("13", f"{x = },\n{y = }")
        container(
            "14",
            f"""
{x = },\n{y = }
""",
        )

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
