"""
마이페이지 라우트.
"""

from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from services.address_utils import compose_address, parse_address
from services.mypage_service import (
    ProfileUpdateError,
    change_user_password,
    get_all_orders,
    get_membership_info,
    get_mypage_summary,
    update_shipping_address,
    update_user_profile,
)
from services.order_service import OrderValidationError, cancel_order_by_user, get_order_by_number
from services.point_service import get_point_history
from services.inquiry_service import get_user_inquiries
from services.product_question_service import QuestionError, get_user_questions
from services.register_options import KOREA_REGIONS
from services.review_service import ReviewError, create_review, get_reviewable_items, get_user_reviews
from services.coupon_service import get_coupon_previews
from services.wishlist_service import (
    get_wishlist_products,
    remove_from_wishlist,
    serialize_wishlist,
    toggle_wishlist,
    add_to_wishlist,
)

mypage_bp = Blueprint("mypage", __name__)

_GUEST_USERNAMES = {"guest_checkout", "guest"}


def _block_guest():
    if current_user.username in _GUEST_USERNAMES or current_user.email == "guest@shop.local":
        return redirect(url_for("auth.login"))
    return None


def _summary():
    return get_mypage_summary(
        current_user.id,
        display_name=current_user.full_name or current_user.username,
    )


def _render(template: str, active_page: str, **context):
    return render_template(
        template,
        summary=_summary(),
        active_page=active_page,
        **context,
    )


@mypage_bp.route("/mypage")
@login_required
def index():
    if blocked := _block_guest():
        return blocked
    orders = get_all_orders(current_user.id)
    return _render("mypage/index.html", "orders", orders=orders)


@mypage_bp.route("/mypage/orders/<order_number>")
@login_required
def order_detail(order_number: str):
    if blocked := _block_guest():
        return blocked
    order = get_order_by_number(order_number)
    if not order or order.user_id != current_user.id:
        flash("주문을 찾을 수 없습니다.", "error")
        return redirect(url_for("mypage.index"))
    return _render("mypage/order_detail.html", "orders", order=order)


@mypage_bp.route("/mypage/orders/<order_number>/cancel", methods=["POST"])
@login_required
def order_cancel(order_number: str):
    """주문 취소."""
    if blocked := _block_guest():
        return blocked

    order = get_order_by_number(order_number)
    if not order or order.user_id != current_user.id:
        flash("주문을 찾을 수 없습니다.", "error")
        return redirect(url_for("mypage.index"))

    try:
        cancel_order_by_user(order=order, user_id=current_user.id)
    except OrderValidationError as exc:
        flash(str(exc), "error")
        return redirect(url_for("mypage.order_detail", order_number=order_number))

    if order.payment_key:
        flash(
            f"주문 {order_number}이(가) 취소되었습니다. 카드 환불은 영업일 기준 3~5일 내 처리됩니다.",
            "success",
        )
    else:
        flash(f"주문 {order_number}이(가) 취소되었습니다.", "success")

    return redirect(url_for("mypage.index"))


@mypage_bp.route("/mypage/wishlist")
@login_required
def wishlist():
    if blocked := _block_guest():
        return blocked
    products = get_wishlist_products()
    return _render("mypage/wishlist.html", "wishlist", products=products)


@mypage_bp.route("/mypage/wishlist/remove/<int:product_id>", methods=["POST"])
@login_required
def wishlist_remove(product_id: int):
    if blocked := _block_guest():
        return blocked
    if remove_from_wishlist(product_id):
        flash("위시리스트에서 삭제했습니다.", "success")
    return redirect(url_for("mypage.wishlist"))


@mypage_bp.route("/api/wishlist")
@login_required
def wishlist_api():
    """위시리스트 상태 JSON."""
    if blocked := _block_guest():
        return jsonify({"ok": False, "message": "로그인이 필요합니다."}), 401
    data = serialize_wishlist()
    return jsonify({"ok": True, **data})


@mypage_bp.route("/api/wishlist/add", methods=["POST"])
@login_required
def wishlist_add_api():
    """위시리스트에 상품 추가."""
    if blocked := _block_guest():
        return jsonify({"ok": False, "message": "로그인이 필요합니다."}), 401

    payload = request.get_json(silent=True) or {}
    product_id = payload.get("product_id")
    slug = (payload.get("slug") or "").strip()

    if not product_id and slug:
        from models import Product

        product = Product.query.filter_by(slug=slug, is_active=True).first()
        if product:
            product_id = product.id

    try:
        product_id = int(product_id)
    except (TypeError, ValueError):
        return jsonify({"ok": False, "message": "상품 정보가 없습니다."}), 400

    try:
        added = add_to_wishlist(product_id)
    except ValueError as exc:
        return jsonify({"ok": False, "message": str(exc)}), 400

    data = serialize_wishlist()
    return jsonify({"ok": True, "added": added, **data})


@mypage_bp.route("/api/wishlist/toggle", methods=["POST"])
@login_required
def wishlist_toggle_api():
    if blocked := _block_guest():
        return jsonify({"ok": False, "message": "로그인이 필요합니다."}), 401

    payload = request.get_json(silent=True) or {}
    try:
        product_id = int(payload.get("product_id"))
    except (TypeError, ValueError):
        return jsonify({"ok": False, "message": "잘못된 요청입니다."}), 400

    try:
        in_wishlist = toggle_wishlist(product_id)
    except ValueError as exc:
        return jsonify({"ok": False, "message": str(exc)}), 400

    return jsonify({"ok": True, "in_wishlist": in_wishlist, **serialize_wishlist()})


@mypage_bp.route("/mypage/coupons")
@login_required
def coupons():
    if blocked := _block_guest():
        return blocked
    coupon_list = get_coupon_previews(current_user.id)
    return _render("mypage/coupons.html", "coupons", coupons=coupon_list)


@mypage_bp.route("/mypage/points")
@login_required
def points():
    if blocked := _block_guest():
        return blocked
    history = get_point_history(current_user.id)
    return _render("mypage/points.html", "points", point_history=history)


@mypage_bp.route("/mypage/membership")
@login_required
def membership():
    if blocked := _block_guest():
        return blocked
    summary = _summary()
    info = get_membership_info(current_user.id, summary.membership_label)
    return _render("mypage/membership.html", "membership", membership=info)


def _address_from_form(form, *, prefix: str = "profile") -> str:
    composed = compose_address(
        postcode=form.get(f"{prefix}_postcode", ""),
        road=form.get(f"{prefix}_road", ""),
        jibun=form.get(f"{prefix}_jibun", ""),
        detail=form.get(f"{prefix}_detail", ""),
    )
    hidden = form.get("address", "").strip()
    return composed or hidden


@mypage_bp.route("/mypage/profile", methods=["GET", "POST"])
@login_required
def profile():
    if blocked := _block_guest():
        return blocked

    if request.method == "POST":
        try:
            change_user_password(
                current_user,
                current_password=request.form.get("current_password", ""),
                new_password=request.form.get("new_password", ""),
                new_password_confirm=request.form.get("new_password_confirm", ""),
            )
            update_user_profile(
                current_user,
                full_name=request.form.get("full_name", ""),
                email=request.form.get("email", ""),
                phone=request.form.get("phone", ""),
                region=request.form.get("region", ""),
                address=_address_from_form(request.form, prefix="profile"),
            )
            flash("회원정보가 저장되었습니다.", "success")
            return redirect(url_for("mypage.profile"))
        except ProfileUpdateError as exc:
            flash(str(exc), "error")

    return _render(
        "mypage/profile.html",
        "profile",
        regions=KOREA_REGIONS,
        user=current_user,
        parsed_address=parse_address(current_user.address),
    )


@mypage_bp.route("/mypage/addresses", methods=["GET", "POST"])
@login_required
def addresses():
    if blocked := _block_guest():
        return blocked

    if request.method == "POST":
        try:
            address = _address_from_form(request.form, prefix="addr")
            if not address:
                address = request.form.get("address", "").strip()
            update_shipping_address(
                current_user,
                address=address,
                phone=request.form.get("phone"),
            )
            flash("배송지가 저장되었습니다.", "success")
            return redirect(url_for("mypage.addresses"))
        except ProfileUpdateError as exc:
            flash(str(exc), "error")

    return _render(
        "mypage/addresses.html",
        "addresses",
        user=current_user,
        parsed_address=parse_address(current_user.address),
    )


@mypage_bp.route("/mypage/qna")
@login_required
def qna():
    if blocked := _block_guest():
        return blocked
    questions = get_user_questions(current_user.id)
    inquiries = get_user_inquiries(current_user.id)
    return _render("mypage/qna.html", "qna", questions=questions, inquiries=inquiries)


@mypage_bp.route("/mypage/reviews", methods=["GET", "POST"])
@login_required
def reviews():
    if blocked := _block_guest():
        return blocked

    if request.method == "POST":
        try:
            create_review(
                user_id=current_user.id,
                order_item_id=int(request.form.get("order_item_id", 0)),
                rating=int(request.form.get("rating", 0)),
                content=request.form.get("content", ""),
            )
            flash("리뷰가 등록되었습니다.", "success")
            return redirect(url_for("mypage.reviews"))
        except (ReviewError, ValueError) as exc:
            flash(str(exc), "error")

    user_reviews = get_user_reviews(current_user.id)
    reviewable = get_reviewable_items(current_user.id)
    return _render(
        "mypage/reviews.html",
        "reviews",
        reviews=user_reviews,
        reviewable_items=reviewable,
    )
