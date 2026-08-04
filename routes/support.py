"""
고객센터
"""

from flask import Blueprint, abort, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from models import Notice
from services.help_center_service import (
    HELP_CATEGORIES,
    ensure_help_center_faqs,
    get_category_label,
    get_faq_by_id,
    get_faq_count,
    get_faq_groups,
)
from services.inquiry_service import (
    INQUIRY_TYPES,
    InquiryError,
    create_inquiry,
    get_user_orders_for_select,
    inquiry_to_dict,
)

support_bp = Blueprint("support", __name__, url_prefix="/support")


@support_bp.route("/")
def center():
    """고객센터 메인 — 검색·카테고리·FAQ 목록."""
    ensure_help_center_faqs()
    active = request.args.get("category", "all")
    valid_slugs = {c["slug"] for c in HELP_CATEGORIES}
    if active not in valid_slugs:
        active = "all"

    active_label = next(
        (c["label"] for c in HELP_CATEGORIES if c["slug"] == active),
        "전체",
    )

    return render_template(
        "support/center.html",
        categories=HELP_CATEGORIES,
        active_category=active,
        active_label=active_label,
        faq_groups=get_faq_groups(active),
        faq_count=get_faq_count(active),
    )


@support_bp.route("/faq/<int:faq_id>")
def faq_detail(faq_id: int):
    """FAQ 상세."""
    ensure_help_center_faqs()
    faq = get_faq_by_id(faq_id)
    if not faq:
        abort(404)
    return render_template(
        "support/faq_detail.html",
        faq=faq,
        category_label=get_category_label(faq.category),
    )


@support_bp.route("/faq")
def faq_list():
    return redirect(url_for("support.center"))


@support_bp.route("/notices")
def notice_list():
    """공지사항 목록."""
    notices = (
        Notice.query.filter_by(is_active=True)
        .order_by(Notice.is_pinned.desc(), Notice.created_at.desc())
        .all()
    )
    return render_template("support/notices.html", notices=notices)


@support_bp.route("/api/inquiry-meta")
@login_required
def inquiry_meta():
    """문의 모달 — 유형·주문 목록."""
    return jsonify({
        "inquiry_types": [{"value": v, "label": l} for v, l in INQUIRY_TYPES],
        "orders": get_user_orders_for_select(current_user.id),
    })


@support_bp.route("/api/inquiries", methods=["POST"])
@login_required
def submit_inquiry():
    """1:1 문의 접수."""
    try:
        row = create_inquiry(
            user=current_user,
            inquiry_type=(request.form.get("inquiry_type") or "").strip(),
            title=(request.form.get("title") or "").strip(),
            content=(request.form.get("content") or "").strip(),
            order_number=(request.form.get("order_number") or "").strip() or None,
            files=request.files.getlist("attachments"),
        )
        return jsonify({
            "success": True,
            "message": "문의가 접수되었습니다. 고객센터에서 순차적으로 확인해 드립니다.",
            "inquiry": inquiry_to_dict(row),
        })
    except InquiryError as exc:
        return jsonify({"success": False, "error": str(exc)}), 400
    except Exception:
        return jsonify({"success": False, "error": "문의 접수 중 오류가 발생했습니다."}), 500

