"""
상품 라우트 — 상세 페이지.
"""

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from models import Product
from services.product_question_service import QuestionError, create_question, get_product_questions
from services.review_service import get_product_reviews
from services.product_detail_content import (
    EXCHANGE_CONTENT,
    SHIPPING_CONTENT,
    get_product_detail_table,
    get_product_shipping_label,
    get_product_summary_specs,
)
from services.search_filters import get_product_specs
from services.wishlist_service import is_in_wishlist

product_bp = Blueprint("product", __name__)

DEFAULT_SHOP_CATEGORY = "light"


@product_bp.route("/products")
def product_index():
    """상품목록 진입 — 기본 카테고리로 이동."""
    return redirect(url_for("category.listing", slug=DEFAULT_SHOP_CATEGORY))


@product_bp.route("/product/<slug>")
def detail_alias(slug: str):
    """예전 URL(/product/...) 호환."""
    return redirect(url_for("product.detail", slug=slug))


@product_bp.route("/products/code/<path:mood_code>")
def detail_by_mood_code(mood_code: str):
    """갤러리 MC-SF-005 등 무드코드 → 상품 상세."""
    from services.product_lookup import find_product_by_mood_code

    product = find_product_by_mood_code(mood_code)
    if not product:
        abort(404)
    return redirect(url_for("product.detail", slug=product.slug))


@product_bp.route("/products/<slug>")
def detail(slug: str):
    product = Product.query.filter_by(slug=slug, is_active=True).first()
    if not product:
        abort(404)

    related = (
        Product.query.filter(
            Product.category_id == product.category_id,
            Product.id != product.id,
            Product.is_active.is_(True),
        )
        .order_by(Product.is_best.desc(), Product.created_at.desc())
        .limit(4)
        .all()
    )

    return render_template(
        "product/detail.html",
        product=product,
        related_products=related,
        in_wishlist=is_in_wishlist(product.id),
        questions=get_product_questions(product.id),
        reviews=get_product_reviews(product.id),
        product_specs=get_product_specs(product),
        summary_specs=get_product_summary_specs(product),
        detail_table=get_product_detail_table(product),
        shipping_label=get_product_shipping_label(product),
        shipping_content=SHIPPING_CONTENT,
        exchange_content=EXCHANGE_CONTENT,
    )


@product_bp.route("/products/<slug>/questions", methods=["POST"])
@login_required
def ask_question(slug: str):
    product = Product.query.filter_by(slug=slug, is_active=True).first()
    if not product:
        abort(404)

    try:
        create_question(
            user_id=current_user.id,
            product_id=product.id,
            question=request.form.get("question", ""),
        )
        flash("문의가 등록되었습니다. 답변은 마이페이지에서 확인할 수 있습니다.", "success")
    except QuestionError as exc:
        flash(str(exc), "error")

    return redirect(url_for("product.detail", slug=slug) + "#product-qna")
