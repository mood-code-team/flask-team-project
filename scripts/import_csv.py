"""
스크래핑 CSV → DB 상품 import.

사용:
  python scripts/fetch_csv_data.py          # data-analysis 브랜치에서 CSV 가져오기
  python scripts/seed_db.py                 # 카테고리·관리자 시드 (선행)
  python scripts/import_csv.py              # CSV → products 테이블
  python scripts/import_csv.py --dry-run    # DB 변경 없이 미리보기

CSV 위치: data/csv/output_*/  (fetch_csv_data.py 실행 후 생성)
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import create_app  # noqa: E402
from extensions import db
from models import Category, Product
from scripts.seed_db import seed_admin, seed_catalog, seed_faqs, seed_notices
from services.db_schema import (
    ensure_category_schema,
    ensure_product_filter_schema,
    ensure_user_schema,
)

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CSV_DIR = ROOT / "data" / "csv"

# CSV category_code → 상위 카테고리 slug (catalog_data.py 기준)
CATEGORY_CODE_TO_PARENT: dict[str, str] = {
    "SOFA": "sofa",
    "LIGHTING": "light",
    "DIFFUSER": "diffuser",
    "LIVING_TABLE": "side-table",
    "LIVING_ROOM_TABLE": "side-table",
    "DINING_TABLE": "table",
    "BED": "bed",
    "BALCONY": "balcony",
    "BALCONY_OUTDOOR": "balcony",
}

# 상위 카테고리 → 기본 하위 카테고리 slug (CSV에 하위 분류 없을 때)
DEFAULT_SUBCATEGORY: dict[str, str] = {
    "sofa": "sofa-3",
    "light": "table-lamp",
    "diffuser": "wood-diffuser",
    "side-table": "side-table-item",
    "table": "standard-dining",
    "bed": "bed-frame",
    "balcony": "outdoor-table",
}

# 카테고리 → filter_space 기본값
CATEGORY_FILTER_SPACE: dict[str, str] = {
    "sofa": "living",
    "light": "living",
    "diffuser": "living",
    "side-table": "living",
    "table": "kitchen",
    "bed": "bedroom",
    "balcony": "balcony",
}


def slugify(text: str, external_id: str, category_code: str) -> str:
    """고유 slug 생성 (external_id 기반)."""
    base = re.sub(r"[^a-z0-9]+", "-", external_id.lower()).strip("-")
    prefix = category_code.lower().replace("_", "-")
    slug = f"{prefix}-{base}"[:200]
    return slug or f"{prefix}-product"


def parse_price(raw: str) -> int:
    try:
        return max(int(float(raw)), 0)
    except (TypeError, ValueError):
        return 0


def parse_stock(stock_status: str) -> int:
    status = (stock_status or "").lower()
    if "outofstock" in status or "out_of_stock" in status:
        return 0
    return 50


def resolve_category(category_code: str) -> Category | None:
    parent_slug = CATEGORY_CODE_TO_PARENT.get(category_code.upper())
    if not parent_slug:
        return None

    sub_slug = DEFAULT_SUBCATEGORY.get(parent_slug, parent_slug)
    category = Category.query.filter_by(slug=sub_slug).first()
    if category:
        return category

    return Category.query.filter_by(slug=parent_slug).first()


def pick_image_url(row: dict, csv_path: Path) -> str:
    thumbnail = (row.get("thumbnail_url") or "").strip()
    if thumbnail.startswith("http"):
        return thumbnail[:500]

    local = (row.get("local_image_path") or "").strip()
    if local:
        local_path = (csv_path.parent / local).resolve()
        if not local_path.is_file():
            local_path = (ROOT / local).resolve()
        if local_path.is_file():
            dest_dir = ROOT / "static" / "images" / "products" / "imported"
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest = dest_dir / local_path.name
            if not dest.exists():
                dest.write_bytes(local_path.read_bytes())
            return f"/static/images/products/imported/{local_path.name}"

    return ""


def iter_csv_rows(csv_dir: Path):
    for csv_path in sorted(csv_dir.glob("output_*/*_products.csv")):
        with csv_path.open(encoding="utf-8-sig", newline="") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                yield csv_path, row


def import_products(
    csv_dir: Path,
    *,
    dry_run: bool = False,
    skip_existing: bool = True,
    limit: int | None = None,
) -> dict[str, int]:
    stats = {"files": 0, "rows": 0, "created": 0, "updated": 0, "skipped": 0, "errors": 0}
    seen_files: set[Path] = set()

    for csv_path, row in iter_csv_rows(csv_dir):
        if csv_path not in seen_files:
            seen_files.add(csv_path)
            stats["files"] += 1

        stats["rows"] += 1
        if limit and stats["rows"] > limit:
            break

        category_code = (row.get("category_code") or "").strip()
        external_id = (row.get("external_id") or "").strip()
        name = (row.get("product_name") or "").strip()

        if not category_code or not external_id or not name:
            stats["skipped"] += 1
            continue

        category = resolve_category(category_code)
        if not category:
            stats["errors"] += 1
            continue

        slug = slugify(name, external_id, category_code)
        price = parse_price(row.get("price", "0"))
        if price <= 0:
            stats["skipped"] += 1
            continue

        parent_slug = CATEGORY_CODE_TO_PARENT.get(category_code.upper(), "")
        fields = {
            "name": name[:200],
            "category_id": category.id,
            "description": (row.get("description") or name)[:5000],
            "price": price,
            "discount_price": None,
            "stock": parse_stock(row.get("stock_status", "")),
            "image_url": pick_image_url(row, csv_path) or None,
            "brand": (row.get("brand") or "IKEA")[:80],
            "filter_space": CATEGORY_FILTER_SPACE.get(parent_slug, "living"),
            "filter_style": "",
            "filter_color": "",
            "has_installation": parent_slug in {"sofa", "bed", "table"},
            "is_popular": False,
            "is_new": False,
            "is_best": False,
            "is_active": True,
        }

        if dry_run:
            stats["created"] += 1
            continue

        product = Product.query.filter_by(slug=slug).first()
        if product:
            if skip_existing:
                stats["skipped"] += 1
                continue
            for key, value in fields.items():
                setattr(product, key, value)
            stats["updated"] += 1
        else:
            db.session.add(Product(slug=slug, **fields))
            stats["created"] += 1

    if not dry_run:
        db.session.commit()

    return stats


def main() -> None:
    parser = argparse.ArgumentParser(description="Import scraped CSV products into DB")
    parser.add_argument(
        "--csv-dir",
        type=Path,
        default=DEFAULT_CSV_DIR,
        help=f"CSV root directory (default: {DEFAULT_CSV_DIR})",
    )
    parser.add_argument("--dry-run", action="store_true", help="Preview without DB writes")
    parser.add_argument("--update", action="store_true", help="Update existing products by slug")
    parser.add_argument("--limit", type=int, default=None, help="Max rows to process")
    parser.add_argument("--skip-seed", action="store_true", help="Skip seed_db steps")
    args = parser.parse_args()

    csv_dir = args.csv_dir.resolve()
    if not csv_dir.is_dir():
        print(f"[ERROR] CSV directory not found: {csv_dir}")
        print("        Run: python scripts/fetch_csv_data.py")
        sys.exit(1)

    app = create_app()
    with app.app_context():
        db.create_all()
        ensure_user_schema()
        ensure_category_schema()
        ensure_product_filter_schema()

        if not args.skip_seed:
            seed_catalog()
            seed_admin()
            seed_faqs()
            seed_notices()

        stats = import_products(
            csv_dir,
            dry_run=args.dry_run,
            skip_existing=not args.update,
            limit=args.limit,
        )

    mode = "DRY-RUN" if args.dry_run else "IMPORT"
    print(f"[{mode}] CSV import finished")
    print(f"  files   : {stats['files']}")
    print(f"  rows    : {stats['rows']}")
    print(f"  created : {stats['created']}")
    print(f"  updated : {stats['updated']}")
    print(f"  skipped : {stats['skipped']}")
    print(f"  errors  : {stats['errors']}")


if __name__ == "__main__":
    main()
