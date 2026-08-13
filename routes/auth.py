"""
회원 인증 라우트 — 로그인·회원가입·계정 찾기.
"""

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user
from sqlalchemy.exc import IntegrityError

from extensions import db
from services.auth_service import (
    AuthValidationError,
    clear_password_reset_session,
    find_username,
    get_password_reset_user,
    register_user,
    reset_password,
    start_password_reset_session,
    verify_user_for_password_reset,
)
from services.guest_order_service import find_guest_order
from services.register_options import EMPTY_REGISTER_FORM, KOREA_REGIONS
from services.social_auth_service import (
    SocialAuthError,
    apple_authorize_url,
    fetch_apple_profile,
    fetch_kakao_profile,
    find_or_create_social_user,
    is_apple_enabled,
    is_apple_oauth_enabled,
    is_kakao_enabled,
    is_social_demo_enabled,
    kakao_authorize_url,
    login_demo_social_user,
    pop_oauth_next,
    store_oauth_state,
    verify_oauth_state,
)

from models import User

auth_bp = Blueprint("auth", __name__)

_EMPTY_GUEST_FORM = {"recipient_name": "", "order_number": ""}
_EMPTY_FIND_FORM = {"name": "", "contact": "", "username": ""}


def _safe_next_url(raw: str | None) -> str:
    """내부 경로만 허용."""
    url = (raw or "").strip()
    if url.startswith("/") and not url.startswith("//"):
        return url
    return ""


def _auth_template_context(**extra):
    next_url = _safe_next_url(request.args.get("next"))
    return {
        "kakao_login_enabled": is_kakao_enabled(),
        "apple_login_enabled": is_apple_enabled(),
        "social_demo_mode": is_social_demo_enabled(),
        "next_url": next_url,
        **extra,
    }


def _social_login_redirect(user: User, *, created: bool) -> str:
    next_url = request.args.get("next", "")
    if next_url and next_url.startswith("/"):
        store_oauth_state(next_url=next_url)
    return redirect(_complete_social_login(user, created=created))


def _complete_social_login(user: User, *, created: bool) -> str:
    login_user(user)
    from services.user_session_service import on_user_login

    on_user_login(user.id)
    if created:
        flash(
            f"{user.full_name or user.username}님, 가입을 환영합니다! 10,000원 할인 쿠폰이 발급되었습니다.",
            "success",
        )
    else:
        flash(f"{user.full_name or user.username}님, 환영합니다!", "success")
    next_url = pop_oauth_next()
    return next_url or url_for("main.index")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """로그인 페이지."""
    if current_user.is_authenticated:
        next_url = request.args.get("next", "")
        if next_url.startswith("/"):
            return redirect(next_url)
        if current_user.is_admin:
            return redirect(url_for("admin.dashboard"))
        return redirect(url_for("main.index"))

    if request.method == "POST":
        login_id = request.form.get("login_id", "").strip()
        password = request.form.get("password", "")

        normalized_id = login_id.lower()
        user = User.query.filter(
            User.is_active.is_(True),
            (User.email == normalized_id) | (User.username == normalized_id),
        ).first()

        if user and user.check_password(password):
            remember = request.form.get("remember") == "on"
            login_user(user, remember=remember)
            from services.user_session_service import on_user_login

            on_user_login(user.id)
            next_url = _safe_next_url(request.args.get("next") or request.form.get("next"))
            if next_url:
                return redirect(next_url)
            return redirect(url_for("main.index"))

        flash("아이디 또는 비밀번호가 올바르지 않습니다.", "error")

    return render_template("auth/login.html", **_auth_template_context())


@auth_bp.route("/auth/kakao")
def kakao_login():
    """카카오 OAuth 시작."""
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    if is_social_demo_enabled():
        user, created = login_demo_social_user("kakao")
        return _social_login_redirect(user, created=created)

    if not (current_app.config.get("KAKAO_REST_API_KEY") or "").strip():
        flash("카카오 로그인 API 키가 설정되지 않았습니다. `.env`에 KAKAO_REST_API_KEY를 추가해 주세요.", "error")
        return redirect(request.referrer or url_for("auth.login"))

    state = store_oauth_state(next_url=request.args.get("next", ""))
    return redirect(kakao_authorize_url(state=state))


@auth_bp.route("/auth/kakao/callback")
def kakao_callback():
    """카카오 OAuth 콜백."""
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    error = request.args.get("error")
    if error:
        flash("카카오 로그인이 취소되었습니다.", "error")
        return redirect(url_for("auth.login"))

    try:
        verify_oauth_state(request.args.get("state"))
        code = request.args.get("code", "")
        if not code:
            raise SocialAuthError("카카오 인증 코드가 없습니다.")
        profile = fetch_kakao_profile(code)
        user, created = find_or_create_social_user(profile)
    except SocialAuthError as exc:
        flash(str(exc), "error")
        return redirect(url_for("auth.login"))

    return redirect(_complete_social_login(user, created=created))


@auth_bp.route("/auth/apple")
def apple_login():
    """Apple OAuth 시작."""
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    if is_social_demo_enabled():
        user, created = login_demo_social_user("apple")
        return _social_login_redirect(user, created=created)

    if not is_apple_oauth_enabled():
        flash("Apple 로그인 키가 설정되지 않았습니다. `.env`에 Apple Developer 설정을 추가해 주세요.", "error")
        return redirect(request.referrer or url_for("auth.login"))

    state = store_oauth_state(next_url=request.args.get("next", ""))
    return redirect(apple_authorize_url(state=state))


@auth_bp.route("/auth/apple/callback", methods=["GET", "POST"])
def apple_callback():
    """Apple OAuth 콜백 (form_post)."""
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    error = request.values.get("error")
    if error:
        flash("Apple 로그인이 취소되었습니다.", "error")
        return redirect(url_for("auth.login"))

    try:
        verify_oauth_state(request.values.get("state"))
        code = request.values.get("code", "")
        if not code:
            raise SocialAuthError("Apple 인증 코드가 없습니다.")
        profile = fetch_apple_profile(code, user_payload=request.values.get("user"))
        user, created = find_or_create_social_user(profile)
    except SocialAuthError as exc:
        flash(str(exc), "error")
        return redirect(url_for("auth.login"))

    return redirect(_complete_social_login(user, created=created))


@auth_bp.route("/logout")
def logout():
    """로그아웃."""
    logout_user()
    return redirect(url_for("main.index"))


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """회원가입."""
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    next_url = _safe_next_url(request.args.get("next") or request.form.get("next"))

    if request.method == "POST":
        form = {
            "username": request.form.get("username", "").strip(),
            "email": request.form.get("email", "").strip(),
            "name": request.form.get("name", "").strip(),
            "phone": request.form.get("phone", "").strip(),
            "birth_year": request.form.get("birth_year", "").strip(),
            "birth_month": request.form.get("birth_month", "").strip(),
            "birth_day": request.form.get("birth_day", "").strip(),
            "calendar_type": request.form.get("calendar_type", "solar"),
            "region": request.form.get("region", "서울").strip(),
        }
        if request.form.get("agree_terms") != "on":
            flash("이용약관에 동의해 주세요.", "error")
            return render_template(
                "auth/register.html",
                **_auth_template_context(form=form, regions=KOREA_REGIONS, next_url=next_url),
            )
        if request.form.get("agree_privacy") != "on":
            flash("개인정보 수집·이용에 동의해 주세요.", "error")
            return render_template(
                "auth/register.html",
                **_auth_template_context(form=form, regions=KOREA_REGIONS, next_url=next_url),
            )

        try:
            user = register_user(
                username=form["username"],
                email=form["email"],
                password=request.form.get("password", ""),
                password_confirm=request.form.get("password_confirm", ""),
                name=form["name"],
                phone=form["phone"],
                birth_year=form["birth_year"],
                birth_month=form["birth_month"],
                birth_day=form["birth_day"],
                calendar_type=form["calendar_type"],
                region=form["region"],
                agree_sms=request.form.get("agree_sms") == "on",
                agree_email=request.form.get("agree_email") == "on",
            )
        except AuthValidationError as exc:
            flash(str(exc), "error")
            return render_template(
                "auth/register.html",
                **_auth_template_context(form=form, regions=KOREA_REGIONS, next_url=next_url),
            )
        except IntegrityError:
            db.session.rollback()
            flash("이미 사용 중인 아이디 또는 이메일입니다.", "error")
            return render_template(
                "auth/register.html",
                **_auth_template_context(form=form, regions=KOREA_REGIONS, next_url=next_url),
            )

        login_user(user)
        flash(
            f"{user.full_name or user.username}님, 가입을 환영합니다! 10,000원 할인 쿠폰이 발급되었습니다.",
            "success",
        )
        return redirect(next_url or url_for("main.index"))

    return render_template(
        "auth/register.html",
        **_auth_template_context(form=EMPTY_REGISTER_FORM, regions=KOREA_REGIONS, next_url=next_url),
    )


@auth_bp.route("/find-id", methods=["GET", "POST"])
def find_id():
    """아이디 찾기."""
    if request.method == "POST":
        form = {
            "name": request.form.get("name", "").strip(),
            "contact": request.form.get("contact", "").strip(),
        }
        method = request.form.get("verify_method", "email")
        username = find_username(name=form["name"], method=method, contact=form["contact"])

        if username:
            return render_template(
                "auth/find_id.html",
                form=form,
                result_username=username,
            )

        flash("입력하신 이름과 연락처가 일치하는 회원을 찾을 수 없습니다.", "error")
        return render_template("auth/find_id.html", form=form)

    return render_template("auth/find_id.html", form=_EMPTY_FIND_FORM, result_username=None)


@auth_bp.route("/find-password", methods=["GET", "POST"])
def find_password():
    """비밀번호 찾기 — 본인 확인 후 비밀번호 재설정."""
    reset_user = get_password_reset_user()

    if request.method == "POST":
        step = request.form.get("step", "verify")

        if step == "reset":
            form = {
                "username": request.form.get("username", "").strip(),
                "name": request.form.get("name", "").strip(),
                "contact": request.form.get("contact", "").strip(),
            }
            try:
                user = reset_password(
                    password=request.form.get("new_password", ""),
                    password_confirm=request.form.get("new_password_confirm", ""),
                )
            except AuthValidationError as exc:
                flash(str(exc), "error")
                return render_template(
                    "auth/find_password.html",
                    form=form,
                    reset_verified=True,
                    verified_username=reset_user.username if reset_user else form["username"],
                )

            flash(f"{user.full_name or user.username}님, 비밀번호가 변경되었습니다. 새 비밀번호로 로그인해 주세요.", "success")
            return redirect(url_for("auth.login"))

        form = {
            "username": request.form.get("username", "").strip(),
            "name": request.form.get("name", "").strip(),
            "contact": request.form.get("contact", "").strip(),
        }
        method = request.form.get("verify_method", "email")
        user = verify_user_for_password_reset(
            username=form["username"],
            name=form["name"],
            method=method,
            contact=form["contact"],
        )

        if user:
            start_password_reset_session(user)
            return render_template(
                "auth/find_password.html",
                form=form,
                reset_verified=True,
                verified_username=user.username,
            )

        flash("입력하신 정보와 일치하는 계정을 찾을 수 없습니다.", "error")
        return render_template("auth/find_password.html", form=form)

    if reset_user:
        return render_template(
            "auth/find_password.html",
            form={"username": reset_user.username, "name": reset_user.full_name or "", "contact": ""},
            reset_verified=True,
            verified_username=reset_user.username,
        )

    clear_password_reset_session()
    return render_template(
        "auth/find_password.html",
        form=_EMPTY_FIND_FORM,
        reset_verified=False,
    )


@auth_bp.route("/guest-order", methods=["GET", "POST"])
def guest_order():
    """비회원 주문 조회."""
    if request.method == "POST":
        recipient_name = request.form.get("recipient_name", "").strip()
        order_number = request.form.get("order_number", "").strip()
        guest_password = request.form.get("guest_password", "")

        order = find_guest_order(
            recipient_name=recipient_name,
            order_number=order_number,
            guest_password=guest_password,
        )
        if order:
            return render_template("auth/guest_order_result.html", order=order)

        flash("주문 정보를 찾을 수 없습니다. 입력값을 다시 확인해 주세요.", "error")
        return render_template(
            "auth/guest_order.html",
            form={
                "recipient_name": recipient_name,
                "order_number": order_number,
            },
        )

    return render_template("auth/guest_order.html", form=_EMPTY_GUEST_FORM)
