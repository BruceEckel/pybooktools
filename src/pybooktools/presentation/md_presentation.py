"""
md_presentation.py

Creates an interactive browser presentation from a Markdown file containing
headers and fenced code blocks. The presentation displays:
- Markdown headers and subheads as leveled bullet points on slides
- Code blocks as syntax-highlighted examples on their own slides

Features:
- Right/left arrow keys to navigate slides
- 'b' key to toggle background color (dark/light)
- '=' key to increase font size
- '-' key to decrease font size
- 'q' key to quit
- Mouse wheel to scroll within code examples
- Code reformatting using Ruff when font size changes

Usage:
    python md_presentation.py path/to/markdown_file.md
"""

import argparse
import http.server
import json
import socketserver
import threading
import time
import uuid
import webbrowser
from pathlib import Path
from subprocess import run, PIPE
from typing import Dict, List, NamedTuple
from urllib.parse import urlparse, parse_qs

from markdown_it import MarkdownIt

PORT = 8765


class Slide(NamedTuple):
    """Represents a slide in the presentation."""
    type: str  # "header" or "code"
    content: str  # HTML content for headers, raw code for code blocks
    language: str = ""  # Only for code slides


def extract_slides(md_text: str) -> List[Slide]:
    """
    Extracts slides from markdown text.

    Creates slides following these rules:
    1. Headers and subheaders are collected until a code block is encountered
    2. The collected headers form one slide
    3. Each code block forms its own slide
    4. Process repeats for subsequent headers and code blocks
    """
    md = MarkdownIt()
    tokens = md.parse(md_text)

    slides: List[Slide] = []
    current_headers: List[str] = []

    for token in tokens:
        if token.type == "heading_open":
            level = int(token.tag[1])  # h1 -> 1, h2 -> 2, etc.
            content_token = tokens[tokens.index(token) + 1]
            header_text = content_token.content

            # Add bullet point with appropriate indentation
            indent = "  " * (level - 1)
            current_headers.append(f"{indent}• {header_text}")

        elif token.type == "fence":
            # First, if we have collected headers, create a header slide
            if current_headers:
                header_content = "<br>".join(current_headers)
                slides.append(Slide(type="header", content=header_content))
                current_headers = []

            # Then create a code slide
            slides.append(Slide(
                type="code",
                content=token.content,
                language=token.info.strip() or "plaintext"
            ))

    # Don't forget any remaining headers
    if current_headers:
        header_content = "<br>".join(current_headers)
        slides.append(Slide(type="header", content=header_content))

    return slides


class PresentationHandler(http.server.BaseHTTPRequestHandler):
    """Handles HTTP requests for the presentation server."""
    _slides: List[Slide]
    _presentation_dir: Path

    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == "/":
            self._serve_html()
        elif parsed.path == "/format":
            self._serve_formatted_code(parse_qs(parsed.query))
        else:
            self.send_error(404, "Not Found")

    def _serve_html(self):
        """Serves the main HTML page with the presentation."""
        js_slides = json.dumps([
            {"type": slide.type, "content": slide.content, "language": slide.language}
            for slide in self._slides
        ])

        html = generate_html(js_slides)
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    def _serve_formatted_code(self, qs: Dict[str, List[str]]) -> None:
        """Formats Python code using Ruff and serves the result."""
        try:
            index = int(qs.get("index", [0])[0])
            width = int(qs.get("width", [88])[0])

            slide = self._slides[index]
            if slide.type != "code" or slide.language != "python":
                raise ValueError("Only Python code is supported for formatting")

            result = run(
                ["ruff", "format", "--line-length", str(width), "-"],
                input=slide.content,
                stdout=PIPE,
                stderr=PIPE,
                encoding="utf-8"
            )
            formatted = result.stdout if result.returncode == 0 else slide.content
        except Exception as e:
            formatted = f"// Formatting failed: {str(e)}"

        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(formatted.encode("utf-8"))

    def log_message(self, *args):
        """Silence log messages."""
        pass


class PresentationServer(socketserver.TCPServer):
    """Server for the presentation."""
    allow_reuse_address = True

    def __init__(self, slides: List[Slide], presentation_dir: Path):
        handler = lambda *args, **kwargs: PresentationHandler(*args, **kwargs)
        PresentationHandler._slides = slides
        PresentationHandler._presentation_dir = presentation_dir
        super().__init__(("localhost", PORT), handler)


def generate_html(js_slides: str) -> str:
    """Generates the HTML for the presentation."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>Markdown Presentation</title>
  <link href="https://fonts.googleapis.com/css2?family=Fira+Code&family=Roboto:wght@300;400;700&display=swap" rel="stylesheet">
  <link id="hljs-theme" rel="stylesheet"
        href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.8.0/styles/atom-one-dark.min.css" />
  <style>
    html, body {{
      margin: 0;
      height: 100%;
      background: #111;
      color: #eee;
      font-family: 'Roboto', sans-serif;
      display: flex;
      align-items: flex-start;
      justify-content: flex-start;
      padding: 2rem;
      overflow: auto;
      transition: background 0.3s, color 0.3s;
      scrollbar-width: none;
      -ms-overflow-style: none;
    }}
    body::-webkit-scrollbar {{ display: none; }}
    body.light {{ background: #fdfdfd; color: #000; }}

    .slide {{
      display: none;
      width: 100%;
    }}
    .slide.active {{
      display: block;
    }}

    .header-slide {{
      font-size: 2rem;
      line-height: 1.5;
    }}

    pre {{
      font-family: 'Fira Code', monospace;
      font-size: 2rem;
      line-height: 1.5;
      white-space: pre-wrap;
      overflow-wrap: break-word;
      margin: 0;
      padding-left: 2rem;
      text-align: left;
    }}
    pre.hljs {{
      background: transparent !important;
    }}

    .controls {{
      position: fixed;
      bottom: 10px;
      right: 10px;
      background: rgba(0, 0, 0, 0.5);
      color: white;
      padding: 5px 10px;
      border-radius: 5px;
      font-size: 0.8rem;
      opacity: 0.7;
    }}
    .controls.light {{
      background: rgba(200, 200, 200, 0.5);
      color: black;
    }}
  </style>
</head>
<body>
  <div id="slides-container"></div>
  <div class="controls">
    ← → Navigate | b Toggle theme | = - Font size | q Quit
  </div>

  <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.8.0/highlight.min.js"></script>
  <script>
    const slides = {js_slides};
    let currentIndex = 0;
    let fontSize = 2;

    const container = document.getElementById("slides-container");
    const controls = document.querySelector(".controls");

    // Create all slides
    slides.forEach((slide, index) => {{
      const slideDiv = document.createElement("div");
      slideDiv.className = `slide ${{index === 0 ? "active" : ""}}`;
      slideDiv.dataset.index = index;

      if (slide.type === "header") {{
        slideDiv.className += " header-slide";
        slideDiv.innerHTML = slide.content;
      }} else if (slide.type === "code") {{
        const pre = document.createElement("pre");
        const code = document.createElement("code");
        code.className = `hljs ${{slide.language}}`;
        code.textContent = slide.content;
        pre.appendChild(code);
        slideDiv.appendChild(pre);
      }}

      container.appendChild(slideDiv);
    }});

    // Initialize highlighting
    document.querySelectorAll('pre code').forEach(block => {{
      hljs.highlightElement(block);
    }});

    async function showSlide(index, forceRuff = false) {{
      // Hide current slide
      document.querySelector(".slide.active").classList.remove("active");

      // Show new slide
      const newSlide = document.querySelector(`.slide[data-index="${{index}}"]`);
      newSlide.classList.add("active");

      // Update current index
      currentIndex = index;

      // If it's a code slide and Python, maybe reformat
      const slide = slides[index];
      if (slide.type === "code" && slide.language === "python" && forceRuff) {{
        const pre = newSlide.querySelector("pre");
        const code = pre.querySelector("code");

        // Calculate width based on font size
        const width = estimateCharWidth();

        // Request formatted code
        const res = await fetch(`/format?index=${{index}}&width=${{width}}`);
        if (res.ok) {{
          const formatted = await res.text();
          code.textContent = formatted;
          hljs.highlightElement(code);
        }}
      }}

      // Reset scroll position
      document.body.scrollTop = 0;
      document.documentElement.scrollTop = 0;

      // Update font size
      updateFontSize();
    }}

    function updateFontSize() {{
      document.querySelectorAll('.header-slide').forEach(el => {{
        el.style.fontSize = fontSize + 'rem';
      }});
      document.querySelectorAll('pre').forEach(el => {{
        el.style.fontSize = fontSize + 'rem';
      }});
    }}

    function estimateCharWidth() {{
      const span = document.createElement('span');
      span.textContent = 'M'.repeat(100);
      span.style.fontFamily = 'Fira Code';
      span.style.fontSize = fontSize + 'rem';
      span.style.visibility = 'hidden';
      document.body.appendChild(span);
      const width = span.getBoundingClientRect().width;
      document.body.removeChild(span);
      return Math.floor(window.innerWidth / (width / 100));
    }}

    document.addEventListener('keydown', async e => {{
      if (e.key === 'ArrowRight') {{
        if (currentIndex < slides.length - 1) {{
          await showSlide(currentIndex + 1, true);
        }}
      }} else if (e.key === 'ArrowLeft') {{
        if (currentIndex > 0) {{
          await showSlide(currentIndex - 1, true);
        }}
      }} else if (e.key === '=' || e.key === '+') {{
        fontSize = Math.min(fontSize + 0.2, 6);
        updateFontSize();

        // If it's a code slide, reformat
        const slide = slides[currentIndex];
        if (slide.type === "code" && slide.language === "python") {{
          // Force Ruff formatting
          const width = estimateCharWidth();
          const res = await fetch(`/format?index=${{currentIndex}}&width=${{width}}`);
          if (res.ok) {{
            const formatted = await res.text();
            const code = document.querySelector(".slide.active pre code");
            code.textContent = formatted;
            hljs.highlightElement(code);
          }}
        }}
      }} else if (e.key === '-') {{
        fontSize = Math.max(fontSize - 0.2, 0.5);
        updateFontSize();

        // If it's a code slide, reformat
        const slide = slides[currentIndex];
        if (slide.type === "code" && slide.language === "python") {{
          // Force Ruff formatting
          const width = estimateCharWidth();
          const res = await fetch(`/format?index=${{currentIndex}}&width=${{width}}`);
          if (res.ok) {{
            const formatted = await res.text();
            const code = document.querySelector(".slide.active pre code");
            code.textContent = formatted;
            hljs.highlightElement(code);
          }}
        }}
      }} else if (e.key.toLowerCase() === 'b') {{
        document.body.classList.toggle('light');
        controls.classList.toggle('light');

        // Toggle highlight.js theme
        const theme = document.getElementById('hljs-theme');
        theme.href = document.body.classList.contains('light')
          ? 'https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.8.0/styles/github.min.css'
          : 'https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.8.0/styles/atom-one-dark.min.css';
      }} else if (e.key.toLowerCase() === 'q') {{
        window.close();
      }}
    }});
  </script>
</body>
</html>
"""


def create_presentation_dir(md_path: Path) -> Path:
    """
    Creates a .presentation directory in the same directory as the markdown file.
    Returns the path to the directory.
    """
    presentation_dir = md_path.parent / ".presentation"
    presentation_dir.mkdir(exist_ok=True)

    # Create a unique subdirectory for this run
    run_id = time.strftime("%Y%m%d_%H%M%S") + "_" + str(uuid.uuid4())[:8]
    run_dir = presentation_dir / run_id
    run_dir.mkdir(exist_ok=True)

    return run_dir


def main() -> None:
    """Main entry point for the presentation tool."""
    parser = argparse.ArgumentParser(
        description="Create an interactive browser presentation from a Markdown file"
    )
    parser.add_argument("markdown_file", type=Path, help="Path to the Markdown file")
    args = parser.parse_args()

    md_path = args.markdown_file
    if not md_path.exists():
        print(f"Error: File not found: {md_path}")
        return

    # Create presentation directory
    presentation_dir = create_presentation_dir(md_path)

    # Extract slides from markdown
    md_text = md_path.read_text(encoding="utf-8")
    slides = extract_slides(md_text)

    if not slides:
        print("No slides found in the Markdown file.")
        return

    # Start the server
    with PresentationServer(slides, presentation_dir) as server:
        thread = threading.Thread(target=server.serve_forever)
        thread.daemon = True
        thread.start()

        # Open browser
        webbrowser.open(f"http://localhost:{PORT}")
        print(f"Presentation started at http://localhost:{PORT}")
        print("Press Ctrl+C to quit.")

        try:
            thread.join()
        except KeyboardInterrupt:
            print("\nShutting down...")
            server.shutdown()


if __name__ == "__main__":
    main()
