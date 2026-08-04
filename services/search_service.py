"""상품 검색."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import func, or_

from extensions import db
from models import Category, Product
from services.search_filters import ActiveFilters, product_matches_filters

# 추천 검색어 (헤더 패널·검색 페이지 — 표시는 영어)
RECOMMENDED_KEYWORDS: list[str] = ["Lighting", "Sofa", "Side Table", "Diffuser"]

# 카테고리·동의어 — 한글 입력 시 영어 카테고리/상품까지 확장
KEYWORD_ALIASES: dict[str, list[str]] = {
    "Lighting": ["lighting", "light", "led", "조명", "펜던트", "스탠드", "램프"],
    "Sofa": ["sofa", "쇼파", "소파", "리클라이너"],
    "Side Table": ["side table", "side-table", "협탁", "사이드", "테이블", "night"],
    "Diffuser": ["diffuser", "디퓨저", "향", "아로마", "캔들"],
    "조명": ["Lighting", "lighting", "light", "led", "펜던트", "스탠드", "램프"],
    "쇼파": ["Sofa", "sofa", "소파", "리클라이너"],
    "소파": ["Sofa", "sofa", "쇼파", "리클라이너"],
    "협탁": ["Side Table", "side table", "side-table", "사이드", "테이블", "night"],
    "디퓨저": ["Diffuser", "diffuser", "향", "아로마", "캔들"],
    "침대": ["bed", "매트리스"],
    "수납": ["storage", "장", "수납장"],
    "시공": ["installation", "붙박이", "인테리어"],
}


def _matches_term(query: str, query_lower: str, candidate: str) -> bool:
    """검색어와 후보 키워드 일치 여부 (한글·영문, 부분 일치)."""
    candidate_lower = candidate.lower()
    return (
        query == candidate
        or query_lower == candidate_lower
        or candidate_lower in query_lower
        or query_lower in candidate_lower
    )


@dataclass
class SearchResult:
    """검색 결과 페이지 데이터."""

    products: list[Product]
    total: int
    page: int
    per_page: int
    query: str
    sort: str
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


def expand_query_terms(query: str) -> list[str]:
    """검색어와 동의어/관련어 목록 반환."""
    normalized = query.strip()
    if not normalized:
        return []

    terms = {normalized}
    lower = normalized.lower()
    for key, aliases in KEYWORD_ALIASES.items():
        candidates = (key, *aliases)
        if any(_matches_term(normalized, lower, candidate) for candidate in candidates):
            terms.add(key)
            terms.update(aliases)

    return list(terms)


def _build_search_filter(terms: list[str]):
    """SQLAlchemy OR 필터 생성."""
    conditions = []
    for term in terms:
        pattern = f"%{term}%"
        conditions.extend(
            [
                Product.name.ilike(pattern),
                Product.description.ilike(pattern),
                Product.slug.ilike(pattern),
                Category.name.ilike(pattern),
                Category.slug.ilike(pattern),
            ]
        )
    return or_(*conditions)


def _apply_sort(query, sort: str, terms: list[str]):
    """정렬 적용."""
    sale_price = func.coalesce(Product.discount_price, Product.price)

    if sort == "price_asc":
        return query.order_by(sale_price.asc(), Product.id.asc())
    if sort == "price_desc":
        return query.order_by(sale_price.desc(), Product.id.desc())
    if sort == "name":
        return query.order_by(Product.name.asc(), Product.id.asc())
    if sort == "popular":
        return query.order_by(
            Product.is_popular.desc(),
            Product.is_best.desc(),
            Product.id.desc(),
        )
    if sort == "newest":
        return query.order_by(Product.created_at.desc(), Product.id.desc())

    # 기본 — 신상품순
    return query.order_by(Product.created_at.desc(), Product.id.desc())


def search_products(
    query: str,
    *,
    filters: ActiveFilters | None = None,
    sort: str | None = None,
    page: int = 1,
    per_page: int = 12,
) -> SearchResult:
    """활성 상품 통합 검색."""
    if filters is None:
        filters = ActiveFilters()

    if sort is not None:
        filters.sort = sort

    sort_key = filters.sort
    page = max(page, 1)
    per_page = max(min(per_page, 48), 1)
    terms = expand_query_terms(query)

    base = (
        db.session.query(Product)
        .join(Category)
        .filter(Product.is_active.is_(True))
    )

    if terms:
        base = base.filter(_build_search_filter(terms))

    ordered = _apply_sort(base, sort_key, terms)
    all_products = ordered.all()
    filtered = [p for p in all_products if product_matches_filters(p, filters)]

    total = len(filtered)
    start = (page - 1) * per_page
    products = filtered[start : start + per_page]

    return SearchResult(
        products=products,
        total=total,
        page=page,
        per_page=per_page,
        query=query.strip(),
        sort=sort_key,
        filters=filters,
    )
