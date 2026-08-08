"""Recreate Mood Code venv when USB copy still points at another PC."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
VENV = PROJECT / "venv"
VENV_PY = VENV / "Scripts" / "python.exe"
REQ = PROJECT / "requirements.txt"


def find_python() -> Path:
    for cmd in (["py", "-3"], ["python"]):
        try:
            result = subprocess.run(
                [*cmd, "-c", "import sys; print(sys.executable)"],
                capture_output=True,
                text=True,
                check=True,
                timeout=30,
            )
            exe = Path(result.stdout.strip())
            if exe.is_file():
                return exe
        except (subprocess.CalledProcessError, OSError, subprocess.TimeoutExpired):
            continue
    raise SystemExit(
        "Python 3 not found.\n"
        "  Install from https://www.python.org/downloads/\n"
        "  Or run: py -3 -m venv venv"
    )


def venv_ok() -> bool:
    if not VENV_PY.is_file() or not REQ.is_file():
        return False
    result = subprocess.run(
        [str(VENV_PY), "-c", "import flask"],
        cwd=str(PROJECT),
        capture_output=True,
    )
    return result.returncode == 0


def recreate(python: Path) -> None:
    if VENV.is_dir():
        backup = PROJECT / "venv_broken_backup"
        if backup.exists():
            shutil.rmtree(backup)
        VENV.rename(backup)
        print(f"[setup] backed up broken venv -> {backup.name}")

    subprocess.run([str(python), "-m", "venv", str(VENV)], cwd=str(PROJECT), check=True)
    subprocess.run(
        [str(VENV_PY), "-m", "pip", "install", "-U", "pip", "-q"],
        cwd=str(PROJECT),
        check=True,
    )
    subprocess.run(
        [str(VENV_PY), "-m", "pip", "install", "-r", str(REQ.name), "-q"],
        cwd=str(PROJECT),
        check=True,
    )


def main() -> None:
    if venv_ok():
        return

    python = find_python()
    print("[setup] venv missing or broken - recreating for this PC...")
    recreate(python)
    print("[setup] venv OK:", VENV_PY)


if __name__ == "__main__":
    main()
