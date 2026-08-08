"""동일 상품명 중복 레코드 정리 — 최신 CSV import(slug·색상)만 유지."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app import create_app  # noqa: E402
from extensions import db  # noqa: E402
from models import Product  # noqa: E402


def canonical_score(product: Product) -> float:
    """높을수록 유지 우선."""
    slug = product.slug or ""
    name = product.name or ""
    score = 0.0
    if product.filter_color:
        score += 100
    if "-outdoor-" in slug or "-table-" in slug:
        score -= 50
    if slug.startswith(("balcony-", "dining-", "sofa-", "lighting-", "living-room-")):
        score += 30
    if slug.startswith("bed-") and any(token in name for token in ("테이블", "협탁", "보조테이블")):
        score -= 40
    score += product.id / 1000.0
    return score


def deduplicate(*, dry_run: bool = False) -> dict[str, int]:
    stats = {"groups": 0, "deactivated": 0, "kept": 0}
    names = (
        db.session.query(Product.name)
        .filter(Product.is_active.is_(True))
        .group_by(Product.name)
        .having(db.func.count(Product.id) > 1)
        .all()
    )

    for (name,) in names:
        products = (
            Product.query.filter_by(name=name, is_active=True)
            .order_by(Product.id)
            .all()
        )
        if len(products) < 2:
            continue

        stats["groups"] += 1
        keep = max(products, key=canonical_score)
        stats["kept"] += 1

        for product in products:
            if product.id == keep.id:
                continue
            if not dry_run:
                product.is_active = False
            stats["deactivated"] += 1
            print(
                f"{'[DRY]' if dry_run else '[OFF]'} id={product.id} "
                f"color={product.filter_color or '-'} slug={product.slug}"
            )
            print(f"      keep id={keep.id} color={keep.filter_color or '-'} slug={keep.slug}")

    if not dry_run:
        db.session.commit()
    return stats


def main() -> None:
    dry_run = "--dry-run" in sys.argv
    app = create_app()
    with app.app_context():
        stats = deduplicate(dry_run=dry_run)
        print(
            f"\nGroups={stats['groups']} kept={stats['kept']} "
            f"deactivated={stats['deactivated']}"
        )


if __name__ == "__main__":
    main()
