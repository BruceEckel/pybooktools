# viewer_server.py
from __future__ import annotations

import argparse
import http.server
import json
import socketserver
import threading
import webbrowser
from pathlib import Path
from subprocess import run, PIPE
from urllib.parse import urlparse, parse_qs

from markdown_it import MarkdownIt

PORT = 8765


def extract_code_blocks(md_text: str) -> list[tuple[str, str]]:
    md = MarkdownIt()
    tokens = md.parse(md_text)
    return [
        (token.info.strip(), token.content)
        for token in tokens
        if token.type == "fence"
    ]


class CodeViewerHandler(http.server.BaseHTTPRequestHandler):
    _blocks: list[tuple[str, str]]

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/":
            self._serve_html()
        elif parsed.path == "/format":
            self._serve_formatted_code(parse_qs(parsed.query))
        else:
            self.send_error(404, "Not Found")

    def _serve_html(self):
        js_blocks = json.dumps([
            {"lang": lang or "plaintext", "code": code}
            for lang, code in self._blocks
        ])
        html = generate_html(js_blocks)
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    def _serve_formatted_code(self, qs: dict[str, list[str]]) -> None:
        try:
            index = int(qs.get("index", [0])[0])
            width = int(qs.get("width", [88])[0])
            lang, code = self._blocks[index]
            if lang != "python":
                raise ValueError("Only Python code is supported")

            result = run(
                ["ruff", "format", "--line-length", str(width), "-"],
                input=code,
                stdout=PIPE,
                stderr=PIPE,
                encoding="utf-8"
            )
            formatted = result.stdout if result.returncode == 0 else code
        except Exception:
            formatted = "// formatting failed"

        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(formatted.encode("utf-8"))

    def log_message(self, *args):
        pass


class CodeViewerServer(socketserver.TCPServer):
    allow_reuse_address = True

    def __init__(self, code_blocks: list[tuple[str, str]]):
        handler = lambda *args, **kwargs: CodeViewerHandler(*args, **kwargs)
        CodeViewerHandler._blocks = code_blocks
        super().__init__(("localhost", PORT), handler)


def generate_html(js_blocks: str) -> str:
    return f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <title>Code Viewer</title>
  <link href=\"https://fonts.googleapis.com/css2?family=Fira+Code&display=swap\" rel=\"stylesheet\">
  <link id=\"hljs-theme\" rel=\"stylesheet\"
        href=\"https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.8.0/styles/atom-one-dark.min.css\" />
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
      scrollbar-width: none;
      -ms-overflow-style: none;
    }}
    body::-webkit-scrollbar {{ display: none; }}
    body.light {{ background: #fdfdfd; color: #000; }}
    pre {{
      font-size: 2rem;
      line-height: 1.5;
      white-space: pre-wrap;
      overflow-wrap: break-word;
      margin: 0;
    }}
    pre.hljs {{ background: transparent !important; }}
  </style>
</head>
<body>
  <pre><code id=\"code\" class=\"hljs\"></code></pre>
  <script src=\"https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.8.0/highlight.min.js\"></script>
  <script>
    const blocks = {js_blocks};
    let i = 0;
    let fontSize = 2;
    const el = document.getElementById("code");

    async function render(forceRuff = false) {{
      const {{ lang }} = blocks[i];
      let code = blocks[i].code;

      if (lang === "python" && forceRuff) {{
        const width = estimateCharWidth();
        const res = await fetch(`/format?index=${{i}}&width=${{width}}`);
        if (res.ok) code = await res.text();
      }}

      el.textContent = code;
      el.className = '';
      el.classList.add(lang);
      el.style.fontSize = fontSize + 'rem';
      hljs.highlightElement(el);
      requestAnimationFrame(() => document.body.scrollTop = 0);
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

    document.addEventListener('keydown', e => {{
      if (e.key === 'ArrowRight') {{ i = Math.min(i + 1, blocks.length - 1); render(true); }}
      else if (e.key === 'ArrowLeft') {{ i = Math.max(i - 1, 0); render(true); }}
      else if (e.key === '+') {{ fontSize = Math.min(fontSize + 0.2, 6); render(true); }}
      else if (e.key === '-') {{ fontSize = Math.max(fontSize - 0.2, 0.5); render(true); }}
      else if (e.key.toLowerCase() === 'r') {{ render(true); }}
      else if (e.key.toLowerCase() === 'b') {{
        document.body.classList.toggle('light');
        document.getElementById('hljs-theme').href =
          document.body.classList.contains('light')
            ? 'https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.8.0/styles/github.min.css'
            : 'https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.8.0/styles/atom-one-dark.min.css';
      }}
    }});

    render(true);
  </script>
</body>
</html>
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Launch code viewer for Markdown fenced blocks")
    parser.add_argument("markdown_file", type=Path)
    args = parser.parse_args()

    code_blocks = extract_code_blocks(args.markdown_file.read_text(encoding="utf-8"))
    with CodeViewerServer(code_blocks) as server:
        thread = threading.Thread(target=server.serve_forever)
        thread.daemon = True
        thread.start()
        webbrowser.open(f"http://localhost:{PORT}")
        print("Press Ctrl+C to quit.")
        try:
            thread.join()
        except KeyboardInterrupt:
            print("\nShutting down...")
            server.shutdown()


if __name__ == "__main__":
    main()
