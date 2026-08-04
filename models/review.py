"""상품 리뷰."""

from __future__ import annotations

from datetime import datetime

from extensions import db


class Review(db.Model):
    """구매 후기."""

    __tablename__ = "reviews"
    __table_args__ = (
        db.UniqueConstraint("order_item_id", name="uq_review_order_item"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False, index=True)
    order_item_id = db.Column(db.Integer, db.ForeignKey("order_items.id"), nullable=False, index=True)
    rating = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship("User", back_populates="reviews")
    product = db.relationship("Product", back_populates="reviews")
    order_item = db.relationship("OrderItem", back_populates="review")
