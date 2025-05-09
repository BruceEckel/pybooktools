# fenced_blocks.py
from pathlib import Path
from typing import Generator, NamedTuple, Optional, Literal

FenceTypes = Literal["python", "pyi", "cpp", "java", "bash", "js"]


class FencedBlock(NamedTuple):
    content: str  # Content within fences
    fence_tag: str  # Name after three backticks, if it exists
    raw: str  # Entire block including fences


def fenced_blocks(markdown: Path | str) -> Generator[FencedBlock]:
    """Produces blocks from markdown example_body that are enclosed in ``` fences.

    Accepts either a Path to a markdown file or the markdown example_body as a string.
    Each block is yielded as a FencedBlock, containing the example_body inside the fence,
    the fence tag (e.g., 'python' for ```python), and the raw fenced block text.
    """
    if isinstance(markdown, Path):
        lines = markdown.read_text(encoding="utf-8").splitlines()
    else:
        lines = markdown.splitlines()

    in_fence = False
    fence_tag = ""
    block_lines: list[str] = []
    raw_lines: list[str] = []

    for line in lines:
        stripped = line.lstrip()
        if stripped.startswith("```"):
            raw_lines.append(line)
            if in_fence:
                content = "\n".join(block_lines)
                raw = "\n".join(raw_lines)
                yield FencedBlock(content=content, fence_tag=fence_tag, raw=raw)
                in_fence = False
                fence_tag = ""
                block_lines.clear()
                raw_lines.clear()
            else:
                in_fence = True
                fence_tag = stripped[3:].strip()
        elif in_fence:
            block_lines.append(line)
            raw_lines.append(line)


def fenced_blocks_with_tags(
    markdown: Path | str,
    tags: Optional[set[FenceTypes]] = None
) -> Generator[FencedBlock]:
    """Yields only fenced blocks that have a fence tag.

    If `tag` is provided, only blocks with that exact tag are returned.
    """
    yield from (block for block in fenced_blocks(markdown)
                if block.fence_tag
                and (tags is None or block.fence_tag in tags)
                )


def test_single_block():
    md = """
```python
print("Hello")
print("Goodbye")
```
"""
    blocks = list(fenced_blocks(md))
    assert len(blocks) == 1
    assert blocks[0].fence_tag == "python"
    assert blocks[0].content == 'print("Hello")\nprint("Goodbye")'
    assert blocks[0].raw.strip().startswith("```python")
    assert blocks[0].raw.strip().endswith("```")


def test_multiple_blocks():
    md = """
```js
console.log("A")
console.log("B")
```

Some text.

```bash
echo "C"
echo "D"
```
"""
    blocks = list(fenced_blocks(md))
    assert len(blocks) == 2
    assert blocks[0].fence_tag == "js"
    assert blocks[0].content == 'console.log("A")\nconsole.log("B")'
    assert blocks[1].fence_tag == "bash"
    assert blocks[1].content == 'echo "C"\necho "D"'
    assert blocks[0].raw.strip().startswith("```js")
    assert blocks[1].raw.strip().startswith("```bash")


def test_no_fence_tag():
    md = """
```
generic block
No tag
```
"""
    blocks = list(fenced_blocks(md))
    assert len(blocks) == 1
    assert blocks[0].fence_tag == ""
    assert blocks[0].content == "generic block\nNo tag"
    assert blocks[0].raw.strip().startswith("```")
    assert blocks[0].raw.strip().endswith("```")


if __name__ == "__main__":
    import pytest

    pytest.main([__file__])
