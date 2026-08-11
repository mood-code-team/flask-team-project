"""Blueprint 등록."""

from flask import redirect, url_for

from routes.auth import auth_bp
from routes.cart import cart_bp
from routes.category import category_bp
from routes.main import main_bp
from routes.mypage import mypage_bp
from routes.payment import payment_bp
from routes.product import product_bp
from routes.search import search_bp
from routes.support import support_bp


def register_blueprints(app):
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(mypage_bp)
    app.register_blueprint(search_bp)
    app.register_blueprint(category_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(payment_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(support_bp)

    @app.route("/chatbot")
    @app.route("/chatbot/")
    @app.route("/chatbot/<path:path>")
    def chatbot_redirect(path=""):
        return redirect(url_for("support.center"))
