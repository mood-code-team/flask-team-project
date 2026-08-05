"""
import 후 상품 메타데이터 보강 — 할인·필터·뱃지.

사용:
  python scripts/enrich_products.py
  python scripts/enrich_products.py --dry-run
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import create_app  # noqa: E402
from extensions import db
from models import Category, Product
from scripts.catalog_data import CATALOG
from scripts.product_enrichment import enrich_row_fields

# category_id → parent slug
_parent_slug_cache: dict[int, str] = {}


def _build_parent_slug_map() -> dict[int, str]:
    if _parent_slug_cache:
        return _parent_slug_cache

    slug_to_parent: dict[str, str] = {}
    for group in CATALOG:
        parent = group["slug"]
        slug_to_parent[parent] = parent
        for child in group.get("children", []):
            slug_to_parent[child["slug"]] = parent

    for cat in Category.query.all():
        _parent_slug_cache[cat.id] = slug_to_parent.get(cat.slug, cat.slug)

    return _parent_slug_cache


def enrich_all(*, dry_run: bool = False) -> dict[str, int]:
    parent_map = _build_parent_slug_map()
    stats = {"updated": 0, "skipped": 0}

    # 카테고리별 가격 순 rank (best 뱃지용)
    by_category: dict[int, list[Product]] = {}
    for product in Product.query.filter_by(is_active=True).all():
        by_category.setdefault(product.category_id, []).append(product)

    category_rank: dict[int, int] = {}
    for cat_id, products in by_category.items():
        sorted_products = sorted(products, key=lambda p: p.price, reverse=True)
        for rank, product in enumerate(sorted_products, start=1):
            category_rank[product.id] = rank

    for product in Product.query.all():
        parent_slug = parent_map.get(product.category_id, "living")
        rank = category_rank.get(product.id, 99)

        fields = enrich_row_fields(
            product_id=product.id,
            slug=product.slug,
            name=product.name,
            description=product.description or "",
            price=product.price,
            parent_slug=parent_slug,
            category_rank=rank,
        )

        changed = False
        for key, value in fields.items():
            if key == "brand" and value is None:
                continue
            if getattr(product, key) != value:
                if not dry_run:
                    setattr(product, key, value)
                changed = True

        if changed:
            stats["updated"] += 1
        else:
            stats["skipped"] += 1

    if not dry_run:
        db.session.commit()

    return stats


def main() -> None:
    parser = argparse.ArgumentParser(description="Enrich product metadata for realistic shop UI")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    app = create_app()
    with app.app_context():
        stats = enrich_all(dry_run=args.dry_run)

    mode = "DRY-RUN" if args.dry_run else "ENRICH"
    print(f"[{mode}] products updated: {stats['updated']}, unchanged: {stats['skipped']}")


if __name__ == "__main__":
    main()
