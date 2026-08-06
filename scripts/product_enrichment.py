"""
상품 데이터 보강 — CSV/DB import 후 실제 쇼핑몰처럼 메타데이터 추론.

색상·스타일 키워드, 할인율, 뱃지(is_popular/new/best) 규칙.
2차 육안 검수 CSV 값은 import 시 우선 반영되며, enrich_products는 빈 값만 채움.
"""

from __future__ import annotations

import hashlib
import re
from typing import Any

from services.search_filters import infer_style_from_color

# 지정 색상 팔레트 (search_filters.py 와 동일)
PALETTE_COLORS = frozenset({
    "white", "beige", "gray", "wood", "black", "pink", "yellow", "green", "blue",
})

STYLES = ("spring", "summer", "fall", "winter")

# 한/영 색상 키워드 → filter_color
COLOR_KEYWORDS: list[tuple[str, str]] = [
    ("화이트", "white"),
    ("white", "white"),
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
    ("yellow", "yellow"),
    ("노란", "yellow"),
    ("그린", "green"),
    ("green", "green"),
    ("초록", "green"),
    ("블루", "blue"),
    ("blue", "blue"),
    ("파란", "blue"),
    ("네이비", "blue"),
]

# 할인율 후보 (%)
DISCOUNT_RATES = (5, 10, 15, 20, 25, 30)


def stable_hash(text: str) -> int:
    return int(hashlib.md5(text.encode("utf-8")).hexdigest(), 16)


def infer_color(name: str, description: str = "") -> str:
    text = f"{name} {description}".lower()
    for keyword, color in COLOR_KEYWORDS:
        if keyword.lower() in text:
            return color
    return ""


def normalize_filter_color(
    raw: str,
    *,
    name: str = "",
    description: str = "",
) -> str:
    """지정 팔레트 명칭으로 통일. 없으면 키워드 추론."""
    value = (raw or "").strip().lower()
    if value in PALETTE_COLORS:
        return value
    if value:
        mapped = infer_color(value, "")
        if mapped:
            return mapped
    return infer_color(name, description)


def normalize_filter_style(raw: str) -> str:
    value = (raw or "").strip().lower()
    return value if value in STYLES else ""


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
    idx = stable_hash(f"{product_id}:{slug}") % len(STYLES)
    return STYLES[idx]


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
    if row.get("filter_color"):
        filter_color = csv_color
    elif prev.get("filter_color"):
        filter_color = str(prev["filter_color"])
    else:
        filter_color = csv_color or infer_color(name, description)

    csv_style = normalize_filter_style(row.get("filter_style") or row.get("mood_code") or "")
    if csv_style:
        filter_style = csv_style
    elif normalize_filter_style(str(prev.get("filter_style") or "")):
        filter_style = str(prev["filter_style"])
    elif filter_color:
        filter_style = infer_style_from_color(filter_color)
        if not filter_style and filter_color != "white":
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
