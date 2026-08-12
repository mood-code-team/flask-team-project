"""서버 실행 전 환경 점검 — 팀원 PC에서 python hspace_server.py 직접 실행 시 안내."""

from __future__ import annotations

import importlib
import shutil
import subprocess
import sys
from pathlib import Path

REQUIRED_PACKAGES: tuple[tuple[str, str], ...] = (
    ("flask", "Flask"),
    ("flask_sqlalchemy", "Flask-SQLAlchemy"),
    ("flask_migrate", "Flask-Migrate"),
    ("flask_login", "Flask-Login"),
    ("dotenv", "python-dotenv"),
)


def _missing_packages() -> list[str]:
    missing: list[str] = []
    for module_name, pip_name in REQUIRED_PACKAGES:
        try:
            importlib.import_module(module_name)
        except ImportError:
            missing.append(pip_name)
    return missing


def _print_setup_help(project_dir: Path, *, reason: str) -> None:
    print()
    print("=" * 60)
    print("[Mood Code] 서버를 시작할 수 없습니다.")
    print(f"  원인: {reason}")
    print()
    print("  해결 방법 (Windows — 가장 쉬움):")
    print(f"    1) {project_dir}\\실행_서버.bat 더블클릭")
    print("       → venv 생성 + pip install + 서버 시작을 자동 처리")
    print()
    print("  해결 방법 (터미널):")
    print(f"    cd /d \"{project_dir}\"")
    print("    pip install -r requirements.txt")
    print("    python hspace_server.py")
    print()
    print("  ※ 프로젝트 루트(app.py 있는 폴더)에서 실행해야 합니다.")
    print("  ※ python 대신 py -3 를 써야 할 수도 있습니다.")
    print("=" * 60)
    print()


def _try_pip_install(project_dir: Path) -> bool:
    req = project_dir / "requirements.txt"
    if not req.is_file():
        return False
    print("[setup] 필요 패키지 설치 중... (pip install -r requirements.txt)")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-r", str(req)],
        cwd=str(project_dir),
    )
    return result.returncode == 0


def ensure_env_file(project_dir: Path) -> None:
    env_path = project_dir / ".env"
    example = project_dir / ".env.example"
    if env_path.is_file() or not example.is_file():
        return
    shutil.copyfile(example, env_path)
    print("[setup] .env 파일을 .env.example 에서 생성했습니다.")


def ensure_server_ready(project_dir: Path) -> None:
    """패키지·경로·.env 점검. 실패 시 안내 후 종료."""
    if not (project_dir / "app.py").is_file():
        _print_setup_help(project_dir, reason="app.py 를 찾을 수 없음 (프로젝트 루트가 아님)")
        raise SystemExit(1)

    ensure_env_file(project_dir)

    missing = _missing_packages()
    if missing:
        print(f"[setup] 누락 패키지: {', '.join(missing)}")
        if _try_pip_install(project_dir):
            missing = _missing_packages()

    if missing:
        _print_setup_help(
            project_dir,
            reason=f"Python 패키지 미설치 ({', '.join(missing)})",
        )
        raise SystemExit(1)

    db_path = project_dir / "database" / "shop.db"
    if not db_path.is_file():
        print("[warn] database/shop.db 가 없습니다.")
        print("       python scripts/seed_db.py 실행 후 다시 시도하세요.")
        print("       (또는 frontend 브랜치를 pull 하면 DB가 포함됩니다.)")
        print()
