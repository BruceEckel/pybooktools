import re
import tempfile
from dataclasses import dataclass
from functools import partial
from pathlib import Path
from typing import List, Pattern, Set, Callable

from pybooktools.md_examples.fenced_blocks import fenced_blocks

default_slug_line_pattern: Pattern[str] = re.compile(r"^\s*(?:#|//)\s*(\S+\.[a-zA-Z0-9_]+)")


@dataclass
class Example:
    filename: str
    content: str
    code_dir: Path
    fence_tag: str

    def __str__(self) -> str:
        full_path = " " + str(self.code_dir / self.filename) + " "
        return f"""--- {full_path.center(70, "-")} ---
{self.content.strip()}"""


def examples_with_sluglines(
    markdown_content: str,
    code_repo: Path,
    slug_pattern: Pattern[str] = default_slug_line_pattern,
    fence_tags: Set[str] | None = None
) -> List[Example]:
    examples: List[Example] = []

    for block in fenced_blocks(markdown_content):
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
                code_dir = code_dir / "markdown"

            content = "\n".join(lines).rstrip() + "\n"
            examples.append(Example(filename=parts[-1], content=content, code_dir=code_dir, fence_tag=block.fence_tag))

    return examples


python_examples: Callable[[str, Path], List[Example]] = partial(examples_with_sluglines, fence_tags={"python"})


def examples_without_sluglines(markdown_content: str) -> List[str]:
    return [
        block.raw
        for block in fenced_blocks(markdown_content)
        if block.content.splitlines() and not default_slug_line_pattern.match(block.content.splitlines()[0])
    ]


def examples_without_fence_tags(markdown_content: str) -> List[str]:
    return [block.raw for block in fenced_blocks(markdown_content) if not block.fence_tag]


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


# --------------------------- TESTS ---------------------------


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
        code_repo = Path(tmp_dir) / "repo"
        code_repo.mkdir()

        examples = examples_with_sluglines(md_content, code_repo)

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
        code_repo = Path(tmp_dir) / "repo"
        code_repo.mkdir()

        examples = examples_with_sluglines(md_content, code_repo, fence_tags={"python"})

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
    blocks = examples_without_sluglines(md_content)
    assert len(blocks) == 1
    assert "print(\"No slug line\")" in blocks[0]
    assert blocks[0].strip().startswith("```python")
    assert blocks[0].strip().endswith("```")


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
    blocks = examples_without_fence_tags(md_content)
    assert len(blocks) == 1
    assert "# raw.py" in blocks[0]
    assert blocks[0].strip().startswith("```")
    assert blocks[0].strip().endswith("```")


def test_python_examples():
    md_content = """
```python
# script1.py
print("One")
```

```java
// Script.java
System.out.println("Not Python");
```

```python
# script2.py
print("Two")
```
"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        code_repo = Path(tmp_dir) / "repo"
        code_repo.mkdir()

        examples = python_examples(md_content, code_repo)
        assert len(examples) == 2
        assert {e.filename for e in examples} == {"script1.py", "script2.py"}
        assert all(e.fence_tag == "python" for e in examples)


if __name__ == "__main__":
    import pytest

    pytest.main([__file__])
