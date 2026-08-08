"""Verify each color filter excludes obvious mismatches."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app import create_app  # noqa: E402
from extensions import db  # noqa: E402
from models import Product  # noqa: E402
from scripts.product_enrichment import infer_primary_color_from_name  # noqa: E402
from services.search_filters import FILTER_GROUPS, product_matches_filters, ActiveFilters  # noqa: E402

CONFLICT_HINTS = {
    "white": ("옐로", "yellow", "노란", "블루", "blue", "핑크", "pink", "그린", "green"),
    "yellow": ("화이트", "white", "블랙", "black"),
    "black": (),
    "blue": (),
    "green": (),
    "pink": (),
    "beige": (),
    "gray": (),
    "wood": (),
}


def main() -> None:
    app = create_app()
    with app.app_context():
        products = Product.query.filter_by(is_active=True).all()
        print(f"Active products: {len(products)}\n")
        for color in FILTER_GROUPS["color"]["options"]:
            filters = ActiveFilters(color=color)
            matched = [p for p in products if product_matches_filters(p, filters)]
            bad = []
            for product in matched:
                primary = infer_primary_color_from_name(product.name)
                if primary and primary != color:
                    bad.append((product.name[:70], primary))
                    continue
                hints = CONFLICT_HINTS.get(color, ())
                lower = product.name.lower()
                if any(h in lower or h in product.name for h in hints):
                    if not primary or primary == color:
                        continue
                    bad.append((product.name[:70], f"hint conflict ({primary})"))
            label = FILTER_GROUPS["color"]["options"][color]
            print(f"{label} ({color}): {len(matched)} items, mismatches={len(bad)}")
            for name, reason in bad[:5]:
                print(f"  ! {reason}: {name}")


if __name__ == "__main__":
    main()
