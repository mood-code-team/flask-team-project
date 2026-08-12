"""Recreate Mood Code venv when USB copy still points at another PC."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
VENV = PROJECT / "venv"
REQ = PROJECT / "requirements.txt"


def venv_python() -> Path:
    """OS별 venv Python 경로."""
    if sys.platform == "win32":
        return VENV / "Scripts" / "python.exe"
    return VENV / "bin" / "python"


def find_python() -> Path:
    candidates: list[list[str]] = []
    if sys.platform == "win32":
        candidates.extend([["py", "-3"], ["python"]])
    else:
        candidates.extend([["python3"], ["python"]])

    for cmd in candidates:
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
        "  Or run: python3 -m venv venv"
    )


def venv_ok() -> bool:
    py = venv_python()
    if not py.is_file() or not REQ.is_file():
        return False
    result = subprocess.run(
        [str(py), "-c", "import flask"],
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
    py = venv_python()
    subprocess.run(
        [str(py), "-m", "pip", "install", "-U", "pip", "-q"],
        cwd=str(PROJECT),
        check=True,
    )
    subprocess.run(
        [str(py), "-m", "pip", "install", "-r", str(REQ.name), "-q"],
        cwd=str(PROJECT),
        check=True,
    )


def main() -> None:
    if venv_ok():
        return

    python = find_python()
    print("[setup] venv missing or broken - recreating for this PC...")
    recreate(python)
    print("[setup] venv OK:", venv_python())


if __name__ == "__main__":
    main()
