"""
토스페이먼츠 결제 승인 API.
"""

from __future__ import annotations

import base64

import requests
from flask import current_app


class TossPaymentError(Exception):
    """토스 API 오류."""

    def __init__(self, message: str, *, code: str | None = None):
        super().__init__(message)
        self.code = code


def confirm_payment(*, payment_key: str, order_id: str, amount: int) -> dict:
    """결제 승인 — 실제 PG 승인 처리."""
    secret_key = current_app.config["TOSS_SECRET_KEY"]
    api_url = current_app.config["TOSS_API_URL"]

    token = base64.b64encode(f"{secret_key}:".encode()).decode()
    headers = {
        "Authorization": f"Basic {token}",
        "Content-Type": "application/json",
    }
    payload = {
        "paymentKey": payment_key,
        "orderId": order_id,
        "amount": amount,
    }

    try:
        response = requests.post(api_url, json=payload, headers=headers, timeout=15)
    except requests.RequestException as exc:
        raise TossPaymentError("결제 서버와 통신하지 못했습니다.") from exc

    data = response.json()
    if not response.ok:
        message = data.get("message", "결제 승인에 실패했습니다.")
        raise TossPaymentError(message, code=data.get("code"))

    return data
