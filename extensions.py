"""
Flask 확장 객체 모듈.

앱 팩토리 패턴에서 순환 import 를 방지하기 위해
db, login_manager 등을 이 파일에서 한곳에 모읍니다.
"""

from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

# SQLAlchemy ORM
db = SQLAlchemy()

# DB 마이그레이션 (flask db init / migrate / upgrade)
migrate = Migrate()

# 로그인 세션 관리 (4단계에서 활성화)
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "로그인이 필요한 서비스입니다."
login_manager.login_message_category = "warning"
