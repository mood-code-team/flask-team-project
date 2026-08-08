"""시범용 로컬 이미지 상품(엑박) 삭제."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import create_app
from extensions import db
from models import CartItem, OrderItem, Product, ProductQuestion, Review, WishlistItem


def image_file_missing(image_url: str | None, static_dir: Path) -> bool:
    url = (image_url or "").strip()
    if not url.startswith("/static/") and not url.startswith("static/"):
        return False
    rel = url.removeprefix("/static/").removeprefix("static/")
    return not (static_dir / rel).is_file()


def delete_product_refs(product_ids: list[int]) -> None:
    if not product_ids:
        return
    CartItem.query.filter(CartItem.product_id.in_(product_ids)).delete(synchronize_session=False)
    WishlistItem.query.filter(WishlistItem.product_id.in_(product_ids)).delete(synchronize_session=False)
    Review.query.filter(Review.product_id.in_(product_ids)).delete(synchronize_session=False)
    ProductQuestion.query.filter(ProductQuestion.product_id.in_(product_ids)).delete(synchronize_session=False)
    OrderItem.query.filter(OrderItem.product_id.in_(product_ids)).delete(synchronize_session=False)


def main() -> None:
    app = create_app()
    static_dir = Path(__file__).resolve().parent.parent / "static"

    with app.app_context():
        targets = [
            product
            for product in Product.query.all()
            if image_file_missing(product.image_url, static_dir)
        ]
        if not targets:
            print("No broken-image products found.")
            return

        product_ids = [product.id for product in targets]
        for product in targets:
            print(f"delete id={product.id} slug={product.slug}")

        delete_product_refs(product_ids)
        Product.query.filter(Product.id.in_(product_ids)).delete(synchronize_session=False)
        db.session.commit()
        print(f"Removed {len(targets)} products.")


if __name__ == "__main__":
    main()
