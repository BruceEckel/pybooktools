# conftest.py
"""
Pytest fixture that creates a temporary demonstration directory structure
for testing. Automatically cleans up by deleting the created directories
when the test ends.

Usage in a test file:

    def test_demo_dir(demo_dir_factory):
        text_spec = \"\"\"[my_demo]
        ---
        print('Hello from my_demo')
        \"\"\"
        demo_dir = demo_dir_factory(text_spec)
        # Now there is a directory named `my_demo` under tmp_path with a .py file.
        assert demo_dir.dirpath.exists()
        # Cleanup is automatic when the test completes
"""

import re
from pathlib import Path

import pytest

from xperiments.pydemo.demo_dir import DemoDir


@pytest.fixture
def demo_dir_factory(tmp_path: Path):
    """
    Provides a factory function that creates DemoDir objects
    from a specification string (of the form described in demo_dir.py) but
    automatically placing the generated directory under tmp_path for isolation.

    Usage:
        def test_something(demo_dir_factory):
            spec = \"\"\"[my_demo]
            ---
            print('Some content')
            \"\"\"
            demo = demo_dir_factory(spec)
            # `demo.dirpath` is now tmp_path/my_demo
    """

    created_dirs: list[DemoDir] = []

    def _factory(input_text: str) -> DemoDir:
        """
        Inner factory function that rewrites the bracketed directory line to
        reside under tmp_path, creates the DemoDir, and returns it.
        """
        lines = input_text.strip().splitlines()
        # Find the line with [dir_name]
        start_index = next(
            (i for i, line in enumerate(lines) if re.match(r"^\[.+]$", line.strip())),
            None
        )
        if start_index is None:
            raise ValueError("Input text does not contain a valid directory name in square brackets.")

        # Extract the directory name, then replace it with a path under tmp_path
        dir_line = lines[start_index].strip(" []")
        forced_dir = tmp_path / dir_line
        lines[start_index] = f"[{forced_dir}]"

        # Create the DemoDir using the updated input text
        dd = DemoDir("\n".join(lines))
        created_dirs.append(dd)
        return dd

    yield _factory

    # Cleanup after tests
    for dd in created_dirs:
        dd.delete()
