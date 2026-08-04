"""검색·카테고리 필터."""

from __future__ import annotations

from dataclasses import dataclass, fields

from models import Product

FILTER_GROUPS: dict[str, dict] = {
    "sort": {
        "label": "정렬",
        "options": {
            "newest": "신상품",
            "name": "상품명",
            "price_asc": "낮은가격",
            "price_desc": "높은가격",
            "popular": "인기상품",
        },
    },
    "space": {
        "label": "공간",
        "options": {
            "living": "거실",
            "bedroom": "침실",
            "kitchen": "주방",
            "balcony": "발코니",
        },
    },
    "style": {
        "label": "스타일",
        "options": {
            "spring": "Spring",
            "summer": "Summer",
            "fall": "Fall",
            "winter": "Winter",
        },
    },
    "color": {
        "label": "컬러",
        "options": {
            "white": "화이트",
            "beige": "베이지",
            "gray": "그레이",
            "wood": "우드",
            "black": "블랙",
            "pink": "핑크",
            "yellow": "옐로우",
            "green": "그린",
            "blue": "블루",
        },
    },
    "brand": {
        "label": "브랜드",
        "options": {},
    },
}

COLOR_SWATCHES: dict[str, str] = {
    "white": "#ffffff",
    "beige": "#d4b896",
    "gray": "#9e9e9e",
    "wood": "#a67c52",
    "black": "#333333",
    "pink": "#f4a6b8",
    "yellow": "#f5d76e",
    "green": "#7cb68a",
    "blue": "#7ba7d7",
}


SEASON_STYLE_NAV: tuple[dict[str, str], ...] = (
    {"style": "spring", "label": "Spring", "scroll_id": "season-spring"},
    {"style": "summer", "label": "Summer", "scroll_id": "season-summer"},
    {"style": "fall", "label": "Fall", "scroll_id": "season-autumn"},
    {"style": "winter", "label": "Winter", "scroll_id": "season-winter"},
)


def build_season_nav() -> list[dict]:
    """헤더 계절 메뉴 — 홈은 스크롤, 카테고리/검색은 스타일 필터."""
    from flask import request, url_for

    endpoint = request.endpoint
    active_style = request.args.get("style", "").strip()
    query_params = {key: value for key, value in request.args.items() if key != "page"}

    if endpoint == "category.listing":
        slug = request.view_args.get("slug")
        if not slug:
            return _season_nav_scroll_items()

        items: list[dict] = []
        for item in SEASON_STYLE_NAV:
            params = dict(query_params)
            style = item["style"]
            if active_style == style:
                params.pop("style", None)
            else:
                params["style"] = style
            items.append({
                "label": item["label"],
                "href": url_for("category.listing", slug=slug, **params),
                "is_active": active_style == style,
                "mode": "filter",
            })
        return items

    if endpoint == "search.results":
        items = []
        for item in SEASON_STYLE_NAV:
            params = dict(query_params)
            style = item["style"]
            if active_style == style:
                params.pop("style", None)
            else:
                params["style"] = style
            items.append({
                "label": item["label"],
                "href": url_for("search.results", **params),
                "is_active": active_style == style,
                "mode": "filter",
            })
        return items

    return _season_nav_scroll_items()


def _season_nav_scroll_items() -> list[dict]:
    """홈 등 — 시즌 섹션으로 스크롤."""
    return [
        {
            "label": item["label"],
            "href": "#",
            "scroll_target": item["scroll_id"],
            "is_active": False,
            "mode": "scroll",
        }
        for item in SEASON_STYLE_NAV
    ]


@dataclass
class ActiveFilters:
    """현재 적용 중인 검색 필터."""

    sort: str = "newest"
    space: str = ""
    style: str = ""
    color: str = ""
    brand: str = ""

    def as_query_params(self) -> dict[str, str]:
        params: dict[str, str] = {"sort": self.sort}
        for field in fields(self):
            if field.name == "sort":
                continue
            value = getattr(self, field.name)
            if value:
                params[field.name] = value
        return params

    def active_count(self) -> int:
        count = sum(
            1 for field in fields(self)
            if field.name != "sort" and getattr(self, field.name)
        )
        if self.sort != "newest":
            count += 1
        return count


def get_active_filter_tags(filters: ActiveFilters) -> list[dict]:
    """선택된 필터 태그 목록."""
    tags: list[dict] = []

    if filters.sort and filters.sort != "newest":
        tags.append({
            "key": "sort",
            "label": get_option_label("sort", filters.sort),
            "swatch": None,
        })

    for key in ("space", "style", "color", "brand"):
        value = getattr(filters, key)
        if not value:
            continue
        tags.append({
            "key": key,
            "label": get_option_label(key, value),
            "swatch": COLOR_SWATCHES.get(value) if key == "color" else None,
        })

    return tags


def get_brand_options() -> dict[str, str]:
    """DB에 등록된 브랜드 목록."""
    from extensions import db

    rows = (
        db.session.query(Product.brand)
        .filter(
            Product.is_active.is_(True),
            Product.brand.isnot(None),
            Product.brand != "",
        )
        .distinct()
        .all()
    )
    brands = sorted({row[0] for row in rows if row[0]})
    return {brand: brand for brand in brands}


def get_filter_groups() -> dict[str, dict]:
    """필터 UI — 브랜드는 DB에서 동적 로드."""
    groups = {
        key: {"label": value["label"], "options": dict(value["options"])}
        for key, value in FILTER_GROUPS.items()
    }
    groups["brand"]["options"] = get_brand_options()
    if not groups["brand"]["options"]:
        groups.pop("brand")
    return groups


def parse_filters(args) -> ActiveFilters:
    """요청 쿼리에서 필터 파싱."""
    sort = args.get("sort", "newest")
    if sort == "relevance":
        sort = "newest"
    if sort not in FILTER_GROUPS["sort"]["options"]:
        sort = "newest"

    brand_options = get_brand_options()

    def pick(key: str) -> str:
        value = args.get(key, "").strip()
        options = FILTER_GROUPS[key]["options"]
        if key == "brand":
            options = brand_options
        return value if value in options else ""

    return ActiveFilters(
        sort=sort,
        space=pick("space"),
        style=pick("style"),
        color=pick("color"),
        brand=pick("brand"),
    )


def product_matches_filters(product: Product, filters: ActiveFilters) -> bool:
    """상품이 선택 필터에 맞는지 확인 (DB 컬럼 기준)."""
    checks = (
        ("space", product.filter_space or ""),
        ("style", product.filter_style or ""),
        ("color", product.filter_color or ""),
    )
    for key, value in checks:
        selected = getattr(filters, key)
        if selected and value != selected:
            return False

    if filters.brand and (product.brand or "") != filters.brand:
        return False

    return True


def get_product_specs(product: Product) -> list[dict[str, str]]:
    """상품 상세 — 스펙 표시."""
    specs: list[dict[str, str]] = []
    if product.brand:
        specs.append({"label": "브랜드", "value": product.brand})
    if product.filter_space:
        specs.append({"label": "공간", "value": get_option_label("space", product.filter_space)})
    if product.filter_style:
        specs.append({"label": "스타일", "value": get_option_label("style", product.filter_style)})
    if product.filter_color:
        specs.append({"label": "컬러", "value": get_option_label("color", product.filter_color)})
    flags = []
    if product.is_new:
        flags.append("신상품")
    if product.is_best:
        flags.append("베스트")
    if product.is_popular:
        flags.append("인기")
    if flags:
        specs.append({"label": "제품정보", "value": " · ".join(flags)})
    return specs


def get_option_label(group_key: str, value: str) -> str:
    """필터 값 → 표시 라벨."""
    if not value:
        return ""
    if group_key == "brand":
        return value
    return FILTER_GROUPS[group_key]["options"].get(value, value)
