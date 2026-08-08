"""Audit filter_color vs product name across CSV and DB."""
from __future__ import annotations

import csv
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.product_enrichment import (  # noqa: E402
    infer_primary_color_from_name,
    normalize_filter_color,
)
from services.search_filters import FILTER_GROUPS  # noqa: E402

PALETTE = set(FILTER_GROUPS["color"]["options"])

COLOR_HINTS = {
    "white": ("화이트", "오프화이트", "white", "흰"),
    "yellow": ("옐로", "yellow", "노란", "오렌지", "브라이트옐로", "다크옐로"),
    "black": ("블랙", "black", "검정", "앤트러싸이트", "anthracite"),
    "gray": ("그레이", "gray", "grey", "회색", "니켈"),
    "beige": ("베이지", "beige", "아이보리", "크림", "오트밀"),
    "wood": ("우드", "wood", "나무", "아카시아", "오크", "birch", "walnut", "원목"),
    "pink": ("핑크", "pink", "레드", "red", "브라이트레드"),
    "green": ("그린", "green", "초록"),
    "blue": ("블루", "blue", "파란", "네이비"),
}


def name_suggests_color(name: str) -> set[str]:
    lower = name.lower()
    found: set[str] = set()
    for color, hints in COLOR_HINTS.items():
        if any(h in lower or h in name for h in hints):
            found.add(color)
    return found


def audit_csv() -> list[dict]:
    issues: list[dict] = []
    csv_root = ROOT / "data" / "csv"
    for csv_path in sorted(csv_root.rglob("*_products.csv")):
        with csv_path.open(encoding="utf-8-sig", newline="") as fh:
            for row in csv.DictReader(fh):
                name = (row.get("product_name") or "").strip()
                raw = (row.get("filter_color") or "").strip()
                if not name:
                    continue
                normalized = normalize_filter_color(raw, name=name, description=row.get("description") or "")
                primary = infer_primary_color_from_name(name)
                suggested = name_suggests_color(name)

                problem = None
                if normalized and primary and normalized != primary:
                    problem = f"normalized({normalized}) != primary({primary})"
                elif normalized and suggested and normalized not in suggested and len(suggested) == 1:
                    only = next(iter(suggested))
                    if only != normalized:
                        problem = f"normalized({normalized}) vs name-hints({only})"
                elif raw and not normalized:
                    problem = f"unmapped raw={raw!r}"

                if problem:
                    issues.append({
                        "source": csv_path.name,
                        "name": name[:70],
                        "raw": raw,
                        "normalized": normalized,
                        "primary": primary,
                        "hints": ",".join(sorted(suggested)),
                        "problem": problem,
                    })
    return issues


def audit_db() -> list[dict]:
    conn = sqlite3.connect(ROOT / "database" / "shop.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT name, filter_color FROM products WHERE is_active=1")
    issues: list[dict] = []
    for row in cur.fetchall():
        name = row["name"]
        fc = row["filter_color"] or ""
        primary = infer_primary_color_from_name(name)
        suggested = name_suggests_color(name)
        if fc and primary and fc != primary:
            issues.append({"name": name[:70], "filter_color": fc, "primary": primary, "hints": ",".join(sorted(suggested))})
        elif fc and suggested and len(suggested) == 1 and fc not in suggested:
            only = next(iter(suggested))
            if fc != only:
                issues.append({"name": name[:70], "filter_color": fc, "primary": primary, "hints": only})
    conn.close()
    return issues


if __name__ == "__main__":
    csv_issues = audit_csv()
    db_issues = audit_db()
    print(f"CSV issues: {len(csv_issues)}")
    for item in csv_issues[:40]:
        print(f"  [{item['source']}] {item['problem']}")
        print(f"    {item['name']}")
        print(f"    raw={item['raw']!r} -> {item['normalized']} | primary={item['primary']} hints={item['hints']}")
    if len(csv_issues) > 40:
        print(f"  ... and {len(csv_issues) - 40} more")

    print(f"\nDB issues: {len(db_issues)}")
    for item in db_issues[:40]:
        print(f"  {item['filter_color']} vs primary={item['primary']} hints={item['hints']}")
        print(f"    {item['name']}")
    if len(db_issues) > 40:
        print(f"  ... and {len(db_issues) - 40} more")
