"""
data-analysis 브랜치에서 스크래핑 CSV·이미지를 로컬 data/csv/ 로 복사.

사용:
  python scripts/fetch_csv_data.py
  python scripts/fetch_csv_data.py --remote team --branch data-analysis
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT = ROOT / "data" / "csv"

CSV_FILES = [
    "output_sofa/sofa_100_products.csv",
    "output_lighting/lighting_100_products.csv",
    "output_diffuser/diffuser_100_products.csv",
    "output_living_table/ikea_living_table_100_products.csv",
    "output_dining_table/dining_table_100_products.csv",
    "output_bed/bed_100_products.csv",
    "output_balcony/balcony_100_products.csv",
]


def run_git(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )


def list_tree(remote: str, branch: str, prefix: str) -> list[str]:
    ref = f"{remote}/{branch}"
    result = run_git(["ls-tree", "-r", "--name-only", ref, prefix])
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def fetch_file(remote: str, branch: str, rel_path: str, out_dir: Path) -> bool:
    ref = f"{remote}/{branch}"
    result = run_git(["show", f"{ref}:{rel_path}"])
    if result.returncode != 0:
        return False

    dest = out_dir / rel_path
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(result.stdout, encoding="utf-8")
    return True


def fetch_binary(remote: str, branch: str, rel_path: str, out_dir: Path) -> bool:
    ref = f"{remote}/{branch}"
    result = subprocess.run(
        ["git", "show", f"{ref}:{rel_path}"],
        cwd=ROOT,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return False

    dest = out_dir / rel_path
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(result.stdout)
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch CSV data from data-analysis branch")
    parser.add_argument("--remote", default="team", help="Git remote name (default: team)")
    parser.add_argument("--branch", default="data-analysis", help="Source branch")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="Output directory")
    parser.add_argument("--skip-images", action="store_true", help="CSV only, skip images")
    args = parser.parse_args()

    fetch = run_git(["fetch", args.remote, args.branch])
    if fetch.returncode != 0:
        print(f"[ERROR] git fetch failed:\n{fetch.stderr}")
        sys.exit(1)

    out_dir = args.out.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    fetched = 0

    for rel_path in CSV_FILES:
        if fetch_file(args.remote, args.branch, rel_path, out_dir):
            fetched += 1
            print(f"[OK] {rel_path}")
        else:
            print(f"[WARN] skip: {rel_path}")

    if not args.skip_images:
        for folder in {Path(p).parts[0] for p in CSV_FILES}:
            image_dir = f"{folder}/images"
            for rel_path in list_tree(args.remote, args.branch, image_dir):
                if rel_path.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                    if fetch_binary(args.remote, args.branch, rel_path, out_dir):
                        fetched += 1

        print(f"[OK] images fetched from output_*/images/")

    print(f"\n[DONE] {fetched} files → {out_dir}")
    print("Next: python scripts/seed_db.py && python scripts/import_csv.py")


if __name__ == "__main__":
    main()
