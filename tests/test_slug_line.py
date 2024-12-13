# test_slug_line.py
from pathlib import Path

from pybooktools.ptag.slug_line import ensure_slug_line

# -- Test --
# ensure_slug_line()
test_file_path = Path("testfile.py")


def test_ensure_slug_line_existing_correct():
    pyfile = "# testfile.py\nprint('Hello, world!')"
    result = ensure_slug_line(pyfile, test_file_path)
    assert isinstance(result, str)
    assert result == "# testfile.py\nprint('Hello, world!')"


def test_ensure_slug_line_existing_incorrect():
    pyfile = "# wrong_name.py\nprint('Hello, world!')"
    result = ensure_slug_line(pyfile, test_file_path)
    assert isinstance(result, str)
    assert result == "# testfile.py\nprint('Hello, world!')"


def test_ensure_slug_line_missing():
    pyfile = "print('Hello, world!')"
    result = ensure_slug_line(pyfile, test_file_path)
    assert isinstance(result, str)
    assert result == "# testfile.py\nprint('Hello, world!')"


def test_ensure_slug_line_empty_file():
    pyfile = ""
    result = ensure_slug_line(pyfile, test_file_path)
    assert isinstance(result, str)
    assert result == "# testfile.py\n"

# -- Test --
# main()


# def test_main_no_files_found(mocker):
#     # Mock the arguments to simulate no files provided and no recursion
#     mocker.patch(
#         "argparse.ArgumentParser.parse_args",
#         return_value=argparse.Namespace(files=None, recursive=False),
#     )
#     # Mock the Path.glob to return an empty iterator, simulating no Python files found
#     mocker.patch.object(Path, "glob", return_value=iter([]))
#     # Mock the console print function
#     mock_console = mocker.patch("pybooktools.slug_line.console.print")
#     main()
#     mock_console.assert_any_call("No Python files found")
#
#
# @pytest.mark.skip(reason="only works when started in tests directory")
# @patch("argparse.ArgumentParser.parse_args")
# @patch("pybooktools.slug_line.console.print")
# def test_main_local_files_found(mock_console, mock_args):
#     """Finds the local files in the test directory, which already have sluglines"""
#     mock_args.return_value = argparse.Namespace(files=None, recursive=False)
#     main()
#     mock_console.assert_any_call("[bold blue]Number of changes[/bold blue]: 0")
#
#
# @pytest.fixture
# def temp_file(tmp_path: Path) -> Path:
#     """A temporary file."""
#     file_path = tmp_path / "testfile.py"
#     file_path.write_text('print("Hello")')
#     return file_path
#
#
# @patch("argparse.ArgumentParser.parse_args")
# @patch("pybooktools.slug_line.console.print")
# def test_main_files_provided(mock_console, mock_args, temp_file):
#     mock_args.return_value = argparse.Namespace(
#         files=[str(temp_file)], recursive=False
#     )
#     main()
#     mock_console.assert_any_call(f"[bold blue]Number of changes[/bold blue]: 1")
#
#
# @pytest.fixture
# def temp_python_files(tmp_path: Path) -> Path:
#     """A temporary directory tree containing Python files."""
#     (tmp_path / "file1.py").write_text("print('Hello from file1')")
#     (tmp_path / "file2.py").write_text("print('Hello from file2')")
#     subdir = tmp_path / "subdir"
#     subdir.mkdir()
#     (subdir / "file3.py").write_text("print('Hello from file3')")
#     return tmp_path
#
#
# @patch("argparse.ArgumentParser.parse_args")
# @patch("pybooktools.slug_line.console.print")
# def test_main_recursive(mock_console, mock_args, temp_python_files):
#     mock_args.return_value = argparse.Namespace(files=None, recursive=True)
#     with patch.object(
#         Path, "rglob", return_value=temp_python_files.rglob("*.py")
#     ):
#         main()
#
#     processed_files = [
#         call_args[0] for call_args in mock_console.call_args_list
#     ]
#     for result in [
#         "[bold red]file1.py[/bold red]",
#         "[bold red]file2.py[/bold red]",
#         "[bold red]file3.py[/bold red]",
#         "[bold blue]Number of changes[/bold blue]: 3",
#     ]:
#         assert any(result in pf for pf in processed_files)
