from pathlib import Path

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck

from pydemo import DemoDir


@pytest.mark.parametrize("input_text, expected_error", [
    ("", ValueError),  # No directory name
    ("---\nprint('No directory name')", ValueError),  # No valid directory header
    ("[valid_dir]", ValueError),  # No separator
    ("[valid_dir]\n--- ###\n", ValueError),  # Invalid filename
])
def test_invalid_input(input_text: str, expected_error: type[Exception], tmp_path: Path):
    """Test that invalid inputs raise the appropriate exceptions."""
    with pytest.raises(expected_error):
        DemoDir(input_text.replace("valid_dir", str(tmp_path / "valid_dir")))


@given(st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_categories=('Cs',))))
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_example_content(content: str):
    """Test that any valid content is preserved in examples."""
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        input_text = f"""[{tmpdir}/prop_test_dir]
---
{content}"""
        try:
            demo_dir = DemoDir(input_text=input_text)
            assert content.strip() in demo_dir.examples[0].example_text
        except ValueError:
            pytest.skip("Invalid input for DemoDir")


def test_control_character_preservation(tmp_path: Path):
    """Test that control characters are preserved in example content."""
    content = '0\x1e0'  # Control character
    input_text = f"""[{tmp_path / "control_char_dir"}]
---
{content}"""
    demo_dir = DemoDir(input_text=input_text)
    assert content in demo_dir.examples[0].example_text
