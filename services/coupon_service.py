"""
쿠폰 발급·적용.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from extensions import db
from models import Coupon, Order, UserCoupon
from services.membership_service import membership_label


class CouponError(ValueError):
    """쿠폰 검증 실패."""


@dataclass
class CouponPreview:
    """마이페이지·주문 화면용 쿠폰."""

    user_coupon_id: int
    code: str
    title: str
    description: str
    discount_label: str
    min_amount: int
    expires_at: str
    is_usable: bool


@dataclass
class CouponApplication:
    """주문에 적용된 쿠폰 결과."""

    user_coupon: UserCoupon
    product_discount: int
    shipping_discount: int


def _discount_label(coupon: Coupon) -> str:
    if coupon.discount_type == "percent":
        return f"{coupon.discount_value}%"
    if coupon.discount_type == "shipping":
        return "배송비"
    return f"{coupon.discount_value:,}원"


def issue_coupon_to_user(user_id: int, coupon_code: str) -> UserCoupon | None:
    """쿠폰 발급 (중복 발급 방지)."""
    coupon = Coupon.query.filter_by(code=coupon_code, is_active=True).first()
    if not coupon:
        return None

    existing = UserCoupon.query.filter_by(user_id=user_id, coupon_id=coupon.id).first()
    if existing:
        return existing

    user_coupon = UserCoupon(user_id=user_id, coupon_id=coupon.id)
    db.session.add(user_coupon)
    db.session.commit()
    return user_coupon


def ensure_tier_coupons(user_id: int) -> None:
    """등급별 쿠폰 자동 발급."""
    label = membership_label(user_id)
    if label == "MEMBER":
        issue_coupon_to_user(user_id, "MEMBER5")
    elif label == "MOOD VIP":
        issue_coupon_to_user(user_id, "MEMBER5")
        issue_coupon_to_user(user_id, "VIP15")
        issue_coupon_to_user(user_id, "VIPSHIP")


def get_user_coupon_rows(user_id: int) -> list[UserCoupon]:
    """회원 보유 쿠폰 (미사용·유효)."""
    ensure_tier_coupons(user_id)
    now = datetime.utcnow()
    rows = (
        UserCoupon.query.filter_by(user_id=user_id)
        .join(Coupon)
        .filter(UserCoupon.used_at.is_(None), Coupon.is_active.is_(True))
        .order_by(Coupon.expires_at.asc())
        .all()
    )
    return [row for row in rows if row.coupon.expires_at >= now]


def get_coupon_previews(user_id: int) -> list[CouponPreview]:
    """마이페이지 표시용."""
    previews: list[CouponPreview] = []
    for row in get_user_coupon_rows(user_id):
        coupon = row.coupon
        previews.append(
            CouponPreview(
                user_coupon_id=row.id,
                code=coupon.code,
                title=coupon.title,
                description=coupon.description or "",
                discount_label=_discount_label(coupon),
                min_amount=coupon.min_amount,
                expires_at=coupon.expires_at.strftime("%Y.%m.%d"),
                is_usable=True,
            )
        )
    return previews


def calculate_coupon_application(
    *,
    user_coupon: UserCoupon,
    product_total: int,
    shipping_fee: int,
) -> CouponApplication:
    """쿠폰 할인 금액 계산."""
    coupon = user_coupon.coupon
    now = datetime.utcnow()

    if user_coupon.used_at is not None:
        raise CouponError("이미 사용한 쿠폰입니다.")
    if not coupon.is_active or coupon.expires_at < now:
        raise CouponError("사용할 수 없는 쿠폰입니다.")
    if product_total < coupon.min_amount:
        raise CouponError(
            f"최소 주문 금액 {coupon.min_amount:,}원 이상일 때 사용할 수 있습니다."
        )

    product_discount = 0
    shipping_discount = 0

    if coupon.discount_type == "percent":
        product_discount = min(product_total * coupon.discount_value // 100, product_total)
    elif coupon.discount_type == "fixed":
        product_discount = min(coupon.discount_value, product_total)
    elif coupon.discount_type == "shipping":
        shipping_discount = shipping_fee

    return CouponApplication(
        user_coupon=user_coupon,
        product_discount=product_discount,
        shipping_discount=shipping_discount,
    )


def apply_coupon_for_order(
    *,
    user_id: int,
    user_coupon_id: int,
    product_total: int,
    shipping_fee: int,
) -> CouponApplication:
    """주문에 사용할 쿠폰 검증."""
    row = (
        UserCoupon.query.filter_by(id=user_coupon_id, user_id=user_id)
        .join(Coupon)
        .first()
    )
    if not row:
        raise CouponError("쿠폰을 찾을 수 없습니다.")
    return calculate_coupon_application(
        user_coupon=row,
        product_total=product_total,
        shipping_fee=shipping_fee,
    )


def mark_coupon_used(*, user_coupon: UserCoupon, order: Order) -> None:
    """결제 완료 시 쿠폰 사용 처리."""
    user_coupon.used_at = datetime.utcnow()
    user_coupon.order_id = order.id
    order.user_coupon_id = user_coupon.id
    db.session.commit()


def restore_coupon_for_order(order: Order) -> None:
    """주문 취소 시 쿠폰 복원."""
    if not order.user_coupon_id:
        return
    user_coupon = UserCoupon.query.get(order.user_coupon_id)
    if not user_coupon:
        return
    user_coupon.used_at = None
    user_coupon.order_id = None
    db.session.commit()
