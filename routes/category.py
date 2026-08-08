"""카테고리 상품 목록."""

from flask import Blueprint, abort, redirect, render_template, request, url_for

from services.category_service import (
    get_category_banner_image,
    get_category_by_slug,
    get_category_root,
    list_category_products,
)
from services.search_filters import (
    get_active_filter_tags,
    get_category_filter_groups,
    get_subcategory_options,
    parse_filters,
)

category_bp = Blueprint("category", __name__)

DEFAULT_SHOP_CATEGORY = "light"

CATEGORY_SLUG_ALIASES: dict[str, str] = {
    "lighting": "light",
    "side table": "side-table",
    "dining table": "table",
    "dining-table": "table",
}


def normalize_category_slug(raw_slug: str) -> str:
    slug = (raw_slug or "").strip().lower()
    return CATEGORY_SLUG_ALIASES.get(slug, slug)


@category_bp.route("/shop")
def shop():
    """상품목록 바로가기."""
    return redirect(url_for("category.listing", slug=DEFAULT_SHOP_CATEGORY))


@category_bp.route("/category/<slug>")
def listing(slug: str):
    """Lighting·Sofa·Side Table·Diffuser 등 카테고리 상품 목록."""
    slug = normalize_category_slug(slug)
    category = get_category_by_slug(slug)
    if not category:
        abort(404)

    try:
        page = int(request.args.get("page", 1))
    except ValueError:
        page = 1

    listing_root = get_category_root(category)
    subcategory_options = get_subcategory_options(listing_root)
    filters = parse_filters(request.args, subcategory_options=subcategory_options)
    result = list_category_products(slug, filters=filters, page=page)
    if result is None:
        abort(404)

    return render_template(
        "category/list.html",
        result=result,
        banner_image=get_category_banner_image(result.category),
        filter_groups=get_category_filter_groups(listing_root),
        active_filters=filters,
        active_filter_tags=get_active_filter_tags(
            filters,
            subcategory_options=subcategory_options,
        ),
    )
