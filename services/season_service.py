"""시즌 상세 추천 상품."""

from __future__ import annotations

from extensions import db
from models import Category, Product
from services.search_filters import product_matches_style, season_id_to_style


def get_season_products(
    category_slugs: tuple[str, ...],
    *,
    season_id: str | None = None,
    limit: int = 4,
) -> list[Product]:
    """시즌에 맞는 카테고리 상품 목록 (컬러-시즌 매핑 반영)."""
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
    season_style = season_id_to_style(season_id or "")

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

    if season_style:
        products = [p for p in products if product_matches_style(p, season_style)]

    products.sort(key=lambda p: slug_order.get(p.category.slug, 99))
    return products[:limit]
