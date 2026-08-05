"""
상품 데이터 보강 — CSV/DB import 후 실제 쇼핑몰처럼 메타데이터 추론.

색상·스타일 키워드, 할인율, 뱃지(is_popular/new/best) 규칙.
"""

from __future__ import annotations

import hashlib
import re
from typing import Any

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

STYLES = ("spring", "summer", "fall", "winter")

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
) -> dict[str, Any]:
    """CSV optional columns 우선, 없으면 추론."""
    row = csv_row or {}

    filter_space = (row.get("filter_space") or "").strip() or _default_space(parent_slug)
    filter_style = (row.get("filter_style") or row.get("mood_code") or "").strip().lower()
    filter_color = (row.get("filter_color") or "").strip().lower()

    if filter_style not in STYLES:
        filter_style = infer_style(product_id, slug)
    if not filter_color:
        filter_color = infer_color(name, description)

    discount_price = parse_optional_int(row.get("discount_price"))
    if discount_price is None:
        rate = parse_optional_int(row.get("discount_rate"))
        if rate and 0 < rate < 100:
            discount_price = int(price * (100 - rate) / 100)
        else:
            discount_price = infer_discount(price, slug)

    badges = infer_badges(slug, price, category_rank)
    for key in ("is_popular", "is_new", "is_best"):
        parsed = parse_optional_bool(row.get(key))
        if parsed is not None:
            badges[key] = parsed

    brand = (row.get("brand") or "").strip()
    if brand.upper() == "IKEA":
        brand = "IKEA"

    return {
        "filter_space": filter_space,
        "filter_style": filter_style,
        "filter_color": filter_color,
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
