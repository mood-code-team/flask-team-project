"""
MySQL 연결 헬퍼 — 팀 공용 DB 설정.

개발: SQLite (기본, config.py)
팀/운영: MySQL — .env 에 DATABASE_URL 설정

예)
  DATABASE_URL=mysql+pymysql://moodcode:moodcode123@localhost:3306/moodcode_shop
"""

from __future__ import annotations

import os

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine


def get_database_url() -> str:
    """환경 변수 DATABASE_URL 또는 SQLite 기본값."""
    default = "sqlite:///database/shop.db"
    return os.environ.get("DATABASE_URL", default)


def create_db_engine(echo: bool = False) -> Engine:
    """SQLAlchemy Engine 생성."""
    return create_engine(get_database_url(), echo=echo)


def ping() -> bool:
    """DB 연결 테스트."""
    engine = create_db_engine()
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return True


if __name__ == "__main__":
    url = get_database_url()
    safe = url.split("@")[-1] if "@" in url else url
    print(f"DATABASE_URL → …@{safe}" if "@" in url else f"DATABASE_URL → {safe}")
    try:
        ping()
        print("[OK] DB 연결 성공")
    except Exception as exc:
        print(f"[FAIL] DB 연결 실패: {exc}")
