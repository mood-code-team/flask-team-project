"""
데모 콘텐츠 시드 — 리뷰·Q&A·샘플 주문 (실제 쇼핑몰처럼 보이게).

사용:
  python scripts/seed_demo_content.py
  python scripts/seed_demo_content.py --reset   # 기존 데모 데이터 삭제 후 재생성
"""

from __future__ import annotations

import argparse
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import create_app  # noqa: E402
from extensions import db
from models import Order, OrderItem, OrderStatus, Product, ProductQuestion, Review, User

DEMO_USERS = [
    {
        "email": "demo1@shop.local",
        "username": "demo_user1",
        "full_name": "김서연",
        "password": "demo1234",
    },
    {
        "email": "demo2@shop.local",
        "username": "demo_user2",
        "full_name": "이준호",
        "password": "demo1234",
    },
    {
        "email": "demo3@shop.local",
        "username": "demo_user3",
        "full_name": "박민지",
        "password": "demo1234",
    },
]

REVIEW_TEMPLATES = [
    ("색감이 사진과 동일해요. 거실 분위기가 확 살았습니다.", 5),
    ("배송 빠르고 포장도 깔끔했어요. 조립도 쉬웠습니다.", 5),
    ("가격 대비 만족합니다. 사이즈도 딱 맞아요.", 4),
    ("디자인이 깔끔해서 1인 가구에 잘 어울려요.", 5),
    ("촉감/마감 모두 좋아요. 추천합니다.", 4),
    ("생각보다 가볍고 이동하기 편해요.", 4),
    ("은은한 색감이 예쁩니다. 사진 그대로예요.", 5),
]

QNA_TEMPLATES = [
    ("배송 기간이 보통 며칠 정도 걸리나요?", "결제 완료 후 2~5일(영업일) 내 출고됩니다."),
    ("조립 서비스도 가능한가요?", "해당 상품은 셀프 조립이며, 시공 포함 상품은 상세페이지에 표시됩니다."),
    ("실물 색상이 사진과 많이 다른가요?", "모니터 설정에 따라 약간 차이 있을 수 있으나 실물과 유사하게 촬영했습니다."),
    ("교환/반품 가능한가요?", "수령 후 7일 이내, 미사용·미개봉 상태에서 가능합니다."),
    ("1인 가구에도 사이즈가 적당한가요?", "상세 스펙의 가로·세로·높이를 참고해 주세요. 문의 주시면 추천드립니다."),
]


def _get_or_create_demo_users() -> list[User]:
    users: list[User] = []
    for data in DEMO_USERS:
        user = User.query.filter_by(email=data["email"]).first()
        if not user:
            user = User(
                email=data["email"],
                username=data["username"],
                full_name=data["full_name"],
                phone="010-1234-5678",
                is_active=True,
            )
            user.set_password(data["password"])
            db.session.add(user)
        users.append(user)
    db.session.flush()
    return users


def _reset_demo_content() -> None:
    demo_emails = [u["email"] for u in DEMO_USERS]
    demo_users = User.query.filter(User.email.in_(demo_emails)).all()
    demo_ids = [u.id for u in demo_users]

    if demo_ids:
        Review.query.filter(Review.user_id.in_(demo_ids)).delete(synchronize_session=False)
        ProductQuestion.query.filter(ProductQuestion.user_id.in_(demo_ids)).delete(synchronize_session=False)
        Order.query.filter(Order.user_id.in_(demo_ids)).delete(synchronize_session=False)


def _create_demo_orders_and_reviews(users: list[User], products: list[Product]) -> tuple[int, int]:
    order_count = 0
    review_count = 0
    now = datetime.now(UTC).replace(tzinfo=None)

    for idx, user in enumerate(users):
        product = products[idx % len(products)]
        order_number = f"DEMO{now.strftime('%Y%m%d')}{idx + 1:03d}"

        if Order.query.filter_by(order_number=order_number).first():
            continue

        unit_price = product.sale_price
        order = Order(
            user_id=user.id,
            order_number=order_number,
            status=OrderStatus.DELIVERED,
            product_total=unit_price,
            shipping_fee=0,
            total_amount=unit_price,
            payment_method="card",
            paid_at=now - timedelta(days=7 + idx),
            recipient_name=user.full_name or user.username,
            recipient_phone=user.phone or "010-0000-0000",
            shipping_address="서울특별시 강남구 테헤란로 123",
        )
        db.session.add(order)
        db.session.flush()

        item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            product_name=product.name,
            unit_price=unit_price,
            quantity=1,
            subtotal=unit_price,
        )
        db.session.add(item)
        db.session.flush()
        order_count += 1

        template, rating = REVIEW_TEMPLATES[idx % len(REVIEW_TEMPLATES)]
        if not Review.query.filter_by(order_item_id=item.id).first():
            db.session.add(
                Review(
                    user_id=user.id,
                    product_id=product.id,
                    order_item_id=item.id,
                    rating=rating,
                    content=template,
                    created_at=now - timedelta(days=3 + idx),
                )
            )
            review_count += 1

    return order_count, review_count


def _create_demo_qna(users: list[User], products: list[Product]) -> int:
    count = 0
    now = datetime.now(UTC).replace(tzinfo=None)

    for idx, product in enumerate(products[:15]):
        user = users[idx % len(users)]
        question, answer = QNA_TEMPLATES[idx % len(QNA_TEMPLATES)]

        exists = ProductQuestion.query.filter_by(
            user_id=user.id,
            product_id=product.id,
            question=question,
        ).first()
        if exists:
            continue

        db.session.add(
            ProductQuestion(
                user_id=user.id,
                product_id=product.id,
                question=question,
                answer=answer,
                answered_at=now - timedelta(days=1),
                is_public=True,
                created_at=now - timedelta(days=2),
            )
        )
        count += 1

    return count


def seed_demo_content(*, reset: bool = False) -> dict[str, int]:
    if reset:
        _reset_demo_content()

    users = _get_or_create_demo_users()
    popular = (
        Product.query.filter_by(is_active=True, is_popular=True)
        .order_by(Product.id)
        .limit(20)
        .all()
    )
    if len(popular) < 10:
        popular = Product.query.filter_by(is_active=True).order_by(Product.price.desc()).limit(20).all()

    orders, reviews = _create_demo_orders_and_reviews(users, popular[: len(users)])
    qna = _create_demo_qna(users, popular)

    db.session.commit()
    return {
        "users": len(users),
        "orders": orders,
        "reviews": reviews,
        "qna": qna,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed demo reviews, Q&A, and orders")
    parser.add_argument("--reset", action="store_true", help="Remove existing demo data first")
    args = parser.parse_args()

    app = create_app()
    with app.app_context():
        stats = seed_demo_content(reset=args.reset)

    print("[DEMO] seed complete")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    print("  demo login: demo1@shop.local / demo1234")


if __name__ == "__main__":
    main()
