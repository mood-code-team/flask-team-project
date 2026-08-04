"""사이드 메뉴 — DB 카테고리에서 로드."""

from __future__ import annotations

from dataclasses import dataclass

from models import Category


@dataclass(frozen=True)
class SideMenuSubItem:
    name: str
    query: str = ""
    category_slug: str = ""


@dataclass(frozen=True)
class SideMenuCategory:
    name: str
    subitems: tuple[SideMenuSubItem, ...]


# 사이드 메뉴에 노출할 대분류 slug (순서 고정)
SIDE_MENU_ROOT_SLUGS: tuple[str, ...] = (
    "light",
    "sofa",
    "side-table",
    "diffuser",
    "table",
    "bed",
    "balcony",
)

# 대분류별 '모두' 라벨
SHOW_ALL_LABEL: dict[str, bool] = {
    "light": True,
    "sofa": True,
    "side-table": True,
    "diffuser": True,
    "table": True,
    "bed": True,
    "balcony": True,
}


def get_side_menu_categories() -> tuple[SideMenuCategory, ...]:
    """DB categories → 사이드 메뉴 구조."""
    roots = (
        Category.query.filter(
            Category.slug.in_(SIDE_MENU_ROOT_SLUGS),
            Category.is_active.is_(True),
        ).all()
    )
    by_slug = {cat.slug: cat for cat in roots}
    ordered_roots = [by_slug[slug] for slug in SIDE_MENU_ROOT_SLUGS if slug in by_slug]

    menu: list[SideMenuCategory] = []
    for root in ordered_roots:
        label = root.name_en or root.name
        subitems: list[SideMenuSubItem] = []

        if SHOW_ALL_LABEL.get(root.slug, True):
            subitems.append(SideMenuSubItem("모두", category_slug=root.slug))

        children = (
            Category.query.filter_by(parent_id=root.id, is_active=True)
            .order_by(Category.sort_order, Category.id)
            .all()
        )
        for child in children:
            subitems.append(SideMenuSubItem(child.name, category_slug=child.slug))

        menu.append(SideMenuCategory(name=label, subitems=tuple(subitems)))

    return tuple(menu)
