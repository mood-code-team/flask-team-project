"""
고객센터 FAQ — 카테고리·검색·DB 시드.
"""

from __future__ import annotations

from dataclasses import dataclass

from extensions import db
from models import FAQ

HELP_CATEGORIES: list[dict[str, str]] = [
    {"slug": "all", "label": "전체"},
    {"slug": "order", "label": "주문/결제"},
    {"slug": "shipping", "label": "배송"},
    {"slug": "return", "label": "취소/교환/반품"},
    {"slug": "receipt", "label": "영수증/증빙"},
    {"slug": "member", "label": "회원/로그인"},
    {"slug": "benefits", "label": "적립금/쿠폰/멤버십"},
    {"slug": "service", "label": "서비스 이용"},
]

DEFAULT_FAQS: list[tuple[str, str, str, int]] = [
    # 주문/결제
    ("order", "어떤 결제 수단을 이용할 수 있나요?", "신용·체크카드, 계좌이체, 무통장입금, 토스페이 등을 이용할 수 있습니다. 결제 단계에서 사용 가능한 수단을 확인해 주세요.", 1),
    ("order", "비회원으로 주문할 수 있나요?", "회원 가입 없이도 주문할 수 있습니다. 다만 주문 조회·쿠폰·적립금 혜택은 회원에게만 제공됩니다.", 2),
    ("order", "결제 후 결제 방법을 변경할 수 있나요?", "결제 완료 후에는 결제 수단 변경이 어렵습니다. 주문 취소 후 재주문하시거나 고객센터로 문의해 주세요.", 3),
    ("order", "주문 후 배송지나 수령인 정보를 변경할 수 있나요?", "상품 준비 전(결제 완료·배송 준비 중)까지 마이페이지 > 주문내역에서 변경 가능합니다. 출고 후에는 변경이 제한됩니다.", 4),
    # 배송
    ("shipping", "배송 유형은 어떤 것이 있나요?", "일반 택배 배송, 대형 가구 설치 배송(착불/비례 배송비), 주문 제작 상품 별도 배송 등 상품별로 안내됩니다.", 1),
    ("shipping", "배송비는 얼마인가요?", "30만 원 미만 주문 시 기본 배송비 4,000원이 부과됩니다. 50만 원 이상 대형 상품은 별도 배송비 정책이 적용됩니다.", 2),
    ("shipping", "배송은 얼마나 걸리나요?", "일반 상품은 결제 완료 후 2~5영업일, 주문 제작 상품은 2~4주 소요될 수 있습니다.", 3),
    ("shipping", "배송완료로 표시되는데 상품을 받지 못했습니다.", "운송장 배송완료 후 1~2일 내 수령되지 않으면 고객센터로 문의해 주세요. 택배사 확인 후 재발송 또는 환불을 안내드립니다.", 4),
    # 취소/교환/반품
    ("return", "배송 상태별로 취소 가능 여부가 다른가요?", "결제 완료·상품 준비 중에는 마이페이지에서 직접 취소 가능합니다. 출고 후에는 반품 절차로 진행됩니다.", 1),
    ("return", "교환·반품 신청 기간이 정해져 있나요?", "상품 수령 후 7일 이내, 미개봉·미사용 상태에서 신청 가능합니다. 설치·시공 상품은 별도 정책이 적용됩니다.", 2),
    ("return", "교환·반품은 어떻게 신청하나요?", "마이페이지 > 주문내역 > 해당 주문에서 취소/반품 신청 또는 고객센터 문의하기를 이용해 주세요.", 3),
    ("return", "환불은 언제 받을 수 있나요?", "반품 상품 검수 완료 후 3~7영업일 내 결제 수단으로 환불됩니다. 카드사에 따라 승인 취소까지 추가 시간이 소요될 수 있습니다.", 4),
    # 영수증/증빙
    ("receipt", "세금계산서를 받을 수 있나요?", "사업자 회원 또는 주문 시 사업자 정보 입력 후 고객센터로 요청하시면 발행해 드립니다.", 1),
    ("receipt", "현금영수증을 발급받으려면 어떻게 해야 하나요?", "무통장입금·계좌이체 결제 시 주문 단계에서 현금영수증 정보를 입력하거나, 결제 후 고객센터로 요청해 주세요.", 2),
    ("receipt", "결제 영수증은 어디서 확인할 수 있나요?", "마이페이지 > 주문내역 > 주문 상세에서 결제 영수증을 확인·출력할 수 있습니다.", 3),
    # 회원/로그인
    ("member", "회원가입은 어떻게 하나요?", "상단 메뉴의 회원가입에서 이메일·비밀번호·기본 정보를 입력하면 가입할 수 있습니다.", 1),
    ("member", "비밀번호를 잊어버렸어요.", "로그인 화면의 '비밀번호 찾기'를 이용하거나, 가입 이메일로 재설정 링크를 요청해 주세요.", 2),
    ("member", "로그인이 되지 않습니다.", "아이디·비밀번호 확인 후에도 문제가 있으면 브라우저 쿠키를 삭제하거나 다른 브라우저로 시도해 주세요.", 3),
    # 적립금/쿠폰/멤버십
    ("benefits", "포인트는 어떻게 적립되나요?", "회원가입·구매·리뷰 작성·이벤트 참여 시 포인트가 적립됩니다. 적립 내역은 마이페이지 > 포인트에서 확인할 수 있습니다.", 1),
    ("benefits", "포인트는 언제 사용할 수 있나요?", "적립 즉시 사용 가능하며, 주문 결제 단계에서 사용할 포인트를 입력해 주세요.", 2),
    ("benefits", "환불 시 사용한 포인트는 어떻게 되나요?", "주문 취소·반품 완료 시 사용한 포인트는 자동으로 복원됩니다.", 3),
    ("benefits", "쿠폰은 어디서 확인하나요?", "마이페이지 > 쿠폰함에서 보유 쿠폰과 사용 조건·유효기간을 확인할 수 있습니다.", 4),
    # 서비스 이용
    ("service", "PC에서도 이용할 수 있나요?", "네, Mood Code는 PC·모바일 웹 브라우저에서 모두 이용할 수 있습니다.", 1),
    ("service", "사이트가 정상 작동하지 않습니다.", "브라우저 캐시 삭제, 새로고침 후에도 동일하면 사용 중인 기기·브라우저 정보와 함께 고객센터로 문의해 주세요.", 2),
    ("service", "위시리스트는 어떻게 사용하나요?", "상품 카드 또는 상세 페이지의 하트 아이콘을 눌러 저장할 수 있으며, 마이페이지 > 위시리스트에서 확인합니다.", 3),
]

CATEGORY_LABELS = {item["slug"]: item["label"] for item in HELP_CATEGORIES if item["slug"] != "all"}


@dataclass
class FAQGroup:
    slug: str
    label: str
    items: list[FAQ]


def ensure_help_center_faqs() -> None:
    """고객센터 기본 FAQ 시드."""
    valid_slugs = set(CATEGORY_LABELS.keys())
    existing_slugs = {f.category for f in FAQ.query.all()}

    if valid_slugs <= existing_slugs and FAQ.query.filter_by(is_active=True).count() >= len(DEFAULT_FAQS):
        return

    if existing_slugs and not (existing_slugs & valid_slugs):
        FAQ.query.delete()
        db.session.commit()

    existing_questions = {f.question for f in FAQ.query.all()}
    for slug, question, answer, order in DEFAULT_FAQS:
        if question in existing_questions:
            continue
        db.session.add(
            FAQ(
                category=slug,
                question=question,
                answer=answer,
                sort_order=order,
            )
        )
    db.session.commit()


def get_category_label(slug: str) -> str:
    return CATEGORY_LABELS.get(slug, slug)


def get_faq_groups(active_slug: str = "all") -> list[FAQGroup]:
    """카테고리별 FAQ 그룹."""
    query = FAQ.query.filter_by(is_active=True).order_by(FAQ.category, FAQ.sort_order, FAQ.id)
    if active_slug and active_slug != "all":
        query = query.filter_by(category=active_slug)

    grouped: dict[str, list[FAQ]] = {}
    for item in query.all():
        grouped.setdefault(item.category, []).append(item)

    order = [c["slug"] for c in HELP_CATEGORIES if c["slug"] != "all"]
    result: list[FAQGroup] = []
    for slug in order:
        items = grouped.get(slug, [])
        if items:
            result.append(FAQGroup(slug=slug, label=get_category_label(slug), items=items))
    return result


def get_faq_count(active_slug: str = "all") -> int:
    query = FAQ.query.filter_by(is_active=True)
    if active_slug and active_slug != "all":
        query = query.filter_by(category=active_slug)
    return query.count()


def get_faq_by_id(faq_id: int) -> FAQ | None:
    return FAQ.query.filter_by(id=faq_id, is_active=True).first()
