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
        "products": [],
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
            {"name": "3인소파", "slug": "sofa-3", "sort_order": 2},
            {"name": "암체어", "slug": "armchair", "sort_order": 3},
            {"name": "안락의자", "slug": "lounge-chair", "sort_order": 4},
            {"name": "소파기타", "slug": "sofa-other", "sort_order": 5},
        ],
        "products": [],
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
        "products": [],
    },
    {
        "name": "Diffuser",
        "name_en": "Diffuser",
        "slug": "diffuser",
        "icon": "🕯️",
        "sort_order": 4,
        "description": "Diffuser category",
        "children": [
            {"name": "미니향초", "slug": "mini-candle", "sort_order": 1},
            {"name": "유리컵향초", "slug": "glass-candle", "sort_order": 2},
            {"name": "주머니", "slug": "sachet", "sort_order": 3},
            {"name": "포푸리", "slug": "potpourri", "sort_order": 4},
        ],
        "products": [],
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
        "products": [],
    },
    {
        "name": "Bed",
        "name_en": "Bed",
        "slug": "bed",
        "icon": "🛏️",
        "sort_order": 6,
        "description": "Bed category",
        "children": [
            {"name": "길이조절침대", "slug": "adjustable-bed", "sort_order": 1},
            {"name": "데이베드", "slug": "daybed", "sort_order": 2},
            {"name": "매트리스", "slug": "mattress", "sort_order": 3},
            {"name": "매트리스커버", "slug": "mattress-cover", "sort_order": 4},
            {"name": "소파베드", "slug": "sofa-bed", "sort_order": 5},
            {"name": "수납침대", "slug": "storage-bed", "sort_order": 6},
            {"name": "기타", "slug": "bed-other", "sort_order": 7},
        ],
        "products": [],
    },
    {
        "name": "Balcony",
        "name_en": "Balcony",
        "slug": "balcony",
        "icon": "🌿",
        "sort_order": 7,
        "description": "Balcony category",
        "children": [
            {"name": "선반유닛", "slug": "shelf-unit", "sort_order": 1},
            {"name": "수납박스", "slug": "storage-box", "sort_order": 2},
            {"name": "수납장", "slug": "storage-cabinet", "sort_order": 3},
            {"name": "조립마루", "slug": "deck-tile", "sort_order": 4},
            {"name": "테이블", "slug": "outdoor-table", "sort_order": 5},
            {"name": "화분", "slug": "planter", "sort_order": 6},
        ],
        "products": [],
    },
]
