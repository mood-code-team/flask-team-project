"""
Mood Code 상품 카탈로그 시드 데이터.

Notion 기획 + 사이드 메뉴·필터 UI 기준.
팀원은 이 파일 또는 Admin에서 상품/카테고리를 수정합니다.
"""

from __future__ import annotations

# fmt: off
CATALOG: list[dict] = [
    {
        "name": "Lighting",
        "name_en": "Lighting",
        "slug": "light",
        "icon": "💡",
        "sort_order": 1,
        "description": "Lighting category",
        "children": [
            {"name": "테이블 램프", "slug": "table-lamp"},
            {"name": "플로어 램프", "slug": "floor-lamp"},
            {"name": "펜던트 램프", "slug": "pendant-lamp"},
            {"name": "벽등", "slug": "wall-lamp"},
        ],
        "products": [
            {"name": "LED 스탠드 조명", "slug": "led-stand-light", "category": "table-lamp", "price": 89000, "is_popular": True, "filter_space": "bedroom", "filter_style": "winter", "filter_color": "white", "brand": "Mood Code"},
            {"name": "브라스 테이블 램프", "slug": "brass-table-lamp", "category": "table-lamp", "price": 118000, "is_new": True, "filter_space": "living", "filter_style": "fall", "filter_color": "beige", "brand": "IKEA"},
            {"name": "아크 플로어 램프", "slug": "arc-floor-lamp", "category": "floor-lamp", "price": 245000, "discount_price": 219000, "filter_space": "living", "filter_style": "spring", "filter_color": "black", "brand": "Mood Code"},
            {"name": "미니멀 플로어 스탠드", "slug": "minimal-floor-lamp", "category": "floor-lamp", "price": 189000, "is_best": True, "filter_space": "bedroom", "filter_style": "summer", "filter_color": "white", "brand": "Mood Code"},
            {"name": "펜던트 조명", "slug": "pendant-light", "category": "pendant-lamp", "price": 128000, "is_new": True, "filter_space": "living", "filter_style": "winter", "filter_color": "white", "brand": "Mood Code"},
            {"name": "글래스 펜던트 3구", "slug": "glass-pendant-triple", "category": "pendant-lamp", "price": 198000, "is_popular": True, "filter_space": "kitchen", "filter_style": "fall", "filter_color": "gray", "brand": "Mood Code"},
            {"name": "벽등 인테리어 조명", "slug": "wall-sconce-light", "category": "wall-lamp", "price": 76000, "filter_space": "bedroom", "filter_style": "spring", "filter_color": "wood", "brand": "Mood Code"},
        ],
    },
    {
        "name": "Sofa",
        "name_en": "Sofa",
        "slug": "sofa",
        "icon": "🛋️",
        "sort_order": 2,
        "description": "Sofa category",
        "children": [
            {"name": "2인소파", "slug": "sofa-2", "sort_order": 1},
            {"name": "3인 소파", "slug": "sofa-3", "sort_order": 2},
            {"name": "암체어", "slug": "armchair", "sort_order": 3},
            {"name": "안락의자", "slug": "lounge-chair", "sort_order": 4},
            {"name": "소파 기타", "slug": "sofa-other", "sort_order": 5},
        ],
        "products": [
            {"name": "모던 패브릭 3인 소파", "slug": "modern-fabric-sofa", "category": "sofa-3", "price": 890000, "discount_price": 790000, "is_popular": True, "is_best": True, "has_installation": True, "filter_space": "living", "filter_style": "spring", "filter_color": "beige", "brand": "Mood Code"},
            {"name": "린넨 3인 소파", "slug": "linen-sofa-3", "category": "sofa-3", "price": 720000, "is_new": True, "filter_space": "living", "filter_style": "summer", "filter_color": "beige", "brand": "MUJI"},
            {"name": "패밀리 4인 소파", "slug": "family-sofa-4", "category": "sofa-other", "price": 1120000, "discount_price": 998000, "filter_space": "living", "filter_style": "fall", "filter_color": "gray", "brand": "Mood Code"},
            {"name": "코너형 리클라이너 소파", "slug": "corner-recliner", "category": "lounge-chair", "price": 1350000, "discount_price": 1190000, "is_new": True, "is_best": True, "filter_space": "living", "filter_style": "summer", "filter_color": "gray", "brand": "Mood Code"},
            {"name": "L형 코너소파", "slug": "l-corner-sofa", "category": "sofa-other", "price": 1580000, "is_popular": True, "has_installation": True, "filter_space": "living", "filter_style": "winter", "filter_color": "black", "brand": "Mood Code"},
        ],
    },
    {
        "name": "Side Table",
        "name_en": "Side Table",
        "slug": "side-table",
        "icon": "🪵",
        "sort_order": 3,
        "description": "Side Table category",
        "children": [
            {"name": "사이드 테이블", "slug": "side-table-item"},
            {"name": "나이트스탠드", "slug": "nightstand"},
            {"name": "콘솔", "slug": "console-table"},
        ],
        "products": [
            {"name": "원목 사이드 테이블", "slug": "wood-side-table", "category": "side-table-item", "price": 189000, "discount_price": 169000, "is_new": True, "is_popular": True, "filter_space": "living", "filter_style": "spring", "filter_color": "wood", "brand": "Mood Code"},
            {"name": "마블 협탁", "slug": "marble-side-table", "category": "side-table-item", "price": 245000, "is_best": True, "filter_space": "bedroom", "filter_style": "summer", "filter_color": "white", "brand": "Nordik Living"},
            {"name": "라운드 나이트 스탠드", "slug": "round-night-stand", "category": "nightstand", "price": 156000, "is_new": True, "filter_space": "bedroom", "filter_style": "fall", "filter_color": "beige", "brand": "Mood Code"},
            {"name": "원목 콘솔 테이블", "slug": "wood-console-table", "category": "console-table", "price": 298000, "filter_space": "living", "filter_style": "winter", "filter_color": "wood", "brand": "Mood Code"},
        ],
    },
    {
        "name": "Diffuser",
        "name_en": "Diffuser",
        "slug": "diffuser",
        "icon": "🕯️",
        "sort_order": 4,
        "description": "Diffuser category",
        "children": [
            {"name": "우드디퓨저", "slug": "wood-diffuser"},
            {"name": "아로마디퓨저", "slug": "aroma-diffuser"},
            {"name": "캔들", "slug": "candle"},
            {"name": "룸스프레이", "slug": "room-spray"},
        ],
        "products": [
            {"name": "우드 디퓨저 세트", "slug": "wood-diffuser-set", "category": "wood-diffuser", "price": 68000, "is_popular": True, "is_new": True, "filter_space": "living", "filter_style": "spring", "filter_color": "wood", "brand": "Mood Code"},
            {"name": "스톤 아로마 디퓨저", "slug": "stone-aroma-diffuser", "category": "aroma-diffuser", "price": 92000, "is_best": True, "filter_space": "balcony", "filter_style": "winter", "filter_color": "gray", "brand": "Mood Code"},
            {"name": "리드 캔들 디퓨저", "slug": "reed-candle-diffuser", "category": "candle", "price": 45000, "is_popular": True, "filter_space": "balcony", "filter_style": "fall", "filter_color": "beige", "brand": "Mood Code"},
            {"name": "린넨 룸스프레이", "slug": "linen-room-spray", "category": "room-spray", "price": 32000, "is_new": True, "filter_space": "bedroom", "filter_style": "summer", "filter_color": "white", "brand": "Mood Code"},
        ],
    },
    {
        "name": "Dining Table",
        "name_en": "Dining Table",
        "slug": "table",
        "icon": "🪑",
        "sort_order": 5,
        "description": "Dining Table category",
        "children": [
            {"name": "일반식탁", "slug": "standard-dining"},
            {"name": "원형식탁", "slug": "round-dining"},
            {"name": "아일랜드식탁", "slug": "island-dining"},
        ],
        "products": [
            {"name": "원목 식탁 세트 4인", "slug": "wood-dining-set", "category": "standard-dining", "price": 650000, "is_new": True, "is_popular": True, "filter_space": "kitchen", "filter_style": "summer", "filter_color": "wood", "brand": "Mood Code"},
            {"name": "원형 4인 식탁", "slug": "round-dining-table", "category": "round-dining", "price": 580000, "discount_price": 522000, "filter_space": "kitchen", "filter_style": "spring", "filter_color": "white", "brand": "IKEA"},
            {"name": "아일랜드 식탁 6인", "slug": "island-dining-table", "category": "island-dining", "price": 890000, "is_best": True, "has_installation": True, "filter_space": "kitchen", "filter_style": "fall", "filter_color": "gray", "brand": "Mood Code"},
        ],
    },
    {
        "name": "Bed",
        "name_en": "Bed",
        "slug": "bed",
        "icon": "🛏️",
        "sort_order": 6,
        "description": "Bed category",
        "children": [
            {"name": "수납침대", "slug": "storage-bed"},
            {"name": "데이베드", "slug": "daybed"},
            {"name": "소파베드", "slug": "sofa-bed"},
            {"name": "침대프레임", "slug": "bed-frame"},
        ],
        "products": [
            {"name": "퀸사이즈 침대 프레임", "slug": "queen-bed-frame", "category": "bed-frame", "price": 520000, "discount_price": 468000, "is_best": True, "has_installation": True, "filter_space": "bedroom", "filter_style": "fall", "filter_color": "white", "brand": "Mood Code"},
            {"name": "수납형 퀸 침대", "slug": "storage-queen-bed", "category": "storage-bed", "price": 680000, "is_popular": True, "filter_space": "bedroom", "filter_style": "winter", "filter_color": "beige", "brand": "Mood Code"},
            {"name": "린넨 데이베드", "slug": "linen-daybed", "category": "daybed", "price": 790000, "is_new": True, "filter_space": "living", "filter_style": "summer", "filter_color": "beige", "brand": "Mood Code"},
            {"name": "접이식 소파베드", "slug": "folding-sofa-bed", "category": "sofa-bed", "price": 450000, "filter_space": "living", "filter_style": "spring", "filter_color": "gray", "brand": "Mood Code"},
        ],
    },
    {
        "name": "Balcony",
        "name_en": "Balcony",
        "slug": "balcony",
        "icon": "🌿",
        "sort_order": 7,
        "description": "Balcony category",
        "children": [
            {"name": "야외테이블", "slug": "outdoor-table"},
            {"name": "벤치", "slug": "outdoor-bench"},
            {"name": "수납선반", "slug": "outdoor-shelf"},
            {"name": "기타", "slug": "deck-tile"},
        ],
        "products": [
            {"name": "접이식 야외 테이블", "slug": "folding-outdoor-table", "category": "outdoor-table", "price": 128000, "is_new": True, "filter_space": "balcony", "filter_style": "summer", "filter_color": "wood", "brand": "Balcony Lab"},
            {"name": "우드 발코니 벤치", "slug": "balcony-wood-bench", "category": "outdoor-bench", "price": 156000, "is_popular": True, "filter_space": "balcony", "filter_style": "spring", "filter_color": "wood", "brand": "Mood Code"},
            {"name": "발코니 수납 선반", "slug": "balcony-storage-shelf", "category": "outdoor-shelf", "price": 89000, "filter_space": "balcony", "filter_style": "fall", "filter_color": "white", "brand": "Mood Code"},
            {"name": "데크 조립마루 4장", "slug": "deck-tile-set", "category": "deck-tile", "price": 68000, "is_best": True, "filter_space": "balcony", "filter_style": "summer", "filter_color": "wood", "brand": "Mood Code"},
        ],
    },
]
