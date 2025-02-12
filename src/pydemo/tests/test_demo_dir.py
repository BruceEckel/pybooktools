# test_demo_dir.py

import pytest

from pydemo import DemoDir, Example


@pytest.fixture
def simple_demo_input():
    """Provide a simple demo directory input for testing."""
    return """
[test_demo]
--- example_1.py
print('Hello, World!')
"""


@pytest.fixture
def complex_demo_input():
    """Provide a more complex demo directory input for testing."""
    return """
[complex_demo]
--- example_1.py
print('First file')
--- example_2.py
print('Second file')
--- example_3.py
print('Third file')
"""


# Test DemoDir class
def test_demo_dir_creation(tmp_path, simple_demo_input):
    """Test basic DemoDir creation and file writing."""
    demo = DemoDir(simple_demo_input)
    assert demo.dirpath.name == "test_demo"
    assert len(demo.examples) == 1
    assert demo.examples[0].filename == "example_1.py"


def test_demo_dir_complex_structure(complex_demo_input):
    """Test DemoDir with multiple files."""
    Example.reset_counter()  # Ensure counter is reset
    demo = DemoDir(complex_demo_input)
    assert len(demo.examples) == 3
    filenames = [example.filename for example in demo.examples]
    assert "example_1.py" in filenames
    assert "example_2.py" in filenames
    assert "example_3.py" in filenames


def test_demo_dir_from_directory(tmp_path):
    """Test creating DemoDir from existing directory."""
    # Create test files
    test_dir = tmp_path / "test_from_dir"
    test_dir.mkdir()
    Example.demo_dir_path = test_dir  # Set before creating files

    # Create files with proper sluglines
    (test_dir / "test1.py").write_text("# test1.py\nprint('test1')")
    (test_dir / "test2.py").write_text("# test2.py\nprint('test2')")

    Example.reset_counter()
    demo = DemoDir.from_directory(test_dir)
    assert len(demo.examples) == 2

    # Check that generated files exist with auto-generated names
    example_files = list(demo.dirpath.glob("*.py"))
    assert len(example_files) == 2
    assert any(f.name == "example_1.py" for f in example_files)
    assert any(f.name == "example_2.py" for f in example_files)


def test_demo_dir_invalid_input():
    """Test DemoDir creation with invalid input."""
    with pytest.raises(ValueError):
        DemoDir("Invalid input without directory name")


def test_demo_dir_delete(tmp_path, simple_demo_input):
    """Test directory deletion."""
    demo = DemoDir(simple_demo_input)
    assert demo.dirpath.exists()
    demo.delete()
    assert not demo.dirpath.exists()


# Test Example class
def test_example_filename_generation(tmp_path):
    """Test automatic filename generation."""
    Example.reset_counter()
    example = Example(tmp_path, "print('test')")
    assert example.filename == "example_1.py"

    example2 = Example(tmp_path, "print('test2')")
    assert example2.filename == "example_2.py"


def test_example_slug_line(tmp_path):
    """Test slug line handling."""
    Example.reset_counter()
    # Even with an explicit filename in the content, it should use generated filename
    example = Example(tmp_path, """# test1.py
print('test')""")
    assert example.lines[0] == "# example_1.py"

    # Test with no initial slug line
    example2 = Example(tmp_path, "print('test')")
    assert example2.lines[0] == "# example_2.py"


def test_example_write_to_disk(tmp_path):
    """Test writing example to disk."""
    Example.reset_counter()
    Example.demo_dir_path = tmp_path
    example = Example(tmp_path, "print('test')")
    example.write_to_disk()
    assert example.file_path.exists()
    content = example.file_path.read_text()
    assert content.strip() == f"# {example.filename}\nprint('test')"


def test_example_repr_and_str(tmp_path):
    """Test string representations."""
    Example.reset_counter()
    example = Example(tmp_path, """# test.py
print('test')""")
    assert repr(example).startswith("---")
    assert str(example).endswith("print('test')")


# Integration tests
def test_flat_structure_workflow(tmp_path):
    """Test the workflow with flat file structure."""
    Example.reset_counter()
    input_text = """
[integration_test]
--- example_1.py
print('Main file')
--- example_2.py
def helper():
    return 'Helper function'
"""

    demo = DemoDir(input_text)
    assert demo.dirpath.exists()
    assert len(demo.examples) == 2

    # Check for generated filenames
    assert (demo.dirpath / "example_1.py").exists()
    assert (demo.dirpath / "example_2.py").exists()

    demo.delete()
    assert not demo.dirpath.exists()
