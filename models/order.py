"""
Order / OrderItem 모델 — 주문.

orders, order_items 테이블: 주문 생성, 배송지, 주문 내역.
"""

from __future__ import annotations

from datetime import datetime

from extensions import db


class OrderStatus:
    """주문 상태 상수."""

    PENDING = "pending"       # 주문 접수
    PAID = "paid"             # 결제 완료
    PREPARING = "preparing"   # 상품 준비
    SHIPPING = "shipping"     # 배송 중
    DELIVERED = "delivered"   # 배송 완료
    CANCELLED = "cancelled"   # 취소

    LABELS = {
        PENDING: "주문 접수",
        PAID: "결제 완료",
        PREPARING: "상품 준비",
        SHIPPING: "배송 중",
        DELIVERED: "배송 완료",
        CANCELLED: "취소",
    }


class Order(db.Model):
    """주문."""

    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    order_number = db.Column(db.String(30), unique=True, nullable=False, index=True)
    status = db.Column(db.String(20), default=OrderStatus.PENDING, nullable=False)
    product_total = db.Column(db.Integer, nullable=False, default=0)
    shipping_fee = db.Column(db.Integer, nullable=False, default=0)
    coupon_discount = db.Column(db.Integer, nullable=False, default=0)
    point_used = db.Column(db.Integer, nullable=False, default=0)
    user_coupon_id = db.Column(db.Integer, db.ForeignKey("user_coupons.id"))
    total_amount = db.Column(db.Integer, nullable=False)
    payment_key = db.Column(db.String(200))
    payment_method = db.Column(db.String(40))
    paid_at = db.Column(db.DateTime)
    # 배송지 정보
    recipient_name = db.Column(db.String(80), nullable=False)
    recipient_phone = db.Column(db.String(20), nullable=False)
    shipping_address = db.Column(db.String(255), nullable=False)
    shipping_memo = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # 관계
    user = db.relationship("User", back_populates="orders")
    items = db.relationship(
        "OrderItem", back_populates="order", cascade="all, delete-orphan", lazy="joined"
    )
    applied_coupon = db.relationship(
        "UserCoupon",
        foreign_keys=[user_coupon_id],
    )
    point_entries = db.relationship("PointLedger", back_populates="order", lazy="dynamic")

    @property
    def status_label(self) -> str:
        return OrderStatus.LABELS.get(self.status, self.status)

    @property
    def can_cancel(self) -> bool:
        """배송 시작 전까지 취소 가능."""
        return self.status in {
            OrderStatus.PENDING,
            OrderStatus.PAID,
            OrderStatus.PREPARING,
        }

    def __repr__(self) -> str:
        return f"<Order {self.order_number}>"


class OrderItem(db.Model):
    """주문 상품 (스냅샷 — 주문 시점 가격/이름 보존)."""

    __tablename__ = "order_items"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    product_name = db.Column(db.String(200), nullable=False)
    unit_price = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    subtotal = db.Column(db.Integer, nullable=False)

    # 관계
    order = db.relationship("Order", back_populates="items")
    product = db.relationship("Product", back_populates="order_items")
    review = db.relationship("Review", back_populates="order_item", uselist=False)

    def __repr__(self) -> str:
        return f"<OrderItem {self.product_name} x{self.quantity}>"
