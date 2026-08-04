"""비회원 주문 조회."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GuestOrderItem:
    product_name: str
    quantity: int
    subtotal: int


@dataclass(frozen=True)
class GuestOrder:
    order_number: str
    recipient_name: str
    guest_password: str
    status_label: str
    total_amount: int
    recipient_phone: str
    shipping_address: str
    items: tuple[GuestOrderItem, ...]


GUEST_ORDERS: tuple[GuestOrder, ...] = (
    GuestOrder(
        order_number="MC20260801001",
        recipient_name="홍길동",
        guest_password="1234",
        status_label="배송 중",
        total_amount=916000,
        recipient_phone="010-1234-5678",
        shipping_address="서울특별시 강남구 테헤란로 123 Mood Code 빌딩 101호",
        items=(
            GuestOrderItem("펜던트 조명", 1, 128000),
            GuestOrderItem("모던 패브릭 3인 소파", 1, 790000),
        ),
    ),
    GuestOrder(
        order_number="MC20260801002",
        recipient_name="김무드",
        guest_password="mood1234",
        status_label="결제 완료",
        total_amount=169000,
        recipient_phone="010-9876-5432",
        shipping_address="경기도 성남시 분당구 정자동 12-3",
        items=(
            GuestOrderItem("원목 사이드 테이블", 1, 169000),
        ),
    ),
)


def find_guest_order(
    *,
    recipient_name: str,
    order_number: str,
    guest_password: str,
) -> GuestOrder | None:
    """주문자명·주문번호·비밀번호로 비회원 주문 조회."""
    name = recipient_name.strip()
    number = order_number.strip().upper()
    password = guest_password.strip()

    if not name or not number or not password:
        return None

    for order in GUEST_ORDERS:
        if (
            order.recipient_name == name
            and order.order_number.upper() == number
            and order.guest_password == password
        ):
            return order
    return None
