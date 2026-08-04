"""
User 모델 — 회원 정보.

users 테이블: 회원가입, 로그인, 마이페이지, 관리자 권한.
"""

from __future__ import annotations

from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db


class User(UserMixin, db.Model):
    """회원."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    full_name = db.Column(db.String(80))
    birth_year = db.Column(db.Integer)
    birth_month = db.Column(db.Integer)
    birth_day = db.Column(db.Integer)
    calendar_type = db.Column(db.String(10), default="solar")
    region = db.Column(db.String(40))
    agree_sms = db.Column(db.Boolean, default=False, nullable=False)
    agree_email = db.Column(db.Boolean, default=False, nullable=False)
    auth_provider = db.Column(db.String(20))
    auth_provider_id = db.Column(db.String(128), index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.String(255))
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # 관계: 1:N
    cart_items = db.relationship("CartItem", back_populates="user", cascade="all, delete-orphan")
    orders = db.relationship("Order", back_populates="user", cascade="all, delete-orphan")
    wishlist_items = db.relationship(
        "WishlistItem", back_populates="user", cascade="all, delete-orphan"
    )
    user_coupons = db.relationship(
        "UserCoupon", back_populates="user", cascade="all, delete-orphan"
    )
    point_entries = db.relationship(
        "PointLedger", back_populates="user", cascade="all, delete-orphan"
    )
    reviews = db.relationship("Review", back_populates="user", cascade="all, delete-orphan")
    product_questions = db.relationship(
        "ProductQuestion", back_populates="user", cascade="all, delete-orphan"
    )
    customer_inquiries = db.relationship(
        "CustomerInquiry", back_populates="user", cascade="all, delete-orphan"
    )

    def set_password(self, password: str) -> None:
        """비밀번호 해시 저장."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """비밀번호 검증."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self) -> str:
        return f"<User {self.username}>"
