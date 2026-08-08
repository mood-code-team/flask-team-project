"""잘못 비활성화된 상품 복구 + 고아 상품 색상 수정."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app import create_app  # noqa: E402
from extensions import db  # noqa: E402
from models import Product  # noqa: E402


def main() -> None:
    app = create_app()
    with app.app_context():
        fixes = [
            ("OLSERÖD 올세뢰드 보조테이블 - 앤트러싸이트/다크그레이 53x50 cm", 368, 133),
        ]
        for name, keep_id, off_id in fixes:
            keep = db.session.get(Product, keep_id)
            off = db.session.get(Product, off_id)
            if keep and keep.name == name:
                keep.is_active = True
                keep.filter_color = "black"
            if off and off.name == name:
                off.is_active = False

        pendant = Product.query.filter(
            Product.name == "BLÅSVERK 블로스베르크 펜던트등 - 베이지 37 cm",
            Product.is_active.is_(True),
        ).first()
        if pendant:
            pendant.filter_color = "beige"

        db.session.commit()
        print("[DONE] repaired OLSERÖD duplicate + BLÅSVERK pendant color")


if __name__ == "__main__":
    main()
