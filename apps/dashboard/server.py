"""ContentEngine Dashboard — static file server + API proxy.

Serves the dashboard on port 3000 and proxies all API calls to seo-agent (port 8000).
This eliminates CORS issues — dashboard and API share the same origin.
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
        # Publish workflow
        if self.path.startswith("/publish/"):
            self._handle_publish("GET")
            return
        # Proxy API calls to seo-agent
        if self.path.startswith("/api/") or self.path in ("/health", "/ready", "/projects", "/articles", "/kb", "/analytics"):
            self._proxy("GET")
            return
        # Proxy /settings
        if self.path.startswith("/settings"):
            self._proxy("GET")
            return
        super().do_GET()

    def do_POST(self):
        # Publish workflow endpoints
        if self.path.startswith("/publish/"):
            self._handle_publish("POST")
            return
        if self.path.startswith("/api/") or self.path.startswith("/kb/") or self.path.startswith("/settings") or self.path.startswith("/projects") or self.path.startswith("/articles"):
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
                    # SSE — stream through
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

    def _handle_publish(self, method: str):
        """Handle /publish/* endpoints for QR login and one-click publish."""
        from publish_handler import login_platform, publish_content, list_accounts

        path = self.path

        if path == "/publish/accounts" and method == "GET":
            accounts = list_accounts()
            self._json_response(200, {"accounts": accounts})

        elif path == "/publish/login" and method == "POST":
            content_length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(content_length)) if content_length > 0 else {}
            platform = body.get("platform", "douyin")
            account = body.get("account", "default")
            result = login_platform(platform, account, headless=False)
            self._json_response(200, result)

        elif path == "/publish/send" and method == "POST":
            content_length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(content_length)) if content_length > 0 else {}
            platform = body.get("platform", "douyin")
            account = body.get("account", "default")
            content_url = body.get("content_url", f"{SEO_AGENT}/api/content/export/latest?format=sau")
            images = body.get("images", [])
            result = publish_content(platform, account, content_url, image_files=images)
            self._json_response(200, result)

        elif path.startswith("/publish/qr/") and method == "GET":
            # Serve QR code image
            filename = Path(path).name
            qr_path = Path("cookies") / filename
            from publish_handler import SAU_DIR
            qr_path = SAU_DIR / "cookies" / filename.split("_")[0] / filename
            if qr_path.exists():
                self.send_response(200)
                self.send_header("Content-Type", "image/png")
                self.end_headers()
                self.wfile.write(qr_path.read_bytes())
            else:
                self.send_error(404, "QR code not found")

        else:
            self.send_error(404, f"Unknown publish endpoint: {path}")

    def _json_response(self, code: int, data: dict):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())

    def log_message(self, format, *args):
        # Quieter logging
        if "/health" not in str(args):
            super().log_message(format, *args)


if __name__ == "__main__":
    print(f"ContentEngine Dashboard → http://127.0.0.1:{PORT}")
    print(f"API proxy → {SEO_AGENT}")
    http.server.HTTPServer(("127.0.0.1", PORT), ProxyHandler).serve_forever()
