"""Publish workflow — QR login, image upload, one-click publish.

Called by dashboard server as subprocess/import.
"""

import json
import subprocess
import tempfile
import shutil
import os
from pathlib import Path

SAU_DIR = Path(__file__).parent.parent / "social-upload"
EXPORTS_DIR = Path("data/publish-exports")
EXPORTS_DIR.mkdir(parents=True, exist_ok=True)


def login_platform(platform: str, account: str = "default", headless: bool = True) -> dict:
    """Trigger SAU platform login. Returns QR code path for frontend display."""
    cookie_dir = SAU_DIR / "cookies" / platform
    cookie_dir.mkdir(parents=True, exist_ok=True)
    cookie_file = cookie_dir / f"{account}.json"

    if cookie_file.exists():
        return {"status": "already_logged_in", "cookie_file": str(cookie_file)}

    try:
        result = subprocess.run(
            ["sau", platform, "login", "--account", account]
            + (["--headless"] if headless else []),
            cwd=str(SAU_DIR),
            capture_output=True, text=True, timeout=120,
            env={**os.environ, "PYTHONPATH": str(SAU_DIR)},
        )

        # SAU login saves QR code to cookies/{platform}/{account}.png
        qr_path = cookie_dir / f"{account}_qrcode.png"
        if qr_path.exists():
            return {"status": "qr_ready", "qr_path": str(qr_path), "stdout": result.stdout[-500:]}
        elif cookie_file.exists():
            return {"status": "login_success", "cookie_file": str(cookie_file)}
        else:
            return {"status": "failed", "stderr": result.stderr[:500], "stdout": result.stdout[-500:]}
    except subprocess.TimeoutExpired:
        return {"status": "timeout", "message": "Login timed out (2 min)"}
    except FileNotFoundError:
        return {"status": "error", "message": "SAU not installed. Run: pip install -r apps/social-upload/requirements.txt"}


def publish_content(
    platform: str,
    account: str,
    content_url: str,
    video_file: str = "",
    image_files: list[str] | None = None,
    schedule: str = "",
) -> dict:
    """Publish content to a platform via SAU CLI."""
    if image_files:
        # Image/note publish
        cmd = [
            "sau", platform, "upload-note",
            "--account", account,
            "--images", *image_files,
            "--content-url", content_url,
        ]
    elif video_file:
        cmd = [
            "sau", platform, "upload-video",
            "--account", account,
            "--file", video_file,
            "--content-url", content_url,
        ]
    else:
        cmd = [
            "sau", platform, "upload-video",
            "--account", account,
            "--file", "",
            "--content-url", content_url,
        ]

    if schedule:
        cmd.extend(["--schedule", schedule])

    try:
        result = subprocess.run(
            cmd,
            cwd=str(SAU_DIR),
            capture_output=True, text=True, timeout=300,
            env={**os.environ, "PYTHONPATH": str(SAU_DIR)},
        )
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout[-1000:],
            "stderr": result.stderr[-500:],
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Publish timed out (5 min)"}
    except FileNotFoundError:
        return {"success": False, "error": "SAU not installed"}


def list_accounts(platform: str = "") -> list[dict]:
    """List logged-in accounts per platform."""
    accounts = []
    cookie_base = SAU_DIR / "cookies"
    if not cookie_base.exists():
        return []

    platforms = [platform] if platform else os.listdir(str(cookie_base))
    for pf in platforms:
        pf_dir = cookie_base / pf
        if not pf_dir.is_dir():
            continue
        for f in pf_dir.iterdir():
            if f.suffix == ".json":
                accounts.append({
                    "platform": pf,
                    "account": f.stem,
                    "cookie_file": str(f),
                })
    return accounts
