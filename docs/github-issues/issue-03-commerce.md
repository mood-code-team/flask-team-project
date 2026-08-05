## Summary

주문·결제·혜택 도메인 — 장바구니, checkout, Toss Payments, 쿠폰/포인트.

## 담당 파일

| routes | services | models |
|--------|----------|--------|
| `routes/cart.py` | `cart_service.py` | `models/cart.py` |
| `routes/payment.py` | `order_service.py` | `models/order.py` |
| | `toss_service.py` | `models/coupon.py` |
| | `coupon_service.py` | `models/point.py` |
| | `point_service.py` | |
| | `benefits_service.py` | |

## 할 일

- [ ] Toss Payments sandbox 연동 테스트 (`TOSS_CLIENT_KEY`, `TOSS_SECRET_KEY`)
- [ ] 주문 상태 전환 정리: pending → paid → shipped → cancelled
- [ ] 쿠폰 + 포인트 동시 사용 규칙 문서화 및 코드 정리
- [ ] 배송비 계산 로직 (무료배송 기준, 지역별)
- [ ] 주문 취소 시 쿠폰/포인트 복구 (4번 CX와 협업)
- [ ] `/api/cart/*` REST API 응답 형식 통일

## 완료 기준

- [ ] 테스트 결제 1건 성공 (sandbox)
- [ ] 주문 생성 → 결제 confirm → paid 상태 확인
- [ ] 쿠폰 적용 주문 + 포인트 사용 주문 각각 테스트
- [ ] PR: `backend/commerce-*` → `dvelop`

## Labels

`backend`, `commerce`, `payment`

## 협업

- **2번(Auth):** guest cart / member cart merge
- **4번(CX):** 주문 취소, 리뷰 자격 (paid order 기준)
