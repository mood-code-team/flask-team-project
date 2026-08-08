"""사이드 메뉴 — DB 카테고리에서 로드."""

from __future__ import annotations

from dataclasses import dataclass

from models import Category

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


@dataclass(frozen=True)
class SideMenuCategory:
    name: str
    slug: str


def get_side_menu_categories() -> tuple[SideMenuCategory, ...]:
    """DB categories → 사이드 메뉴 대분류 링크."""
    roots = (
        Category.query.filter(
            Category.slug.in_(SIDE_MENU_ROOT_SLUGS),
            Category.is_active.is_(True),
        ).all()
    )
    by_slug = {cat.slug: cat for cat in roots}
    ordered_roots = [by_slug[slug] for slug in SIDE_MENU_ROOT_SLUGS if slug in by_slug]

    return tuple(
        SideMenuCategory(name=root.name_en or root.name, slug=root.slug)
        for root in ordered_roots
    )
