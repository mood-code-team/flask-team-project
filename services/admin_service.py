"""관리자 페이지 서비스."""

from __future__ import annotations

from sqlalchemy import func

from extensions import db
from models import Category, CustomerInquiry, FAQ, InquiryStatus, Notice, Order, OrderStatus, Product, User


def parse_int(value: str | None, *, default: int = 0, minimum: int = 0) -> int:
    try:
        return max(int(value or default), minimum)
    except (TypeError, ValueError):
        return default


def parse_optional_int(value: str | None) -> int | None:
    raw = (value or "").strip()
    if not raw:
        return None
    try:
        return max(int(raw), 0)
    except (TypeError, ValueError):
        return None


def get_dashboard_stats() -> dict[str, int]:
    paid_statuses = (
        OrderStatus.PAID,
        OrderStatus.PREPARING,
        OrderStatus.SHIPPING,
        OrderStatus.DELIVERED,
    )
    revenue = (
        db.session.query(func.coalesce(func.sum(Order.total_amount), 0))
        .filter(Order.status.in_(paid_statuses))
        .scalar()
    )
    return {
        "products_total": Product.query.count(),
        "products_active": Product.query.filter_by(is_active=True).count(),
        "orders_total": Order.query.count(),
        "orders_pending": Order.query.filter_by(status=OrderStatus.PENDING).count(),
        "users_total": User.query.filter_by(is_admin=False).count(),
        "notices_active": Notice.query.filter_by(is_active=True).count(),
        "faqs_active": FAQ.query.filter_by(is_active=True).count(),
        "inquiries_pending": CustomerInquiry.query.filter_by(status=InquiryStatus.PENDING).count(),
        "revenue_total": int(revenue or 0),
    }


def get_recent_orders(limit: int = 8):
    return Order.query.order_by(Order.created_at.desc()).limit(limit).all()


def get_pending_inquiries(limit: int = 5):
    return (
        CustomerInquiry.query.filter_by(status=InquiryStatus.PENDING)
        .order_by(CustomerInquiry.created_at.desc())
        .limit(limit)
        .all()
    )


def search_products(*, q: str = "", category_id: int | None = None, page: int = 1, per_page: int = 20):
    query = Product.query.order_by(Product.updated_at.desc())
    if q:
        like = f"%{q.strip()}%"
        query = query.filter(Product.name.ilike(like))
    if category_id:
        query = query.filter_by(category_id=category_id)
    return query.paginate(page=page, per_page=per_page, error_out=False)


def search_orders(*, status: str = "", q: str = "", page: int = 1, per_page: int = 20):
    query = Order.query.order_by(Order.created_at.desc())
    if status and status in OrderStatus.LABELS:
        query = query.filter_by(status=status)
    if q:
        like = f"%{q.strip()}%"
        query = query.filter(Order.order_number.ilike(like))
    return query.paginate(page=page, per_page=per_page, error_out=False)


def search_users(*, q: str = "", page: int = 1, per_page: int = 20):
    query = User.query.filter_by(is_admin=False).order_by(User.created_at.desc())
    if q:
        like = f"%{q.strip()}%"
        query = query.filter(
            (User.username.ilike(like)) | (User.email.ilike(like)) | (User.full_name.ilike(like))
        )
    return query.paginate(page=page, per_page=per_page, error_out=False)


def search_inquiries(*, status: str = "", page: int = 1, per_page: int = 20):
    query = CustomerInquiry.query.order_by(CustomerInquiry.created_at.desc())
    if status and status in InquiryStatus.LABELS:
        query = query.filter_by(status=status)
    return query.paginate(page=page, per_page=per_page, error_out=False)


def list_notices():
    return Notice.query.order_by(Notice.is_pinned.desc(), Notice.created_at.desc()).all()


def list_faqs():
    return FAQ.query.order_by(FAQ.category, FAQ.sort_order, FAQ.id).all()


def get_leaf_categories():
    return (
        Category.query.filter(Category.parent_id.isnot(None), Category.is_active.is_(True))
        .order_by(Category.sort_order, Category.name)
        .all()
    )


def get_category_rows():
    rows: list[dict] = []
    parents = (
        Category.query.filter_by(parent_id=None, is_active=True)
        .order_by(Category.sort_order)
        .all()
    )
    for parent in parents:
        children = (
            Category.query.filter_by(parent_id=parent.id, is_active=True)
            .order_by(Category.sort_order)
            .all()
        )
        if children:
            for child in children:
                rows.append(
                    {
                        "parent": parent,
                        "category": child,
                        "product_count": Product.query.filter_by(category_id=child.id, is_active=True).count(),
                    }
                )
        else:
            rows.append(
                {
                    "parent": parent,
                    "category": parent,
                    "product_count": Product.query.filter_by(category_id=parent.id, is_active=True).count(),
                }
            )
    return rows


def get_admin_sidebar_counts() -> dict[str, int]:
    return {
        "pending_orders": Order.query.filter_by(status=OrderStatus.PENDING).count(),
        "pending_inquiries": CustomerInquiry.query.filter_by(status=InquiryStatus.PENDING).count(),
    }
