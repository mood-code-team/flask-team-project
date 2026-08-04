"""쿠폰 모델."""

from __future__ import annotations

from datetime import datetime

from extensions import db


class Coupon(db.Model):
    """쿠폰 정의."""

    __tablename__ = "coupons"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(40), unique=True, nullable=False, index=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(255))
    discount_type = db.Column(db.String(20), nullable=False)  # percent, fixed, shipping
    discount_value = db.Column(db.Integer, nullable=False, default=0)
    min_amount = db.Column(db.Integer, nullable=False, default=0)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user_coupons = db.relationship("UserCoupon", back_populates="coupon", lazy="dynamic")


class UserCoupon(db.Model):
    """회원별 발급·사용 쿠폰."""

    __tablename__ = "user_coupons"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    coupon_id = db.Column(db.Integer, db.ForeignKey("coupons.id"), nullable=False, index=True)
    issued_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    used_at = db.Column(db.DateTime)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"))

    user = db.relationship("User", back_populates="user_coupons")
    coupon = db.relationship("Coupon", back_populates="user_coupons")
