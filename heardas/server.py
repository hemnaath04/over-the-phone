"""Local server for the Heard As page.

    uv run python -m heardas.server        # http://127.0.0.1:8765

GET / serves the page; POST /api/check takes {"text", "voice", "locale", "condition"}
and returns `otp.heardas.compare`. Standard library only, bound to localhost: it
spends the AssemblyAI key in .env on every check, so it is not for the open internet.
"""

from __future__ import annotations

import json
import sys
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from otp.heardas import compare  # noqa: E402

PAGE = Path(__file__).resolve().parent / "index.html"
VOICES = {"aai-audrey", "aai-titus", "aai-sara", "aai-ewald", "aai-nancy", "aai-buford",
          "aai-carrie", "aai-percival", "aai-steven", "aai-troy"}
CONDITIONS = {"api24", "resampled8", "lossy8"}
MAX_CHARS = 1200


class Handler(BaseHTTPRequestHandler):
    def _send(self, status: int, body: bytes, kind: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", kind)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _json(self, status: int, obj: dict) -> None:
        self._send(status, json.dumps(obj).encode(), "application/json")

    def do_GET(self) -> None:  # noqa: N802
        if self.path in ("/", "/index.html"):
            self._send(200, PAGE.read_bytes(), "text/html; charset=utf-8")
        else:
            self._send(404, b"not found", "text/plain")

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/api/check":
            return self._send(404, b"not found", "text/plain")
        try:
            req = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))))
        except (ValueError, json.JSONDecodeError):
            return self._json(400, {"error": "Send JSON."})
        text = (req.get("text") or "").strip()
        voice = req.get("voice", "aai-audrey")
        locale = req.get("locale", "en-US")
        condition = req.get("condition", "resampled8")
        if not text:
            return self._json(400, {"error": "Type what the agent will say."})
        if len(text) > MAX_CHARS:
            return self._json(400, {"error": f"Keep it under {MAX_CHARS} characters, about one reply."})
        if voice not in VOICES or locale not in ("en-US", "en-GB") or condition not in CONDITIONS:
            return self._json(400, {"error": "Unknown voice, locale or line."})
        try:
            self._json(200, compare(text, voice, locale, condition))
        except Exception as exc:  # report it on the page rather than dropping the connection
            traceback.print_exc()
            self._json(502, {"error": f"The check failed: {exc}"})

    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write("%s %s\n" % (self.command, self.path))


def main(port: int = 8765) -> None:
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"Heard As on http://127.0.0.1:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 8765)
