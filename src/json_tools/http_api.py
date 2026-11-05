"""API HTTP simples (stdlib). GET /tools, POST /call/<nome> com corpo JSON."""

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from . import tools

MAX_BODY = 1_000_000


class Handler(BaseHTTPRequestHandler):
    def _send(self, status: int, payload) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):  # noqa: N802
        if self.path == "/tools":
            self._send(200, [t.describe() for t in tools.REGISTRY.values()])
        else:
            self._send(404, {"ok": False, "error": "não encontrado"})

    def do_POST(self):  # noqa: N802
        if not self.path.startswith("/call/"):
            return self._send(404, {"ok": False, "error": "não encontrado"})
        try:
            length = int(self.headers.get("Content-Length", 0))
            if length > MAX_BODY:
                return self._send(413, {"ok": False, "error": "corpo grande demais"})
            args = json.loads(self.rfile.read(length) or b"{}")
        except (ValueError, json.JSONDecodeError):
            return self._send(400, {"ok": False, "error": "JSON inválido"})
        out = tools.call_tool(self.path[len("/call/"):], args)
        self._send(200 if out["ok"] else 400, out)

    def log_message(self, *args):
        pass


def make_server(host: str = "127.0.0.1", port: int = 8000):
    return ThreadingHTTPServer((host, port), Handler)


def serve(host: str = "127.0.0.1", port: int = 8000) -> None:
    server = make_server(host, port)
    print(f"json-tools HTTP em http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
