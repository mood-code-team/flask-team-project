"""
Mood Code 관리자 백오피스.

접속: /admin  (관리자 계정 필요)
"""

from __future__ import annotations

import re
from datetime import datetime
from functools import wraps

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user

from extensions import db
from models import Category, CustomerInquiry, FAQ, InquiryStatus, Notice, Order, OrderStatus, Product, User
from services.admin_service import (
    get_category_rows,
    get_dashboard_stats,
    get_leaf_categories,
    get_pending_inquiries,
    get_recent_orders,
    list_faqs,
    list_notices,
    parse_int,
    parse_optional_int,
    search_inquiries,
    search_orders,
    search_products,
    search_users,
)

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("관리자 로그인이 필요합니다.", "error")
            return redirect(url_for("auth.login", next=request.path))
        if not current_user.is_admin:
            abort(403)
        return view(*args, **kwargs)

    return wrapped


@admin_bp.context_processor
def inject_admin_sidebar():
    from services.admin_service import get_admin_sidebar_counts

    return {"admin_sidebar": get_admin_sidebar_counts()}


@admin_bp.route("/")
@admin_bp.route("/dashboard")
@admin_required
def dashboard():
    return render_template(
        "admin/dashboard.html",
        stats=get_dashboard_stats(),
        recent_orders=get_recent_orders(),
        pending_inquiries=get_pending_inquiries(),
        order_labels=OrderStatus.LABELS,
    )


@admin_bp.route("/orders")
@admin_required
def orders():
    status = request.args.get("status", "")
    q = request.args.get("q", "")
    page = parse_int(request.args.get("page"), default=1, minimum=1)
    pagination = search_orders(status=status, q=q, page=page)
    return render_template(
        "admin/orders.html",
        pagination=pagination,
        status=status,
        q=q,
        order_labels=OrderStatus.LABELS,
        order_statuses=OrderStatus.LABELS,
    )


@admin_bp.route("/orders/<int:order_id>", methods=["GET", "POST"])
@admin_required
def order_detail(order_id: int):
    order = db.session.get(Order, order_id)
    if not order:
        abort(404)

    if request.method == "POST":
        new_status = (request.form.get("status") or "").strip()
        if new_status not in OrderStatus.LABELS:
            flash("유효하지 않은 주문 상태입니다.", "error")
        else:
            order.status = new_status
            if new_status == OrderStatus.PAID and not order.paid_at:
                order.paid_at = datetime.utcnow()
            db.session.commit()
            flash(f"주문 {order.order_number} 상태를 「{OrderStatus.LABELS[new_status]}」(으)로 변경했습니다.", "success")
            return redirect(url_for("admin.order_detail", order_id=order.id))

    return render_template(
        "admin/order_detail.html",
        order=order,
        order_statuses=OrderStatus.LABELS,
    )


@admin_bp.route("/users")
@admin_required
def users():
    q = request.args.get("q", "")
    page = parse_int(request.args.get("page"), default=1, minimum=1)
    pagination = search_users(q=q, page=page)
    return render_template("admin/users.html", pagination=pagination, q=q)


@admin_bp.route("/users/<int:user_id>/toggle", methods=["POST"])
@admin_required
def user_toggle(user_id: int):
    user = db.session.get(User, user_id)
    if not user or user.is_admin:
        abort(404)
    user.is_active = not user.is_active
    db.session.commit()
    state = "활성화" if user.is_active else "비활성화"
    flash(f"회원 {user.username} 계정을 {state}했습니다.", "success")
    return redirect(url_for("admin.users", q=request.args.get("q", "")))


@admin_bp.route("/categories")
@admin_required
def categories():
    return render_template("admin/categories.html", category_rows=get_category_rows())


@admin_bp.route("/products")
@admin_required
def products():
    q = request.args.get("q", "")
    category_id = parse_optional_int(request.args.get("category_id"))
    page = parse_int(request.args.get("page"), default=1, minimum=1)
    pagination = search_products(q=q, category_id=category_id, page=page)
    return render_template(
        "admin/products.html",
        pagination=pagination,
        q=q,
        category_id=category_id,
        categories=get_leaf_categories(),
    )


@admin_bp.route("/products/new", methods=["GET", "POST"])
@admin_bp.route("/products/<int:product_id>", methods=["GET", "POST"])
@admin_required
def product_form(product_id: int | None = None):
    product = db.session.get(Product, product_id) if product_id else None
    if product_id and not product:
        abort(404)
    categories = get_leaf_categories()

    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        category_id = parse_int(request.form.get("category_id"), minimum=1)
        if not name or not category_id:
            flash("상품명과 카테고리는 필수입니다.", "error")
            return render_template(
                "admin/product_form.html",
                product=product,
                categories=categories,
            )

        category = db.session.get(Category, category_id)
        if not category:
            flash("카테고리를 찾을 수 없습니다.", "error")
            return render_template(
                "admin/product_form.html",
                product=product,
                categories=categories,
            )

        if not product:
            base_slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")[:120] or "product"
            slug = base_slug
            suffix = 1
            while Product.query.filter_by(slug=slug).first():
                slug = f"{base_slug}-{suffix}"
                suffix += 1
            product = Product(name=name, slug=slug, category_id=category_id, price=0, stock=0)
            db.session.add(product)

        product.name = name
        product.category_id = category_id
        product.description = (request.form.get("description") or "").strip()
        product.price = parse_int(request.form.get("price"), minimum=0)
        product.discount_price = parse_optional_int(request.form.get("discount_price"))
        product.stock = parse_int(request.form.get("stock"), minimum=0)
        product.brand = (request.form.get("brand") or "").strip()
        product.image_url = (request.form.get("image_url") or "").strip()
        product.filter_space = (request.form.get("filter_space") or "").strip()
        product.filter_style = (request.form.get("filter_style") or "").strip()
        product.filter_color = (request.form.get("filter_color") or "").strip()
        product.is_active = request.form.get("is_active") == "on"
        product.is_popular = request.form.get("is_popular") == "on"
        product.is_new = request.form.get("is_new") == "on"
        product.is_best = request.form.get("is_best") == "on"
        db.session.commit()
        flash(f"「{product.name}」 상품을 저장했습니다.", "success")
        return redirect(url_for("admin.products"))

    return render_template("admin/product_form.html", product=product, categories=categories)


@admin_bp.route("/inquiries")
@admin_required
def inquiries():
    status = request.args.get("status", "")
    page = parse_int(request.args.get("page"), default=1, minimum=1)
    pagination = search_inquiries(status=status, page=page)
    return render_template(
        "admin/inquiries.html",
        pagination=pagination,
        status=status,
        inquiry_statuses=InquiryStatus.LABELS,
    )


@admin_bp.route("/inquiries/<int:inquiry_id>", methods=["GET", "POST"])
@admin_required
def inquiry_detail(inquiry_id: int):
    inquiry = db.session.get(CustomerInquiry, inquiry_id)
    if not inquiry:
        abort(404)

    if request.method == "POST":
        answer = (request.form.get("answer") or "").strip()
        status = (request.form.get("status") or InquiryStatus.ANSWERED).strip()
        if status not in InquiryStatus.LABELS:
            status = InquiryStatus.ANSWERED
        inquiry.answer = answer
        inquiry.status = status
        if answer:
            inquiry.answered_at = datetime.utcnow()
        db.session.commit()
        flash("문의 답변을 저장했습니다.", "success")
        return redirect(url_for("admin.inquiries"))

    return render_template(
        "admin/inquiry_detail.html",
        inquiry=inquiry,
        inquiry_statuses=InquiryStatus.LABELS,
    )


@admin_bp.route("/notices")
@admin_required
def notices():
    return render_template("admin/notices.html", notices=list_notices())


@admin_bp.route("/notices/new", methods=["GET", "POST"])
@admin_bp.route("/notices/<int:notice_id>/edit", methods=["GET", "POST"])
@admin_required
def notice_form(notice_id: int | None = None):
    notice = db.session.get(Notice, notice_id) if notice_id else None
    if notice_id and not notice:
        abort(404)

    if request.method == "POST":
        title = (request.form.get("title") or "").strip()
        content = (request.form.get("content") or "").strip()
        if not title or not content:
            flash("제목과 내용을 입력해 주세요.", "error")
            return render_template("admin/notice_form.html", notice=notice)

        if not notice:
            notice = Notice(title=title, content=content)
            db.session.add(notice)
        else:
            notice.title = title
            notice.content = content

        notice.is_pinned = request.form.get("is_pinned") == "on"
        notice.is_active = request.form.get("is_active") == "on"
        db.session.commit()
        flash("공지사항을 저장했습니다.", "success")
        return redirect(url_for("admin.notices"))

    return render_template("admin/notice_form.html", notice=notice)


@admin_bp.route("/faqs")
@admin_required
def faqs():
    return render_template("admin/faqs.html", faqs=list_faqs())


@admin_bp.route("/faqs/new", methods=["GET", "POST"])
@admin_bp.route("/faqs/<int:faq_id>/edit", methods=["GET", "POST"])
@admin_required
def faq_form(faq_id: int | None = None):
    faq = db.session.get(FAQ, faq_id) if faq_id else None
    if faq_id and not faq:
        abort(404)

    if request.method == "POST":
        category = (request.form.get("category") or "").strip()
        question = (request.form.get("question") or "").strip()
        answer = (request.form.get("answer") or "").strip()
        if not category or not question or not answer:
            flash("카테고리, 질문, 답변을 모두 입력해 주세요.", "error")
            return render_template("admin/faq_form.html", faq=faq)

        if not faq:
            faq = FAQ(category=category, question=question, answer=answer)
            db.session.add(faq)
        else:
            faq.category = category
            faq.question = question
            faq.answer = answer

        faq.sort_order = parse_int(request.form.get("sort_order"), default=0, minimum=0)
        faq.is_active = request.form.get("is_active") == "on"
        db.session.commit()
        flash("FAQ를 저장했습니다.", "success")
        return redirect(url_for("admin.faqs"))

    return render_template("admin/faq_form.html", faq=faq)
