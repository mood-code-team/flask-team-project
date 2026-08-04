"""
Notice / FAQ 모델 — 고객센터.

notices: 공지사항
faqs: FAQ (DB 관리 — 관리자 페이지에서 CRUD 가능)
"""

from __future__ import annotations

from datetime import datetime

from extensions import db


class Notice(db.Model):
    """공지사항."""

    __tablename__ = "notices"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_pinned = db.Column(db.Boolean, default=False, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    def __repr__(self) -> str:
        return f"<Notice {self.title}>"


class FAQ(db.Model):
    """FAQ — 고객센터 자주 묻는 질문."""

    __tablename__ = "faqs"

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False, index=True)
    question = db.Column(db.String(300), nullable=False)
    answer = db.Column(db.Text, nullable=False)
    sort_order = db.Column(db.Integer, default=0, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<FAQ [{self.category}] {self.question[:30]}>"
