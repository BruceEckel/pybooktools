import tempfile
from pathlib import Path

from icecream import ic

from ocl_container import (
    OCLContainer,
)  # Assuming the classes are in ocl_container.py


def test_ocl_container_write_read():
    # Create a temporary file to act as the JSON output
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir) / "test_ocls.json"

        # Initialize an OCLContainer
        container = OCLContainer(output_json=temp_path)

        # Add some OCL entries
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
        # container("7", (x * 2 for x in range(3)))  # A generator expression
        # container("8", (1, 2, 3))  # A tuple
        # container("9", {1, 2, 3})  # A set

        # Write to the JSON file
        ic("container before writing to JSON", container)
        container.write()

        # Read back the container from the JSON file
        read_container = OCLContainer.read(temp_path)
        ic("read_container", read_container)

        # Assert that the written and read data are equivalent
        assert len(read_container.ocls) == len(container.ocls)
        ic(list(zip(container.ocls, read_container.ocls)))

        for original, read in zip(container.ocls, read_container.ocls):
            assert original.arg == read.arg
            assert original.ident == read.ident
            assert original.result == read.result
            assert original.output_lines == read.output_lines
            assert original.output == read.output


if __name__ == "__main__":
    test_ocl_container_write_read()
    print("All tests passed.")
