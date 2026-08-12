"""
주문 생성·결제 완료 처리.
"""

from __future__ import annotations

from datetime import datetime

from flask_login import current_user

from extensions import db
from models import Order, OrderItem, OrderStatus, Product, User
from services.cart_service import (
    CartLine,
    compute_cart_totals,
    get_cart_lines,
)
from services.coupon_service import CouponApplication, apply_coupon_for_order, mark_coupon_used
from services.point_service import (
    earn_purchase_points,
    has_point_usage_for_order,
    use_points,
    validate_point_usage,
)


class OrderValidationError(ValueError):
    """주문 검증 실패."""


def _guest_user_id() -> int:
    guest = User.query.filter_by(email="guest@shop.local").first()
    if guest:
        return guest.id

    guest = User(
        username="guest_checkout",
        email="guest@shop.local",
        full_name="비회원",
        phone="010-0000-0000",
    )
    guest.set_password("guest-not-for-login")
    db.session.add(guest)
    db.session.commit()
    return guest.id


def _generate_order_number() -> str:
    stamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    suffix = datetime.utcnow().microsecond % 1000
    return f"MC{stamp}{suffix:03d}"


def get_lines_for_checkout(product_ids: list[int] | None = None) -> list[CartLine]:
    lines = get_cart_lines()
    if not product_ids:
        return lines
    id_set = set(product_ids)
    return [line for line in lines if line.product.id in id_set]


def calculate_order_totals(
    *,
    lines: list[CartLine],
    user_coupon_id: int | None = None,
    point_used: int = 0,
    user_id: int | None = None,
) -> dict:
    """주문 금액 미리 계산."""
    cart_totals = compute_cart_totals(lines)
    product_total = cart_totals["product_total"]
    original_total = cart_totals["original_total"]
    discount_total = cart_totals["discount_total"]
    base_shipping_fee = cart_totals["shipping_fee"]
    shipping_fee = base_shipping_fee
    coupon_discount = 0
    shipping_discount = 0
    coupon_app: CouponApplication | None = None

    if user_coupon_id and user_id:
        coupon_app = apply_coupon_for_order(
            user_id=user_id,
            user_coupon_id=user_coupon_id,
            product_total=product_total,
            shipping_fee=base_shipping_fee,
        )
        coupon_discount = coupon_app.product_discount
        shipping_discount = coupon_app.shipping_discount
        shipping_fee = max(base_shipping_fee - shipping_discount, 0)

    payable_product = max(product_total - coupon_discount, 0)
    if user_id and point_used > 0:
        point_used = validate_point_usage(
            user_id,
            point_used,
            max_usable=payable_product,
        )

    total_amount = max(payable_product - point_used, 0) + shipping_fee
    return {
        "original_total": original_total,
        "product_total": product_total,
        "discount_total": discount_total,
        "base_shipping_fee": base_shipping_fee,
        "shipping_fee": shipping_fee,
        "coupon_discount": coupon_discount,
        "shipping_discount": shipping_discount,
        "point_used": point_used,
        "total_amount": total_amount,
        "coupon_app": coupon_app,
    }


def create_pending_order(
    *,
    lines: list[CartLine],
    recipient_name: str,
    recipient_phone: str,
    shipping_address: str,
    shipping_memo: str = "",
    user_coupon_id: int | None = None,
    point_used: int = 0,
) -> Order:
    recipient_name = recipient_name.strip()
    recipient_phone = recipient_phone.strip()
    shipping_address = shipping_address.strip()
    shipping_memo = shipping_memo.strip()

    if not lines:
        raise OrderValidationError("주문할 상품이 없습니다.")
    if not recipient_name:
        raise OrderValidationError("수령인 이름을 입력해 주세요.")
    if not recipient_phone:
        raise OrderValidationError("연락처를 입력해 주세요.")
    if not shipping_address:
        raise OrderValidationError("배송지 주소를 입력해 주세요.")

    is_member = current_user.is_authenticated
    user_id = current_user.id if is_member else _guest_user_id()

    try:
        point_used = int(point_used or 0)
    except (TypeError, ValueError):
        point_used = 0

    totals = calculate_order_totals(
        lines=lines,
        user_coupon_id=user_coupon_id,
        point_used=point_used,
        user_id=user_id if is_member else None,
    )

    order = Order(
        user_id=user_id,
        order_number=_generate_order_number(),
        status=OrderStatus.PENDING,
        product_total=totals["product_total"],
        shipping_fee=totals["shipping_fee"],
        coupon_discount=totals["coupon_discount"],
        point_used=totals["point_used"],
        total_amount=totals["total_amount"],
        recipient_name=recipient_name,
        recipient_phone=recipient_phone,
        shipping_address=shipping_address,
        shipping_memo=shipping_memo or None,
    )
    db.session.add(order)
    db.session.flush()

    for line in lines:
        db.session.add(
            OrderItem(
                order_id=order.id,
                product_id=line.product.id,
                product_name=line.product.name,
                unit_price=line.product.sale_price,
                quantity=line.quantity,
                subtotal=line.subtotal,
            )
        )

    if totals["coupon_app"]:
        order.user_coupon_id = totals["coupon_app"].user_coupon.id

    db.session.commit()
    return order


def get_order_by_number(order_number: str) -> Order | None:
    return Order.query.filter_by(order_number=order_number).first()


def complete_order_payment(
    *,
    order: Order,
    payment_key: str,
    payment_method: str,
    amount: int,
) -> Order:
    if order.status == OrderStatus.PAID:
        return order

    if order.status != OrderStatus.PENDING:
        raise OrderValidationError("결제할 수 없는 주문 상태입니다.")

    if amount != order.total_amount:
        raise OrderValidationError("결제 금액이 주문 금액과 일치하지 않습니다.")

    order.status = OrderStatus.PAID
    order.payment_key = payment_key
    order.payment_method = payment_method
    order.paid_at = datetime.utcnow()
    db.session.commit()

    if order.user_coupon_id:
        from models import UserCoupon

        user_coupon = UserCoupon.query.get(order.user_coupon_id)
        if user_coupon and user_coupon.used_at is None:
            mark_coupon_used(user_coupon=user_coupon, order=order)

    guest = User.query.filter_by(email="guest@shop.local").first()

    if guest is None or order.user_id != guest.id:
        if order.point_used > 0 and not has_point_usage_for_order(order.id):
            use_points(
                order.user_id,
                order.point_used,
                f"주문 사용 ({order.order_number})",
                order_id=order.id,
            )

        earn_purchase_points(
            user_id=order.user_id,
            order_id=order.id,
            product_total=max(
                order.product_total
                - order.coupon_discount
                - order.point_used,
                0,
            ),
        )

    from flask import session

    from services.cart_service import clear_cart_for_user

    product_ids = [item.product_id for item in order.items]
    if guest and order.user_id == guest.id:
        cart = session.get("cart") or {}
        changed = False
        for product_id in product_ids:
            key = str(product_id)
            if key in cart:
                cart.pop(key)
                changed = True
        if changed:
            session["cart"] = cart
            session.modified = True
    else:
        clear_cart_for_user(order.user_id, product_ids)
    return order


CANCELLABLE_STATUSES = {
    OrderStatus.PENDING,
    OrderStatus.PAID,
    OrderStatus.PREPARING,
}


def cancel_order_by_user(*, order: Order, user_id: int) -> Order:
    """회원 주문 취소."""
    if order.user_id != user_id:
        raise OrderValidationError("본인 주문만 취소할 수 있습니다.")
    if order.status not in CANCELLABLE_STATUSES:
        raise OrderValidationError("취소할 수 없는 주문 상태입니다.")

    was_paid = order.status in {OrderStatus.PAID, OrderStatus.PREPARING}

    order.status = OrderStatus.CANCELLED
    db.session.commit()

    if was_paid:
        from services.coupon_service import restore_coupon_for_order
        from services.point_service import reverse_order_points

        restore_coupon_for_order(order)
        reverse_order_points(user_id=user_id, order=order)

    return order
