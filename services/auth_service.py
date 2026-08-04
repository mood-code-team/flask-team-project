"""
회원가입·아이디/비밀번호 찾기 비즈니스 로직.
"""

from __future__ import annotations

import re
import time
from calendar import monthrange
from datetime import date

from flask import session

from extensions import db
from models import User
from services.register_options import KOREA_REGIONS


class AuthValidationError(ValueError):
    """폼 검증 실패."""


_USERNAME_RE = re.compile(r"^[a-z0-9_]{4,16}$")
_PHONE_RE = re.compile(r"^01[0-9]-?\d{3,4}-?\d{4}$")

PASSWORD_RESET_SESSION_KEY = "password_reset_user_id"
PASSWORD_RESET_SESSION_TS_KEY = "password_reset_user_ts"
PASSWORD_RESET_TTL_SECONDS = 600


def _normalize_phone(phone: str) -> str:
    return phone.replace("-", "").replace(" ", "")


def _validate_birth(year: int, month: int, day: int) -> None:
    today = date.today()
    if year < 1900 or year > today.year:
        raise AuthValidationError("올바른 출생 연도를 입력해 주세요.")
    if month < 1 or month > 12:
        raise AuthValidationError("올바른 출생 월을 입력해 주세요.")
    max_day = monthrange(year, month)[1]
    if day < 1 or day > max_day:
        raise AuthValidationError("올바른 출생 일을 입력해 주세요.")
    if date(year, month, day) > today:
        raise AuthValidationError("출생일은 오늘 이전이어야 합니다.")


def register_user(
    *,
    username: str,
    email: str,
    password: str,
    password_confirm: str,
    name: str,
    phone: str = "",
    birth_year: str = "",
    birth_month: str = "",
    birth_day: str = "",
    calendar_type: str = "solar",
    region: str = "",
    agree_sms: bool = False,
    agree_email: bool = False,
) -> User:
    """신규 회원 생성."""
    username = username.strip().lower()
    email = email.strip().lower()
    name = name.strip()
    phone = phone.strip()
    region = region.strip()

    if not _USERNAME_RE.match(username):
        raise AuthValidationError("아이디는 영문 소문자·숫자·_ 조합 4~16자입니다.")
    if len(password) < 8:
        raise AuthValidationError("비밀번호는 8자 이상 입력해 주세요.")
    if password != password_confirm:
        raise AuthValidationError("비밀번호 확인이 일치하지 않습니다.")
    if not name:
        raise AuthValidationError("이름을 입력해 주세요.")
    if "@" not in email:
        raise AuthValidationError("올바른 이메일을 입력해 주세요.")
    if not phone:
        raise AuthValidationError("휴대폰 번호를 입력해 주세요.")
    if not _PHONE_RE.match(_normalize_phone(phone)):
        raise AuthValidationError("휴대폰 번호 형식을 확인해 주세요.")

    if not birth_year or not birth_month or not birth_day:
        raise AuthValidationError("생년월일을 입력해 주세요.")
    try:
        year = int(birth_year)
        month = int(birth_month)
        day = int(birth_day)
    except ValueError as exc:
        raise AuthValidationError("생년월일은 숫자로 입력해 주세요.") from exc
    _validate_birth(year, month, day)

    if calendar_type not in {"solar", "lunar"}:
        raise AuthValidationError("생년월일 구분을 선택해 주세요.")
    if not region or region not in KOREA_REGIONS:
        raise AuthValidationError("지역을 선택해 주세요.")

    if User.query.filter_by(username=username).first():
        raise AuthValidationError("이미 사용 중인 아이디입니다.")
    if User.query.filter_by(email=email).first():
        raise AuthValidationError("이미 가입된 이메일입니다.")

    user = User(
        username=username,
        email=email,
        full_name=name,
        phone=phone,
        birth_year=year,
        birth_month=month,
        birth_day=day,
        calendar_type=calendar_type,
        region=region,
        agree_sms=agree_sms,
        agree_email=agree_email,
    )
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    from services.benefits_service import issue_welcome_benefits

    issue_welcome_benefits(user.id)
    return user


def _find_user_by_contact(*, name: str, method: str, contact: str) -> User | None:
    """이름 + 이메일/휴대폰으로 회원 조회."""
    name = name.strip()
    contact = contact.strip()
    if not name or not contact:
        return None

    query = User.query.filter(User.is_active.is_(True))

    if method == "phone":
        normalized = _normalize_phone(contact)
        for user in query.filter(User.phone.isnot(None)).all():
            if not user.phone:
                continue
            if _normalize_phone(user.phone) != normalized:
                continue
            if not user.full_name or user.full_name != name:
                continue
            return user
        return None

    user = query.filter(User.email == contact.lower()).first()
    if not user:
        return None
    if not user.full_name or user.full_name != name:
        return None
    return user


def find_username(*, name: str, method: str, contact: str) -> str | None:
    """이름 + 이메일/휴대폰으로 아이디 조회."""
    user = _find_user_by_contact(name=name, method=method, contact=contact)
    return user.username if user else None


def verify_user_for_password_reset(
    *,
    username: str,
    name: str,
    method: str,
    contact: str,
) -> User | None:
    """비밀번호 재설정을 위한 본인 확인."""
    username = username.strip().lower()
    name = name.strip()
    contact = contact.strip()
    if not username or not name or not contact:
        return None

    user = User.query.filter_by(username=username, is_active=True).first()
    if not user or not user.full_name or user.full_name != name:
        return None

    if method == "phone":
        if not user.phone:
            return None
        return user if _normalize_phone(user.phone) == _normalize_phone(contact) else None

    return user if user.email.lower() == contact.lower() else None


def start_password_reset_session(user: User) -> None:
    """본인 확인 완료 후 비밀번호 재설정 세션 시작."""
    session[PASSWORD_RESET_SESSION_KEY] = user.id
    session[PASSWORD_RESET_SESSION_TS_KEY] = time.time()


def get_password_reset_user() -> User | None:
    """세션에 저장된 비밀번호 재설정 대상 회원."""
    user_id = session.get(PASSWORD_RESET_SESSION_KEY)
    started_at = session.get(PASSWORD_RESET_SESSION_TS_KEY)
    if not user_id or not started_at:
        return None
    if time.time() - float(started_at) > PASSWORD_RESET_TTL_SECONDS:
        clear_password_reset_session()
        return None

    user = db.session.get(User, int(user_id))
    if not user or not user.is_active:
        clear_password_reset_session()
        return None
    return user


def clear_password_reset_session() -> None:
    session.pop(PASSWORD_RESET_SESSION_KEY, None)
    session.pop(PASSWORD_RESET_SESSION_TS_KEY, None)


def reset_password(*, password: str, password_confirm: str) -> User:
    """세션 검증 후 비밀번호를 실제로 변경."""
    user = get_password_reset_user()
    if not user:
        raise AuthValidationError("본인 확인이 만료되었습니다. 처음부터 다시 진행해 주세요.")
    if len(password) < 8:
        raise AuthValidationError("비밀번호는 8자 이상 입력해 주세요.")
    if password != password_confirm:
        raise AuthValidationError("비밀번호 확인이 일치하지 않습니다.")

    user.set_password(password)
    db.session.commit()
    clear_password_reset_session()
    return user
