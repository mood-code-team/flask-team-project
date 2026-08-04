"""카카오·Apple 소셜 로그인."""

from __future__ import annotations

import hashlib
import secrets
import time
from dataclasses import dataclass
from urllib.parse import urlencode

import jwt
import requests
from flask import current_app, session, url_for

from extensions import db
from models import User


class SocialAuthError(ValueError):
    """소셜 로그인 처리 오류."""


OAUTH_STATE_KEY = "oauth_state"
OAUTH_NEXT_KEY = "oauth_next"

KAKAO_AUTH_URL = "https://kauth.kakao.com/oauth/authorize"
KAKAO_TOKEN_URL = "https://kauth.kakao.com/oauth/token"
KAKAO_USER_URL = "https://kapi.kakao.com/v2/user/me"

APPLE_AUTH_URL = "https://appleid.apple.com/auth/authorize"
APPLE_TOKEN_URL = "https://appleid.apple.com/auth/token"


@dataclass
class SocialProfile:
    provider: str
    provider_id: str
    email: str
    name: str
    phone: str = ""


def is_kakao_enabled() -> bool:
    if is_social_demo_enabled():
        return True
    return bool((current_app.config.get("KAKAO_REST_API_KEY") or "").strip())


def is_social_demo_enabled() -> bool:
    return bool(current_app.config.get("SOCIAL_DEMO_LOGIN"))


def is_apple_enabled() -> bool:
    if is_social_demo_enabled():
        return True
    return all(
        current_app.config.get(key)
        for key in ("APPLE_CLIENT_ID", "APPLE_TEAM_ID", "APPLE_KEY_ID", "APPLE_PRIVATE_KEY")
    )


def login_demo_social_user(provider: str) -> tuple[User, bool]:
    """카카오/Apple 콘솔 없이 데모 소셜 로그인."""
    profiles = {
        "kakao": SocialProfile(
            provider="kakao",
            provider_id="demo",
            email="kakao.demo@moodcode.local",
            name="카카오 데모",
            phone="01090000001",
        ),
        "apple": SocialProfile(
            provider="apple",
            provider_id="demo",
            email="apple.demo@moodcode.local",
            name="Apple 데모",
            phone="01090000002",
        ),
    }
    profile = profiles.get(provider)
    if not profile:
        raise SocialAuthError("지원하지 않는 소셜 로그인입니다.")
    return find_or_create_social_user(profile)


def is_apple_oauth_enabled() -> bool:
    return all(
        current_app.config.get(key)
        for key in ("APPLE_CLIENT_ID", "APPLE_TEAM_ID", "APPLE_KEY_ID", "APPLE_PRIVATE_KEY")
    )


def kakao_redirect_uri() -> str:
    configured = (current_app.config.get("KAKAO_REDIRECT_URI") or "").strip()
    if configured:
        return configured
    return url_for("auth.kakao_callback", _external=True)


def store_oauth_state(*, next_url: str = "") -> str:
    state = secrets.token_urlsafe(16)
    session[OAUTH_STATE_KEY] = state
    session[OAUTH_NEXT_KEY] = next_url if next_url.startswith("/") else ""
    return state


def pop_oauth_next() -> str:
    return session.pop(OAUTH_NEXT_KEY, "") or ""


def verify_oauth_state(state: str | None) -> None:
    expected = session.pop(OAUTH_STATE_KEY, None)
    if not expected or not state or expected != state:
        raise SocialAuthError("소셜 로그인 인증이 만료되었습니다. 다시 시도해 주세요.")


def kakao_authorize_url(*, state: str) -> str:
    redirect_uri = kakao_redirect_uri()
    params = {
        "client_id": current_app.config["KAKAO_REST_API_KEY"].strip(),
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "state": state,
    }
    # scope는 카카오 콘솔 [동의항목] 설정을 따릅니다. (미설정 scope 요청 시 KOE205)
    return f"{KAKAO_AUTH_URL}?{urlencode(params)}"


def apple_authorize_url(*, state: str) -> str:
    redirect_uri = url_for("auth.apple_callback", _external=True)
    params = {
        "client_id": current_app.config["APPLE_CLIENT_ID"],
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "response_mode": "form_post",
        "scope": "name email",
        "state": state,
    }
    return f"{APPLE_AUTH_URL}?{urlencode(params)}"


def _kakao_token(code: str) -> str:
    redirect_uri = kakao_redirect_uri()
    payload = {
        "grant_type": "authorization_code",
        "client_id": current_app.config["KAKAO_REST_API_KEY"].strip(),
        "redirect_uri": redirect_uri,
        "code": code,
    }
    client_secret = current_app.config.get("KAKAO_CLIENT_SECRET")
    if client_secret:
        payload["client_secret"] = client_secret

    response = requests.post(KAKAO_TOKEN_URL, data=payload, timeout=10)
    if response.status_code != 200:
        raise SocialAuthError("카카오 로그인 토큰 발급에 실패했습니다.")
    data = response.json()
    token = data.get("access_token")
    if not token:
        raise SocialAuthError("카카오 액세스 토큰을 받지 못했습니다.")
    return token


def fetch_kakao_profile(code: str) -> SocialProfile:
    token = _kakao_token(code)
    response = requests.get(
        KAKAO_USER_URL,
        headers={"Authorization": f"Bearer {token}"},
        timeout=10,
    )
    if response.status_code != 200:
        raise SocialAuthError("카카오 회원 정보를 가져오지 못했습니다.")

    data = response.json()
    provider_id = str(data.get("id", ""))
    if not provider_id:
        raise SocialAuthError("카카오 회원 정보가 올바르지 않습니다.")

    account = data.get("kakao_account") or {}
    profile = account.get("profile") or {}
    email = (account.get("email") or "").strip().lower()
    name = (profile.get("nickname") or "").strip()
    phone = (account.get("phone_number") or "").replace("+82 ", "0").replace("-", "")

    if not email:
        email = f"kakao_{provider_id}@social.moodcode.local"
    if not name:
        name = f"카카오회원{provider_id[-4:]}"

    return SocialProfile(
        provider="kakao",
        provider_id=provider_id,
        email=email,
        name=name,
        phone=phone,
    )


def _apple_client_secret() -> str:
    private_key = current_app.config["APPLE_PRIVATE_KEY"]
    if "\\n" in private_key:
        private_key = private_key.replace("\\n", "\n")

    now = int(time.time())
    headers = {"kid": current_app.config["APPLE_KEY_ID"], "alg": "ES256"}
    claims = {
        "iss": current_app.config["APPLE_TEAM_ID"],
        "iat": now,
        "exp": now + 60 * 60 * 24,
        "aud": "https://appleid.apple.com",
        "sub": current_app.config["APPLE_CLIENT_ID"],
    }
    return jwt.encode(claims, private_key, algorithm="ES256", headers=headers)


def _apple_token(code: str) -> dict:
    redirect_uri = url_for("auth.apple_callback", _external=True)
    payload = {
        "client_id": current_app.config["APPLE_CLIENT_ID"],
        "client_secret": _apple_client_secret(),
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": redirect_uri,
    }
    response = requests.post(APPLE_TOKEN_URL, data=payload, timeout=10)
    if response.status_code != 200:
        raise SocialAuthError("Apple 로그인 토큰 발급에 실패했습니다.")
    return response.json()


def fetch_apple_profile(code: str, *, user_payload: str | None = None) -> SocialProfile:
    import json

    token_data = _apple_token(code)
    id_token = token_data.get("id_token")
    if not id_token:
        raise SocialAuthError("Apple ID 토큰을 받지 못했습니다.")

    claims = jwt.decode(id_token, options={"verify_signature": False})
    provider_id = str(claims.get("sub", ""))
    email = (claims.get("email") or "").strip().lower()
    name = ""

    if user_payload:
        try:
            user_data = json.loads(user_payload)
            person = user_data.get("name") or {}
            first = (person.get("firstName") or "").strip()
            last = (person.get("lastName") or "").strip()
            name = f"{last}{first}".strip()
        except json.JSONDecodeError:
            name = ""

    if not provider_id:
        raise SocialAuthError("Apple 회원 정보가 올바르지 않습니다.")
    if not email:
        email = f"apple_{provider_id[:12]}@social.moodcode.local"
    if not name:
        name = f"Apple회원{provider_id[-4:]}"

    return SocialProfile(
        provider="apple",
        provider_id=provider_id,
        email=email,
        name=name,
    )


def _generate_username(provider: str, provider_id: str) -> str:
    if provider == "kakao":
        base = f"k{provider_id[-8:]}" if len(provider_id) >= 8 else f"k{provider_id}"
    else:
        digest = hashlib.sha256(provider_id.encode()).hexdigest()[:8]
        base = f"a{digest}"

    base = "".join(ch for ch in base.lower() if ch.isalnum() or ch == "_")[:16]
    if len(base) < 4:
        base = f"{provider[:1]}{base}0000"[:16]

    candidate = base
    suffix = 1
    while User.query.filter_by(username=candidate).first():
        tail = str(suffix)
        candidate = f"{base[: 16 - len(tail)]}{tail}"
        suffix += 1
    return candidate


def find_or_create_social_user(profile: SocialProfile) -> tuple[User, bool]:
    user = User.query.filter_by(
        auth_provider=profile.provider,
        auth_provider_id=profile.provider_id,
        is_active=True,
    ).first()
    if user:
        if profile.name and not user.full_name:
            user.full_name = profile.name
        if profile.phone and not user.phone:
            user.phone = profile.phone
        if profile.email and user.email.endswith("@social.moodcode.local"):
            existing_email = User.query.filter(
                User.email == profile.email,
                User.id != user.id,
            ).first()
            if not existing_email:
                user.email = profile.email
        db.session.commit()
        return user, False

    if profile.email and not profile.email.endswith("@social.moodcode.local"):
        by_email = User.query.filter_by(email=profile.email, is_active=True).first()
        if by_email:
            if by_email.auth_provider and by_email.auth_provider != profile.provider:
                raise SocialAuthError("이미 다른 방식으로 가입된 이메일입니다.")
            by_email.auth_provider = profile.provider
            by_email.auth_provider_id = profile.provider_id
            if profile.name and not by_email.full_name:
                by_email.full_name = profile.name
            db.session.commit()
            return by_email, False

    username = _generate_username(profile.provider, profile.provider_id)
    user = User(
        username=username,
        email=profile.email,
        full_name=profile.name,
        phone=profile.phone or None,
        region="서울",
        auth_provider=profile.provider,
        auth_provider_id=profile.provider_id,
    )
    user.set_password(secrets.token_urlsafe(32))
    db.session.add(user)
    db.session.commit()

    from services.benefits_service import issue_welcome_benefits

    issue_welcome_benefits(user.id)
    return user, True
