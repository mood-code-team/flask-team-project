"""소파 CSV sub_category를 팀 기획 5분류로 정규화."""

from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = ROOT / "data" / "csv" / "output_sofa" / "sofa_100_products.csv"

LOUNGE_KEYWORDS = ("안락", "라운지체어", "이지체어", "게이밍안락", "회전라운지")
ARMCHAIR_KEYWORDS = ("암체어", "윙체어")


def classify_sofa_subcategory(raw: str, product_name: str) -> str:
    name = product_name or ""
    value = (raw or "").strip()

    if value in {"2인용", "2인소파"}:
        return "2인소파"
    if value in {"3인용", "3인 소파"}:
        return "3인 소파"

    if value == "기타소파" or value == "기타":
        if any(keyword in name for keyword in ARMCHAIR_KEYWORDS):
            return "암체어"
        if any(keyword in name for keyword in LOUNGE_KEYWORDS):
            return "안락의자"
        return "기타"

    if value in {"암체어", "안락의자"}:
        return value

    return value or "기타"


def main() -> None:
    with CSV_PATH.open(encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
        fieldnames = rows[0].keys() if rows else []

    for row in rows:
        row["sub_category"] = classify_sofa_subcategory(
            row.get("sub_category", ""),
            row.get("product_name", ""),
        )

    with CSV_PATH.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    from collections import Counter

    counts = Counter(row["sub_category"] for row in rows)
    print(f"[OK] updated {CSV_PATH}")
    for key, count in counts.most_common():
        print(f"  {key}: {count}")


if __name__ == "__main__":
    main()
