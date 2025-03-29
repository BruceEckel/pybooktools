# test_demo_dir_factory.py
"""
Tests for the `demo_dir_factory` Pytest fixture.

Ensure the factory correctly creates and manages a temporary
demo directory structure based on a specification string. The specification is of
the form:

    [my_demo_dir]
    ---
    [Python code lines...]
    ---
    foo/bar
    [Python code lines...]

Verify that:
1. The directory and files are created where expected (under `tmp_path`).
2. Auto-generated filenames are handled properly.
3. Explicit filenames (e.g. `--- file_name.py`) are respected.
4. Cleanup occurs automatically after the test run.
"""

import pytest


def test_single_auto_named_file(demo_dir_factory):
    """
    Test creation of a single file with auto-generated filename in the top-level demo directory.
    """
    spec = """[single_auto_demo]
---
print('Auto-named file #1')
"""
    demo_dir = demo_dir_factory(spec)

    # The directory should be under tmp_path
    assert demo_dir.dirpath.name == "single_auto_demo"
    assert demo_dir.dirpath.exists(), "Directory was not created."

    # There should be exactly one .py file
    py_files = list(demo_dir.dirpath.rglob("*.py"))
    assert len(py_files) == 1, f"Expected 1 file, found {len(py_files)}."

    # Check the contents of the file
    text = py_files[0].read_text(encoding="utf-8")
    assert "print('Auto-named file #1')" in text, "File content not as expected."


def test_multiple_auto_named_files(demo_dir_factory):
    """
    Test creation of multiple files with auto-generated filenames in the top-level directory.
    """
    spec = """[multi_auto_demo]
---
print('File #1')
---
print('File #2')
---
print('File #3')
"""
    demo_dir = demo_dir_factory(spec)

    py_files = list(demo_dir.dirpath.rglob("*.py"))
    assert len(py_files) == 3, f"Expected 3 .py files, found {len(py_files)}."


def test_named_file_in_subdir(demo_dir_factory):
    """
    Test creation of an explicitly named file in a subdirectory.
    """
    spec = """[named_subdir_demo]
--- foo/bar.py
print('Inside foo/bar.py')
"""
    demo_dir = demo_dir_factory(spec)

    # The directory should be named 'named_subdir_demo'
    assert demo_dir.dirpath.name == "named_subdir_demo"
    assert demo_dir.dirpath.exists(), "Directory was not created."

    # Check that foo/bar.py exists
    bar_file = demo_dir.dirpath / "foo" / "bar.py"
    assert bar_file.exists(), "File foo/bar.py was not created as expected."

    # Read and verify contents
    text = bar_file.read_text(encoding="utf-8")
    assert "print('Inside foo/bar.py')" in text, "Contents of bar.py are incorrect."


def test_auto_named_file_in_subdir(demo_dir_factory):
    """
    Test creation of an auto-named file in a subdirectory (no explicit .py name).
    """
    spec = """[auto_subdir_demo]
--- foo
print('Inside foo, auto-named file')
"""
    demo_dir = demo_dir_factory(spec)

    # The directory should be named 'auto_subdir_demo'
    assert demo_dir.dirpath.name == "auto_subdir_demo"
    assert demo_dir.dirpath.exists(), "Directory was not created."

    # There should be exactly one .py file under foo
    py_files = list((demo_dir.dirpath / "foo").rglob("*.py"))
    assert len(py_files) == 1, f"Expected 1 .py file in foo, found {len(py_files)}."

    text = py_files[0].read_text(encoding="utf-8")
    assert "print('Inside foo, auto-named file')" in text, "Content of the auto-named file is incorrect."


def test_multiple_blocks_in_subdir(demo_dir_factory):
    """
    Test multiple blocks within the same subdirectory and confirm they create separate .py files.
    """
    spec = """[multi_block_subdir_demo]
--- foo
print('Block #1 in foo')
---
print('Block #2 also in foo')
"""
    demo_dir = demo_dir_factory(spec)

    # We expect two auto-named files, both in 'foo'
    py_files = list((demo_dir.dirpath / "foo").rglob("*.py"))
    assert len(py_files) == 2, f"Expected 2 files in foo, found {len(py_files)}."

    contents = [f.read_text(encoding="utf-8") for f in py_files]
    assert any("Block #1 in foo" in c for c in contents)
    assert any("Block #2 also in foo" in c for c in contents)


def test_error_no_dir_name(demo_dir_factory):
    """
    Test that providing a spec without [dir_name] raises a ValueError.
    """
    spec = """---
print('No directory name specified!')
"""
    with pytest.raises(ValueError) as excinfo:
        demo_dir_factory(spec)

    assert "valid directory name in square brackets" in str(excinfo.value), \
        "Expected ValueError when directory name is missing."
