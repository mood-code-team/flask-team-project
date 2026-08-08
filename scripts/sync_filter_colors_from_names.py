"""CSV filter_color를 상품명 기반 정규화 결과와 동기화."""
from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.product_enrichment import normalize_filter_color  # noqa: E402

PALETTE_TO_KOREAN = {
    "white": "화이트",
    "beige": "베이지",
    "gray": "그레이",
    "wood": "우드",
    "black": "블랙",
    "pink": "핑크",
    "yellow": "옐로우",
    "green": "그린",
    "blue": "블루",
}


def sync_csv(csv_path: Path, *, dry_run: bool = False) -> int:
    with csv_path.open(encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        fieldnames = reader.fieldnames or []
        rows = list(reader)

    if "filter_color" not in fieldnames:
        return 0

    changed = 0
    for row in rows:
        name = (row.get("product_name") or "").strip()
        if not name:
            continue
        normalized = normalize_filter_color(
            row.get("filter_color") or "",
            name=name,
            description=row.get("description") or "",
        )
        if not normalized:
            continue
        korean = PALETTE_TO_KOREAN.get(normalized, normalized)
        if (row.get("filter_color") or "").strip() != korean:
            if not dry_run:
                row["filter_color"] = korean
            changed += 1

    if changed and not dry_run:
        with csv_path.open("w", encoding="utf-8-sig", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    return changed


def main() -> None:
    dry_run = "--dry-run" in sys.argv
    csv_root = ROOT / "data" / "csv"
    total = 0
    for csv_path in sorted(csv_root.rglob("*_products.csv")):
        count = sync_csv(csv_path, dry_run=dry_run)
        if count:
            print(f"{'[DRY]' if dry_run else '[OK]'} {csv_path.name}: {count} rows")
            total += count
    print(f"\nTotal {'would change' if dry_run else 'changed'}: {total}")


if __name__ == "__main__":
    main()
