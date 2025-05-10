# md_to_presentation.py
#!/usr/bin/env python3
"""
Convert Markdown files with fenced code blocks to interactive Reveal.js presentations.

This tool parses Markdown files, extracts headers and code blocks, and generates
an interactive browser presentation using Reveal.js.
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
import webbrowser
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, List, Optional, Tuple, Union

try:
    import ruff
except ImportError:
    print("Warning: ruff not installed. Code reformatting will not be available.")
    ruff = None


@dataclass
class SlideContent:
    """Represents the content of a single slide."""
    bullets: List[Tuple[int, str]] = None  # List of (level, text) tuples
    code_block: str = None
    language: str = None

    def __post_init__(self):
        if self.bullets is None:
            self.bullets = []


def extract_header_level(line: str) -> Tuple[int, str]:
    """Extract header level and text from a Markdown header line."""
    match = re.match(r'^(#+)\s+(.+)$', line)
    if match:
        level = len(match.group(1))
        text = match.group(2).strip()
        return level, text
    return 0, line


def parse_markdown(markdown: str) -> Iterator[SlideContent]:
    """Parse Markdown content into a sequence of slides."""
    bullets = []
    in_code_block = False
    code_lines = []
    language = None
    current_paragraph = []

    for line in markdown.splitlines():
        if line.startswith("```"):
            # Handle code blocks
            if in_code_block:
                # End of code block
                yield SlideContent(code_block="\n".join(code_lines), language=language)
                code_lines = []
                language = None
                in_code_block = False
            else:
                # Start of code block
                # First, handle any accumulated paragraph text
                if current_paragraph:
                    # Add paragraph as a bullet point
                    bullets.append((7, " ".join(current_paragraph)))
                    current_paragraph = []

                # Then yield any accumulated bullets
                if bullets:
                    yield SlideContent(bullets=bullets.copy())
                    bullets = []

                in_code_block = True
                # Extract language if specified
                lang_match = re.match(r'^```(\w+)$', line)
                if lang_match:
                    language = lang_match.group(1)
        elif in_code_block:
            # Inside code block, just collect lines
            code_lines.append(line)
        elif line.startswith("#"):
            # Handle headers
            # First, handle any accumulated paragraph text
            if current_paragraph:
                bullets.append((7, " ".join(current_paragraph)))
                current_paragraph = []

            level, text = extract_header_level(line)
            if level > 0:
                bullets.append((level, text))
        elif line.startswith("-") and line.strip() != "-":
            # Handle bullet points
            # First, handle any accumulated paragraph text
            if current_paragraph:
                bullets.append((7, " ".join(current_paragraph)))
                current_paragraph = []

            text = line.strip()[1:].strip()
            if text:
                # Treat bullet points as level 6 (lowest level header)
                bullets.append((6, text))
        elif line.strip():
            # Non-empty line that's not a header or bullet point
            # Collect as part of a paragraph
            current_paragraph.append(line.strip())
        elif current_paragraph:
            # Empty line after paragraph text
            # Add the paragraph as a bullet point
            bullets.append((7, " ".join(current_paragraph)))
            current_paragraph = []

    # Handle any remaining content
    if current_paragraph:
        bullets.append((7, " ".join(current_paragraph)))

    if bullets:
        yield SlideContent(bullets=bullets.copy())


def format_code(code: str, width: int, language: str = None) -> str:
    """Format code to fit within the specified width using ruff if available."""
    if not code.strip():
        return code

    if ruff and language and language.lower() in ('python', 'py'):
        try:
            # Create a temporary file for ruff to format
            with tempfile.NamedTemporaryFile(mode='w+', suffix='.py', delete=False) as temp:
                temp.write(code)
                temp_path = temp.name

            # Run ruff format with line length
            subprocess.run(
                ["ruff", "format", "--line-length", str(width), temp_path],
                check=True,
                capture_output=True
            )

            # Read the formatted code
            formatted_code = Path(temp_path).read_text()
            os.unlink(temp_path)
            return formatted_code
        except Exception as e:
            print(f"Warning: Failed to format code with ruff: {e}", file=sys.stderr)

    return code


def generate_reveal_html(
    slides: List[SlideContent],
    title: str = "Markdown Presentation",
    theme: str = "black",
    code_theme: str = "github-dark",
    font_size: int = 24,
    code_width: int = 80
) -> str:
    """Generate HTML for a Reveal.js presentation."""
    slide_sections = []

    for slide in slides:
        if slide.bullets:
            # Create a hierarchical bullet list based on header levels
            bullets_by_level = {}
            for level, text in slide.bullets:
                if level not in bullets_by_level:
                    bullets_by_level[level] = []
                bullets_by_level[level].append(text)

            # Generate HTML for the bullet points
            bullets_html = ""
            for level in sorted(bullets_by_level.keys()):
                indent = "  " * (level - 1)
                for text in bullets_by_level[level]:
                    bullets_html += f"{indent}<li>{text}</li>\n"

            slide_sections.append(f"""
<section>
  <h2>Topics</h2>
  <ul>
    {bullets_html}
  </ul>
</section>""")

        elif slide.code_block:
            # Format and escape the code
            formatted_code = format_code(slide.code_block, code_width, slide.language)
            escaped_code = (
                formatted_code
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
            )

            # Determine the language class for syntax highlighting
            lang_class = f"language-{slide.language}" if slide.language else "language-plaintext"

            slide_sections.append(f"""
<section>
  <pre><code class="{lang_class}">{escaped_code}</code></pre>
</section>""")

    slides_html = "\n".join(slide_sections)

    return f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>{title}</title>
  <link rel="stylesheet" href="reveal.js/dist/reveal.css">
  <link rel="stylesheet" href="reveal.js/dist/theme/{theme}.css">
  <link rel="stylesheet" href="reveal.js/plugin/highlight/monokai.css">
  <style>
    :root {{
      --base-font-size: {font_size}px;
    }}
    body {{ background: #111; color: #eee; }}
    .reveal h2 {{ font-size: calc(var(--base-font-size) * 1.5); }}
    .reveal ul {{ font-size: var(--base-font-size); }}
    .reveal pre {{ 
      background: #222; 
      padding: 1rem 1rem 0.5rem 1rem; 
      border-radius: 0.5rem; 
      font-size: var(--base-font-size); 
      overflow: auto; 
      max-height: 90vh;
      width: 100%;
      margin: 0;
      text-align: left;
    }}
    .reveal section:has(pre) {{
      padding: 0;
      margin: 0;
      height: 100%;
      display: flex;
      align-items: center;
    }}
    .reveal code {{ font-family: 'Fira Code', monospace; }}
    .reveal .slides {{ text-align: left; }}
  </style>
</head>
<body>
  <div class="reveal">
    <div class="slides">
      {slides_html}
    </div>
  </div>
  <script src="reveal.js/dist/reveal.js"></script>
  <script src="reveal.js/plugin/highlight/highlight.js"></script>
  <script>
    let baseFontSize = {font_size};
    let codeWidth = {code_width};

    // Initialize Reveal.js
    Reveal.initialize({{
      hash: true,
      controls: true,
      progress: true,
      center: false,
      plugins: [ RevealHighlight ]
    }});

    // Handle keyboard shortcuts
    document.addEventListener('keydown', function(event) {{
      if (event.key === '=') {{
        // Increase font size
        baseFontSize += 2;
        document.documentElement.style.setProperty('--base-font-size', baseFontSize + 'px');
        codeWidth = Math.max(40, Math.floor(120 * 24 / baseFontSize));
        event.preventDefault();
        reloadWithNewFontSize();
      }} else if (event.key === '-') {{
        // Decrease font size
        baseFontSize = Math.max(12, baseFontSize - 2);
        document.documentElement.style.setProperty('--base-font-size', baseFontSize + 'px');
        codeWidth = Math.max(40, Math.floor(120 * 24 / baseFontSize));
        event.preventDefault();
        reloadWithNewFontSize();
      }} else if (event.key === 'q') {{
        // Quit presentation
        window.close();
      }}
    }});

    function reloadWithNewFontSize() {{
      // Add parameters to URL to reload with new font size
      const url = new URL(window.location);
      url.searchParams.set('fontSize', baseFontSize);
      url.searchParams.set('codeWidth', codeWidth);
      window.location.href = url.toString();
    }}

    // Apply font size from URL parameters if present
    window.addEventListener('load', function() {{
      const params = new URLSearchParams(window.location.search);
      const fontSize = params.get('fontSize');
      const width = params.get('codeWidth');

      if (fontSize) {{
        baseFontSize = parseInt(fontSize);
        document.documentElement.style.setProperty('--base-font-size', baseFontSize + 'px');
      }}

      if (width) {{
        codeWidth = parseInt(width);
      }}
    }});
  </script>
</body>
</html>"""


def setup_presentation_directory(markdown_path: Path) -> Path:
    """Set up the presentation directory structure."""
    # Create .presentation directory in the same directory as the markdown file
    presentation_dir = markdown_path.parent / ".presentation"
    presentation_dir.mkdir(exist_ok=True)

    # Create a unique subdirectory for this run
    timestamp = Path(tempfile.mkdtemp(dir=presentation_dir, prefix="")).name
    output_dir = presentation_dir / timestamp
    output_dir.mkdir(exist_ok=True)

    # Create reveal.js directory and copy necessary files
    reveal_dir = output_dir / "reveal.js"
    reveal_dir.mkdir(exist_ok=True, parents=True)

    # Copy reveal.js files from node_modules if available, otherwise use CDN
    source_reveal_dir = Path(__file__).parent.parent / "slide_show" / "node_modules" / "reveal.js"

    if source_reveal_dir.exists():
        # Copy dist, plugin directories
        for subdir in ["dist", "plugin"]:
            src = source_reveal_dir / subdir
            dst = reveal_dir / subdir
            if src.exists():
                shutil.copytree(src, dst)
    else:
        # Create minimal structure for CDN fallback
        (reveal_dir / "dist").mkdir(exist_ok=True)
        (reveal_dir / "plugin").mkdir(exist_ok=True)
        (reveal_dir / "plugin" / "highlight").mkdir(exist_ok=True)

        # Create minimal JS files that will load from CDN
        cdn_reveal_js = """
// CDN fallback
document.write('<script src="https://cdn.jsdelivr.net/npm/reveal.js@4.6.2/dist/reveal.js"><\\/script>');
"""
        cdn_highlight_js = """
// CDN fallback
document.write('<script src="https://cdn.jsdelivr.net/npm/highlight.js@11.8.0/lib/highlight.min.js"><\\/script>');
const RevealHighlight = { id: 'highlight' };
"""
        (reveal_dir / "dist" / "reveal.js").write_text(cdn_reveal_js)
        (reveal_dir / "plugin" / "highlight" / "highlight.js").write_text(cdn_highlight_js)

        # Create CSS files that will load from CDN
        cdn_reveal_css = """
@import url('https://cdn.jsdelivr.net/npm/reveal.js@4.6.2/dist/reveal.css');
"""
        (reveal_dir / "dist" / "reveal.css").write_text(cdn_reveal_css)

        # Create theme directory
        (reveal_dir / "dist" / "theme").mkdir(exist_ok=True)
        for theme in ["black", "white", "league", "beige", "sky", "night", "serif", "simple", "solarized", "blood", "moon"]:
            theme_css = f"""
@import url('https://cdn.jsdelivr.net/npm/reveal.js@4.6.2/dist/theme/{theme}.css');
"""
            (reveal_dir / "dist" / "theme" / f"{theme}.css").write_text(theme_css)

        # Create highlight theme
        (reveal_dir / "plugin" / "highlight" / "monokai.css").write_text("""
@import url('https://cdn.jsdelivr.net/npm/highlight.js@11.8.0/styles/monokai.css');
""")

    return output_dir


def create_presentation(
    markdown_path: Path,
    font_size: int = 24,
    code_width: int = 80,
    theme: str = "black",
    code_theme: str = "monokai",
    open_browser: bool = True
) -> Path:
    """Create a presentation from a Markdown file."""
    # Read the markdown file
    markdown = markdown_path.read_text(encoding="utf-8")

    # Parse the markdown
    slides = list(parse_markdown(markdown))

    # Set up the presentation directory
    output_dir = setup_presentation_directory(markdown_path)

    # Generate the HTML
    title = markdown_path.stem.replace("_", " ").title()
    html = generate_reveal_html(
        slides,
        title=title,
        theme=theme,
        code_theme=code_theme,
        font_size=font_size,
        code_width=code_width
    )

    # Write the HTML to a file
    output_path = output_dir / "index.html"
    output_path.write_text(html, encoding="utf-8")

    # Open the presentation in a browser
    if open_browser:
        # Ensure we have an absolute path before converting to URI
        abs_path = output_path.resolve()
        webbrowser.open(abs_path.as_uri())

    return output_path


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Convert Markdown files with fenced code blocks to interactive Reveal.js presentations."
    )
    parser.add_argument(
        "markdown_file",
        type=str,
        help="Path to the Markdown file to convert"
    )
    parser.add_argument(
        "--font-size",
        type=int,
        default=24,
        help="Base font size for the presentation (default: 24)"
    )
    parser.add_argument(
        "--code-width",
        type=int,
        default=80,
        help="Character width for code formatting (default: 80)"
    )
    parser.add_argument(
        "--theme",
        type=str,
        default="black",
        choices=["black", "white", "league", "beige", "sky", "night", "serif", "simple", "solarized", "blood", "moon"],
        help="Reveal.js theme to use (default: black)"
    )
    parser.add_argument(
        "--code-theme",
        type=str,
        default="monokai",
        choices=["monokai", "github-dark", "github", "vs", "vs2015", "xcode", "atom-one-dark"],
        help="Code highlighting theme to use (default: monokai)"
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Don't open the presentation in a browser"
    )

    args = parser.parse_args()

    # Convert the markdown file to a presentation
    markdown_path = Path(args.markdown_file)
    if not markdown_path.exists():
        print(f"Error: File not found: {markdown_path}", file=sys.stderr)
        sys.exit(1)

    try:
        output_path = create_presentation(
            markdown_path,
            font_size=args.font_size,
            code_width=args.code_width,
            theme=args.theme,
            code_theme=args.code_theme,
            open_browser=not args.no_browser
        )
        print(f"Presentation created: {output_path}")
    except Exception as e:
        print(f"Error creating presentation: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
