"""메인·시즌 페이지 라우트."""

from flask import Blueprint, abort, render_template

from services.home_content import HERO_SLIDES, SEASON_ROOMS, get_season
from services.season_service import get_season_products

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    """메인 페이지 — 히어로 슬라이더 + 시즌별 방 컨셉."""
    return render_template(
        "index.html",
        hero_slides=HERO_SLIDES,
        season_rooms=SEASON_ROOMS,
    )


@main_bp.route("/season/<season_id>")
def season_detail(season_id: str):
    """시즌별 컨셉 상세 페이지."""
    season = get_season(season_id)
    if season is None:
        abort(404)

    products = get_season_products(season["category_slugs"], season_id=season_id)
    return render_template(
        "season/detail.html",
        season=season,
        products=products,
        season_rooms=SEASON_ROOMS,
    )


@main_bp.route("/space")
def space():
    """공간 상세페이지."""
    return render_template("space/space_detail.html")
