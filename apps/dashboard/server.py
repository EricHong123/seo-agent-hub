"""SEO Agent Hub Dashboard — static file server + API proxy.

Serves the dashboard on port 3000 and proxies all API calls to seo-agent (port 8000).
Eliminates CORS issues — dashboard and API share the same origin.
"""

import http.server
import urllib.request
import urllib.error
import json
import os
from pathlib import Path

SEO_AGENT = os.environ.get("SEO_AGENT_URL", "http://127.0.0.1:8000")
PORT = int(os.environ.get("PORT", "3000"))
DASHBOARD_DIR = Path(__file__).parent


class ProxyHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DASHBOARD_DIR), **kwargs)

    def do_GET(self):
        if self.path.startswith("/api/") or self.path in ("/health", "/ready",
                "/projects", "/articles", "/kb", "/analytics", "/settings"):
            self._proxy("GET")
            return
        super().do_GET()

    def do_POST(self):
        if self.path.startswith("/api/") or any(self.path.startswith(p)
                for p in ("/kb/", "/settings", "/projects", "/articles")):
            self._proxy("POST")
            return
        self.send_error(404)

    def do_PUT(self):
        if self.path.startswith("/settings"):
            self._proxy("PUT")
            return
        self.send_error(404)

    def do_DELETE(self):
        if self.path.startswith("/api/") or self.path.startswith("/kb/"):
            self._proxy("DELETE")
            return
        self.send_error(404)

    def _proxy(self, method: str):
        url = f"{SEO_AGENT}{self.path}"
        try:
            body = None
            content_length = int(self.headers.get("Content-Length", 0))
            if content_length > 0:
                body = self.rfile.read(content_length)

            req = urllib.request.Request(url, data=body, method=method)
            req.add_header("Content-Type", self.headers.get("Content-Type", "application/json"))
            req.add_header("Authorization", self.headers.get("Authorization", ""))

            with urllib.request.urlopen(req, timeout=120) as resp:
                self.send_response(resp.status)
                self.send_header("Content-Type", resp.headers.get("Content-Type", "application/json"))
                if self.path.startswith("/api/agent/run"):
                    self.send_header("Cache-Control", "no-cache")
                    self.send_header("Connection", "keep-alive")
                    self.end_headers()
                    while True:
                        chunk = resp.read(4096)
                        if not chunk:
                            break
                        self.wfile.write(chunk)
                        self.wfile.flush()
                else:
                    self.end_headers()
                    self.wfile.write(resp.read())

        except urllib.error.HTTPError as e:
            self.send_response(e.code)
            self.end_headers()
            self.wfile.write(e.read())
        except urllib.error.URLError as e:
            self.send_error(502, f"SEO Agent unreachable: {e.reason}")

    def log_message(self, format, *args):
        if "/health" not in str(args):
            super().log_message(format, *args)


if __name__ == "__main__":
    print(f"SEO Agent Hub Dashboard → http://127.0.0.1:{PORT}")
    print(f"API proxy → {SEO_AGENT}")
    http.server.HTTPServer(("127.0.0.1", PORT), ProxyHandler).serve_forever()
