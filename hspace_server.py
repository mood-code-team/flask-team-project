"""Mood Code 서버 실행."""

from __future__ import annotations

import os
import sys
import threading
import time
import webbrowser
from pathlib import Path

# bat/루트 launcher 어디서 실행해도 import 되도록 프로젝트 폴더 고정
PROJECT_DIR = Path(__file__).resolve().parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))
os.chdir(PROJECT_DIR)

from app import create_app

HOST = "127.0.0.1"
PORT = 5000
URL = f"http://{HOST}:{PORT}/"


def open_browser() -> None:
    time.sleep(1.2)
    webbrowser.open(URL)


if __name__ == "__main__":
    if sys.platform == "win32":
        os.system("")  # ANSI 색상 활성화

    app = create_app()

    if os.environ.get("WERKZEUG_RUN_MAIN") != "true":
        threading.Thread(target=open_browser, daemon=True).start()

    app.run(host=HOST, port=PORT, debug=True, use_reloader=True)
