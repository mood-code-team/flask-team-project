"""카테고리 상품 목록."""

from flask import Blueprint, abort, render_template, request

from services.category_service import list_category_products
from services.search_filters import (
    get_active_filter_tags,
    get_filter_groups,
    parse_filters,
)

category_bp = Blueprint("category", __name__)


@category_bp.route("/category/<slug>")
def listing(slug: str):
    """Lighting·Sofa·Side Table·Diffuser 등 카테고리 상품 목록."""
    filters = parse_filters(request.args)
    try:
        page = int(request.args.get("page", 1))
    except ValueError:
        page = 1

    result = list_category_products(slug, filters=filters, page=page)
    if result is None:
        abort(404)

    return render_template(
        "category/list.html",
        result=result,
        filter_groups=get_filter_groups(),
        active_filters=filters,
        active_filter_tags=get_active_filter_tags(filters),
    )
