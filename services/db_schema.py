"""SQLite 등 개발 DB 스키마 보정."""

from sqlalchemy import inspect, text

from extensions import db

_USER_COLUMN_PATCHES: dict[str, str] = {
    "full_name": "VARCHAR(80)",
    "birth_year": "INTEGER",
    "birth_month": "INTEGER",
    "birth_day": "INTEGER",
    "calendar_type": "VARCHAR(10)",
    "region": "VARCHAR(40)",
    "agree_sms": "BOOLEAN DEFAULT 0",
    "agree_email": "BOOLEAN DEFAULT 0",
    "auth_provider": "VARCHAR(20)",
    "auth_provider_id": "VARCHAR(128)",
}


def ensure_user_schema() -> None:
    """users 테이블에 누락된 컬럼을 추가한다."""
    inspector = inspect(db.engine)
    if "users" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("users")}
    for name, ddl in _USER_COLUMN_PATCHES.items():
        if name in columns:
            continue
        db.session.execute(text(f"ALTER TABLE users ADD COLUMN {name} {ddl}"))
    db.session.commit()


_ORDER_COLUMN_PATCHES: dict[str, str] = {
    "product_total": "INTEGER DEFAULT 0",
    "shipping_fee": "INTEGER DEFAULT 0",
    "payment_key": "VARCHAR(200)",
    "payment_method": "VARCHAR(40)",
    "paid_at": "DATETIME",
}


def ensure_order_schema() -> None:
    """orders 테이블 스키마 보정."""
    inspector = inspect(db.engine)
    if "orders" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("orders")}
    for name, ddl in _ORDER_COLUMN_PATCHES.items():
        if name in columns:
            continue
        db.session.execute(text(f"ALTER TABLE orders ADD COLUMN {name} {ddl}"))
    db.session.commit()


_ORDER_BENEFIT_PATCHES: dict[str, str] = {
    "coupon_discount": "INTEGER DEFAULT 0",
    "point_used": "INTEGER DEFAULT 0",
    "user_coupon_id": "INTEGER",
}


def ensure_order_benefit_schema() -> None:
    """orders 테이블 — 쿠폰·적립금 컬럼."""
    inspector = inspect(db.engine)
    if "orders" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("orders")}
    for name, ddl in _ORDER_BENEFIT_PATCHES.items():
        if name in columns:
            continue
        db.session.execute(text(f"ALTER TABLE orders ADD COLUMN {name} {ddl}"))
    db.session.commit()


_CATEGORY_COLUMN_PATCHES: dict[str, str] = {
    "name_en": "VARCHAR(100)",
}


def ensure_category_schema() -> None:
    """categories 테이블 스키마 보정."""
    inspector = inspect(db.engine)
    if "categories" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("categories")}
    for name, ddl in _CATEGORY_COLUMN_PATCHES.items():
        if name in columns:
            continue
        db.session.execute(text(f"ALTER TABLE categories ADD COLUMN {name} {ddl}"))
    db.session.commit()


_PRODUCT_FILTER_PATCHES: dict[str, str] = {
    "brand": "VARCHAR(80)",
    "filter_space": "VARCHAR(20)",
    "filter_style": "VARCHAR(20)",
    "filter_color": "VARCHAR(20)",
    "mood_code_number": "VARCHAR(32)",
}


def ensure_product_filter_schema() -> None:
    """products 테이블 — 필터·브랜드 컬럼."""
    inspector = inspect(db.engine)
    if "products" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("products")}
    for name, ddl in _PRODUCT_FILTER_PATCHES.items():
        if name in columns:
            continue
        db.session.execute(text(f"ALTER TABLE products ADD COLUMN {name} {ddl}"))
    db.session.commit()
