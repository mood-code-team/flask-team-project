"""상품 Q&A."""

from __future__ import annotations

from datetime import datetime

from extensions import db


class ProductQuestion(db.Model):
    """상품 문의."""

    __tablename__ = "product_questions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False, index=True)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text)
    answered_at = db.Column(db.DateTime)
    is_public = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship("User", back_populates="product_questions")
    product = db.relationship("Product", back_populates="questions")
