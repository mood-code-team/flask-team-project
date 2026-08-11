"""공간·무드 인테리어 갤러리 (선영 팀 CSV + originals 연동)."""

from __future__ import annotations

import csv
import random
from pathlib import Path

from services.product_lookup import resolve_product_link

ROOT = Path(__file__).resolve().parent.parent

SPACE_META: dict[str, str] = {
    "living": "거실",
    "bedroom": "침실",
    "dining": "다이닝",
    "balcony": "발코니",
}

SPACE_ORDER: tuple[str, ...] = ("living", "dining", "bedroom", "balcony")

SPACE_META_EN: dict[str, str] = {
    "living": "LIVING",
    "bedroom": "BEDROOM",
    "dining": "DINING",
    "balcony": "BALCONY",
}

SEASON_META: dict[str, dict[str, str]] = {
    "spring": {"title_ko": "봄", "subtitle": "화사한 햇살, 가벼운 리듬"},
    "summer": {"title_ko": "여름", "subtitle": "청량한 여백, 시원한 공기"},
    "fall": {"title_ko": "가을", "subtitle": "따뜻한 톤, 아늑한 온기"},
    "winter": {"title_ko": "겨울", "subtitle": "모던 모노톤, 세련된 무드"},
}

CATEGORY_TO_SEASON: dict[str, str] = {
    "fresh": "spring",
    "vibrant": "summer",
    "cozy": "fall",
    "chic_key": "winter",
}

MOOD_SLUG_TO_CATEGORY: dict[str, str] = {
    "bloom": "fresh",
    "clear": "vibrant",
    "calm": "cozy",
    "chic": "chic_key",
}

CATEGORY_TO_MOOD_KEY: dict[str, str] = {
    "fresh": "bloom",
    "vibrant": "clear",
    "cozy": "calm",
    "chic_key": "chic",
}

SEASON_TO_MOOD_KEY: dict[str, str] = {
    "spring": "bloom",
    "summer": "clear",
    "fall": "calm",
    "winter": "chic",
}

SEASON_TO_MOOD: dict[str, str] = {
    "spring": "BLOOM",
    "summer": "CLEAR",
    "fall": "CALM",
    "winter": "CHIC",
}

MOOD_SUBTITLES: dict[str, str] = {
    "fresh": "화사한 햇살, 가벼운 리듬",
    "vibrant": "청량한 여백, 시원한 공기",
    "cozy": "따뜻한 톤, 아늑한 온기",
    "chic_key": "모던 모노톤, 세련된 무드",
}

PRIMARY_PRODUCT_FIELDS: tuple[tuple[str, str], ...] = (
    ("sofa_code", "sofa_image_name"),
    ("bed_code", "bed_image_name"),
    ("dining_code", "dining_image_name"),
    ("balcony_code", "balcony_image_name"),
)

PRODUCT_CODE_FIELDS: tuple[tuple[str, str], ...] = (
    *PRIMARY_PRODUCT_FIELDS,
    ("table_code", "table_image_name"),
    ("side_table_code", "side_table_image_name"),
    ("light_code", "light_image_name"),
    ("scent_code", "scent_image_name"),
)

GALLERY_MOODS: list[tuple[str, str]] = [
    ("bloom", "BLOOM"),
    ("clear", "CLEAR"),
    ("calm", "CALM"),
    ("chic", "CHIC"),
]

MOOD_DETAIL: dict[str, dict] = {
    "bloom": {
        "title": "BLOOM",
        "subtitle": "화사한 햇살, 가벼운 리듬",
        "highlights": [
            ("파스텔 & 라이트 우드", "가벼운 톤으로 공간에 리듬을."),
            ("자연광", "낮은 조도로 저녁 무드까지."),
        ],
        "palettes": [
            {"name": "Fresh Ivory", "hex": "#F7F2E8"},
            {"name": "Sage Leaf", "hex": "#A8B8A0"},
            {"name": "Blush Petal", "hex": "#E7B7B2"},
            {"name": "Butter Bloom", "hex": "#E8D58A"},
            {"name": "Light Oak", "hex": "#C9A77B"},
        ],
    },
    "clear": {
        "title": "CLEAR",
        "subtitle": "청량한 여백, 시원한 공기",
        "highlights": [
            ("쿨 화이트", "깨끗하고 시원한 무드."),
            ("시트러스 포인트", "가벼운 활기."),
        ],
        "palettes": [
            {"name": "Cool White", "hex": "#F4F8F7"},
            {"name": "Sea Glass", "hex": "#A8D8D0"},
            {"name": "Sky Blue", "hex": "#82B7D9"},
            {"name": "Deep Aqua", "hex": "#2F7F8F"},
            {"name": "Citrus Yellow", "hex": "#E7D35C"},
        ],
    },
    "calm": {
        "title": "CALM",
        "subtitle": "따뜻한 톤, 아늑한 온기",
        "highlights": [
            ("오트밀 & 올리브", "편안한 공간 밸런스."),
            ("러스틱 텍스처", "깊이 있는 감성."),
        ],
        "palettes": [
            {"name": "Oatmeal", "hex": "#D8C3A5"},
            {"name": "Ochre", "hex": "#C8922F"},
            {"name": "Rust", "hex": "#B65A3A"},
            {"name": "Olive", "hex": "#7A7B47"},
            {"name": "Walnut", "hex": "#6B4A32"},
        ],
    },
    "chic": {
        "title": "CHIC",
        "subtitle": "모던 모노톤, 세련된 무드",
        "highlights": [
            ("스노 화이트 & 차콜", "도시적 세련함."),
            ("아이스 블루 & 플럼", "고요한 포인트."),
        ],
        "palettes": [
            {"name": "Snow White", "hex": "#F3F4F2"},
            {"name": "Ice Blue", "hex": "#B7CFDA"},
            {"name": "Dove Gray", "hex": "#A9ADB2"},
            {"name": "Plum", "hex": "#6F5267"},
            {"name": "Soft Charcoal", "hex": "#34383D"},
        ],
    },
}


def get_mood_detail(mood_key: str) -> dict | None:
    """무드 상세 페이지 카피·팔레트."""
    return MOOD_DETAIL.get(mood_key.lower())


def get_mood_name(category_key: str) -> str:
    names = {
        "fresh": "BLOOM",
        "vibrant": "CLEAR",
        "cozy": "CALM",
        "chic_key": "CHIC",
    }
    return names.get(category_key.lower(), "Interior Style")


def _csv_path(space: str) -> Path:
    return ROOT / "static" / "csv" / f"moodcode_{space}_4seasons_16_final.csv"


def _palette_path() -> Path:
    return (
        ROOT
        / "static"
        / "moodcode_season_color_palette_package"
        / "moodcode_season_color_palette.csv"
    )


def _image_url(space: str, season: str, filename: str) -> str:
    return f"/static/originals/{space}/{season}/{filename}"


def _primary_product_from_row(row: dict) -> tuple[str, str]:
    for code_key, image_key in PRIMARY_PRODUCT_FIELDS:
        code = (row.get(code_key) or "").strip().upper()
        image_name = (row.get(image_key) or "").strip()
        if code.startswith("MC-") and image_name:
            return code, image_name
    return "", ""


def _scene_products_from_row(row: dict) -> list[dict]:
    products: list[dict] = []
    for code_key, image_key in PRODUCT_CODE_FIELDS:
        code = (row.get(code_key) or "").strip().upper()
        image_name = (row.get(image_key) or "").strip()
        if not code.startswith("MC-") or not image_name:
            continue
        link = resolve_product_link(code, image_name)
        if not link:
            continue
        products.append(
            {
                "code": code,
                "image_name": image_name,
                "label": (row.get(code_key.replace("_code", "_name")) or "").strip(),
                **link,
            }
        )
    return products


def _build_gallery_item(
    row: dict,
    *,
    space: str,
    season: str,
    category: str | None = None,
) -> dict:
    image_name = (row.get("original_image_name") or "").strip()
    primary_code, primary_image = _primary_product_from_row(row)
    primary_product = resolve_product_link(primary_code, primary_image)
    scene_products = _scene_products_from_row(row)

    item = {
        "name": row.get("scene_code", ""),
        "scene_code": row.get("scene_code", ""),
        "space": space,
        "season": season,
        "image_url": _image_url(space, season, image_name),
        "primary_product": primary_product,
        "products": scene_products,
    }
    if category:
        item["category"] = category
    if primary_product:
        item["product_url"] = primary_product["url"]
        item["product_name"] = primary_product["name"]
        item["mood_code_number"] = primary_product["mood_code_number"]
    return item


def get_all_products(*, space: str | None = None) -> list[dict]:
    products: list[dict] = []
    spaces = (space,) if space else ("living", "bedroom", "dining", "balcony")
    seasons = ("spring", "summer", "fall", "winter")
    season_to_category = {
        "spring": "fresh",
        "summer": "vibrant",
        "fall": "cozy",
        "winter": "chic_key",
    }

    for space in spaces:
        csv_file = _csv_path(space)
        if not csv_file.is_file():
            continue
        with csv_file.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                season = (row.get("season") or "").strip().lower()
                if season not in seasons:
                    continue
                image_name = (row.get("original_image_name") or "").strip()
                if not image_name:
                    continue
                products.append(
                    _build_gallery_item(
                        row,
                        space=space,
                        season=season,
                        category=season_to_category[season],
                    )
                )
    return products


def get_space_products(space: str, season: str) -> list[dict]:
    products: list[dict] = []
    csv_file = _csv_path(space)
    if not csv_file.is_file():
        return products

    target_season = season.strip().lower()
    with csv_file.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if (row.get("season") or "").strip().lower() != target_season:
                continue
            image_name = (row.get("original_image_name") or "").strip()
            if not image_name:
                continue
            products.append(_build_gallery_item(row, space=space, season=target_season))
    return products


def get_season_palette(season: str) -> list[dict[str, str]]:
    palette: list[dict[str, str]] = []
    palette_file = _palette_path()
    if not palette_file.is_file():
        return palette

    target = season.strip().lower()
    with palette_file.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = sorted(
            [row for row in reader if (row.get("season_en") or "").strip().lower() == target],
            key=lambda item: int(item.get("color_order") or 0),
        )
        for row in rows:
            palette.append(
                {
                    "hex": row.get("hex", ""),
                    "name_en": row.get("color_name_en", ""),
                }
            )
    return palette


def get_mood_gallery_sections(category: str) -> list[dict]:
    """무드 상세 — 거실·침실·다이닝·발코니 공간별 4장(계절 16장 세트)."""
    matched = [
        item
        for item in get_all_products()
        if item["category"] == category
    ]
    sections: list[dict] = []
    for space in SPACE_ORDER:
        space_items = sorted(
            [item for item in matched if item["space"] == space],
            key=lambda item: item.get("scene_code", ""),
        )
        if not space_items:
            continue
        sections.append(
            {
                "space": space,
                "label": SPACE_META[space],
                "label_en": SPACE_META_EN[space],
                "scenes": space_items[:4],
            }
        )
    return sections


def get_mood_products(category: str, *, limit: int = 16) -> list[dict]:
    """무드 상세 — 공간별 4장 × 4공간 (기본 16장)."""
    items: list[dict] = []
    for section in get_mood_gallery_sections(category):
        items.extend(section["scenes"])
    return items[:limit]


def build_space_main_items() -> list[dict]:
    items: list[dict] = []
    for space, label in SPACE_META.items():
        products = get_space_products(space, "spring")
        if not products:
            continue
        product = random.choice(products)
        items.append(
            {
                "name": label,
                "image_url": product["image_url"],
                "link": f"/space/{space}/spring",
            }
        )
    return items


def build_mood_main_items() -> list[dict]:
    products = get_all_products()
    items: list[dict] = []
    for category in ("fresh", "vibrant", "cozy", "chic_key"):
        matched = [item for item in products if item["category"] == category]
        if not matched:
            continue
        product = random.choice(matched)
        items.append(
            {
                "name": get_mood_name(category),
                "mood_slug": CATEGORY_TO_MOOD_KEY[category],
                "image_url": product["image_url"],
                "link": f"/gallery/{CATEGORY_TO_MOOD_KEY[category]}",
            }
        )
    return items


def build_mood_detail_meta(category: str) -> dict:
    season = CATEGORY_TO_SEASON[category]
    palette = get_season_palette(season)
    return {
        "title": get_mood_name(category),
        "subtitle": MOOD_SUBTITLES.get(category, ""),
        "colors": [color["hex"] for color in palette],
        "color_desc": ", ".join(color["name_en"] for color in palette),
    }


def build_space_detail_meta(season: str) -> dict:
    palette = get_season_palette(season)
    return {
        "title": SEASON_TO_MOOD.get(season, "STYLE"),
        "subtitle": SEASON_META.get(season, {}).get("subtitle", ""),
        "colors": [color["hex"] for color in palette],
        "color_desc": ", ".join(color["name_en"] for color in palette),
    }
