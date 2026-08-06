"""CSV sub_category → 카탈로그 slug 매핑 (엑셀 DB 기준)."""

from __future__ import annotations

# 발코니: 선반유닛, 수납박스, 수납장, 조립마루, 테이블, 화분
BALCONY_SUBCATEGORY_SLUGS: dict[str, str] = {
    "선반유닛": "shelf-unit",
    "수납박스": "storage-box",
    "수납장": "storage-cabinet",
    "조립마루": "deck-tile",
    "테이블": "outdoor-table",
    "화분": "planter",
}

# 침대: 길이조절침대, 데이베드, 매트리스, 매트리스커버, 소파베드, 수납침대, 침대프레임, 기타
BED_SUBCATEGORY_SLUGS: dict[str, str] = {
    "길이조절침대": "adjustable-bed",
    "데이베드": "daybed",
    "데이베드프레임": "daybed",
    "매트리스": "mattress",
    "매트리스커버": "mattress-cover",
    "소파베드": "sofa-bed",
    "수납침대": "storage-bed",
    "수납침대프레임": "storage-bed",
    "오토만침대": "storage-bed",
    "침대프레임": "bed-frame",
    "침대": "bed-other",
    "기타": "bed-other",
}

# 디퓨저: 미니향초, 유리컵향초, 주머니, 포푸리
DIFFUSER_SUBCATEGORY_SLUGS: dict[str, str] = {
    "미니향초": "mini-candle",
    "유리컵향초": "glass-candle",
    "주머니": "sachet",
    "포푸리": "potpourri",
}


def normalize_balcony_sub_category(row: dict) -> str:
    raw = (row.get("sub_category") or "").strip()
    name = (row.get("product_name") or "").strip()

    if raw in BALCONY_SUBCATEGORY_SLUGS:
        return raw

    if raw == "기타":
        if any(keyword in name for keyword in ("화분", "화분대")):
            return "화분"
        if any(keyword in name for keyword in ("조립마루", "마감재", "데크", "코너마")):
            return "조립마루"
        if any(keyword in name for keyword in ("테이블", "벤치", "스툴", "소파", "의자")):
            return "테이블"
        if "수납박스" in name or "파티션" in name:
            return "수납박스"
        if "수납장" in name or "수납함" in name:
            return "수납장"
        if "선반" in name:
            return "선반유닛"
        return "선반유닛"

    return raw or "선반유닛"


def normalize_bed_sub_category(row: dict) -> str:
    raw = (row.get("sub_category") or "").strip()
    name = (row.get("product_name") or "").strip()

    if raw in BED_SUBCATEGORY_SLUGS:
        mapped = raw
        if mapped == "침대":
            return "기타"
        return mapped if mapped in BED_SUBCATEGORY_SLUGS else raw

    if raw in {"데이베드프레임"}:
        return "데이베드"
    if raw in {"수납침대프레임", "오토만침대"}:
        return "수납침대"

    if "매트리스커버" in raw or "매트리스커버" in name:
        return "매트리스커버"
    if "소파베드" in raw or "소파베드" in name:
        return "소파베드"
    if "데이베드" in raw or "데이베드" in name:
        return "데이베드"
    if "길이조절" in raw or "길이조절" in name:
        return "길이조절침대"
    if "수납" in raw or "수납" in name or "오토만" in name:
        return "수납침대"
    if "매트리스" in name and "침대프레임" not in name and "소파베드" not in name:
        return "매트리스"
    if "침대프레임" in raw or "침대프레임" in name or raw == "침대프레임":
        return "침대프레임"

    return raw or "기타"


def normalize_diffuser_sub_category(row: dict) -> str:
    raw = (row.get("sub_category") or "").strip()
    name = (row.get("product_name") or "").strip()

    if raw in DIFFUSER_SUBCATEGORY_SLUGS:
        return raw

    if "미니향초" in name or "미니양초" in name:
        return "미니향초"
    if "유리컵향초" in name or "향초" in name:
        return "유리컵향초"
    if "주머니" in name:
        return "주머니"
    if "포푸리" in name:
        return "포푸리"

    return raw or "포푸리"
