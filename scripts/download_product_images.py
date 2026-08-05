"""
외부 상품 이미지(IKEA CDN 등)를 로컬 static/ 으로 캐시.

사용:
  python scripts/download_product_images.py
  python scripts/download_product_images.py --limit 50
"""

from __future__ import annotations

import argparse
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import create_app  # noqa: E402
from extensions import db
from models import Product

ROOT = Path(__file__).resolve().parent.parent
IMAGE_DIR = ROOT / "static" / "images" / "products" / "imported"
USER_AGENT = "MoodCode-Dev/1.0 (education project)"


def download_url(url: str, dest: Path) -> bool:
    if dest.exists() and dest.stat().st_size > 0:
        return True

    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            data = response.read()
        if len(data) < 500:
            return False
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        return True
    except (urllib.error.URLError, TimeoutError, OSError):
        return False


def cache_product_images(*, limit: int | None = None, delay: float = 0.3) -> dict[str, int]:
    stats = {"total": 0, "downloaded": 0, "skipped": 0, "failed": 0, "updated": 0}

    query = Product.query.filter(
        Product.image_url.isnot(None),
        Product.image_url != "",
        Product.image_url.like("http%"),
    )
    if limit:
        products = query.limit(limit).all()
    else:
        products = query.all()

    for product in products:
        stats["total"] += 1
        url = product.image_url or ""
        ext = ".jpg"
        if ".png" in url.lower():
            ext = ".png"
        elif ".webp" in url.lower():
            ext = ".webp"

        filename = f"{product.slug[:120]}{ext}"
        dest = IMAGE_DIR / filename
        local_url = f"/static/images/products/imported/{filename}"

        if product.image_url.startswith("/static/"):
            stats["skipped"] += 1
            continue

        if download_url(url, dest):
            stats["downloaded"] += 1
            if product.image_url != local_url:
                product.image_url = local_url
                stats["updated"] += 1
        else:
            stats["failed"] += 1

        time.sleep(delay)

    db.session.commit()
    return stats


def main() -> None:
    parser = argparse.ArgumentParser(description="Cache external product images locally")
    parser.add_argument("--limit", type=int, default=None, help="Max products to process")
    parser.add_argument("--delay", type=float, default=0.3, help="Delay between downloads (sec)")
    args = parser.parse_args()

    app = create_app()
    with app.app_context():
        stats = cache_product_images(limit=args.limit, delay=args.delay)

    print("[DOWNLOAD] product images cached")
    for key, value in stats.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
