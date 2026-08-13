"""
애플리케이션 설정 모듈.

환경 변수로 DB, 시크릿 키, 채널톡 등을 주입합니다.
개발: SQLite / 운영: MySQL 또는 PostgreSQL 로 전환 가능합니다.
"""

from __future__ import annotations

import os
from pathlib import Path

# 프로젝트 루트 경로
BASE_DIR = Path(__file__).resolve().parent
DATABASE_DIR = BASE_DIR / "database"
DATABASE_DIR.mkdir(exist_ok=True)

try:
    from dotenv import load_dotenv

    load_dotenv(BASE_DIR / ".env")
except ImportError:
    pass


def _normalize_database_url(url: str) -> str:
    """Render PostgreSQL URL은 postgres:// 로 오므로 SQLAlchemy용으로 변환."""
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)
    return url


def _default_sqlite_uri() -> str:
    return f"sqlite:///{DATABASE_DIR / 'shop.db'}"


class Config:
    """공통 설정."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-interior-shop-secret-key-change-in-prod")
    JSON_AS_ASCII = False

    # SQLAlchemy — database/shop.db (개발용 SQLite) / Render는 DATABASE_URL 주입
    SQLALCHEMY_DATABASE_URI = _normalize_database_url(
        os.environ.get("DATABASE_URL", _default_sqlite_uri())
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = os.environ.get("SQLALCHEMY_ECHO", "false").lower() == "true"

    # 세션 / 쿠키
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    REMEMBER_COOKIE_DURATION = 60 * 60 * 24 * 14  # 14일

    UPLOAD_FOLDER = BASE_DIR / "static" / "images" / "uploads"
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

    CHANNEL_TALK_PLUGIN_KEY = os.environ.get("CHANNEL_TALK_PLUGIN_KEY", "")
    CHANNEL_TALK_SECRET = os.environ.get("CHANNEL_TALK_SECRET", "")

    # 페이지네이션 기본값
    PRODUCTS_PER_PAGE = 12

    # 토스페이먼츠 (테스트 키 — docs.tosspayments.com 테스트 연동용)
    TOSS_CLIENT_KEY = os.environ.get(
        "TOSS_CLIENT_KEY",
        "test_ck_D5GePWvyJnrK0W0k6q8gLzN97Eoq",
    )
    TOSS_SECRET_KEY = os.environ.get(
        "TOSS_SECRET_KEY",
        "test_sk_zXLkKEypNArWYo0z18Jql8VoXDL",
    )
    TOSS_API_URL = "https://api.tosspayments.com/v1/payments/confirm"

    # 카카오 로그인 — developers.kakao.com 앱 REST API 키
    KAKAO_REST_API_KEY = (os.environ.get("KAKAO_REST_API_KEY") or "").strip()
    KAKAO_CLIENT_SECRET = (os.environ.get("KAKAO_CLIENT_SECRET") or "").strip()
    KAKAO_REDIRECT_URI = (
        os.environ.get("KAKAO_REDIRECT_URI") or "http://127.0.0.1:5000/auth/kakao/callback"
    ).strip()
    # true — 카카오/Apple 콘솔·심사 없이 버튼 클릭만으로 로그인 (로컬·데모용)
    SOCIAL_DEMO_LOGIN = os.environ.get("SOCIAL_DEMO_LOGIN", "").lower() in ("true", "1", "on", "yes")

    # Apple 로그인 — Apple Developer Service ID / Key
    APPLE_CLIENT_ID = os.environ.get("APPLE_CLIENT_ID", "")
    APPLE_TEAM_ID = os.environ.get("APPLE_TEAM_ID", "")
    APPLE_KEY_ID = os.environ.get("APPLE_KEY_ID", "")
    APPLE_PRIVATE_KEY = os.environ.get("APPLE_PRIVATE_KEY", "")


class DevelopmentConfig(Config):
    """개발 환경."""

    DEBUG = True
    ENV = "development"
    SOCIAL_DEMO_LOGIN = os.environ.get("SOCIAL_DEMO_LOGIN", "true").lower() in (
        "true",
        "1",
        "on",
        "yes",
    )


class ProductionConfig(Config):
    """운영 환경."""

    DEBUG = False
    ENV = "production"
    SESSION_COOKIE_SECURE = True


class TestingConfig(Config):
    """테스트 환경."""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False


config_by_name: dict[str, type[Config]] = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}
