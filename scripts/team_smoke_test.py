"""팀원 PC 설치 후 빠른 점검 — python scripts/team_smoke_test.py"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main() -> int:
    errors: list[str] = []

    required = [
        ROOT / "requirements.txt",
        ROOT / "database" / "shop.db",
        ROOT / "static" / "csv" / "gallery_hotspots.csv",
        ROOT / ".env.example",
    ]
    for path in required:
        if not path.is_file():
            errors.append(f"missing file: {path.relative_to(ROOT)}")

    try:
        from app import create_app
        from models import Category, Coupon, Product, User

        app = create_app()
        with app.app_context():
            product_count = Product.query.count()
            category_count = Category.query.filter_by(parent_id=None).count()
            admin = User.query.filter_by(is_admin=True).first()
            member5 = Coupon.query.filter_by(code="MEMBER5").first()

            if product_count < 100:
                errors.append(
                    f"products too few ({product_count}) — pull frontend branch or run import_csv.py"
                )
            if category_count < 5:
                errors.append(f"categories too few ({category_count})")
            if admin is None:
                errors.append("admin user missing — run scripts/seed_db.py")
            if member5 and member5.is_active:
                errors.append("MEMBER5 should be inactive")

        client = app.test_client()
        for path in ("/", "/gallery/bloom", "/category/sofa", "/login", "/cart"):
            status = client.get(path).status_code
            if status >= 500:
                errors.append(f"{path} returned {status}")

    except Exception as exc:  # noqa: BLE001 — smoke test should report any startup failure
        errors.append(f"app startup failed: {exc}")

    if errors:
        print("[FAIL] team smoke test")
        for item in errors:
            print(" -", item)
        return 1

    print("[OK] team smoke test passed")
    print(f"     products={product_count}, categories={category_count}, admin={admin.username}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
