"""
DB 초기화 및 Mood Code 카탈로그 시드.

실행: python scripts/seed_db.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import create_app  # noqa: E402
from extensions import db
from models import Category, FAQ, Notice, Product, User
from scripts.catalog_data import CATALOG
from services.db_schema import (
    ensure_category_schema,
    ensure_product_filter_schema,
    ensure_user_schema,
)


def seed_catalog() -> None:
    """Notion·사이드 메뉴 기준 카테고리·상품 시드."""
    slug_map: dict[str, Category] = {}

    for group in CATALOG:
        parent = Category.query.filter_by(slug=group["slug"]).first()
        if not parent:
            parent = Category(
                name=group["name"],
                name_en=group["name_en"],
                slug=group["slug"],
                description=group["description"],
                icon=group["icon"],
                sort_order=group["sort_order"],
                is_active=True,
            )
            db.session.add(parent)
        else:
            parent.name = group["name"]
            parent.name_en = group["name_en"]
            parent.description = group["description"]
            parent.icon = group["icon"]
            parent.sort_order = group["sort_order"]
            parent.parent_id = None
            parent.is_active = True

        db.session.flush()
        slug_map[group["slug"]] = parent

        for child in group.get("children", []):
            sub = Category.query.filter_by(slug=child["slug"]).first()
            if not sub:
                sub = Category(
                    name=child["name"],
                    slug=child["slug"],
                    parent_id=parent.id,
                    sort_order=child.get("sort_order", 0),
                    is_active=True,
                )
                db.session.add(sub)
            else:
                sub.name = child["name"]
                sub.parent_id = parent.id
                sub.sort_order = child.get("sort_order", 0)
                sub.is_active = True
            db.session.flush()
            slug_map[child["slug"]] = sub

        expected_child_slugs = {child["slug"] for child in group.get("children", [])}
        for orphan in Category.query.filter_by(parent_id=parent.id).all():
            if orphan.slug not in expected_child_slugs:
                Product.query.filter_by(category_id=orphan.id).update(
                    {"category_id": parent.id},
                    synchronize_session=False,
                )
                orphan.is_active = False

        for raw in group.get("products", []):
            item = dict(raw)
            cat_slug = item.pop("category")
            category = slug_map.get(cat_slug)
            if not category:
                continue

            product = Product.query.filter_by(slug=item["slug"]).first()
            fields = {
                "name": item["name"],
                "category_id": category.id,
                "description": f"{item['name']} — Mood Code 프리미엄 셀렉션",
                "price": item["price"],
                "discount_price": item.get("discount_price"),
                "stock": item.get("stock", 50),
                "image_url": item.get("image_url", f"/static/images/products/{item['slug']}.jpg"),
                "brand": item.get("brand", "Mood Code"),
                "filter_space": item.get("filter_space", ""),
                "filter_style": item.get("filter_style", ""),
                "filter_color": item.get("filter_color", ""),
                "has_installation": item.get("has_installation", False),
                "is_popular": item.get("is_popular", False),
                "is_new": item.get("is_new", False),
                "is_best": item.get("is_best", False),
                "is_active": True,
            }
            if product:
                for key, value in fields.items():
                    setattr(product, key, value)
            else:
                db.session.add(Product(slug=item["slug"], **fields))

    db.session.commit()


ADMIN_USERNAME = "gygs1010"
ADMIN_EMAIL = "gygs1010@gmail.com"
ADMIN_PASSWORD = "dnjsdlf@102360"
ADMIN_FULL_NAME = "Mood Code 관리자"


def seed_admin() -> None:
    """관리자 계정 시드 — gygs1010 (문서·실행_관리자.bat 기준)."""
    admin = User.query.filter(
        (User.username == ADMIN_USERNAME) | (User.email == ADMIN_EMAIL)
    ).first()

    if admin:
        admin.username = ADMIN_USERNAME
        admin.email = ADMIN_EMAIL
        admin.full_name = admin.full_name or ADMIN_FULL_NAME
        admin.is_admin = True
        admin.is_active = True
    else:
        admin = User(
            email=ADMIN_EMAIL,
            username=ADMIN_USERNAME,
            full_name=ADMIN_FULL_NAME,
            phone="010-0000-0000",
            is_admin=True,
        )
        db.session.add(admin)

    admin.set_password(ADMIN_PASSWORD)
    db.session.commit()


def seed_faqs() -> None:
    """FAQ DB 시드."""
    if FAQ.query.first():
        return
    items = [
        ("배송문의", "배송은 얼마나 걸리나요?", "일반 상품 2~5일, 주문 제작 2~4주 소요됩니다.", 1),
        ("배송문의", "설치 서비스가 있나요?", "시공 포함 상품은 전문 설치팀이 방문합니다.", 2),
        ("교환환불", "환불은 가능한가요?", "수령 후 7일 이내, 미사용 상품에 한해 가능합니다.", 1),
        ("회원", "회원가입은 어떻게 하나요?", "상단 메뉴의 회원가입에서 진행할 수 있습니다.", 1),
    ]
    for cat, q, a, order in items:
        db.session.add(FAQ(category=cat, question=q, answer=a, sort_order=order))
    db.session.commit()


def seed_notices() -> None:
    """공지사항 시드."""
    if Notice.query.first():
        return
    notices = [
        ("Grand Open — 신규 회원 10% 할인", "오픈 기념 신규 회원 할인 이벤트 진행 중!", True),
        ("배송 안내", "명절 연휴 배송 일정 변경 안내드립니다.", False),
    ]
    for title, content, pinned in notices:
        db.session.add(Notice(title=title, content=content, is_pinned=pinned))
    db.session.commit()


def main() -> None:
    app = create_app()
    with app.app_context():
        db.create_all()
        ensure_user_schema()
        ensure_category_schema()
        ensure_product_filter_schema()
        seed_catalog()
        seed_admin()
        seed_faqs()
        seed_notices()
        print("[OK] Mood Code DB 초기화 및 카탈로그 시드 완료")
        print(f"     카테고리: {Category.query.count()}개")
        print(f"     상품: {Product.query.count()}개")
        print(f"     관리자: {ADMIN_USERNAME} / {ADMIN_PASSWORD}")


if __name__ == "__main__":
    main()
