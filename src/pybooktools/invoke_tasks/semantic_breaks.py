#: semantic_breaks.py
import re
from pathlib import Path


def is_code_fence(line: str) -> bool:
    return line.strip().startswith("```")


def break_paragraph_into_lines(text: str) -> str:
    """
    Break a paragraph into semantically meaningful lines.
    Sentences are separated by `. `, `! `, `? ` and similar.
    Keeps inline formatting intact.
    """
    # Match sentence-ending punctuation followed by a space
    sentence_end = re.compile(r"(?<=[.?!])\s+(?=[A-Z\"'])")
    sentences = sentence_end.split(text.strip())
    return "\n".join(sentence.strip() for sentence in sentences if sentence.strip())


def semantic_line_breaks(markdown: str) -> str:
    """
    Perform semantic line breaking on a Markdown string.
    Respects code blocks and list items.
    """
    lines = markdown.splitlines()
    output: list[str] = []

    in_code_block = False
    paragraph: list[str] = []

    def flush_paragraph():
        if paragraph:
            full_paragraph = " ".join(paragraph).strip()
            if full_paragraph:
                output.append(break_paragraph_into_lines(full_paragraph))
            paragraph.clear()

    for line in lines:
        if is_code_fence(line):
            flush_paragraph()
            output.append(line)
            in_code_block = not in_code_block
            continue

        if in_code_block:
            output.append(line)
            continue

        if not line.strip():
            flush_paragraph()
            output.append("")
        elif line.lstrip().startswith(("-", "*", "+")) or re.match(r"\d+\.", line.lstrip()):
            flush_paragraph()
            output.append(line)
        else:
            paragraph.append(line)

    flush_paragraph()
    return "\n".join(output)


def rewrite_with_semantic_breaks(path: Path) -> None:
    """
    Apply semantic line breaks to the given Markdown file.
    """
    original = path.read_text(encoding="utf-8")
    processed = semantic_line_breaks(original)
    path.write_text(processed, encoding="utf-8")
