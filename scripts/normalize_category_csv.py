"""발코니·침대·디퓨저 CSV sub_category를 엑셀 DB 기준으로 정규화."""

from __future__ import annotations

import csv
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.subcategory_mappings import (
    normalize_balcony_sub_category,
    normalize_bed_sub_category,
    normalize_diffuser_sub_category,
)

ROOT = Path(__file__).resolve().parent.parent
TARGETS: dict[str, tuple[Path, object]] = {
    "balcony": (
        ROOT / "data" / "csv" / "output_balcony" / "balcony_100_products.csv",
        normalize_balcony_sub_category,
    ),
    "bed": (
        ROOT / "data" / "csv" / "output_bed" / "bed_100_products.csv",
        normalize_bed_sub_category,
    ),
    "diffuser": (
        ROOT / "data" / "csv" / "output_diffuser" / "diffuser_100_products.csv",
        normalize_diffuser_sub_category,
    ),
}


def normalize_csv(label: str, csv_path: Path, normalizer) -> None:
    with csv_path.open(encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
        fieldnames = rows[0].keys() if rows else []

    for row in rows:
        row["sub_category"] = normalizer(row)

    with csv_path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    counts = Counter(row["sub_category"] for row in rows)
    print(f"[OK] {label}: {csv_path}")
    for key, count in counts.most_common():
        print(f"  {key}: {count}")


def main() -> None:
    for label, (csv_path, normalizer) in TARGETS.items():
        if not csv_path.exists():
            print(f"[SKIP] missing {csv_path}")
            continue
        normalize_csv(label, csv_path, normalizer)


if __name__ == "__main__":
    main()
