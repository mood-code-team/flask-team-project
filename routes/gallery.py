"""공간·무드 인테리어 갤러리 (선영 팀 작업 통합)."""

from __future__ import annotations

from flask import Blueprint, abort, jsonify, render_template, request

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
    get_scene_detail,
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

@gallery_bp.route("/gallery/scene/<scene_code>")
def scene_detail(scene_code: str):
    """인테리어 장면 상세페이지."""
    scene = get_scene_detail(scene_code)

    if scene is None:
        abort(404)

    return render_template(
        "gallery/scene_detail.html",
        scene=scene,
    )


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


@gallery_bp.route("/api/gallery/hotspot", methods=["POST"])
def save_hotspot():
    data = request.get_json(silent=True) or {}

    scene_code = (data.get("scene_code") or "").strip()
    product_code = (data.get("product_code") or "").strip()
    x = data.get("x")
    y = data.get("y")

    if not scene_code or not product_code:
        return jsonify({
            "ok": False,
            "error": "scene_code 또는 product_code가 없습니다."
        }), 400

    try:
        x = float(x)
        y = float(y)
    except (TypeError, ValueError):
        return jsonify({
            "ok": False,
            "error": "x, y 좌표가 올바르지 않습니다."
        }), 400

    if not (0 <= x <= 100 and 0 <= y <= 100):
        return jsonify({
            "ok": False,
            "error": "좌표는 0~100 사이여야 합니다."
        }), 400

    from services.gallery_service import save_manual_hotspot

    saved = save_manual_hotspot(
        scene_code=scene_code,
        product_code=product_code,
        x=x,
        y=y,
    )

    if not saved:
        return jsonify({
            "ok": False,
            "error": "핫스팟 저장에 실패했습니다."
        }), 500

    return jsonify({
        "ok": True,
        "scene_code": scene_code,
        "product_code": product_code,
        "x": x,
        "y": y,
    })
