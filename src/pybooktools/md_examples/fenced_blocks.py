# fenced_blocks.py
from typing import Generator, NamedTuple


class FencedBlock(NamedTuple):
    content: str
    fence_tag: str


def fenced_blocks(markdown_content: str) -> Generator[FencedBlock]:
    """Produces blocks from markdown content that are enclosed in ``` fences.

    Each block is yielded as a FencedBlock, containing the content inside the fence
    and the fence tag (e.g., 'python' for ```python).
    """
    in_fence = False
    fence_tag = ""
    block_lines: list[str] = []

    for line in markdown_content.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("```"):
            if in_fence:
                yield FencedBlock(content="\n".join(block_lines), fence_tag=fence_tag)
                in_fence = False
                fence_tag = ""
                block_lines.clear()
            else:
                in_fence = True
                fence_tag = stripped[3:].strip()
        elif in_fence:
            block_lines.append(line)


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


if __name__ == "__main__":
    import pytest

    pytest.main([__file__])
