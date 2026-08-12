"""
적립금 적립·사용.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from extensions import db
from models import Order, PointLedger


class PointError(ValueError):
    """적립금 검증 실패."""


@dataclass
class PointHistoryEntry:
    date: datetime
    label: str
    amount: int
    balance: int


def get_point_balance(user_id: int) -> int:
    """현재 적립금 잔액."""
    total = (
        db.session.query(db.func.coalesce(db.func.sum(PointLedger.amount), 0))
        .filter(PointLedger.user_id == user_id)
        .scalar()
    )
    return int(total or 0)


def add_points(user_id: int, amount: int, label: str, *, order_id: int | None = None) -> None:
    """적립."""
    if amount <= 0:
        return
    db.session.add(
        PointLedger(
            user_id=user_id,
            amount=amount,
            label=label,
            order_id=order_id,
        )
    )
    db.session.commit()


def use_points(
    user_id: int,
    amount: int,
    label: str,
    *,
    order_id: int | None = None,
) -> None:
    """사용 (음수 기록)."""
    if amount <= 0:
        return
    balance = get_point_balance(user_id)
    if amount > balance:
        raise PointError(f"사용 가능한 적립금은 {balance:,}원입니다.")
    db.session.add(
        PointLedger(
            user_id=user_id,
            amount=-amount,
            label=label,
            order_id=order_id,
        )
    )
    db.session.commit()


def validate_point_usage(user_id: int, amount: int, *, max_usable: int) -> int:
    """주문 시 사용 가능 적립금 검증."""
    amount = max(amount, 0)
    balance = get_point_balance(user_id)
    usable = min(amount, balance, max_usable)
    if amount > balance:
        raise PointError(f"사용 가능한 적립금은 {balance:,}원입니다.")
    if amount > max_usable:
        raise PointError(f"이번 주문에는 최대 {max_usable:,}원까지 사용할 수 있습니다.")
    return usable


def get_point_history(user_id: int) -> list[PointHistoryEntry]:
    """적립금 내역 (최신순)."""
    rows = (
        PointLedger.query.filter_by(user_id=user_id)
        .order_by(PointLedger.created_at.asc())
        .all()
    )
    history: list[PointHistoryEntry] = []
    balance = 0
    for row in rows:
        balance += row.amount
        history.append(
            PointHistoryEntry(
                date=row.created_at,
                label=row.label,
                amount=row.amount,
                balance=balance,
            )
        )
    history.reverse()
    return history


def has_point_usage_for_order(order_id: int) -> bool:
    return (
        PointLedger.query.filter(
            PointLedger.order_id == order_id,
            PointLedger.amount < 0,
        ).first()
        is not None
    )


def reverse_order_points(*, user_id: int, order: Order) -> None:
    """주문 취소 시 적립금 복원·구매 적립 회수."""
    if order.point_used > 0 and has_point_usage_for_order(order.id):
        db.session.add(
            PointLedger(
                user_id=user_id,
                amount=order.point_used,
                label=f"주문 취소 환불 ({order.order_number})",
                order_id=order.id,
            )
        )

    earned = (
        PointLedger.query.filter(
            PointLedger.order_id == order.id,
            PointLedger.amount > 0,
            PointLedger.label.like("구매 적립%"),
        ).all()
    )
    for row in earned:
        db.session.add(
            PointLedger(
                user_id=user_id,
                amount=-row.amount,
                label=f"주문 취소 적립 회수 ({order.order_number})",
                order_id=order.id,
            )
        )
    db.session.commit()


def earn_purchase_points(*, user_id: int, order_id: int, product_total: int) -> int:
    """구매 적립 (실제 결제금액의 10%)."""
    amount = max(product_total // 10, 0)

    if amount <= 0:
        return 0

    add_points(
        user_id,
        amount,
        f"구매 적립 10% (주문 #{order_id})",
        order_id=order_id,
    )

    return amount