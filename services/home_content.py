"""메인 페이지 콘텐츠."""

from __future__ import annotations

# Unsplash 4K 이미지 파라미터
_IMG_4K = "w=3840&q=92&auto=format&fit=crop"
_IMG_2K = "w=1920&q=90&auto=format&fit=crop"


def _unsplash(photo_id: str) -> dict[str, str]:
    """Unsplash 4K / 2K URL 생성."""
    base = f"https://images.unsplash.com/{photo_id}"
    return {
        "image": f"{base}?{_IMG_4K}",
        "image_2k": f"{base}?{_IMG_2K}",
    }


# 히어로 — 카테고리 광고 (3·4번 톤: 따뜻한 중성 베드룸 / 1·2번도 같은 계열)
HERO_SLIDES = [
    {
        "image": "images/hero/lighting.jpg",
        "image_2k": "images/hero/lighting.jpg",
        "title": "Lighting",
        "headline": "작은 거실, 충분한 빛.",
        "tagline": "은은한 조명으로 거실을 채우세요",
        "concept": "SOFT LIGHT",
        "category_slug": "light",
    },
    {
        "image": "images/hero/sofa.jpg",
        "image_2k": "images/hero/sofa.jpg",
        "title": "Sofa",
        "headline": "혼자지만, 충분히.",
        "tagline": "컴팩트 소파 · 아늑한 라운지",
        "concept": "SOLO LOUNGE",
        "category_slug": "sofa",
    },
    {
        "image": "images/hero/side-table.jpg",
        "image_2k": "images/hero/side-table.jpg",
        "title": "Side Table",
        "headline": "손 닿는 곳, 딱 맞게.",
        "tagline": "좁은 공간을 위한 사이드 테이블",
        "concept": "JUST FIT",
        "category_slug": "side-table",
    },
    {
        "image": "images/hero/diffuser.jpg",
        "image_2k": "images/hero/diffuser.jpg",
        "title": "Diffuser",
        "headline": "은은한 향, 작은 무드.",
        "tagline": "좁은 공간도 OK",
        "concept": "SMALL MOOD",
        "category_slug": "diffuser",
    },
]

def _format_temperature(celsius: float) -> dict[str, str | float | int]:
    """온도 → 카드/상세용 표시값."""
    rounded = round(celsius, 1)
    integer = int(rounded)
    decimal = int(round((rounded - integer) * 10))
    if decimal == 10:
        integer += 1
        decimal = 0

    low = round(celsius - 1.2, 1)
    high = round(celsius + 1.2, 1)
    return {
        "temp_celsius": rounded,
        "temp_integer": integer,
        "temp_decimal": decimal,
        "temperature": f"{rounded:.1f}°C",
        "temp_range": f"{low:.1f}–{high:.1f}°C",
    }


def _season_room(**kwargs: int | str | float) -> dict:
    """시즌 데이터 + 온도 표시값 자동 추가."""
    celsius = float(kwargs["temp_celsius"])
    return {**kwargs, **_format_temperature(celsius)}


SEASON_ROOMS = [
    _season_room(
        id="spring",
        name="Spring",
        name_en="FRESH BLOOM",
        temp_celsius=18.4,
        temp_feel="Refreshing",
        concept="밝고 가벼운 거실",
        description="파스텔·라이트 우드톤",
        image="https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?w=800&q=80",
        hero_image="https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?w=1920&q=85",
        accent="#7cb87c",
        intro="화사한 햇살과 가벼운 소재로 공간에 리듬을 더합니다.",
        highlights=("파스텔 & 라이트 우드", "자연광 커튼", "그린 포인트"),
        palette=(
            ("#E8F5E9", "Mist Green"),
            ("#FFF8E1", "Soft Cream"),
            ("#BCAAA4", "Light Wood"),
        ),
        tips=(
            "베이지·민트 패브릭 레이어드로 공간을 가볍게.",
            "테이블·플로어 조명을 함께 쓰면 저녁 무드 유지.",
        ),
        category_slugs=("light", "side-table"),
    ),
    _season_room(
        id="summer",
        name="Summer",
        name_en="OPEN AIR",
        temp_celsius=28.2,
        temp_feel="Cool & Light",
        concept="여백 있는 서머 리빙",
        description="린넨·화이트 베이스",
        image="https://images.unsplash.com/photo-1600607687920-4e2a09cf159d?w=800&q=80",
        hero_image="https://images.unsplash.com/photo-1600607687920-4e2a09cf159d?w=1920&q=85",
        accent="#5bb5d5",
        intro="통풍과 라이트 톤으로 시원한 실내를 연출합니다.",
        highlights=("린넨·코튼", "화이트 & 스카이", "개방형 레이아웃"),
        palette=(
            ("#FFFFFF", "Pure White"),
            ("#E3F2FD", "Sky Blue"),
            ("#CFD8DC", "Cool Gray"),
        ),
        tips=(
            "큰 가구는 줄이고 바닥 노출 면적을 넓히세요.",
            "라탄·원목 사이드로 가벼운 포인트.",
        ),
        category_slugs=("sofa", "light", "side-table"),
    ),
    _season_room(
        id="autumn",
        name="Fall",
        name_en="WARM LAYER",
        temp_celsius=14.6,
        temp_feel="Cozy",
        concept="따뜻한 톤 · 아늑한 거실",
        description="테라코타·브라운",
        image="https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=800&q=80",
        hero_image="https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=1920&q=85",
        accent="#c4843e",
        intro="따뜻한 컬러 레이어로 거실의 온기를 완성합니다.",
        highlights=("테라코타 & 브라운", "간접 조명", "벨벳·울"),
        palette=(
            ("#D84315", "Terracotta"),
            ("#5D4037", "Warm Brown"),
            ("#FFCC80", "Amber Glow"),
        ),
        tips=(
            "카멜 쿠션으로 계절감을 더하세요.",
            "디퓨저·조명으로 깊이 있는 무드.",
        ),
        category_slugs=("sofa", "light", "diffuser"),
    ),
    _season_room(
        id="winter",
        name="Winter",
        name_en="QUIET WARMTH",
        temp_celsius=3.2,
        temp_feel="Snug",
        concept="딥 톤 · 겨울밤 라운지",
        description="니트·앰비언트 라이트",
        image="https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?w=800&q=80",
        hero_image="https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?w=1920&q=85",
        accent="#6b8cce",
        intro="딥 톤과 소프트 라이트로 아늑한 겨울밤을 만듭니다.",
        highlights=("딥 네이비 & 차콜", "니트·울", "앰비언트 조명"),
        palette=(
            ("#37474F", "Deep Charcoal"),
            ("#1A237E", "Midnight Blue"),
            ("#FFAB91", "Warm Blush"),
        ),
        tips=(
            "니트 러그·쿠션으로 체감 온도 UP.",
            "캔들·디퓨저와 낮은 조도로 무드 완성.",
        ),
        category_slugs=("sofa", "diffuser", "light"),
    ),
]

SEASON_BY_ID: dict[str, dict] = {room["id"]: room for room in SEASON_ROOMS}


def get_season(season_id: str) -> dict | None:
    """시즌 ID로 상세 데이터 조회."""
    return SEASON_BY_ID.get(season_id)
