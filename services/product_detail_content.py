"""
상품 상세 — HPIX 스타일 스펙·배송·교환/환불 콘텐츠.
"""

from __future__ import annotations

from models import Product
from services.cart_service import CartLine, line_shipping_info
from services.search_filters import get_option_label, get_product_specs


def get_product_summary_specs(product: Product) -> list[str]:
    """구매 박스 — 한 줄 스펙."""
    lines: list[str] = []
    if product.brand:
        lines.append(product.brand)
    if product.filter_space:
        lines.append(get_option_label("space", product.filter_space))
    if product.filter_style:
        lines.append(get_option_label("style", product.filter_style))
    if product.filter_color:
        lines.append(get_option_label("color", product.filter_color))
    if product.has_installation:
        lines.append("시공 서비스 포함")
    return lines


def get_product_detail_table(product: Product) -> list[dict[str, str]]:
    """PRODUCT DETAIL 테이블 행."""
    rows: list[dict[str, str]] = [
        {"label": "상품명", "value": product.name},
        {"label": "가격", "value": f"KRW {product.sale_price:,}"},
    ]
    if product.description:
        rows.append({"label": "상품간략설명", "value": product.description})
    for spec in get_product_specs(product):
        rows.append(spec)
    if product.category:
        rows.append({"label": "카테고리", "value": product.category.name})
    rows.append({"label": "재고", "value": f"{product.stock}개"})
    if product.has_installation:
        rows.append({"label": "시공", "value": "시공 서비스 포함"})
    return rows


def get_product_shipping_label(product: Product) -> str:
    """상품별 배송 요약."""
    info = line_shipping_info(CartLine(product=product, quantity=1))
    return info["label"].replace("배송 : ", "")


SHIPPING_CONTENT = """
<ul class="hpix-list">
  <li>택배 배송 · <strong>50,000원 미만 4,000원</strong> · 30만원 이상 무료배송</li>
  <li>50만원 이상 고가 가구는 비례 배송비가 적용될 수 있습니다.</li>
  <li>시공 포함 상품은 별도 배송·설치 일정 안내 후 진행됩니다.</li>
  <li>산간·도서 지역은 추가 배송비가 발생할 수 있습니다.</li>
  <li>재고·브랜드·제품에 따라 배송 기간이 상이합니다 (약 2~4주).</li>
  <li>배송·재고 문의는 상품 Q&amp;A 또는 고객센터로 남겨주세요.</li>
</ul>
<h4 class="hpix-subtitle">가구 배송</h4>
<ul class="hpix-list">
  <li>가구 품목에 따라 배송비·설치 방식이 다를 수 있습니다.</li>
  <li>2인 이상 설치가 필요한 경우 추가 비용이 발생할 수 있습니다.</li>
  <li>단순 변심 교환 시 왕복 배송비는 구매자 부담입니다.</li>
</ul>
"""

EXCHANGE_CONTENT = """
<h4 class="hpix-subtitle">교환/환불이 가능한 경우</h4>
<ul class="hpix-list">
  <li>상품 수령일로부터 7일 이내 교환/환불 접수</li>
  <li>상품 불량, 오배송, 배송 중 파손</li>
  <li>동일 상품 내 사이즈·색상 변경 1회 (왕복 배송비 구매자 부담)</li>
  <li>표시·광고 내용과 다른 경우 관련 법령에 따른 청약철회 가능</li>
</ul>
<h4 class="hpix-subtitle">교환/환불이 불가능한 경우</h4>
<ul class="hpix-list">
  <li>주문 제작·개별 생산 상품</li>
  <li>개봉 후 단순 변심 (수입 브랜드 등)</li>
  <li>태그 제거, 사용·훼손으로 가치가 감소한 경우</li>
  <li>설치 완료 후 가구류 환불/교환 불가</li>
</ul>
<p class="hpix-note">교환/환불 의사는 반드시 고객센터 또는 Q&amp;A를 통해 먼저 접수해 주세요.</p>
"""
