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
from scripts.product_enrichment import enrich_row_fields, stable_hash
from scripts.subcategory_mappings import (
    BALCONY_SUBCATEGORY_SLUGS,
    BED_SUBCATEGORY_SLUGS,
    DIFFUSER_SUBCATEGORY_SLUGS,
    normalize_balcony_sub_category,
    normalize_bed_sub_category,
    normalize_diffuser_sub_category,
)
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
    "DINING": "table",
    "BED": "bed",
    "BALCONY": "balcony",
    "BALCONY_OUTDOOR": "balcony",
}

DEFAULT_SUBCATEGORY: dict[str, str] = {
    "sofa": "sofa-3",
    "light": "table-lamp",
    "diffuser": "potpourri",
    "side-table": "side-table-item",
    "table": "standard-dining",
    "bed": "bed-other",
    "balcony": "outdoor-table",
}

SOFA_SUBCATEGORY_SLUGS: dict[str, str] = {
    "2인소파": "sofa-2",
    "2인용": "sofa-2",
    "3인소파": "sofa-3",
    "3인 소파": "sofa-3",
    "3인용": "sofa-3",
    "4인소파": "sofa-other",
    "4인 소파": "sofa-other",
    "4인용": "sofa-other",
    "리클라이너": "sofa-other",
    "코너소파": "sofa-other",
    "2인소파": "sofa-2",
    "2인용": "sofa-2",
    "암체어": "armchair",
    "안락의자": "lounge-chair",
    "소파 기타": "sofa-other",
    "소파기타": "sofa-other",
    "기타": "sofa-other",
    "기타소파": "sofa-other",
}

LOUNGE_KEYWORDS = ("안락", "라운지체어", "이지체어", "게이밍안락", "회전라운지")
ARMCHAIR_KEYWORDS = ("암체어", "윙체어")


def normalize_sofa_sub_category(row: dict) -> str:
    raw = (row.get("sub_category") or "").strip()
    name = (row.get("product_name") or "").strip()

    if raw in {"2인용", "2인소파"}:
        return "2인소파"
    if raw in {"3인용", "3인 소파", "3인소파"}:
        return "3인소파"
    if raw in SOFA_SUBCATEGORY_SLUGS and raw not in {"기타", "기타소파", "3인용", "2인용"}:
        return raw

    if raw in {"기타", "기타소파", "소파 기타", "소파기타"}:
        if any(keyword in name for keyword in ARMCHAIR_KEYWORDS):
            return "암체어"
        if any(keyword in name for keyword in LOUNGE_KEYWORDS):
            return "안락의자"
        return "소파기타"

    return raw or "소파기타"


def resolve_external_id(row: dict) -> str:
    """CSV external_id가 없으면 image_name(예: 104.890.09.jpg) stem을 사용."""
    external_id = (row.get("external_id") or "").strip()
    if external_id:
        return external_id

    image_name = (row.get("image_name") or "").strip()
    if image_name:
        return Path(image_name).stem

    return ""


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


def resolve_category(category_code: str, row: dict | None = None) -> Category | None:
    parent_slug = CATEGORY_CODE_TO_PARENT.get(category_code.upper())
    if not parent_slug:
        return None

    sub_slug = DEFAULT_SUBCATEGORY.get(parent_slug, parent_slug)
    if parent_slug == "sofa" and row:
        normalized = normalize_sofa_sub_category(row)
        sub_slug = SOFA_SUBCATEGORY_SLUGS.get(normalized, sub_slug)
    elif parent_slug == "balcony" and row:
        normalized = normalize_balcony_sub_category(row)
        sub_slug = BALCONY_SUBCATEGORY_SLUGS.get(normalized, sub_slug)
    elif parent_slug == "bed" and row:
        normalized = normalize_bed_sub_category(row)
        sub_slug = BED_SUBCATEGORY_SLUGS.get(normalized, sub_slug)
    elif parent_slug == "diffuser" and row:
        normalized = normalize_diffuser_sub_category(row)
        sub_slug = DIFFUSER_SUBCATEGORY_SLUGS.get(normalized, sub_slug)

    category = Category.query.filter_by(slug=sub_slug).first()
    if category:
        return category

    return Category.query.filter_by(slug=parent_slug).first()


def pick_image_url(row: dict, csv_path: Path) -> str:
    thumbnail = (row.get("thumbnail_url") or "").strip()
    if thumbnail.startswith("http"):
        return thumbnail[:500]

    image_name = (row.get("image_name") or "").strip()
    if image_name:
        image_name = Path(image_name).name

    local = (row.get("local_image_path") or "").strip()
    if image_name and not local:
        local = f"images/{image_name}"

    if local:
        local_path = (csv_path.parent / local).resolve()
        if not local_path.is_file():
            local_path = (ROOT / local).resolve()
        if not local_path.is_file() and image_name:
            local_path = (csv_path.parent / "images" / image_name).resolve()
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
        external_id = resolve_external_id(row)
        name = (row.get("product_name") or "").strip()

        if not category_code or not external_id or not name:
            stats["skipped"] += 1
            continue

        category = resolve_category(category_code, row)
        if not category:
            stats["errors"] += 1
            continue

        slug = slugify(name, external_id, category_code)
        price = parse_price(row.get("price", "0"))
        if price <= 0:
            stats["skipped"] += 1
            continue

        parent_slug = CATEGORY_CODE_TO_PARENT.get(category_code.upper(), "")
        pseudo_id = stable_hash(slug) % 1_000_000
        existing_product = Product.query.filter_by(slug=slug).first()
        existing = {}
        if existing_product:
            existing = {
                "filter_space": existing_product.filter_space,
                "filter_style": existing_product.filter_style,
                "filter_color": existing_product.filter_color,
                "mood_code_number": existing_product.mood_code_number,
                "discount_price": existing_product.discount_price,
                "brand": existing_product.brand,
                "is_popular": existing_product.is_popular,
                "is_new": existing_product.is_new,
                "is_best": existing_product.is_best,
            }

        enriched = enrich_row_fields(
            product_id=pseudo_id,
            slug=slug,
            name=name,
            description=(row.get("description") or name),
            price=price,
            parent_slug=parent_slug,
            category_rank=stable_hash(slug) % 20 + 1,
            csv_row=row,
            existing=existing,
        )

        fields = {
            "name": name[:200],
            "category_id": category.id,
            "description": (row.get("description") or name)[:5000],
            "price": price,
            "discount_price": enriched["discount_price"],
            "stock": parse_stock(row.get("stock_status", "")),
            "image_url": pick_image_url(row, csv_path) or None,
            "brand": (enriched.get("brand") or row.get("brand") or "IKEA")[:80],
            "filter_space": enriched["filter_space"],
            "filter_style": enriched["filter_style"],
            "filter_color": enriched["filter_color"],
            "mood_code_number": enriched.get("mood_code_number"),
            "has_installation": parent_slug in {"sofa", "bed", "table"},
            "is_popular": enriched["is_popular"],
            "is_new": enriched["is_new"],
            "is_best": enriched["is_best"],
            "is_active": True,
        }

        if dry_run:
            stats["created"] += 1
            continue

        product = existing_product
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
