"""Flask 애플리케이션."""

from __future__ import annotations

import os

from flask import Flask, render_template

from config import config_by_name
from extensions import db, login_manager, migrate


def create_app(config_name: str | None = None) -> Flask:
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "default")

    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    import models  # noqa: F401

    from models import User

    @login_manager.user_loader
    def load_user(user_id: str):
        return db.session.get(User, int(user_id))

    from routes import register_blueprints

    register_blueprints(app)

    with app.app_context():
        from services.benefits_service import ensure_default_coupons
        from services.db_schema import (
            ensure_category_schema,
            ensure_order_benefit_schema,
            ensure_order_schema,
            ensure_product_filter_schema,
            ensure_user_schema,
        )
        from services.help_center_service import ensure_help_center_faqs

        db.create_all()
        ensure_user_schema()
        ensure_category_schema()
        ensure_product_filter_schema()
        ensure_order_schema()
        ensure_order_benefit_schema()
        ensure_default_coupons()
        ensure_help_center_faqs()

    upload_dir = app.config.get("UPLOAD_FOLDER")
    if upload_dir:
        upload_dir.mkdir(parents=True, exist_ok=True)

    @app.errorhandler(404)
    def not_found(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(error):
        return render_template("errors/500.html"), 500

    @app.template_filter("currency")
    def currency_filter(value):
        try:
            return f"{int(value):,}"
        except (TypeError, ValueError):
            return value

    @app.template_filter("category_label")
    def category_label_filter(category):
        if not category:
            return ""
        parent = category.parent
        if parent:
            return parent.name_en or parent.name
        return category.name_en or category.name

    @app.context_processor
    def inject_template_globals():
        from flask_login import current_user

        from services.cart_service import get_cart_count
        from services.channel_talk_service import get_boot_options, is_channel_talk_enabled
        from services.side_menu_service import get_side_menu_categories
        from services.search_filters import build_season_nav, COLOR_SWATCHES
        from services.search_service import RECOMMENDED_KEYWORDS
        from services.wishlist_service import wishlist_count

        return {
            "recommended_keywords": RECOMMENDED_KEYWORDS,
            "side_menu_categories": get_side_menu_categories(),
            "cart_count": get_cart_count(),
            "wishlist_count": wishlist_count(),
            "current_user": current_user,
            "channel_talk_boot": get_boot_options(),
            "channel_talk_enabled": is_channel_talk_enabled(),
            "season_nav": build_season_nav(),
            "color_swatches": COLOR_SWATCHES,
        }

    return app


app = create_app()

if __name__ == "__main__":
    from pathlib import Path

    import sys

    project_dir = Path(__file__).resolve().parent
    if str(project_dir) not in sys.path:
        sys.path.insert(0, str(project_dir))

    from scripts.preflight_server import ensure_server_ready

    ensure_server_ready(project_dir)
    app.run(host="127.0.0.1", port=5000, debug=True)
