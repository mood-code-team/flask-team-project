"""기존 회원 혜택 보정."""

from models import PointLedger, UserCoupon
from services.benefits_service import issue_welcome_benefits
from services.cart_service import merge_session_cart_on_login
from services.coupon_service import ensure_tier_coupons


def ensure_user_benefits(user_id: int) -> None:
    """웰컴 혜택·등급 쿠폰 미발급 회원 보정."""
    has_coupons = UserCoupon.query.filter_by(user_id=user_id).first() is not None
    has_points = PointLedger.query.filter_by(user_id=user_id).first() is not None
    if not has_coupons and not has_points:
        issue_welcome_benefits(user_id)
    ensure_tier_coupons(user_id)


def on_user_login(user_id: int) -> None:
    merge_session_cart_on_login(user_id)
    ensure_user_benefits(user_id)
