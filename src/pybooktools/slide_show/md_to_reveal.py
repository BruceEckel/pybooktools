#: md_to_reveal.py
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator


@dataclass
class SlideContent:
    bullets: list[str] | None = None
    code_block: str | None = None


def parse_markdown(markdown: str) -> Iterator[SlideContent]:
    bullets: list[str] = []
    in_code_block = False
    code_lines: list[str] = []

    for line in markdown.splitlines():
        match line:
            case line if line.startswith("```"):
                if in_code_block:
                    yield SlideContent(code_block="\n".join(code_lines))
                    code_lines.clear()
                    in_code_block = False
                else:
                    if bullets:
                        yield SlideContent(bullets=bullets.copy())
                        bullets.clear()
                    in_code_block = True
            case line if in_code_block:
                code_lines.append(line)
            case line if line.startswith("#"):
                clean = line.lstrip("#").strip()
                if clean:
                    if bullets:
                        yield SlideContent(bullets=bullets.copy())
                        bullets.clear()
                    bullets.append(clean)
            case _:
                pass

    if bullets:
        yield SlideContent(bullets=bullets.copy())


def generate_reveal_html(slides: Iterator[SlideContent]) -> str:
    slide_sections = []
    for slide in slides:
        match slide:
            case SlideContent(bullets=bullets) if bullets:
                bullets_html = "\n".join(f"<li>{b}</li>" for b in bullets)
                slide_sections.append(f"""
<section>
  <h2>Topics</h2>
  <ul>
    {bullets_html}
  </ul>
</section>""")
            case SlideContent(code_block=code) if code:
                escaped_code = (code
                                .replace("&", "&amp;")
                                .replace("<", "&lt;")
                                .replace(">", "&gt;")
                                )
                slide_sections.append(f"""
<section>
  <pre><code class="language-python">{escaped_code}</code></pre>
</section>""")
    slides_html = "\n".join(slide_sections)

    return f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Presentation</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@4.6.2/dist/reveal.css">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@4.6.2/dist/theme/black.css">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/highlight.js@11.8.0/styles/github-dark.css">
  <style>
    body {{ background: #111; color: #eee; }}
    h2 {{ font-size: 3rem; }}
    ul {{ font-size: 2rem; }}
    pre {{ background: #222; padding: 1rem; border-radius: 1rem; font-size: 1.8rem; overflow: auto; max-height: 80vh; }}
    code {{ font-family: 'Fira Code', monospace; }}
  </style>
</head>
<body>
  <div class="reveal">
    <div class="slides">
      {slides_html}
    </div>
  </div>
  <script src="https://cdn.jsdelivr.net/npm/reveal.js@4.6.2/dist/reveal.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/highlight.js@11.8.0/lib/highlight.min.js"></script>
  <script>
    Reveal.initialize({{ hash: true }});
    hljs.highlightAll();
  </script>
</body>
</html>"""


def create_presentation(markdown_path: Path, output_path: Path) -> None:
    markdown = markdown_path.read_text(encoding="utf-8")
    slides = parse_markdown(markdown)
    html = generate_reveal_html(slides)
    output_path.write_text(html, encoding="utf-8")


def main() -> None:
    import sys

    if len(sys.argv) != 3:
        print("Usage: python md_to_reveal.py input.md output.html")
        sys.exit(1)

    input_md = Path(sys.argv[1])
    output_html = Path(sys.argv[2])
    create_presentation(input_md, output_html)


if __name__ == "__main__":
    main()
