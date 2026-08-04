"""고객센터 1:1 문의 서비스."""

from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any

from flask import current_app
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from extensions import db
from models import CustomerInquiry, InquiryStatus, Order, User

INQUIRY_TYPES: list[tuple[str, str]] = [
    ("order", "주문/결제"),
    ("shipping", "배송"),
    ("return", "취소/교환/반품"),
    ("receipt", "영수증/증빙"),
    ("member", "회원/로그인"),
    ("benefits", "적립금/쿠폰/멤버십"),
    ("product", "상품 문의"),
    ("etc", "기타"),
]

MAX_ATTACHMENTS = 5
MAX_FILE_BYTES = 10 * 1024 * 1024
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp", "pdf", "doc", "docx", "xls", "xlsx", "zip"}


class InquiryError(Exception):
    pass


def get_inquiry_type_label(slug: str) -> str:
    return dict(INQUIRY_TYPES).get(slug, slug)


def get_user_orders_for_select(user_id: int) -> list[dict[str, str]]:
    orders = (
        Order.query.filter_by(user_id=user_id)
        .order_by(Order.created_at.desc())
        .limit(50)
        .all()
    )
    return [
        {
            "order_number": order.order_number,
            "label": f"{order.order_number} · {order.created_at.strftime('%Y.%m.%d')} · {order.status_label}",
        }
        for order in orders
    ]


def _upload_dir() -> Path:
    base = current_app.config.get("UPLOAD_FOLDER") or Path("static/images/uploads")
    folder = Path(base) / "inquiries"
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def _save_attachments(files: list[FileStorage]) -> list[str]:
    if len(files) > MAX_ATTACHMENTS:
        raise InquiryError(f"첨부파일은 최대 {MAX_ATTACHMENTS}개까지 가능합니다.")

    saved: list[str] = []
    folder = _upload_dir()

    for file in files:
        if not file or not file.filename:
            continue
        ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
        if ext not in ALLOWED_EXTENSIONS:
            raise InquiryError(f"허용되지 않는 파일 형식입니다: {file.filename}")

        file.seek(0, 2)
        size = file.tell()
        file.seek(0)
        if size > MAX_FILE_BYTES:
            raise InquiryError("파일당 10MB 이하만 첨부할 수 있습니다.")

        safe = secure_filename(file.filename)
        name = f"{uuid.uuid4().hex[:12]}_{safe}"
        path = folder / name
        file.save(path)
        saved.append(name)

    return saved


def create_inquiry(
    *,
    user: User,
    inquiry_type: str,
    title: str,
    content: str,
    order_number: str | None = None,
    files: list[FileStorage] | None = None,
) -> CustomerInquiry:
    valid_types = {slug for slug, _ in INQUIRY_TYPES}
    if inquiry_type not in valid_types:
        raise InquiryError("문의 유형을 선택해 주세요.")
    if not title.strip():
        raise InquiryError("제목을 입력해 주세요.")
    if not content.strip():
        raise InquiryError("문의 내용을 입력해 주세요.")

    if order_number:
        owned = Order.query.filter_by(user_id=user.id, order_number=order_number).first()
        if not owned:
            raise InquiryError("선택한 주문번호를 확인할 수 없습니다.")

    attachment_names = _save_attachments(files or [])

    row = CustomerInquiry(
        user_id=user.id,
        inquiry_type=inquiry_type,
        order_number=order_number or None,
        title=title.strip(),
        content=content.strip(),
        attachments=json.dumps(attachment_names) if attachment_names else None,
    )
    db.session.add(row)
    db.session.commit()
    return row


def get_user_inquiries(user_id: int) -> list[CustomerInquiry]:
    return (
        CustomerInquiry.query.filter_by(user_id=user_id)
        .order_by(CustomerInquiry.created_at.desc())
        .all()
    )


def inquiry_to_dict(row: CustomerInquiry) -> dict[str, Any]:
    attachments: list[str] = []
    if row.attachments:
        try:
            attachments = json.loads(row.attachments)
        except json.JSONDecodeError:
            attachments = []

    return {
        "id": row.id,
        "inquiry_type": row.inquiry_type,
        "inquiry_type_label": get_inquiry_type_label(row.inquiry_type),
        "order_number": row.order_number,
        "title": row.title,
        "content": row.content,
        "attachments": attachments,
        "status": row.status,
        "status_label": InquiryStatus.LABELS.get(row.status, row.status),
        "answer": row.answer,
        "created_at": row.created_at.isoformat() if row.created_at else None,
    }
