"""위시리스트 모델."""

from __future__ import annotations

from datetime import datetime

from extensions import db


class WishlistItem(db.Model):
    """회원 위시리스트."""

    __tablename__ = "wishlist"
    __table_args__ = (
        db.UniqueConstraint("user_id", "product_id", name="uq_wishlist_user_product"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship("User", back_populates="wishlist_items")
    product = db.relationship("Product", back_populates="wishlist_items")
