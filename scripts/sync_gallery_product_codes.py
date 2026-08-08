"""Sync mood_code_number from gallery CSV scene mappings into products DB."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(ROOT := Path(__file__).resolve().parent.parent))

from app import create_app
from extensions import db
from models import Product
from services.product_lookup import find_product_by_image_name, normalize_image_filename

CODE_IMAGE_PAIRS: tuple[tuple[str, str], ...] = (
    ("sofa_code", "sofa_image_name"),
    ("bed_code", "bed_image_name"),
    ("dining_code", "dining_image_name"),
    ("balcony_code", "balcony_image_name"),
    ("table_code", "table_image_name"),
    ("side_table_code", "side_table_image_name"),
    ("light_code", "light_image_name"),
    ("scent_code", "scent_image_name"),
)


def collect_gallery_mappings() -> dict[str, str]:
    """image filename -> mood_code_number (gallery is source of truth)."""
    mapping: dict[str, str] = {}
    csv_dir = ROOT / "static" / "csv"
    for csv_file in sorted(csv_dir.glob("moodcode_*_4seasons_16_final.csv")):
        with csv_file.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                for code_key, image_key in CODE_IMAGE_PAIRS:
                    code = (row.get(code_key) or "").strip().upper()
                    image_name = normalize_image_filename(row.get(image_key) or "")
                    if not code.startswith("MC-") or not image_name:
                        continue
                    prev = mapping.get(image_name)
                    if prev and prev != code:
                        print(f"[WARN] {image_name}: {prev} vs {code} ({csv_file.name})")
                    mapping[image_name] = code
    return mapping


def sync_products(*, dry_run: bool = False) -> dict[str, int]:
    stats = {"updated": 0, "skipped": 0, "missing": 0, "conflict": 0}
    mapping = collect_gallery_mappings()
    app = create_app()

    with app.app_context():
        for image_name, mood_code in mapping.items():
            product = find_product_by_image_name(image_name)
            if not product:
                stats["missing"] += 1
                continue

            current = (product.mood_code_number or "").strip().upper()
            if current == mood_code:
                stats["skipped"] += 1
                continue

            if current and current != mood_code:
                print(
                    f"[FIX] {product.slug}: {current} -> {mood_code} ({image_name})"
                )
                stats["conflict"] += 1
            else:
                print(f"[SET] {product.slug}: {mood_code} ({image_name})")

            if not dry_run:
                product.mood_code_number = mood_code
                stats["updated"] += 1

        if not dry_run:
            db.session.commit()

    return stats


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync gallery mood codes to products")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    stats = sync_products(dry_run=args.dry_run)
    print("\nSync complete:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    if args.dry_run:
        print("\n[DRY-RUN] Run without --dry-run to apply.")


if __name__ == "__main__":
    main()
