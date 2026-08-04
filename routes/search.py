"""검색 라우트."""

from flask import Blueprint, redirect, render_template, request, url_for

from services.search_service import RECOMMENDED_KEYWORDS, search_products
from services.search_filters import get_active_filter_tags, get_filter_groups, parse_filters

search_bp = Blueprint("search", __name__)


@search_bp.route("/search")
def results():
    """통합 검색 결과 페이지."""
    query = request.args.get("q", "").strip()
    filters = parse_filters(request.args)
    try:
        page = int(request.args.get("page", 1))
    except ValueError:
        page = 1

    if not query:
        return redirect(url_for("main.index"))

    result = search_products(query, filters=filters, page=page)

    return render_template(
        "search/results.html",
        result=result,
        filter_groups=get_filter_groups(),
        active_filters=filters,
        active_filter_tags=get_active_filter_tags(filters),
        recommended_keywords=RECOMMENDED_KEYWORDS,
    )
