"""멤버십 등급 계산."""

from models import Order, OrderStatus


def paid_order_count(user_id: int) -> int:
    return (
        Order.query.filter(
            Order.user_id == user_id,
            Order.status.notin_([OrderStatus.PENDING, OrderStatus.CANCELLED]),
        ).count()
    )


def membership_label(user_id: int) -> str:
    count = paid_order_count(user_id)
    if count >= 5:
        return "MOOD VIP"
    if count >= 1:
        return "MEMBER"
    return "WELCOME"
