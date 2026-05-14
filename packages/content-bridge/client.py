"""API clients for SEO Agent and Social Upload services."""

import json
import urllib.request
import urllib.error
from dataclasses import dataclass

SEO_AGENT_DEFAULT = "http://localhost:8000"
SAU_DEFAULT = "http://localhost:8001"


class SEOAgentClient:
    """Client for seo-ai-agent REST API."""

    def __init__(self, base_url: str = SEO_AGENT_DEFAULT):
        self.base_url = base_url.rstrip("/")

    def health(self) -> dict:
        return self._get("/health")

    def export_latest(self, format: str = "sau") -> dict:
        return self._get(f"/api/content/export/latest?format={format}")

    def list_exports(self) -> dict:
        return self._get("/api/content/export/list")

    def download_latest(self) -> bytes:
        req = urllib.request.Request(f"{self.base_url}/api/content/export/latest/file")
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.read()

    def _get(self, path: str) -> dict:
        req = urllib.request.Request(f"{self.base_url}{path}")
        req.add_header("Accept", "application/json")
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())


class SAUClient:
    """Client for social-auto-upload REST API (Flask backend, port 8001)."""

    def __init__(self, base_url: str = SAU_DEFAULT):
        self.base_url = base_url.rstrip("/")

    def health(self) -> dict:
        return self._get("/health")

    def list_accounts(self) -> list[dict]:
        return self._get("/getAccounts")

    def upload_video(self, platform: str, account: str, file: str,
                     title: str = "", desc: str = "", tags: str = "") -> dict:
        import subprocess
        # SAU uses CLI, not REST for uploads — wrap subprocess
        cmd = [
            "sau", platform, "upload-video",
            "--account", account,
            "--file", file,
        ]
        if title:
            cmd.extend(["--title", title])
        if desc:
            cmd.extend(["--desc", desc])
        if tags:
            cmd.extend(["--tags", tags])

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }

    def _get(self, path: str) -> dict:
        req = urllib.request.Request(f"{self.base_url}{path}")
        req.add_header("Accept", "application/json")
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())
