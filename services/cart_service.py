"""
장바구니 — 로그인 회원 DB, 비회원 세션.
"""

from __future__ import annotations

from dataclasses import dataclass

from flask import session
from flask_login import current_user

from extensions import db
from models import CartItem, Product


@dataclass
class CartLine:
    product: Product
    quantity: int

    @property
    def subtotal(self) -> int:
        return self.product.sale_price * self.quantity

    @property
    def original_subtotal(self) -> int:
        return self.product.price * self.quantity

    @property
    def discount_amount(self) -> int:
        return max(self.original_subtotal - self.subtotal, 0)


@dataclass
class CartSummary:
    lines: list[CartLine]
    item_count: int
    product_total: int
    original_total: int
    discount_total: int
    shipping_fee: int
    grand_total: int
    cod_separate: bool = False


SHIPPING_FEE = 4000
FREE_SHIPPING_THRESHOLD = 300_000
PROPORTIONAL_SHIPPING_THRESHOLD = 500_000
PROPORTIONAL_SHIPPING_FEE = 80_000


def line_shipping_info(line: CartLine) -> dict:
    """상품별 배송 안내."""
    if line.product.has_installation:
        return {
            "label": "배송 : [고정/착불] / 개별배송",
            "fee": 0,
            "cod_separate": True,
            "standard": False,
        }
    if line.product.price >= PROPORTIONAL_SHIPPING_THRESHOLD:
        fee = PROPORTIONAL_SHIPPING_FEE * line.quantity
        return {
            "label": f"배송 : KRW {PROPORTIONAL_SHIPPING_FEE:,}[비례] / 개별배송",
            "fee": fee,
            "cod_separate": False,
            "standard": False,
        }
    return {
        "label": "배송 : [개별배송] / 무료배송 조건 적용",
        "fee": 0,
        "cod_separate": False,
        "standard": True,
    }


def compute_cart_totals(lines: list[CartLine]) -> dict:
    """선택 상품 기준 합계."""
    original_total = sum(line.original_subtotal for line in lines)
    product_total = sum(line.subtotal for line in lines)
    discount_total = sum(line.discount_amount for line in lines)
    shipping_fee = 0
    cod_separate = False

    for line in lines:
        info = line_shipping_info(line)
        shipping_fee += info["fee"]
        if info["cod_separate"]:
            cod_separate = True

    standard_subtotal = sum(
        line.subtotal
        for line in lines
        if not line.product.has_installation
        and line.product.price < PROPORTIONAL_SHIPPING_THRESHOLD
    )
    if standard_subtotal > 0 and standard_subtotal < FREE_SHIPPING_THRESHOLD:
        shipping_fee += SHIPPING_FEE

    return {
        "original_total": original_total,
        "product_total": product_total,
        "discount_total": discount_total,
        "shipping_fee": shipping_fee,
        "grand_total": product_total + shipping_fee,
        "cod_separate": cod_separate,
    }

_GUEST_EMAILS = {"guest@shop.local"}
_GUEST_USERNAMES = {"guest_checkout", "guest"}


def _uses_db_cart() -> bool:
    return (
        current_user.is_authenticated
        and current_user.username not in _GUEST_USERNAMES
        and current_user.email not in _GUEST_EMAILS
    )


def _read_session_cart() -> dict[str, int]:
    raw = session.get("cart") or {}
    if not isinstance(raw, dict):
        return {}
    result: dict[str, int] = {}
    for key, value in raw.items():
        try:
            qty = int(value)
        except (TypeError, ValueError):
            continue
        if qty > 0:
            result[str(key)] = qty
    return result


def _write_session_cart(cart: dict[str, int]) -> None:
    session["cart"] = cart
    session.modified = True


def merge_session_cart_on_login(user_id: int) -> None:
    """로그인 시 세션 장바구니를 DB로 병합."""
    cart = _read_session_cart()
    if not cart:
        return

    for pid_str, qty in cart.items():
        product_id = int(pid_str)
        row = CartItem.query.filter_by(user_id=user_id, product_id=product_id).first()
        if row:
            row.quantity += qty
        else:
            db.session.add(CartItem(user_id=user_id, product_id=product_id, quantity=qty))
    db.session.commit()
    session.pop("cart", None)
    session.modified = True


def get_cart_lines() -> list[CartLine]:
    if _uses_db_cart():
        rows = (
            CartItem.query.filter_by(user_id=current_user.id)
            .join(Product)
            .filter(Product.is_active.is_(True))
            .all()
        )
        return [CartLine(product=row.product, quantity=row.quantity) for row in rows]

    cart = _read_session_cart()
    if not cart:
        return []

    product_ids = [int(pid) for pid in cart.keys()]
    products = Product.query.filter(
        Product.id.in_(product_ids), Product.is_active.is_(True)
    ).all()
    by_id = {product.id: product for product in products}

    lines: list[CartLine] = []
    for pid_str, qty in cart.items():
        product = by_id.get(int(pid_str))
        if product:
            lines.append(CartLine(product=product, quantity=qty))
    return lines


def get_cart_count() -> int:
    if _uses_db_cart():
        total = (
            db.session.query(db.func.coalesce(db.func.sum(CartItem.quantity), 0))
            .filter(CartItem.user_id == current_user.id)
            .scalar()
        )
        return int(total or 0)
    return sum(_read_session_cart().values())


def get_cart_summary() -> CartSummary:
    lines = get_cart_lines()
    totals = compute_cart_totals(lines)
    return CartSummary(
        lines=lines,
        item_count=get_cart_count(),
        product_total=totals["product_total"],
        original_total=totals["original_total"],
        discount_total=totals["discount_total"],
        shipping_fee=totals["shipping_fee"],
        grand_total=totals["grand_total"],
        cod_separate=totals["cod_separate"],
    )


def remove_product(*, product_id: int) -> int:
    if _uses_db_cart():
        row = CartItem.query.filter_by(
            user_id=current_user.id, product_id=product_id
        ).first()
        if not row:
            raise ValueError("장바구니에 없는 상품입니다.")
        db.session.delete(row)
        db.session.commit()
        return get_cart_count()

    cart = _read_session_cart()
    key = str(product_id)
    if key not in cart:
        raise ValueError("장바구니에 없는 상품입니다.")
    cart.pop(key, None)
    _write_session_cart(cart)
    return get_cart_count()


def set_product_quantity(*, product_id: int, quantity: int) -> int:
    if quantity < 1:
        raise ValueError("최소 주문수량은 1개 입니다.")
    if _uses_db_cart():
        row = CartItem.query.filter_by(
            user_id=current_user.id, product_id=product_id
        ).first()
        if not row:
            raise ValueError("장바구니에 없는 상품입니다.")
        row.quantity = quantity
        db.session.commit()
        return get_cart_count()

    cart = _read_session_cart()
    key = str(product_id)
    if key not in cart:
        raise ValueError("장바구니에 없는 상품입니다.")
    cart[key] = quantity
    _write_session_cart(cart)
    return get_cart_count()


def clear_cart_for_user(user_id: int, product_ids: list[int]) -> None:
    """특정 회원 장바구니에서 상품 제거 (결제 완료용)."""
    if not product_ids:
        return
    (
        CartItem.query.filter(
            CartItem.user_id == user_id,
            CartItem.product_id.in_(product_ids),
        ).delete(synchronize_session=False)
    )
    db.session.commit()


def clear_cart_products(product_ids: list[int]) -> None:
    if not product_ids:
        return

    if _uses_db_cart():
        clear_cart_for_user(current_user.id, product_ids)
        return

    cart = _read_session_cart()
    changed = False
    for product_id in product_ids:
        key = str(product_id)
        if key in cart:
            cart.pop(key)
            changed = True
    if changed:
        _write_session_cart(cart)


def add_product(*, product_id: int, quantity: int = 1) -> int:
    quantity = max(quantity, 1)
    product = Product.query.filter_by(id=product_id, is_active=True).first()
    if not product:
        raise ValueError("상품을 찾을 수 없습니다.")

    if _uses_db_cart():
        row = CartItem.query.filter_by(
            user_id=current_user.id, product_id=product_id
        ).first()
        if row:
            row.quantity += quantity
        else:
            db.session.add(
                CartItem(user_id=current_user.id, product_id=product_id, quantity=quantity)
            )
        db.session.commit()
        return get_cart_count()

    cart = _read_session_cart()
    key = str(product_id)
    cart[key] = cart.get(key, 0) + quantity
    _write_session_cart(cart)
    return get_cart_count()


def add_product_by_slug(slug: str, quantity: int = 1) -> int:
    product = Product.query.filter_by(slug=slug, is_active=True).first()
    if not product:
        raise ValueError("상품을 찾을 수 없습니다.")
    return add_product(product_id=product.id, quantity=quantity)


def serialize_cart() -> dict:
    summary = get_cart_summary()
    items = []
    for line in summary.lines:
        ship = line_shipping_info(line)
        items.append(
            {
                "id": line.product.id,
                "slug": line.product.slug,
                "name": line.product.name,
                "image_url": line.product.image_url or "",
                "price": line.product.price,
                "sale_price": line.product.sale_price,
                "discount_rate": line.product.discount_rate,
                "quantity": line.quantity,
                "subtotal": line.subtotal,
                "original_subtotal": line.original_subtotal,
                "discount_amount": line.discount_amount,
                "has_installation": line.product.has_installation,
                "shipping_label": ship["label"],
                "shipping_fee": ship["fee"],
                "cod_separate": ship["cod_separate"],
                "standard_shipping": ship["standard"],
            }
        )
    return {
        "count": summary.item_count,
        "product_total": summary.product_total,
        "original_total": summary.original_total,
        "discount_total": summary.discount_total,
        "shipping_fee": summary.shipping_fee,
        "grand_total": summary.grand_total,
        "cod_separate": summary.cod_separate,
        "items": items,
    }
