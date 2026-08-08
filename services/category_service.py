"""카테고리별 상품 조회."""

from __future__ import annotations

from dataclasses import dataclass

from extensions import db
from models import Category, Product
from services.category_banners import get_category_banner_urls
from services.search_filters import ActiveFilters, product_matches_filters
from services.search_service import _apply_sort


@dataclass
class CategoryListResult:
    """카테고리 목록 페이지 데이터."""

    category: Category
    products: list[Product]
    total: int
    page: int
    per_page: int
    filters: ActiveFilters

    @property
    def total_pages(self) -> int:
        if self.total == 0:
            return 0
        return (self.total + self.per_page - 1) // self.per_page

    @property
    def has_prev(self) -> bool:
        return self.page > 1

    @property
    def has_next(self) -> bool:
        return self.page < self.total_pages


def get_category_by_slug(slug: str) -> Category | None:
    """slug로 활성 카테고리 조회."""
    return Category.query.filter_by(slug=slug, is_active=True).first()


def get_category_root(category: Category) -> Category:
    """대분류 카테고리 반환."""
    current = category
    while current.parent_id:
        parent = db.session.get(Category, current.parent_id)
        if not parent or not parent.is_active:
            break
        current = parent
    return current


def get_category_banner_image(category: Category) -> dict[str, str]:
    """카테고리 목록 상단 고정 배너 (2K + 4K)."""
    root = get_category_root(category)
    return get_category_banner_urls(root.slug)


def _category_ids_for_listing(category: Category, filters: ActiveFilters) -> list[int]:
    """목록에 포함할 카테고리 ID."""
    if filters.subcategory:
        child = get_category_by_slug(filters.subcategory)
        root = get_category_root(category)
        if child and child.parent_id == root.id:
            return [child.id]

    ids = [category.id]
    for child in category.children:
        if child.is_active:
            ids.append(child.id)
    return ids


def list_category_products(
    slug: str,
    *,
    filters: ActiveFilters | None = None,
    page: int = 1,
    per_page: int = 12,
) -> CategoryListResult | None:
    """카테고리에 속한 상품 목록."""
    category = get_category_by_slug(slug)
    if not category:
        return None

    if filters is None:
        filters = ActiveFilters(sort="newest")

    page = max(page, 1)
    per_page = max(min(per_page, 48), 1)

    category_ids = _category_ids_for_listing(category, filters)

    base = (
        db.session.query(Product)
        .filter(Product.category_id.in_(category_ids), Product.is_active.is_(True))
    )

    ordered = _apply_sort(base, filters.sort, [])
    all_products = ordered.all()
    filtered = [p for p in all_products if product_matches_filters(p, filters)]

    total = len(filtered)
    start = (page - 1) * per_page
    products = filtered[start : start + per_page]

    return CategoryListResult(
        category=category,
        products=products,
        total=total,
        page=page,
        per_page=per_page,
        filters=filters,
    )
