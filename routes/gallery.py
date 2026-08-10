"""공간·무드 인테리어 갤러리 (선영 팀 작업 통합)."""

from __future__ import annotations

from flask import Blueprint, abort, render_template, request

from services.gallery_service import (
    CATEGORY_TO_MOOD_KEY,
    GALLERY_MOODS,
    MOOD_SLUG_TO_CATEGORY,
    SPACE_META,
    SPACE_META_EN,
    build_mood_detail_meta,
    build_mood_main_items,
    get_mood_detail,
    get_mood_gallery_sections,
    get_scene_by_code,
    save_hotspot_position,
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

@gallery_bp.route("/scene/<scene_code>")
def scene_detail(scene_code: str):
    """갤러리 장면 상세 페이지."""
    scene = get_scene_by_code(scene_code)

    if scene is None:
        abort(404)

    return render_template(
        "gallery/scene_detail.html",
        scene=scene,
    )

@gallery_bp.route("/scene/<scene_code>/hotspot", methods=["POST"])
def save_scene_hotspot(scene_code: str):
    """수동으로 수정한 상품 핫스팟 좌표 저장."""

    data = request.get_json(silent=True) or {}

    product_code = (data.get("product_code") or "").strip()

    try:
        x = float(data.get("x"))
        y = float(data.get("y"))
    except (TypeError, ValueError):
        return {"ok": False, "message": "잘못된 좌표입니다."}, 400

    if not product_code:
        return {"ok": False, "message": "상품 코드가 없습니다."}, 400

    saved = save_hotspot_position(
        scene_code=scene_code,
        product_code=product_code,
        x=x,
        y=y,
    )

    if not saved:
        return {
            "ok": False,
            "message": "핫스팟 CSV 저장에 실패했습니다.",
        }, 500

    return {
        "ok": True,
        "scene_code": scene_code,
        "product_code": product_code,
        "x": x,
        "y": y,
    }