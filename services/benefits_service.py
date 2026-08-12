"""
회원 혜택 — 쿠폰 시드·가입 웰컴 혜택.
"""

from __future__ import annotations

from datetime import datetime

from extensions import db
from models import Coupon, UserCoupon
from services.coupon_service import issue_coupon_to_user
from services.point_service import add_points


def ensure_default_coupons() -> None:
    """기본 쿠폰 템플릿 생성."""
    expires = datetime(2026, 12, 31, 23, 59, 59)
    templates = [
        {
            "code": "WELCOME10",
            "title": "웰컴 10% 할인",
            "description": "Mood Code 첫 구매를 위한 웰컴 쿠폰",
            "discount_type": "percent",
            "discount_value": 10,
            "min_amount": 100_000,
        },
        {
            "code": "MOODSHIP",
            "title": "무료 배송 쿠폰",
            "description": "30만원 미만 주문 시 배송비 면제",
            "discount_type": "shipping",
            "discount_value": 0,
            "min_amount": 50_000,
        },
        {
            "code": "MEMBER5",
            "title": "멤버 5% 추가 할인",
            "description": "누적 구매 회원 전용 할인",
            "discount_type": "percent",
            "discount_value": 5,
            "min_amount": 200_000,
        },
        {
            "code": "VIP15",
            "title": "VIP 15% 프리미엄 할인",
            "description": "MOOD VIP 전용 시즌 쿠폰",
            "discount_type": "percent",
            "discount_value": 15,
            "min_amount": 300_000,
        },
        {
            "code": "VIPSHIP",
            "title": "VIP 무료 배송",
            "description": "금액 제한 없이 무료 배송",
            "discount_type": "shipping",
            "discount_value": 0,
            "min_amount": 0,
        },
    ]

    for item in templates:
        coupon = Coupon.query.filter_by(code=item["code"]).first()
        if coupon:
            continue
        db.session.add(
            Coupon(
                **item,
                expires_at=expires,
                is_active=True,
            )
        )
    db.session.commit()


def issue_welcome_benefits(user_id: int) -> None:
    """신규 가입 웰컴 쿠폰 지급."""
    issue_coupon_to_user(user_id, "WELCOME10K")
    issue_coupon_to_user(user_id, "MOODSHIP")
