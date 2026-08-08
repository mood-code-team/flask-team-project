"""
상품 데이터 보강 — CSV/DB import 후 실제 쇼핑몰처럼 메타데이터 추론.

색상·스타일 키워드, 할인율, 뱃지(is_popular/new/best) 규칙.
2차 육안 검수 CSV 값은 import 시 우선 반영되며, enrich_products는 빈 값만 채움.
"""

from __future__ import annotations

import hashlib
import re
from typing import Any

from services.search_filters import (
    SEASON_STYLES,
    infer_style_from_color,
    normalize_filter_style,
)

# 지정 색상 팔레트 (search_filters.py 와 동일)
PALETTE_COLORS = frozenset({
    "white", "beige", "gray", "wood", "black", "pink", "yellow", "green", "blue",
})

# CSV 한글 filter_color → 영문 팔레트
KOREAN_COLOR_MAP: dict[str, str] = {
    "화이트": "white",
    "오프화이트": "white",
    "옐로우": "yellow",
    "옐로": "yellow",
    "그레이": "gray",
    "그레이그린": "green",
    "라이트그레이": "gray",
    "다크그레이": "gray",
    "그린": "green",
    "블루": "blue",
    "라이트블루": "blue",
    "블랙": "black",
    "베이지": "beige",
    "라이트베이지": "beige",
    "우드": "wood",
    "핑크": "pink",
    "레드": "pink",
    "다크레드": "pink",
    "오렌지": "yellow",
    "황동색": "wood",
    "황동": "wood",
    "니켈": "gray",
    "앤트러싸이트": "black",
    "다크베이지": "beige",
    "다크그린": "green",
    "다크블루": "blue",
    "브라이트레드": "pink",
    "레드브라운": "pink",
    "라이트오렌지": "yellow",
    "브라운오렌지": "yellow",
    "옐로베이지": "beige",
    "다크브라운": "wood",
}

# 복합색상명에서 필터 우선순위 (액센트/패브릭 > 프레임 우드)
COLOR_FILTER_PRIORITY = (
    "white", "beige", "yellow", "green", "blue", "pink", "black", "gray", "wood",
)

COLOR_KEYWORDS: list[tuple[str, str]] = [
    ("화이트", "white"),
    ("white", "white"),
    ("오프화이트", "white"),
    ("흰", "white"),
    ("베이지", "beige"),
    ("beige", "beige"),
    ("아이보리", "beige"),
    ("크림", "beige"),
    ("그레이", "gray"),
    ("grey", "gray"),
    ("gray", "gray"),
    ("회색", "gray"),
    ("다크 그레이", "gray"),
    ("블랙", "black"),
    ("black", "black"),
    ("검정", "black"),
    ("우드", "wood"),
    ("원목", "wood"),
    ("oak", "wood"),
    ("walnut", "wood"),
    ("birch", "wood"),
    ("핑크", "pink"),
    ("pink", "pink"),
    ("옐로", "yellow"),
    ("옐로우", "yellow"),
    ("yellow", "yellow"),
    ("노란", "yellow"),
    ("옐로그린", "green"),
    ("다크옐로", "yellow"),
    ("브라이트옐로", "yellow"),
    ("그린", "green"),
    ("green", "green"),
    ("초록", "green"),
    ("블루", "blue"),
    ("blue", "blue"),
    ("파란", "blue"),
    ("네이비", "blue"),
    ("다크블루", "blue"),
    ("앤트러싸이트", "black"),
    ("다크베이지", "beige"),
    ("라이트베이지", "beige"),
    ("다크그린", "green"),
    ("브라이트레드", "pink"),
    ("레드브라운", "pink"),
    ("레드", "pink"),
    ("라이트오렌지", "yellow"),
    ("브라운오렌지", "yellow"),
    ("옐로베이지", "beige"),
    ("다크브라운", "wood"),
    ("블랙브라운", "black"),
    ("브라운", "wood"),
    ("소나무", "wood"),
    ("아카시아", "wood"),
    ("아카시아나무", "wood"),
    ("나무", "wood"),
]

# 할인율 후보 (%)
DISCOUNT_RATES = (5, 10, 15, 20, 25, 30)


def stable_hash(text: str) -> int:
    return int(hashlib.md5(text.encode("utf-8")).hexdigest(), 16)


def infer_color(name: str, description: str = "") -> str:
    text = f"{name} {description}".lower()
    for keyword, color in sorted(COLOR_KEYWORDS, key=lambda item: len(item[0]), reverse=True):
        if keyword.lower() in text:
            return color
    return ""


def infer_primary_color_from_name(name: str) -> str:
    """IKEA 상품명에서 대표 필터 색 추출 (변형명 `-` 뒤, `/` 구분)."""
    if not name:
        return ""
    segment = name.split(" - ")[-1].strip()
    parts = [part.strip() for part in re.split(r"[/]", segment) if part.strip()]
    found: list[str] = []
    for part in parts or [segment]:
        color = infer_color(part, "")
        if color and color not in found:
            found.append(color)
    if not found:
        return infer_color(segment, "")
    if len(found) == 1:
        return found[0]

    non_wood = [color for color in found if color != "wood"]
    if non_wood:
        for preferred in COLOR_FILTER_PRIORITY:
            if preferred in non_wood:
                return preferred
        return non_wood[0]
    return found[0]


def _map_raw_color_to_palette(raw: str) -> str:
    """CSV filter_color(한/영, 복합) → 팔레트."""
    text = (raw or "").strip()
    if not text:
        return ""

    lowered = text.lower()
    if lowered in PALETTE_COLORS:
        return lowered

    if text in KOREAN_COLOR_MAP:
        return KOREAN_COLOR_MAP[text]

    for token in re.split(r"[\s/]+", text):
        token = token.strip()
        if not token:
            continue
        if token.lower() in PALETTE_COLORS:
            return token.lower()
        if token in KOREAN_COLOR_MAP:
            return KOREAN_COLOR_MAP[token]
        mapped = infer_color(token, "")
        if mapped:
            return mapped

    return infer_color(text, "")


def normalize_filter_color(
    raw: str,
    *,
    name: str = "",
    description: str = "",
) -> str:
    """지정 팔레트 명칭으로 통일. CSV 오기 시 상품명 대표색 우선."""
    name_color = infer_primary_color_from_name(name)
    mapped = _map_raw_color_to_palette(raw)
    if mapped and name_color and mapped != name_color:
        return name_color
    if mapped:
        return mapped
    if name_color:
        return name_color
    return infer_color(name, description)


def parse_mood_code_number(row: dict | None) -> str:
    """CSV mood_code_number / moodcode_no."""
    if not row:
        return ""
    for key in ("mood_code_number", "moodcode_no", "mood_code_no"):
        value = (row.get(key) or "").strip().upper()
        if value:
            return value[:32]
    return ""


def infer_style(product_id: int, slug: str) -> str:
    idx = stable_hash(f"{product_id}:{slug}") % len(SEASON_STYLES)
    return SEASON_STYLES[idx]


def infer_discount(price: int, slug: str) -> int | None:
    """약 30% 상품에 5~30% 할인가."""
    bucket = stable_hash(slug) % 100
    if bucket >= 30 or price < 10000:
        return None
    rate = DISCOUNT_RATES[stable_hash(f"disc:{slug}") % len(DISCOUNT_RATES)]
    discounted = int(price * (100 - rate) / 100)
    return discounted if 0 < discounted < price else None


def infer_badges(slug: str, price: int, category_rank: int) -> dict[str, bool]:
    h = stable_hash(slug)
    return {
        "is_popular": h % 10 == 0 or category_rank <= 3,
        "is_new": h % 7 == 0,
        "is_best": category_rank <= 2 and price >= 50000,
    }


def parse_optional_int(raw: Any) -> int | None:
    if raw is None or raw == "":
        return None
    try:
        return int(float(str(raw).replace(",", "")))
    except (TypeError, ValueError):
        return None


def parse_optional_bool(raw: Any) -> bool | None:
    if raw is None or raw == "":
        return None
    text = str(raw).strip().lower()
    if text in {"1", "true", "yes", "y", "사용", "o"}:
        return True
    if text in {"0", "false", "no", "n", "미사용", "x"}:
        return False
    return None


def enrich_row_fields(
    *,
    product_id: int,
    slug: str,
    name: str,
    description: str,
    price: int,
    parent_slug: str,
    category_rank: int,
    csv_row: dict | None = None,
    existing: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """CSV optional columns 우선, existing(이미 DB에 있는 값) 다음, 없으면 추론."""
    row = csv_row or {}
    prev = existing or {}

    filter_space = (row.get("filter_space") or prev.get("filter_space") or "").strip()
    if not filter_space:
        filter_space = _default_space(parent_slug)

    csv_color = normalize_filter_color(
        row.get("filter_color") or "",
        name=name,
        description=description,
    )
    # CSV 값이 있어도 상품명과 충돌하면 normalize 결과(상품명 우선) 사용
    filter_color = csv_color or str(prev.get("filter_color") or "").strip() or infer_color(name, description)

    csv_style = normalize_filter_style(row.get("filter_style") or row.get("mood_code") or "")
    if csv_style:
        filter_style = csv_style
    elif normalize_filter_style(str(prev.get("filter_style") or "")):
        filter_style = str(prev["filter_style"])
    elif filter_color:
        filter_style = infer_style_from_color(filter_color)
        if not filter_style:
            filter_style = infer_style(product_id, slug)
    else:
        filter_style = infer_style(product_id, slug)

    mood_code_number = parse_mood_code_number(row) or str(prev.get("mood_code_number") or "").strip().upper()

    discount_price = parse_optional_int(row.get("discount_price"))
    if discount_price is None:
        rate = parse_optional_int(row.get("discount_rate"))
        if rate and 0 < rate < 100:
            discount_price = int(price * (100 - rate) / 100)
        elif prev.get("discount_price") is not None:
            discount_price = prev.get("discount_price")
        else:
            discount_price = infer_discount(price, slug)

    badges = infer_badges(slug, price, category_rank)
    for key in ("is_popular", "is_new", "is_best"):
        parsed = parse_optional_bool(row.get(key))
        if parsed is not None:
            badges[key] = parsed
        elif key in prev and prev[key] is not None:
            badges[key] = bool(prev[key])

    brand = (row.get("brand") or prev.get("brand") or "").strip()
    if brand.upper() == "IKEA":
        brand = "IKEA"

    return {
        "filter_space": filter_space,
        "filter_style": filter_style,
        "filter_color": filter_color,
        "mood_code_number": mood_code_number or None,
        "discount_price": discount_price,
        "brand": brand or None,
        **badges,
    }


def _default_space(parent_slug: str) -> str:
    mapping = {
        "sofa": "living",
        "light": "living",
        "diffuser": "living",
        "side-table": "living",
        "table": "kitchen",
        "bed": "bedroom",
        "balcony": "balcony",
    }
    return mapping.get(parent_slug, "living")
