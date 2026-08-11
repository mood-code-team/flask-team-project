"""공간·무드 인테리어 갤러리 (선영 팀 작업 통합)."""

from __future__ import annotations

from flask import Blueprint, abort, render_template, request

from services.gallery_service import (
    CATEGORY_TO_MOOD_KEY,
    GALLERY_MOODS,
    MOOD_SLUG_TO_CATEGORY,
    SEASON_TO_MOOD_KEY,
    SPACE_META,
    SPACE_META_EN,
    build_mood_detail_meta,
    build_mood_main_items,
    build_space_detail_meta,
    build_space_main_items,
    get_mood_detail,
    get_mood_gallery_sections,
    get_space_products,
)

gallery_bp = Blueprint("gallery", __name__)


def _gallery_context(**kwargs):
    """갤러리 템플릿 공통 변수."""
    kwargs.setdefault("gallery_moods", GALLERY_MOODS)
    return kwargs


def _render_mood_detail(category: str, *, mood_key: str | None = None):
    key = mood_key or CATEGORY_TO_MOOD_KEY.get(category, "bloom")
    sections = get_mood_gallery_sections(category)
    return render_template(
        "gallery/gallery_detail.html",
        **_gallery_context(
            gallery_sections=sections,
            meta=build_mood_detail_meta(category),
            mood_key=key,
            active_mood=key,
            mood_detail=get_mood_detail(key),
        ),
    )


@gallery_bp.route("/spaces")
def space_main():
    """공간별 갤러리 — 거실·침실·다이닝·발코니."""
    return render_template(
        "gallery/card_grid.html",
        **_gallery_context(
            gallery_items=build_space_main_items(),
            page_title="공간별 갤러리",
            page_subtitle="원하시는 공간을 선택해 보세요",
            gallery_mode="space",
        ),
    )


@gallery_bp.route("/space/<space_name>/<season>")
def space_gallery(space_name: str, season: str):
    """공간 + 계절 조합 상세 갤러리."""
    if space_name not in SPACE_META:
        abort(404)
    if season not in SEASON_TO_MOOD_KEY:
        abort(404)

    mood_key = SEASON_TO_MOOD_KEY[season]
    products = get_space_products(space_name, season)[:4]

    return render_template(
        "gallery/gallery_detail.html",
        **_gallery_context(
            gallery_sections=[
                {
                    "space": space_name,
                    "label": SPACE_META[space_name],
                    "label_en": SPACE_META_EN[space_name],
                    "scenes": products,
                }
            ],
            meta=build_space_detail_meta(season),
            mood_key=mood_key,
            active_mood=mood_key,
            mood_detail=get_mood_detail(mood_key),
        ),
    )


@gallery_bp.route("/gallery/<mood_slug>")
def mood_gallery_detail(mood_slug: str):
    """BLOOM · CLEAR · CALM · CHIC 상세."""
    category = MOOD_SLUG_TO_CATEGORY.get(mood_slug.lower())
    if not category:
        abort(404)
    return _render_mood_detail(category, mood_key=mood_slug.lower())


@gallery_bp.route("/gallery")
def mood_gallery():
    """무드 선택 — 4카드 후 BLOOM/CLEAR/CALM/CHIC 상세로 이동."""
    category = (request.args.get("category") or "").strip().lower()
    if category in CATEGORY_TO_MOOD_KEY:
        return _render_mood_detail(category)

    return render_template(
        "gallery/card_grid.html",
        **_gallery_context(
            gallery_items=build_mood_main_items(),
            page_title="MOOD GALLERY",
            page_subtitle="원하시는 무드를 선택해 보세요",
            gallery_mode="mood",
        ),
    )
