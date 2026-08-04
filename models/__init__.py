"""
SQLAlchemy 모델 패키지.

모든 모델을 import 해야 Flask-Migrate 가 테이블을 인식합니다.
"""

from models.cart import CartItem
from models.customer_inquiry import CustomerInquiry, InquiryStatus
from models.category import Category
from models.coupon import Coupon, UserCoupon
from models.notice import FAQ, Notice
from models.order import Order, OrderItem, OrderStatus
from models.point import PointLedger
from models.product import Product
from models.product_question import ProductQuestion
from models.review import Review
from models.user import User
from models.wishlist import WishlistItem

__all__ = [
    "User",
    "Category",
    "Product",
    "CartItem",
    "Order",
    "OrderItem",
    "OrderStatus",
    "Notice",
    "FAQ",
    "WishlistItem",
    "Coupon",
    "UserCoupon",
    "PointLedger",
    "Review",
    "ProductQuestion",
    "CustomerInquiry",
    "InquiryStatus",
]
