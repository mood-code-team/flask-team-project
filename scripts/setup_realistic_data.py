"""
실제 쇼핑몰처럼 보이는 데이터 한 번에 세팅.

사용:
  python scripts/setup_realistic_data.py
  python scripts/setup_realistic_data.py --skip-fetch
  python scripts/setup_realistic_data.py --with-images --image-limit 50
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PYTHON = sys.executable


def run_script(name: str, *args: str) -> None:
    script = ROOT / "scripts" / name
    print(f"\n>>> python scripts/{name} {' '.join(args)}")
    result = subprocess.run([PYTHON, str(script), *args], cwd=ROOT, check=False)
    if result.returncode != 0:
        sys.exit(result.returncode)


def main() -> None:
    parser = argparse.ArgumentParser(description="Full realistic data setup pipeline")
    parser.add_argument("--skip-fetch", action="store_true", help="Skip fetch_csv_data.py")
    parser.add_argument("--with-images", action="store_true", help="Download product images")
    parser.add_argument("--image-limit", type=int, default=50)
    parser.add_argument("--reset-demo", action="store_true", help="Reset demo reviews/Q&A")
    args = parser.parse_args()

    if not args.skip_fetch:
        run_script("fetch_csv_data.py", "--skip-images")

    run_script("seed_db.py")
    run_script("import_csv.py", "--update")
    run_script("enrich_products.py")

    if args.with_images:
        run_script("download_product_images.py", "--limit", str(args.image_limit))

    demo_args = ["--reset"] if args.reset_demo else []
    run_script("seed_demo_content.py", *demo_args)

    print("\n[DONE] Realistic data setup complete.")
    print("  Server: python hspace_server.py")
    print("  Guide:  docs/DATA_ENRICHMENT.md")


if __name__ == "__main__":
    main()
