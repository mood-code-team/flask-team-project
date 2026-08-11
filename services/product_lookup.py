"""Product lookup helpers for mood codes and gallery image filenames."""

from __future__ import annotations

from pathlib import Path

from models import Product


def normalize_image_filename(raw: str | None) -> str:
    name = (raw or "").strip()
    if not name:
        return ""
    return Path(name).name.lower()


def find_product_by_mood_code(mood_code: str | None) -> Product | None:
    code = (mood_code or "").strip().upper()
    if not code:
        return None
    return Product.query.filter_by(mood_code_number=code, is_active=True).first()


def find_product_by_image_name(image_name: str | None) -> Product | None:
    filename = normalize_image_filename(image_name)
    if not filename:
        return None

    stem = Path(filename).stem.replace(".", "-")
    return (
        Product.query.filter(
            Product.is_active.is_(True),
            Product.image_url.ilike(f"%{filename}"),
        ).first()
        or Product.query.filter(
            Product.is_active.is_(True),
            Product.image_url.ilike(f"%{stem}%"),
        ).first()
    )


def resolve_product_link(
    mood_code: str | None = None,
    image_name: str | None = None,
) -> dict | None:
    """Return product summary for gallery links."""

    product = None

    # 이미지명이 있으면 이미지명으로 먼저 정확하게 찾기
    if image_name:
        product = find_product_by_image_name(image_name)

    # 이미지명으로 찾지 못한 경우에만 mood code 사용
    if not product:
        product = find_product_by_mood_code(mood_code)

    if not product:
        return None

    return {
        "slug": product.slug,
        "name": product.name,
        "mood_code_number": product.mood_code_number,
        "url": f"/products/{product.slug}",
        "image_url": product.image_url,
    }