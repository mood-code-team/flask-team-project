"""
Product 모델 — 상품 정보.

products 테이블: 상품 목록, 상세, 검색, 인기/신상/베스트 노출.
"""

from __future__ import annotations

from datetime import datetime

from extensions import db


class Product(db.Model):
    """가구/인테리어 상품."""

    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    price = db.Column(db.Integer, nullable=False)  # 원 단위 정수
    discount_price = db.Column(db.Integer)  # 할인가 (nullable)
    stock = db.Column(db.Integer, default=0, nullable=False)
    image_url = db.Column(db.String(500))
    brand = db.Column(db.String(80), index=True)
    filter_space = db.Column(db.String(20), index=True)   # living, bedroom, kitchen, balcony
    filter_style = db.Column(db.String(20), index=True)   # spring, summer, fall, winter, all
    filter_color = db.Column(db.String(20), index=True)   # white, beige, gray, ...
    mood_code_number = db.Column(db.String(32), index=True)  # MC-SF-001 (팀 내부 상품 코드)
    # 시공 서비스 포함 여부 (HFIX 참고)
    has_installation = db.Column(db.Boolean, default=False, nullable=False)
    # 노출 플래그
    is_popular = db.Column(db.Boolean, default=False, nullable=False)
    is_new = db.Column(db.Boolean, default=False, nullable=False)
    is_best = db.Column(db.Boolean, default=False, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # 관계
    category = db.relationship("Category", back_populates="products")
    cart_items = db.relationship("CartItem", back_populates="product", lazy="dynamic")
    order_items = db.relationship("OrderItem", back_populates="product", lazy="dynamic")
    wishlist_items = db.relationship("WishlistItem", back_populates="product", lazy="dynamic")
    reviews = db.relationship("Review", back_populates="product", lazy="dynamic")
    questions = db.relationship("ProductQuestion", back_populates="product", lazy="dynamic")

    @property
    def sale_price(self) -> int:
        """실제 판매가 (할인가 우선)."""
        return self.discount_price if self.discount_price else self.price

    @property
    def discount_rate(self) -> int:
        """할인율 (%)."""
        if self.discount_price and self.price > 0:
            return round((1 - self.discount_price / self.price) * 100)
        return 0

    def __repr__(self) -> str:
        return f"<Product {self.name}>"
