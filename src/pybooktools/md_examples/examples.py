# examples.py
import re
import tempfile
from dataclasses import dataclass, field
from functools import partial
from pathlib import Path
from typing import List, Pattern, Set, Callable, Optional

import pytest

from .fenced_blocks import fenced_blocks_with_tags, FenceTypes, fenced_blocks

default_slug_line_pattern: Pattern[str] = re.compile(  # TODO: unify
    r"^\s*(?:#|//)\s*(\S+\.[a-zA-Z0-9_]+)"
)


@dataclass
class Example:
    slug_filename: str
    example_body: str
    parent_code_dir: Path  # Parent directory where example will be written
    fence_tag: str  # Name after three backticks, if it exists
    md_source_path: Optional[Path] = None  # Markdown file where example came from
    destination_path: Path = field(init=False)  # Full path where example is written

    def __post_init__(self):
        if '/' in self.slug_filename:
            self.destination_path = self.parent_code_dir / self.slug_filename
        else:
            chapter_path = self.md_source_path.stem.replace(" ", "_").lower() if self.md_source_path else ""
            self.destination_path = self.parent_code_dir / chapter_path / self.slug_filename

    def show(self) -> None:
        from dataclasses import fields
        from rich.console import Console
        from rich.panel import Panel
        from rich.text import Text
        from rich.syntax import Syntax
        import sys
        console = Console(
            file=sys.__stdout__,  # force real terminal stdout
            force_terminal=True,
            color_system="truecolor",
        )
        body = Text()
        syntax: Syntax | None = None

        for f in fields(self):  # type: ignore
            if f.name == "example_body":
                syntax = Syntax(self.example_body.strip(), "python", theme="monokai", line_numbers=False)
                continue
            name = Text(f.name, style="bold cyan")
            value = Text(repr(getattr(self, f.name)), style="green")
            body.append_text(name)
            body.append(": ")
            body.append_text(value)
            body.append("\n")

        if syntax:
            syntax_panel = Panel(syntax, title=str(self.destination_path), border_style="dim")
            from rich.console import Group
            content = Group(body, syntax_panel)
        else:
            content = body

        panel = Panel(content, title=f"[bold magenta]{self.destination_path.resolve()}[/]", border_style="blue")
        console.print(panel)

    def __str__(self) -> str:
        return (
            f" {self.destination_path.name} ".center(70, "-")
            + "\n"
            + self.example_body.strip()
        )

    def write(self, verbose: bool = False):
        parent = self.destination_path.parent
        parent.mkdir(parents=True, exist_ok=True)
        init_file = parent / "__init__.py"
        if not init_file.exists():
            init_file.write_text("# __init__.py\n", encoding="utf-8")
            print(f"{init_file}")
        print(f"{self.destination_path}")
        self.destination_path.write_text(self.example_body, encoding="utf-8")
        if verbose:
            self.show()


def examples_with_sluglines(
    markdown_source: Path,
    code_repo_root: Path,
    slug_pattern: Pattern[str] = default_slug_line_pattern,
    fence_tags: Optional[Set[FenceTypes]] = None,
) -> List[Example]:
    source_path = markdown_source.resolve()
    markdown_content = markdown_source.read_text(encoding="utf-8")

    return [
        Example(
            slug_filename=match.group(1),
            example_body="\n".join(block.content.splitlines()).rstrip() + "\n",
            parent_code_dir=code_repo_root,
            fence_tag=block.fence_tag,
            md_source_path=source_path,
        )
        for block in fenced_blocks_with_tags(markdown_content, fence_tags)
        if (fence_tags is None or block.fence_tag in fence_tags)
        if (lines := block.content.splitlines())
        if (match := slug_pattern.match(lines[0]))
    ]


python_examples: Callable[[str, Path], List[Example]] = partial(
    examples_with_sluglines, fence_tags={"python"}
)


def examples_without_sluglines(markdown_content: str, fence_tags: Optional[Set[FenceTypes]] = None, ) -> List[str]:
    return [
        example.raw
        for example in fenced_blocks_with_tags(markdown_content, fence_tags)
        if (lines := example.content.splitlines()) and not default_slug_line_pattern.match(lines[0])
    ]


def examples_without_a_fence_tag(markdown_content: str) -> List[str]:
    return [
        example.raw for example in fenced_blocks(markdown_content) if not example.fence_tag
    ]


def write_examples(examples: List[Example], verbose=False) -> None:
    for example in examples:
        example.write(verbose)


# --------------------------- TESTS ---------------------------


def _write_and_parse(
    md: str, tmp_dir: Path, tag_filter: Optional[Set[str]] = None
) -> List[Example]:
    code_repo = tmp_dir / "example_repo"
    code_repo.mkdir()
    md_file = tmp_dir / "example.md"
    md_file.write_text(md, encoding="utf-8")
    return examples_with_sluglines(md_file, code_repo, fence_tags=tag_filter)


def test_examples_extraction():
    md = """
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
    with tempfile.TemporaryDirectory() as tmp:
        examples = _write_and_parse(md, Path(tmp))
        assert len(examples) == 3
        assert {e.slug_filename for e in examples} == {
            "hello.py",
            "main.java",
            "ignore.txt",
        }
        assert {e.fence_tag for e in examples} == {"python", "java", "text"}


def test_fence_tag_filtering():
    md = """
```python
# a.py
print("A")
```
```bash
# b.sh
echo "B"
```
"""
    with tempfile.TemporaryDirectory() as tmp:
        examples = _write_and_parse(md, Path(tmp), tag_filter={"python"})
        assert len(examples) == 1
        assert examples[0].slug_filename == "a.py"


def test_python_examples():
    md = """
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
    with tempfile.TemporaryDirectory() as tmp:
        examples = _write_and_parse(md, Path(tmp), tag_filter={"python"})
        assert len(examples) == 2
        assert {e.slug_filename for e in examples} == {"script1.py", "script2.py"}
        assert all(e.fence_tag == "python" for e in examples)


def test_nested_paths_in_sluglines():
    md = """
```python
# examples/nested/test.py
print("Nested")
```
"""
    with tempfile.TemporaryDirectory() as tmp:
        examples = _write_and_parse(md, Path(tmp))
        assert len(examples) == 1
        assert examples[0].slug_filename == "examples/nested/test.py"
        assert "nested" in str(examples[0].destination_path)


def test_slugline_match_pattern_respects_comment_markers():
    md = """
```python
// correct.java
System.out.println("Hi");
```
```python
# also_correct.py
print("Hi")
```
"""
    with tempfile.TemporaryDirectory() as tmp:
        examples = _write_and_parse(md, Path(tmp))
        assert {e.slug_filename for e in examples} == {
            "correct.java",
            "also_correct.py",
        }


def test_ignores_blocks_with_no_lines():
    md = """
```python
```
```python
# valid.py
print("Good")
```
"""
    with tempfile.TemporaryDirectory() as tmp:
        examples = _write_and_parse(md, Path(tmp))
        assert len(examples) == 1
        assert examples[0].slug_filename == "valid.py"


def test_ignore_unmatched_tags():
    md = """
```csharp
// file.cs
Console.WriteLine("Hello");
```
```python
# script.py
print("hi")
```
"""
    with tempfile.TemporaryDirectory() as tmp:
        examples = _write_and_parse(md, Path(tmp), tag_filter={"python"})
        assert len(examples) == 1
        assert examples[0].slug_filename == "script.py"


def test_examples_without_sluglines():
    md = """
```python
# good.py
print("OK")
```
```python
print("No slug line")
```
"""
    blocks = examples_without_sluglines(md)
    assert len(blocks) == 1
    assert 'print("No slug line")' in blocks[0]
    assert blocks[0].strip().startswith("```python")
    assert blocks[0].strip().endswith("```")


def test_examples_without_fence_tags():
    md = """
```
# raw.py
print("Raw")
```
```python
# tagged.py
print("Tagged")
```
"""
    blocks = examples_without_a_fence_tag(md)
    assert len(blocks) == 1
    assert "# raw.py" in blocks[0]
    assert blocks[0].strip().startswith("```")
    assert blocks[0].strip().endswith("```")


if __name__ == "__main__":
    pytest.main([__file__])
