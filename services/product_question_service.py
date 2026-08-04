"""
상품 Q&A.
"""

from __future__ import annotations

from extensions import db
from models import Product, ProductQuestion


class QuestionError(ValueError):
    """Q&A 검증 실패."""


def get_product_questions(product_id: int) -> list[ProductQuestion]:
    return (
        ProductQuestion.query.filter_by(product_id=product_id, is_public=True)
        .order_by(ProductQuestion.created_at.desc())
        .all()
    )


def get_user_questions(user_id: int) -> list[ProductQuestion]:
    return (
        ProductQuestion.query.filter_by(user_id=user_id)
        .order_by(ProductQuestion.created_at.desc())
        .all()
    )


def create_question(*, user_id: int, product_id: int, question: str) -> ProductQuestion:
    question = question.strip()
    if len(question) < 5:
        raise QuestionError("문의 내용을 5자 이상 입력해 주세요.")

    product = Product.query.filter_by(id=product_id, is_active=True).first()
    if not product:
        raise QuestionError("상품을 찾을 수 없습니다.")

    row = ProductQuestion(
        user_id=user_id,
        product_id=product_id,
        question=question,
    )
    db.session.add(row)
    db.session.commit()
    return row
