"""
Category 모델 — 상품 카테고리.

categories 테이블: 계층형 카테고리 (소파, 침대, 조명 등).
"""

from __future__ import annotations

from datetime import datetime

from extensions import db


class Category(db.Model):
    """상품 카테고리."""

    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    name_en = db.Column(db.String(100))  # 사이드 메뉴·카테고리 페이지 영문명
    slug = db.Column(db.String(100), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    icon = db.Column(db.String(50))  # CSS 아이콘 클래스 또는 이모지
    sort_order = db.Column(db.Integer, default=0, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # 자기 참조: 하위 카테고리 (선택)
    parent_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=True)
    parent = db.relationship("Category", remote_side=[id], backref="children")

    # 관계: 1:N
    products = db.relationship("Product", back_populates="category", lazy="dynamic")

    def __repr__(self) -> str:
        return f"<Category {self.name}>"
