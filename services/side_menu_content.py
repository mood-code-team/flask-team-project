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
            SideMenuSubItem("3인 소파", category_slug="sofa-3"),
            SideMenuSubItem("암체어", category_slug="armchair"),
            SideMenuSubItem("안락의자", category_slug="lounge-chair"),
            SideMenuSubItem("기타", category_slug="sofa-other"),
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
            SideMenuSubItem("우드디퓨저", query="우드디퓨저"),
            SideMenuSubItem("아로마디퓨저", query="아로마디퓨저"),
            SideMenuSubItem("캔들", query="캔들"),
            SideMenuSubItem("룸스프레이", query="룸스프레이"),
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
            SideMenuSubItem("수납침대", query="수납침대"),
            SideMenuSubItem("데이베드", query="데이베드"),
            SideMenuSubItem("소파베드", query="소파베드"),
            SideMenuSubItem("침대프레임", query="침대프레임"),
        ),
    ),
    SideMenuCategory(
        name="Balcony",
        subitems=(
            SideMenuSubItem("모두", category_slug="balcony"),
            SideMenuSubItem("야외테이블", query="야외테이블"),
            SideMenuSubItem("벤치", query="벤치"),
            SideMenuSubItem("수납선반", query="수납선반"),
            SideMenuSubItem("기타", category_slug="deck-tile"),
        ),
    ),
)
