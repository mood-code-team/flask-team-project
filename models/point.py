"""적립금 원장."""

from __future__ import annotations

from datetime import datetime

from extensions import db


class PointLedger(db.Model):
    """적립금 적립·사용 내역."""

    __tablename__ = "point_ledger"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    amount = db.Column(db.Integer, nullable=False)
    label = db.Column(db.String(120), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship("User", back_populates="point_entries")
    order = db.relationship("Order", back_populates="point_entries")
