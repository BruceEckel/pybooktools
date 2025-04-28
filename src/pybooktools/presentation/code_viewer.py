"""
presentation.py

Launches an in-memory fullscreen HTML viewer for fenced code blocks
from a Markdown file. Uses arrow keys to navigate examples,
B to toggle background color, and syntax highlighting via highlight.js.

No files are written to disk; everything is served from memory.

Usage:
    python presentation.py path/to/examples.md
"""

import argparse
import http.server
import socketserver
import threading
import webbrowser
from pathlib import Path

from markdown_it import MarkdownIt

PORT = 8765


def extract_code_blocks(md_text: str) -> list[tuple[str, str]]:
    """Extracts (language, code) pairs from fenced code blocks."""
    md = MarkdownIt()
    tokens = md.parse(md_text)
    return [
        (token.info.strip(), token.content)
        for token in tokens
        if token.type == "fence"
    ]


def generate_html(code_blocks: list[tuple[str, str]]) -> str:
    import json

    js_blocks = json.dumps([
        {"lang": lang or "plaintext", "code": code}
        for lang, code in code_blocks
    ])

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>Code Viewer</title>
  <link href="https://fonts.googleapis.com/css2?family=Fira+Code&display=swap" rel="stylesheet">
  <link id="hljs-theme" rel="stylesheet"
        href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.8.0/styles/atom-one-dark.min.css" />
  <style>
    html, body {{
      margin: 0;
      height: 100%;
      background: #111;
      color: #eee;
      font-family: 'Fira Code', monospace;
      display: flex;
      align-items: flex-start;
      justify-content: flex-start;
      padding: 2rem;
      overflow: auto;
      transition: background 0.3s, color 0.3s;
      scrollbar-width: none;           /* Firefox */
      -ms-overflow-style: none;        /* IE 10+ */
    }}
    body::-webkit-scrollbar {{
      display: none;                   /* Chrome, Safari, Edge */
    }}
    body.light {{
      background: #fdfdfd;
      color: #000;
    }}
    pre {{
      font-size: 2rem;
      line-height: 1.5;
      white-space: pre-wrap;
      overflow-wrap: break-word;
      margin: 0;
    }}
    pre.hljs {{
      background: transparent !important;
    }}
  </style>
</head>
<body>
  <pre><code id="code" class="hljs"></code></pre>

  <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.8.0/highlight.min.js"></script>
  <script>
    const blocks = {js_blocks};
    let i = 0;
    let fontSize = 3;

    const el = document.getElementById("code");

    function render() {{
      const {{ lang, code }} = blocks[i];
      el.textContent = code;
      el.className = '';
      el.classList.add(lang);
      el.style.fontSize = fontSize + 'rem';
      hljs.highlightElement(el);
      requestAnimationFrame(() => document.body.scrollTop = 0);
    }}

    document.addEventListener('keydown', e => {{
      if (e.key === 'ArrowRight') {{
        i = Math.min(i + 1, blocks.length - 1);
        render();
      }} else if (e.key === 'ArrowLeft') {{
        i = Math.max(i - 1, 0);
        render();
      }} else if (e.key === '=') {{
        fontSize = Math.min(fontSize + 0.2, 6);
        render();
      }} else if (e.key === '-') {{
        fontSize = Math.max(fontSize - 0.2, 0.5);
        render();
      }} else if (e.key.toLowerCase() === 'b') {{
        document.body.classList.toggle('light');
        const theme = document.getElementById('hljs-theme');
        theme.href = document.body.classList.contains('light')
          ? 'https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.8.0/styles/github.min.css'
          : 'https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.8.0/styles/atom-one-dark.min.css';
      }}
    }});

    render();
  </script>
</body>
</html>
"""


class InMemoryHandler(http.server.BaseHTTPRequestHandler):
    """Serves a single in-memory HTML page."""

    def __init__(self, html: str, *args, **kwargs):
        self._html = html
        super().__init__(*args, **kwargs)

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(self._html.encode("utf-8"))))
        self.end_headers()
        self.wfile.write(self._html.encode("utf-8"))

    def log_message(self, format, *args):
        pass  # silence logs


def run_viewer(md_path: Path) -> None:
    md_text = md_path.read_text(encoding="utf-8")
    code_blocks = extract_code_blocks(md_text)
    html = generate_html(code_blocks)

    def handler(*args, **kwargs):
        InMemoryHandler(html, *args, **kwargs)

    with socketserver.TCPServer(("localhost", PORT), handler) as httpd:
        thread = threading.Thread(target=httpd.serve_forever)
        thread.daemon = True
        thread.start()

        webbrowser.open(f"http://localhost:{PORT}")
        print("Press Ctrl+C to exit.")
        try:
            thread.join()  # Keep main thread alive until interrupted
        except KeyboardInterrupt:
            print("\nShutting down...")
            httpd.shutdown()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="View fenced code blocks in Markdown as full-screen slides"
    )
    parser.add_argument("markdown_file", type=Path, help="Path to the Markdown file")
    args = parser.parse_args()
    run_viewer(args.markdown_file)


if __name__ == "__main__":
    main()
