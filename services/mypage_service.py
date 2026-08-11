"""
마이페이지 — 주문 현황·회원 요약.
"""

from __future__ import annotations

from dataclasses import dataclass

from models import Order, OrderStatus
from services.coupon_service import get_coupon_previews
from services.membership_service import membership_label, paid_order_count
from services.point_service import get_point_balance, get_point_history


@dataclass
class OrderStatusCounts:
    unpaid: int = 0
    preparing: int = 0
    shipping: int = 0
    delivered: int = 0
    cancelled: int = 0
    exchange: int = 0
    returned: int = 0


@dataclass
class MypageSummary:
    display_name: str
    membership_label: str
    coupon_count: int
    point_balance: int
    status_counts: OrderStatusCounts
    recent_orders: list[Order]


@dataclass
class MembershipInfo:
    label: str
    tagline: str
    benefits: list[str]
    next_tier: str | None
    orders_until_next: int


class ProfileUpdateError(Exception):
    """회원정보 수정 검증 오류."""


def get_mypage_summary(user_id: int, *, display_name: str) -> MypageSummary:
    orders = (
        Order.query.filter_by(user_id=user_id)
        .order_by(Order.created_at.desc())
        .all()
    )

    counts = OrderStatusCounts()
    for order in orders:
        if order.status == OrderStatus.PENDING:
            counts.unpaid += 1
        elif order.status in (OrderStatus.PAID, OrderStatus.PREPARING):
            counts.preparing += 1
        elif order.status == OrderStatus.SHIPPING:
            counts.shipping += 1
        elif order.status == OrderStatus.DELIVERED:
            counts.delivered += 1
        elif order.status == OrderStatus.CANCELLED:
            counts.cancelled += 1

    label = membership_label(user_id)
    coupons = get_coupon_previews(user_id)

    return MypageSummary(
        display_name=display_name,
        membership_label=label,
        coupon_count=len(coupons),
        point_balance=get_point_balance(user_id),
        status_counts=counts,
        recent_orders=orders[:5],
    )


def get_all_orders(user_id: int) -> list[Order]:
    return (
        Order.query.filter_by(user_id=user_id)
        .order_by(Order.created_at.desc())
        .all()
    )


def get_membership_info(user_id: int, label: str) -> MembershipInfo:
    paid_count = paid_order_count(user_id)

    tiers: dict[str, tuple[str, list[str], str | None, int]] = {
        "WELCOME": (
            "첫 방문을 환영합니다",
            [
                "신규 가입 10,000원 할인 쿠폰",
                "멤버 전용 찜(위시리스트)",
                "멤버 전용 기획전 알림",
            ],
            "MEMBER",
            max(1 - paid_count, 0),
        ),
        "MEMBER": (
            "Mood Code 멤버",
            [
                "구매 금액 1% 적립",
                "멤버 5% 추가 할인 쿠폰",
                "생일 월 특별 쿠폰",
                "신상품 사전 알림",
            ],
            "MOOD VIP",
            max(5 - paid_count, 0),
        ),
        "MOOD VIP": (
            "프리미엄 멤버십",
            [
                "구매 금액 1% 적립 + VIP 보너스",
                "VIP 15% 프리미엄 할인 쿠폰",
                "전 상품 무료 배송",
                "전용 CS 라인 · 우선 배송",
                "시즌 룩북 큐레이션",
            ],
            None,
            0,
        ),
    }

    tagline, benefits, next_tier, until_next = tiers.get(label, tiers["WELCOME"])
    return MembershipInfo(
        label=label,
        tagline=tagline,
        benefits=benefits,
        next_tier=next_tier,
        orders_until_next=until_next,
    )


def change_user_password(
    user,
    *,
    current_password: str,
    new_password: str,
    new_password_confirm: str,
) -> None:
    from extensions import db

    current_password = current_password.strip()
    new_password = new_password.strip()
    new_password_confirm = new_password_confirm.strip()

    if not current_password and not new_password and not new_password_confirm:
        return
    if not current_password:
        raise ProfileUpdateError("현재 비밀번호를 입력해 주세요.")
    if not user.check_password(current_password):
        raise ProfileUpdateError("현재 비밀번호가 올바르지 않습니다.")
    if len(new_password) < 8:
        raise ProfileUpdateError("새 비밀번호는 8자 이상이어야 합니다.")
    if new_password != new_password_confirm:
        raise ProfileUpdateError("새 비밀번호 확인이 일치하지 않습니다.")

    user.set_password(new_password)
    db.session.commit()


def update_user_profile(
    user,
    *,
    full_name: str,
    email: str,
    phone: str,
    region: str,
    address: str | None = None,
) -> None:
    from sqlalchemy.exc import IntegrityError

    from extensions import db

    full_name = full_name.strip()
    email = email.strip().lower()
    phone = phone.strip()
    region = region.strip()

    if not full_name:
        raise ProfileUpdateError("이름을 입력해 주세요.")
    if not email:
        raise ProfileUpdateError("이메일을 입력해 주세요.")
    if not phone:
        raise ProfileUpdateError("휴대폰 번호를 입력해 주세요.")
    if not region:
        raise ProfileUpdateError("지역을 선택해 주세요.")

    user.full_name = full_name
    user.email = email
    user.phone = phone
    user.region = region
    if address is not None:
        address = address.strip()
        if address:
            user.address = address

    try:
        db.session.commit()
    except IntegrityError as exc:
        db.session.rollback()
        raise ProfileUpdateError("이미 사용 중인 이메일입니다.") from exc


def update_shipping_address(user, *, address: str, phone: str | None = None) -> None:
    from extensions import db

    address = address.strip()
    if not address:
        raise ProfileUpdateError("배송지 주소를 입력해 주세요.")

    user.address = address
    if phone:
        user.phone = phone.strip()
    db.session.commit()

