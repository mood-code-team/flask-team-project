"""Mood Code 서버 실행."""

from __future__ import annotations

import os
import sys
import threading
import time
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path

# bat/루트 launcher 어디서 실행해도 import 되도록 프로젝트 폴더 고정
PROJECT_DIR = Path(__file__).resolve().parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))
os.chdir(PROJECT_DIR)

from scripts.preflight_server import ensure_server_ready

ensure_server_ready(PROJECT_DIR)

from app import create_app

HOST = "127.0.0.1"
PORT = 5000
USE_RELOADER = os.environ.get("FLASK_USE_RELOADER", "0") == "1"
_browser_opened = False


def _browser_path() -> str:
    """실행_관리자.bat 등에서 MOODCODE_OPEN_URL=/admin/ 로 지정 가능."""
    path = (os.environ.get("MOODCODE_OPEN_URL") or "/").strip() or "/"
    if not path.startswith("/"):
        path = f"/{path}"
    return path


def _server_url() -> str:
    return f"http://{HOST}:{PORT}/"


def _browser_url() -> str:
    return f"http://{HOST}:{PORT}{_browser_path()}"


def _server_ready() -> bool:
    try:
        with urllib.request.urlopen(_server_url(), timeout=1) as response:
            return response.status < 500
    except (urllib.error.URLError, TimeoutError, OSError):
        return False


def open_browser() -> None:
    """서버가 응답할 때까지 기다린 뒤 브라우저를 한 번만 연다."""
    global _browser_opened
    if _browser_opened:
        return

    for _ in range(30):
        if _server_ready():
            break
        time.sleep(0.5)

    if _browser_opened:
        return
    _browser_opened = True

    target = _browser_url()
    if sys.platform == "win32":
        os.startfile(target)  # type: ignore[attr-defined]
        return

    webbrowser.open(target)


def should_open_browser() -> bool:
    if os.environ.get("MOODCODE_NO_BROWSER") == "1":
        return False
    if USE_RELOADER:
        return os.environ.get("WERKZEUG_RUN_MAIN") == "true"
    return True


if __name__ == "__main__":
    if sys.platform == "win32":
        os.system("")  # ANSI 색상 활성화

    app = create_app()

    if should_open_browser():
        threading.Thread(target=open_browser, daemon=True).start()

    app.run(host=HOST, port=PORT, debug=True, use_reloader=USE_RELOADER)
