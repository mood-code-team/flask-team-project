"""
결제 라우트 — 토스페이먼츠 연동.
"""

from __future__ import annotations

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user

from services.order_service import (
    OrderValidationError,
    complete_order_payment,
    get_order_by_number,
)
from services.toss_service import TossPaymentError, confirm_payment

payment_bp = Blueprint("payment", __name__)


def _order_title(order) -> str:
    if len(order.items) == 1:
        return order.items[0].product_name
    return f"{order.items[0].product_name} 외 {len(order.items) - 1}건"


@payment_bp.route("/payment/<order_number>")
def checkout(order_number: str):
    """토스 결제창 호출 페이지."""
    order = get_order_by_number(order_number)
    if not order:
        flash("주문을 찾을 수 없습니다.", "error")
        return redirect(url_for("cart.index"))
    if order.status != "pending":
        flash("이미 처리된 주문입니다.", "info")
        return redirect(url_for("main.index"))

    return render_template(
        "payment/checkout.html",
        order=order,
        order_title=_order_title(order),
        toss_client_key=current_app.config["TOSS_CLIENT_KEY"],
    )


@payment_bp.route("/payment/success")
def success():
    """결제 성공 리다이렉트 — 서버 승인."""
    payment_key = request.args.get("paymentKey", "").strip()
    order_id = request.args.get("orderId", "").strip()
    amount_raw = request.args.get("amount", "").strip()

    if not payment_key or not order_id or not amount_raw.isdigit():
        flash("결제 정보가 올바르지 않습니다.", "error")
        return redirect(url_for("cart.index"))

    amount = int(amount_raw)
    order = get_order_by_number(order_id)
    if not order:
        flash("주문을 찾을 수 없습니다.", "error")
        return redirect(url_for("cart.index"))

    try:
        result = confirm_payment(payment_key=payment_key, order_id=order_id, amount=amount)
        order = complete_order_payment(
            order=order,
            payment_key=payment_key,
            payment_method=result.get("method", "CARD"),
            amount=amount,
        )
    except (TossPaymentError, OrderValidationError) as exc:
        flash(str(exc), "error")
        return redirect(url_for("payment.fail", orderId=order_id, code="CONFIRM_FAILED"))

    return render_template("payment/success.html", order=order, payment=result)


@payment_bp.route("/payment/fail")
def fail():
    """결제 실패."""
    order_id = request.args.get("orderId", "")
    message = request.args.get("message", "결제가 취소되었거나 실패했습니다.")
    code = request.args.get("code", "")
    order = get_order_by_number(order_id) if order_id else None
    return render_template(
        "payment/fail.html",
        order=order,
        message=message,
        code=code,
    )
