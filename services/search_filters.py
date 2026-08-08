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
            "all": "All Season",
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

# 컬러 → 시즌(filter_style) 매핑 (2차 데이터 정제 가이드)
COLOR_TO_SEASON: dict[str, str] = {
    "blue": "summer",
    "yellow": "summer",
    "pink": "spring",
    "green": "spring",
    "black": "winter",
    "gray": "winter",
    "wood": "fall",
    "beige": "fall",
}

# 화이트·베이지 — 시즌 필터/전체 목록에 항상 노출 (베이지는 fall 배정 + 공통 노출)
NEUTRAL_COLORS = frozenset({"white", "beige"})

# 사계절 공통 상품 — filter_style / mood_code 에 all 입력
UNIVERSAL_STYLE = "all"
SEASON_STYLES = ("spring", "summer", "fall", "winter")

SEASON_ID_TO_STYLE: dict[str, str] = {
    "spring": "spring",
    "summer": "summer",
    "autumn": "fall",
    "fall": "fall",
    "winter": "winter",
}


def normalize_filter_style(raw: str) -> str:
    """시즌 값 정규화 — spring/summer/fall/winter/all."""
    value = (raw or "").strip().lower()
    if value == UNIVERSAL_STYLE:
        return UNIVERSAL_STYLE
    if value in SEASON_STYLES:
        return value
    return ""


def infer_style_from_color(color: str) -> str:
    """지정 컬러 팔레트 → 시즌. 화이트는 사계절(all)."""
    value = (color or "").strip().lower()
    if value == "white":
        return UNIVERSAL_STYLE
    return COLOR_TO_SEASON.get(value, "")


def product_matches_style(product: Product, style: str) -> bool:
    """시즌(스타일) 필터 — all·공통 컬러(화이트·베이지)는 모든 시즌에 노출."""
    if not style or style == UNIVERSAL_STYLE:
        return True
    product_style = (product.filter_style or "").lower()
    if product_style == UNIVERSAL_STYLE:
        return True
    if (product.filter_color or "") in NEUTRAL_COLORS:
        return True
    return product_style == style


def season_id_to_style(season_id: str) -> str:
    """시즌 페이지 id → filter_style 값."""
    return SEASON_ID_TO_STYLE.get((season_id or "").strip().lower(), "")


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
    subcategory: str = ""

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


def get_active_filter_tags(
    filters: ActiveFilters,
    *,
    subcategory_options: dict[str, str] | None = None,
) -> list[dict]:
    """선택된 필터 태그 목록."""
    tags: list[dict] = []

    if filters.sort and filters.sort != "newest":
        tags.append({
            "key": "sort",
            "label": get_option_label("sort", filters.sort),
            "swatch": None,
        })

    for key in ("subcategory", "space", "style", "color"):
        value = getattr(filters, key)
        if not value:
            continue
        if key == "subcategory":
            label = (subcategory_options or {}).get(value, value)
        else:
            label = get_option_label(key, value)
        tags.append({
            "key": key,
            "label": label,
            "swatch": COLOR_SWATCHES.get(value) if key == "color" else None,
        })

    return tags


def get_filter_groups() -> dict[str, dict]:
    """필터 UI — 정렬·공간·스타일·컬러."""
    return {
        key: {"label": value["label"], "options": dict(value["options"])}
        for key, value in FILTER_GROUPS.items()
    }


def get_subcategory_options(category) -> dict[str, str]:
    """대분류 페이지 — 활성 소분류 필터 옵션."""
    children = [
        child for child in category.children
        if child.is_active
    ]
    children.sort(key=lambda item: (item.sort_order, item.id))
    return {child.slug: child.name for child in children}


def get_category_filter_groups(category) -> dict[str, dict]:
    """카테고리 목록 페이지 필터 — 소분류 포함, 브랜드 제외."""
    groups = get_filter_groups()
    subcategories = get_subcategory_options(category)
    if subcategories:
        groups = {
            "sort": groups["sort"],
            "subcategory": {"label": "소분류", "options": subcategories},
            **{key: groups[key] for key in ("space", "style", "color")},
        }
    return groups


def parse_filters(args, *, subcategory_options: dict[str, str] | None = None) -> ActiveFilters:
    """요청 쿼리에서 필터 파싱."""
    sort = args.get("sort", "newest")
    if sort == "relevance":
        sort = "newest"
    if sort not in FILTER_GROUPS["sort"]["options"]:
        sort = "newest"

    def pick(key: str) -> str:
        value = args.get(key, "").strip()
        options = FILTER_GROUPS[key]["options"]
        return value if value in options else ""

    subcategory = args.get("subcategory", "").strip()
    if subcategory_options is None:
        subcategory = ""
    elif subcategory not in subcategory_options:
        subcategory = ""

    return ActiveFilters(
        sort=sort,
        space=pick("space"),
        style=pick("style"),
        color=pick("color"),
        subcategory=subcategory,
    )


def product_matches_filters(product: Product, filters: ActiveFilters) -> bool:
    """상품이 선택 필터에 맞는지 확인 (DB 컬럼 기준)."""
    if filters.space and (product.filter_space or "") != filters.space:
        return False

    if filters.style and not product_matches_style(product, filters.style):
        return False

    if filters.color and (product.filter_color or "") != filters.color:
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
    if product.mood_code_number:
        specs.append({"label": "무드코드", "value": product.mood_code_number})
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


def get_option_label(group_key: str, value: str, *, subcategory_options: dict[str, str] | None = None) -> str:
    """필터 값 → 표시 라벨."""
    if not value:
        return ""
    if group_key == "subcategory":
        return (subcategory_options or {}).get(value, value)
    return FILTER_GROUPS[group_key]["options"].get(value, value)
