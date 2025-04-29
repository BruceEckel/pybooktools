#!/usr/bin/env python3
"""
Convert a Markdown file into a Marp presentation using the Uncover theme,
interleaving bullet slides of headers with individual code-block chunked slides:

- Collect headers (#..######) into bullets until a fenced code block appears.
- When a code block begins, emit the accumulated bullets as one slide.
- Emit the fenced code block broken into fixed-size chunks, each on its own slide.
- Continue until end of file, then emit any remaining bullets.

Output is written under `.marp/`, then opened in Marp preview mode.
"""

import argparse
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

# Number of lines of code per slide to maintain uniform font size
CHUNK_SIZE = 20


@dataclass
class Slide:
    """A single slide's Markdown content."""
    content: str


@dataclass
class Config:
    """Presentation configuration."""
    input_file: Path
    output_dir: Path = Path(".marp")
    theme: str = "uncover"
    marp_cmd: str = "marp"


def generate_slides(config: Config) -> list[Slide]:
    """
    Parse the input Markdown and yield slides in order:
    1. A bullet slide of headers collected up to each code block.
    2. Slides for each chunk of a fenced code block (CHUNK_SIZE lines each).
    3. A final bullet slide if headers remain.
    """
    text = config.input_file.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    slides: list[Slide] = []
    bullets: list[str] = []
    index = 0

    while index < len(lines):
        line = lines[index]
        # Detect fenced code block start
        if match := re.match(r'^```(\w*)\s*$', line):
            # Emit bullet slide
            if bullets:
                slides.append(Slide(content="\n".join(bullets)))
                bullets.clear()

            lang = match.group(1) or ""
            code_lines: list[str] = []
            index += 1
            # Collect until closing fence
            while index < len(lines) and not lines[index].startswith("```"):
                code_lines.append(lines[index])
                index += 1
            # Chunk the code
            for start in range(0, len(code_lines), CHUNK_SIZE):
                chunk = code_lines[start: start + CHUNK_SIZE]
                fenced = f"```{lang}\n{''.join(chunk)}```"
                slides.append(Slide(content=fenced))
        # Header -> accumulate bullets
        elif header := re.match(r'^(#{1,6})\s+(.*)', line):
            level = len(header.group(1))
            text_header = header.group(2)
            indent = "  " * (level - 1)
            bullets.append(f"{indent}* {text_header}")
        index += 1

    # Final bullets
    if bullets:
        slides.append(Slide(content="\n".join(bullets)))

    return slides


def write_presentation(slides: list[Slide], config: Config) -> Path:
    """
    Write slides to a Marp markdown file with YAML front-matter.

    Disables auto-scaling for consistent code font size.
    """
    config.output_dir.mkdir(exist_ok=True)
    output_file = config.output_dir / f"{config.input_file.stem}_slides.md"
    front_matter = (
        "---\n"
        "marp: true\n"
        f"theme: {config.theme}\n"
        "paginate: true\n"
        "style: |\n"
        "  /* @auto-scaling false */\n"
        "---\n"
    )
    parts: list[str] = [front_matter]

    # First slide
    if slides:
        parts.append(slides[0].content)
        # Subsequent slides
        for slide in slides[1:]:
            parts.append("\n---\n")
            parts.append(slide.content)
        parts.append("\n")

    output_file.write_text("".join(parts), encoding="utf-8")
    return output_file


def main() -> None:
    """
    CLI entrypoint: parse args, generate slides, write file, and preview.
    """
    parser = argparse.ArgumentParser(
        description="Markdown → Marp presentation (Uncover theme, chunked slides)"
    )
    parser.add_argument(
        "markdown_file",
        type=Path,
        help="Input Markdown file path"
    )
    parser.add_argument(
        "--marp-cmd",
        type=str,
        default="marp",
        help="Marp CLI executable name or path"
    )
    args = parser.parse_args()

    config = Config(
        input_file=args.markdown_file,
        marp_cmd=args.marp_cmd
    )
    slides = generate_slides(config)
    presentation = write_presentation(slides, config)

    marp_exe = shutil.which(config.marp_cmd)
    if not marp_exe:
        print(f"Error: '{config.marp_cmd}' not found on PATH.", file=sys.stderr)
        sys.exit(1)

    try:
        subprocess.run([marp_exe, str(presentation), "--preview"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Marp CLI exited with code {e.returncode}", file=sys.stderr)
        sys.exit(e.returncode)


if __name__ == "__main__":
    main()
