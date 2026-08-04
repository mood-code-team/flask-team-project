"""
상품 리뷰 작성·조회.
"""

from __future__ import annotations

from dataclasses import dataclass

from extensions import db
from models import Order, OrderItem, OrderStatus, Review


class ReviewError(ValueError):
    """리뷰 검증 실패."""


@dataclass
class ReviewableItem:
    order_item_id: int
    order_number: str
    product_id: int
    product_name: str
    product_slug: str
    image_url: str


def get_user_reviews(user_id: int) -> list[Review]:
    return (
        Review.query.filter_by(user_id=user_id)
        .order_by(Review.created_at.desc())
        .all()
    )


def get_reviewable_items(user_id: int) -> list[ReviewableItem]:
    """리뷰 미작성 + 배송완료/결제완료 주문 상품."""
    eligible_statuses = {
        OrderStatus.PAID,
        OrderStatus.PREPARING,
        OrderStatus.SHIPPING,
        OrderStatus.DELIVERED,
    }
    orders = (
        Order.query.filter(
            Order.user_id == user_id,
            Order.status.in_(eligible_statuses),
        )
        .order_by(Order.created_at.desc())
        .all()
    )

    reviewed_ids = {
        row.order_item_id
        for row in Review.query.filter_by(user_id=user_id).with_entities(Review.order_item_id)
    }

    items: list[ReviewableItem] = []
    for order in orders:
        for order_item in order.items:
            if order_item.id in reviewed_ids:
                continue
            product = order_item.product
            items.append(
                ReviewableItem(
                    order_item_id=order_item.id,
                    order_number=order.order_number,
                    product_id=order_item.product_id,
                    product_name=order_item.product_name,
                    product_slug=product.slug if product else "",
                    image_url=product.image_url if product and product.image_url else "",
                )
            )
    return items


def create_review(
    *,
    user_id: int,
    order_item_id: int,
    rating: int,
    content: str,
) -> Review:
    content = content.strip()
    if not content:
        raise ReviewError("리뷰 내용을 입력해 주세요.")
    if rating < 1 or rating > 5:
        raise ReviewError("별점은 1~5점 사이로 선택해 주세요.")

    order_item = OrderItem.query.get(order_item_id)
    if not order_item:
        raise ReviewError("주문 상품을 찾을 수 없습니다.")

    order = order_item.order
    if order.user_id != user_id:
        raise ReviewError("본인 주문만 리뷰를 작성할 수 있습니다.")
    if order.status not in {
        OrderStatus.PAID,
        OrderStatus.PREPARING,
        OrderStatus.SHIPPING,
        OrderStatus.DELIVERED,
    }:
        raise ReviewError("아직 리뷰를 작성할 수 없는 주문입니다.")

    if Review.query.filter_by(order_item_id=order_item_id).first():
        raise ReviewError("이미 리뷰를 작성한 상품입니다.")

    review = Review(
        user_id=user_id,
        product_id=order_item.product_id,
        order_item_id=order_item_id,
        rating=rating,
        content=content,
    )
    db.session.add(review)
    db.session.commit()
    return review


def get_product_reviews(product_id: int, *, limit: int = 20) -> list[Review]:
    return (
        Review.query.filter_by(product_id=product_id)
        .order_by(Review.created_at.desc())
        .limit(limit)
        .all()
    )
