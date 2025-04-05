import re
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import List, Pattern, Set

from .fenced_blocks import fenced_blocks

# Default pattern to match a slug line:
default_slug_line_pattern: Pattern[str] = re.compile(r"^\s*(?:#|//)\s*(\S+\.[a-zA-Z0-9_]+)")


@dataclass
class Example:
    """
    An extracted code example from a markdown file.

    Attributes:
        filename: The filename as extracted from the slug line (e.g. "# example_1.py" or "// DefaultValues.java").
        content: The code content of the example (excluding the slug line).
        code_dir: The directory where the example will be written.
        fence_tag: The fence tag of the code block (e.g. "python", "java").
    """
    filename: str
    content: str
    code_dir: Path
    fence_tag: str

    def __str__(self) -> str:
        full_path = " " + str(self.code_dir / self.filename) + " "
        return f"""---{full_path.center(70, "-")}---
{self.content.strip()}"""


def examples_with_sluglines(
    markdown_file: Path,
    code_repo: Path,
    slug_pattern: Pattern[str] = default_slug_line_pattern,
    fence_tags: Set[str] | None = None
) -> List[Example]:
    target_dir_name = markdown_file.stem.lower().replace(" ", "_")
    markdown_text = markdown_file.read_text(encoding="utf-8")
    examples: List[Example] = []

    for block in fenced_blocks(markdown_text):
        if fence_tags is not None and block.fence_tag not in fence_tags:
            continue

        lines = block.content.splitlines()
        if not lines:
            continue

        match = slug_pattern.match(lines[0])
        if match:
            filename = match.group(1)
            parts = filename.split('/')
            code_dir = code_repo
            if '/' in filename:
                for part in parts[:-1]:
                    code_dir = code_dir / part
                code_dir.mkdir(parents=True, exist_ok=True)
            else:
                code_dir = code_dir / target_dir_name

            content = "\n".join(lines).rstrip() + "\n"
            examples.append(Example(filename=parts[-1], content=content, code_dir=code_dir, fence_tag=block.fence_tag))

    return examples


def examples_without_sluglines(markdown_file: Path) -> List[str]:
    markdown_text = markdown_file.read_text(encoding="utf-8")
    return [
        block.content
        for block in fenced_blocks(markdown_text)
        if block.content.splitlines() and not default_slug_line_pattern.match(block.content.splitlines()[0])
    ]


def examples_without_fence_tags(markdown_file: Path) -> List[str]:
    markdown_text = markdown_file.read_text(encoding="utf-8")
    return [block.content for block in fenced_blocks(markdown_text) if not block.fence_tag]


def write_examples(examples: List[Example]) -> None:
    for example in examples:
        example.code_dir.mkdir(parents=True, exist_ok=True)
        dunder_init = example.code_dir / "__init__.py"
        if not dunder_init.exists():
            dunder_init.write_text("# __init__.py\n", encoding="utf-8")
            print(f"{dunder_init}")
        file_path = example.code_dir / example.filename
        file_path.write_text(example.content, encoding="utf-8")
        print(f"{file_path}")


def test_examples_extraction():
    md_content = """
Some text

```python
# hello.py
print("Hello World")
```

```java
// main.java
System.out.println("Hello");
```

```text
// ignore.txt
This is not code.
```
"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        md_file = Path(tmp_dir) / "Example Doc.md"
        md_file.write_text(md_content, encoding="utf-8")
        code_repo = Path(tmp_dir) / "repo"
        code_repo.mkdir()

        examples = examples_with_sluglines(md_file, code_repo)

        assert len(examples) == 3
        assert {e.filename for e in examples} == {"hello.py", "main.java", "ignore.txt"}
        assert {e.fence_tag for e in examples} == {"python", "java", "text"}


def test_fence_tag_filtering():
    md_content = """
```python
# a.py
print("A")
```
```bash
# b.sh
echo "B"
```
"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        md_file = Path(tmp_dir) / "Filter.md"
        md_file.write_text(md_content, encoding="utf-8")
        code_repo = Path(tmp_dir) / "repo"
        code_repo.mkdir()

        examples = examples_with_sluglines(md_file, code_repo, fence_tags={"python"})

        assert len(examples) == 1
        assert examples[0].filename == "a.py"
        assert examples[0].fence_tag == "python"


def test_examples_without_sluglines():
    md_content = """
```python
# good.py
print("OK")
```

```python
print("No slug line")
```
"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        md_file = Path(tmp_dir) / "NoSlug.md"
        md_file.write_text(md_content, encoding="utf-8")

        blocks = examples_without_sluglines(md_file)
        assert len(blocks) == 1
        assert blocks[0].strip() == 'print("No slug line")'


def test_examples_without_fence_tags():
    md_content = """
```
# raw.py
print("Raw")
```

```python
# tagged.py
print("Tagged")
```
"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        md_file = Path(tmp_dir) / "NoTag.md"
        md_file.write_text(md_content, encoding="utf-8")

        blocks = examples_without_fence_tags(md_file)
        assert len(blocks) == 1
        assert blocks[0].strip().startswith("# raw.py")


if __name__ == "__main__":
    import pytest

    pytest.main([__file__])
