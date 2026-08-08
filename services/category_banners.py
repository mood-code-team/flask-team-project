"""카테고리 목록 상단 배너 — 로컬 방 구조(인테리어) 고해상도 이미지."""

from __future__ import annotations

CATEGORY_SLUGS: tuple[str, ...] = (
    "light",
    "sofa",
    "side-table",
    "diffuser",
    "table",
    "bed",
    "balcony",
)

DEFAULT_SLUG = "light"
BANNER_VERSION = "3"  # 이미지 교체 시 증가 → 브라우저 캐시 무효화


def _static_path(slug: str, *, high_res: bool = False) -> str:
    """Flask static filename (images/category/...)."""
    suffix = "" if high_res else "-2k"
    return f"images/category/{slug}{suffix}.jpg"


def get_category_banner_urls(root_slug: str) -> dict[str, str]:
    """카테고리 목록 상단 배너 — 로컬 2K + 4K."""
    slug = root_slug if root_slug in CATEGORY_SLUGS else DEFAULT_SLUG
    return {
        "image_2k": _static_path(slug, high_res=False),
        "image_4k": _static_path(slug, high_res=True),
        "version": BANNER_VERSION,
    }
