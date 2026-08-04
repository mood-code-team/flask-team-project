"""
DB 기반 위시리스트.
"""

from __future__ import annotations

from flask_login import current_user

from extensions import db
from models import Product, WishlistItem

_GUEST_EMAILS = {"guest@shop.local"}
_GUEST_USERNAMES = {"guest_checkout", "guest"}


def _can_use_wishlist() -> bool:
    return (
        current_user.is_authenticated
        and current_user.username not in _GUEST_USERNAMES
        and current_user.email not in _GUEST_EMAILS
    )


def get_wishlist_products() -> list[Product]:
    """위시리스트 상품 (최근 추가 순)."""
    if not _can_use_wishlist():
        return []

    rows = (
        WishlistItem.query.filter_by(user_id=current_user.id)
        .order_by(WishlistItem.created_at.desc())
        .all()
    )
    return [row.product for row in rows if row.product and row.product.is_active]


def is_in_wishlist(product_id: int) -> bool:
    if not _can_use_wishlist():
        return False
    return (
        WishlistItem.query.filter_by(
            user_id=current_user.id,
            product_id=product_id,
        ).first()
        is not None
    )


def add_to_wishlist(product_id: int) -> bool:
    """추가. 이미 있으면 False."""
    if not _can_use_wishlist():
        raise ValueError("로그인 후 이용할 수 있습니다.")

    product = Product.query.filter_by(id=product_id, is_active=True).first()
    if not product:
        raise ValueError("상품을 찾을 수 없습니다.")
    if is_in_wishlist(product_id):
        return False

    db.session.add(WishlistItem(user_id=current_user.id, product_id=product_id))
    db.session.commit()
    return True


def remove_from_wishlist(product_id: int) -> bool:
    if not _can_use_wishlist():
        return False

    row = WishlistItem.query.filter_by(
        user_id=current_user.id,
        product_id=product_id,
    ).first()
    if not row:
        return False
    db.session.delete(row)
    db.session.commit()
    return True


def toggle_wishlist(product_id: int) -> bool:
    """토글 후 위시리스트 포함 여부 반환."""
    if is_in_wishlist(product_id):
        remove_from_wishlist(product_id)
        return False
    add_to_wishlist(product_id)
    return True


def serialize_wishlist() -> dict:
    """API/헤더용 위시리스트 JSON."""
    products = get_wishlist_products()
    return {
        "count": len(products),
        "items": [
            {
                "id": product.id,
                "slug": product.slug,
                "name": product.name,
                "image_url": product.image_url or "",
                "sale_price": product.sale_price,
            }
            for product in products
        ],
    }


def wishlist_count() -> int:
    if not _can_use_wishlist():
        return 0
    return WishlistItem.query.filter_by(user_id=current_user.id).count()
