"""고객센터 1:1 문의."""

from __future__ import annotations

from datetime import datetime

from extensions import db


class InquiryStatus:
    PENDING = "pending"
    ANSWERED = "answered"
    CLOSED = "closed"

    LABELS = {
        PENDING: "답변 대기",
        ANSWERED: "답변 완료",
        CLOSED: "처리 완료",
    }


class CustomerInquiry(db.Model):
    """고객센터 1:1 문의."""

    __tablename__ = "customer_inquiries"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    inquiry_type = db.Column(db.String(30), nullable=False)
    order_number = db.Column(db.String(30))
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    attachments = db.Column(db.Text)  # JSON: ["filename", ...]
    status = db.Column(db.String(20), default=InquiryStatus.PENDING, nullable=False)
    answer = db.Column(db.Text)
    answered_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship("User", back_populates="customer_inquiries")

    @property
    def inquiry_type_label(self) -> str:
        from services.inquiry_service import get_inquiry_type_label

        return get_inquiry_type_label(self.inquiry_type)

    @property
    def status_label(self) -> str:
        return InquiryStatus.LABELS.get(self.status, self.status)
