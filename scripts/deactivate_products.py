"""스크린샷으로 지정된 잘못 노출 상품 비활성화."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app import create_app  # noqa: E402
from extensions import db  # noqa: E402
from models import Product  # noqa: E402

TARGET_SLUGS = (
    "sofa-095-899-91",   # KLIPPAN 옐로/화이트/플로럴
    "sofa-706-131-76",   # STRANDMON 블루/베이지
    "sofa-705-861-11",   # STOCKHOLM 다크터쿼이즈
)


def main() -> None:
    app = create_app()
    with app.app_context():
        for slug in TARGET_SLUGS:
            product = Product.query.filter_by(slug=slug).first()
            if not product:
                print(f"[MISS] {slug}")
                continue
            product.is_active = False
            print(f"[OFF] id={product.id} {product.name[:60]}")
        db.session.commit()
        print("[DONE]")


if __name__ == "__main__":
    main()
