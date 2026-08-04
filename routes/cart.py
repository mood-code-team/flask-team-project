"""
장바구니 라우트 — 세션/DB 장바구니 API + 주문.
"""

from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user

from services.cart_service import (
    add_product_by_slug,
    compute_cart_totals,
    get_cart_summary,
    line_shipping_info,
    remove_product,
    serialize_cart,
    set_product_quantity,
)
from services.address_utils import compose_address, parse_address
from services.coupon_service import CouponError, get_coupon_previews
from services.order_service import OrderValidationError, calculate_order_totals, create_pending_order, get_lines_for_checkout
from services.point_service import PointError, get_point_balance

cart_bp = Blueprint("cart", __name__)

_GUEST_EMAILS = {"guest@shop.local"}
_GUEST_USERNAMES = {"guest_checkout", "guest"}


def _is_member() -> bool:
    return (
        current_user.is_authenticated
        and current_user.username not in _GUEST_USERNAMES
        and current_user.email not in _GUEST_EMAILS
    )


def _parse_selected_ids(raw: str) -> list[int] | None:
    if not raw:
        return None
    ids = [int(value) for value in raw.split(",") if value.isdigit()]
    return ids or None


def _address_from_form(form, *, prefix: str = "shipping") -> str:
    composed = compose_address(
        postcode=form.get(f"{prefix}_postcode", ""),
        road=form.get(f"{prefix}_road", ""),
        jibun=form.get(f"{prefix}_jibun", ""),
        detail=form.get(f"{prefix}_detail", ""),
    )
    hidden = form.get(f"{prefix}_address", "").strip()
    legacy = form.get("shipping_address", "").strip()
    return composed or hidden or legacy


def _checkout_form_defaults() -> dict:
    if _is_member():
        parsed = parse_address(current_user.address)
        return {
            "recipient_name": current_user.full_name or "",
            "recipient_phone": current_user.phone or "",
            "shipping_address": current_user.address or "",
            "shipping_addr": parsed,
            "shipping_memo": "",
            "user_coupon_id": "",
            "point_used": "0",
        }
    return {
        "recipient_name": "",
        "recipient_phone": "",
        "shipping_address": "",
        "shipping_addr": parse_address(""),
        "shipping_memo": "",
        "user_coupon_id": "",
        "point_used": "0",
    }


def _order_context(lines, form, selected_raw):
    product_total = sum(line.subtotal for line in lines)
    discount_total = sum(line.discount_amount for line in lines)

    user_coupon_id = None
    point_used = 0
    if _is_member():
        raw_coupon = form.get("user_coupon_id", "").strip()
        if raw_coupon.isdigit():
            user_coupon_id = int(raw_coupon)
        try:
            point_used = int(form.get("point_used", "0") or 0)
        except ValueError:
            point_used = 0

    try:
        totals = calculate_order_totals(
            lines=lines,
            user_coupon_id=user_coupon_id,
            point_used=point_used,
            user_id=current_user.id if _is_member() else None,
        )
    except (CouponError, PointError) as exc:
        totals = calculate_order_totals(lines=lines)

    coupons = get_coupon_previews(current_user.id) if _is_member() else []
    point_balance = get_point_balance(current_user.id) if _is_member() else 0

    return {
        "lines": lines,
        "form": form,
        "selected_ids": selected_raw,
        "product_total": product_total,
        "discount_total": discount_total,
        "shipping_fee": totals["shipping_fee"],
        "coupon_discount": totals["coupon_discount"],
        "point_used": totals["point_used"],
        "grand_total": totals["total_amount"],
        "coupons": coupons,
        "point_balance": point_balance,
    }


@cart_bp.route("/cart")
def index():
    summary = get_cart_summary()
    return render_template(
        "cart/index.html",
        summary=summary,
        line_shipping_info=line_shipping_info,
    )


@cart_bp.route("/order", methods=["GET", "POST"])
def order():
    selected_raw = request.values.get("ids", "")
    selected_ids = _parse_selected_ids(selected_raw)
    lines = get_lines_for_checkout(selected_ids)

    if not lines:
        flash("장바구니가 비어 있거나 선택한 상품이 없습니다.", "error")
        return redirect(url_for("cart.index"))

    if request.method == "POST":
        form = {
            "recipient_name": request.form.get("recipient_name", "").strip(),
            "recipient_phone": request.form.get("recipient_phone", "").strip(),
            "shipping_address": _address_from_form(request.form, prefix="shipping"),
            "shipping_postcode": request.form.get("shipping_postcode", "").strip(),
            "shipping_road": request.form.get("shipping_road", "").strip(),
            "shipping_jibun": request.form.get("shipping_jibun", "").strip(),
            "shipping_detail": request.form.get("shipping_detail", "").strip(),
            "shipping_memo": request.form.get("shipping_memo", "").strip(),
            "user_coupon_id": request.form.get("user_coupon_id", "").strip(),
            "point_used": request.form.get("point_used", "0").strip(),
        }
        form["shipping_addr"] = parse_address(form["shipping_address"])
        user_coupon_id = int(form["user_coupon_id"]) if form["user_coupon_id"].isdigit() else None
        try:
            point_used = int(form["point_used"] or 0)
        except ValueError:
            point_used = 0

        try:
            pending = create_pending_order(
                lines=lines,
                recipient_name=form["recipient_name"],
                recipient_phone=form["recipient_phone"],
                shipping_address=form["shipping_address"],
                shipping_memo=form["shipping_memo"],
                user_coupon_id=user_coupon_id,
                point_used=point_used,
            )
        except (OrderValidationError, CouponError, PointError) as exc:
            flash(str(exc), "error")
            return render_template("cart/order.html", **_order_context(lines, form, selected_raw))

        return redirect(url_for("payment.checkout", order_number=pending.order_number))

    return render_template(
        "cart/order.html",
        **_order_context(lines, _checkout_form_defaults(), selected_raw),
    )


@cart_bp.route("/api/cart")
def api_cart():
    return jsonify(serialize_cart())


@cart_bp.route("/api/cart/add", methods=["POST"])
def api_add():
    payload = request.get_json(silent=True) or {}
    slug = (payload.get("slug") or request.form.get("slug") or "").strip()
    if not slug:
        return jsonify({"ok": False, "message": "상품 정보가 없습니다."}), 400

    try:
        quantity = int(payload.get("quantity", 1))
    except (TypeError, ValueError):
        quantity = 1

    try:
        add_product_by_slug(slug, quantity=max(quantity, 1))
    except ValueError as exc:
        return jsonify({"ok": False, "message": str(exc)}), 404

    data = serialize_cart()
    return jsonify({"ok": True, **data})


@cart_bp.route("/api/cart/update", methods=["POST"])
def api_update():
    payload = request.get_json(silent=True) or {}
    try:
        product_id = int(payload.get("product_id"))
        quantity = int(payload.get("quantity"))
    except (TypeError, ValueError):
        return jsonify({"ok": False, "message": "잘못된 요청입니다."}), 400

    try:
        set_product_quantity(product_id=product_id, quantity=quantity)
    except ValueError as exc:
        return jsonify({"ok": False, "message": str(exc)}), 400

    return jsonify({"ok": True, **serialize_cart()})


@cart_bp.route("/api/cart/remove", methods=["POST"])
def api_remove():
    payload = request.get_json(silent=True) or {}
    try:
        product_id = int(payload.get("product_id"))
    except (TypeError, ValueError):
        return jsonify({"ok": False, "message": "잘못된 요청입니다."}), 400

    try:
        remove_product(product_id=product_id)
    except ValueError as exc:
        return jsonify({"ok": False, "message": str(exc)}), 404

    return jsonify({"ok": True, **serialize_cart()})
