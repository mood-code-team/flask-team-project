"""시즌 상세 추천 상품."""

from __future__ import annotations

from extensions import db
from models import Category, Product


def get_season_products(category_slugs: tuple[str, ...], *, limit: int = 4) -> list[Product]:
    """시즌에 맞는 카테고리 상품 목록."""
    if not category_slugs:
        return []

    categories = Category.query.filter(
        Category.slug.in_(category_slugs),
        Category.is_active.is_(True),
    ).all()
    if not categories:
        return []

    category_ids = [cat.id for cat in categories]
    slug_order = {slug: index for index, slug in enumerate(category_slugs)}

    products = (
        db.session.query(Product)
        .join(Category)
        .filter(
            Product.category_id.in_(category_ids),
            Product.is_active.is_(True),
        )
        .order_by(Product.is_best.desc(), Product.is_popular.desc(), Product.id.desc())
        .all()
    )

    products.sort(key=lambda p: slug_order.get(p.category.slug, 99))
    return products[:limit]
