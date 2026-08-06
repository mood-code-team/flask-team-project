"""사이드 메뉴 카테고리."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SideMenuSubItem:
    name: str
    query: str = ""
    category_slug: str = ""


@dataclass(frozen=True)
class SideMenuCategory:
    name: str
    subitems: tuple[SideMenuSubItem, ...]


SIDE_MENU_CATEGORIES: tuple[SideMenuCategory, ...] = (
    SideMenuCategory(
        name="Lighting",
        subitems=(
            SideMenuSubItem("모두", category_slug="light"),
            SideMenuSubItem("테이블 램프", query="테이블 램프"),
            SideMenuSubItem("플로어 램프", query="플로어 램프"),
            SideMenuSubItem("펜던트 램프", query="펜던트 램프"),
            SideMenuSubItem("벽등", query="벽등"),
        ),
    ),
    SideMenuCategory(
        name="Sofa",
        subitems=(
            SideMenuSubItem("모두", category_slug="sofa"),
            SideMenuSubItem("2인소파", category_slug="sofa-2"),
            SideMenuSubItem("3인소파", category_slug="sofa-3"),
            SideMenuSubItem("4인소파", category_slug="sofa-4"),
            SideMenuSubItem("리클라이너", category_slug="recliner"),
            SideMenuSubItem("코너소파", category_slug="corner-sofa"),
            SideMenuSubItem("암체어", category_slug="armchair"),
            SideMenuSubItem("안락의자", category_slug="lounge-chair"),
            SideMenuSubItem("소파 기타", category_slug="sofa-other"),
        ),
    ),
    SideMenuCategory(
        name="Side Table",
        subitems=(
            SideMenuSubItem("모두", category_slug="side-table"),
            SideMenuSubItem("사이드 테이블", query="사이드 테이블"),
            SideMenuSubItem("나이트스탠드", query="나이트스탠드"),
            SideMenuSubItem("콘솔", query="콘솔"),
        ),
    ),
    SideMenuCategory(
        name="Diffuser",
        subitems=(
            SideMenuSubItem("모두", category_slug="diffuser"),
            SideMenuSubItem("미니향초", category_slug="mini-candle"),
            SideMenuSubItem("유리컵향초", category_slug="glass-candle"),
            SideMenuSubItem("주머니", category_slug="sachet"),
            SideMenuSubItem("포푸리", category_slug="potpourri"),
        ),
    ),
    SideMenuCategory(
        name="Dining Table",
        subitems=(
            SideMenuSubItem("모두", category_slug="table"),
            SideMenuSubItem("일반식탁", category_slug="standard-dining"),
            SideMenuSubItem("원형식탁", query="원형식탁"),
            SideMenuSubItem("아일랜드식탁", query="아일랜드식탁"),
        ),
    ),
    SideMenuCategory(
        name="Bed",
        subitems=(
            SideMenuSubItem("모두", category_slug="bed"),
            SideMenuSubItem("길이조절침대", category_slug="adjustable-bed"),
            SideMenuSubItem("데이베드", category_slug="daybed"),
            SideMenuSubItem("매트리스", category_slug="mattress"),
            SideMenuSubItem("매트리스커버", category_slug="mattress-cover"),
            SideMenuSubItem("소파베드", category_slug="sofa-bed"),
            SideMenuSubItem("수납침대", category_slug="storage-bed"),
            SideMenuSubItem("침대프레임", category_slug="bed-frame"),
            SideMenuSubItem("침대 기타", category_slug="bed-other"),
        ),
    ),
    SideMenuCategory(
        name="Balcony",
        subitems=(
            SideMenuSubItem("모두", category_slug="balcony"),
            SideMenuSubItem("선반유닛", category_slug="shelf-unit"),
            SideMenuSubItem("수납박스", category_slug="storage-box"),
            SideMenuSubItem("수납장", category_slug="storage-cabinet"),
            SideMenuSubItem("조립마루", category_slug="deck-tile"),
            SideMenuSubItem("테이블", category_slug="outdoor-table"),
            SideMenuSubItem("화분", category_slug="planter"),
        ),
    ),
)
