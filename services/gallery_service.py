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

SEASON_META: dict[str, dict[str, str]] = {
    "spring": {"title_ko": "봄", "subtitle": "따스한 햇살과 생기 넘치는 봄의 공간"},
    "summer": {"title_ko": "여름", "subtitle": "청량하고 시원한 여름의 공간"},
    "fall": {"title_ko": "가을", "subtitle": "깊이감 있고 아늑한 가을의 공간"},
    "winter": {"title_ko": "겨울", "subtitle": "모던하고 포근한 겨울의 공간"},
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
    "fresh": "화사한 햇살과 가벼운 소재로 공간에 리듬을 더합니다.",
    "vibrant": "군더더기 없는 투명함과 정돈된 레이아웃을 선사합니다.",
    "cozy": "깊은 안정감을 주는 차분한 톤과 자연의 온기를 담았습니다.",
    "chic_key": "세련된 감각과 모던한 디테일이 돋보이는 스타일입니다.",
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
        "subtitle": "화사한 햇살과 가벼운 소재로 공간에 리듬을 더합니다.",
        "highlights": [
            ("파스텔 & 라이트 우드", "베이지·민트 패브릭 레이어드로 공간을 가볍게."),
            ("자연광 커튼", "테이블·플로어 조명을 함께 쓰면 저녁 무드 유지."),
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
        "subtitle": "시원한 청량감과 투명한 유리 소재로 공간을 시원하게 채웁니다.",
        "highlights": [
            ("쿨 화이트 & 씨글라스", "블루와 아쿠아 톤으로 시원하고 깨끗한 무드 연출."),
            ("시트러스 포인트", "싱그러운 노란색 소품으로 활기찬 여름 분위기 완성."),
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
        "subtitle": "깊이 있는 우드와 따뜻한 오트밀 컬러로 아늑함을 선사합니다.",
        "highlights": [
            ("오트밀 & 올리브", "차분한 자연 톤으로 마음이 편안해지는 공간 밸런스."),
            ("러스틱 텍스처", "월넛과 러스트 컬러 포인트로 깊이 있는 감성 유지."),
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
        "subtitle": "모던하고 시크한 모노톤에 은은한 플럼빛으로 도회적인 매력을 더합니다.",
        "highlights": [
            ("스노 화이트 & 차콜", "대비가 선명한 모던 모노톤으로 세련된 도시적 감각."),
            ("아이스 블루 & 플럼", "차가운 듯 고요한 포인트 컬러로 무드 극대화."),
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


def get_mood_products(category: str, *, limit: int = 16) -> list[dict]:
    """무드 상세 — 4공간(living/bedroom/dining/balcony) × 계절 4장 = 16장 그리드."""
    matched = [
        item
        for item in get_all_products()
        if item["category"] == category
    ]
    space_order = {"living": 0, "bedroom": 1, "dining": 2, "balcony": 3}
    matched.sort(
        key=lambda item: (space_order.get(item["space"], 9), item.get("scene_code", ""))
    )
    return matched[:limit]


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
