## Summary

카탈로그·검색·고객경험 — 상품/카테고리/검색, 마이페이지, 고객센터, 리뷰/위시리스트.

## 담당 파일

| routes | services | models |
|--------|----------|--------|
| `routes/main.py` | `category_service.py` | `models/category.py` |
| `routes/category.py` | `search_service.py` | `models/product.py` |
| `routes/search.py` | `search_filters.py` | |
| `routes/product.py` | `season_service.py`, `home_content.py` | |
| `routes/mypage.py` | `wishlist_service.py` | `models/wishlist.py` |
| `routes/support.py` | `review_service.py` | `models/review.py` |
| | `mypage_service.py` | `models/product_question.py` |
| | `inquiry_service.py` | `models/customer_inquiry.py` |
| | `help_center_service.py` | `models/notice.py` |

## 할 일

- [ ] CSV import 후 카테고리별 상품 노출 확인 (7카테고리)
- [ ] 검색 + 필터 (공간/스타일/색상/브랜드) 동작 검증
- [ ] 상품 상세 페이지 related products 로직 개선
- [ ] 리뷰 작성 조건: paid order 보유 시에만 (`review_service`)
- [ ] 1:1 문의 API (`/api/inquiries`) 파일 첨부 확인
- [ ] 위시리스트 API (`/api/wishlist/*`) 일관성

## 완료 기준

- [ ] 7개 카테고리 페이지 정상 렌더링
- [ ] 검색 "소파" → 결과 + 필터 sidebar 동작
- [ ] 구매 완료 계정으로 리뷰 작성 가능 확인
- [ ] PR: `backend/catalog-*` → `dvelop`

## Labels

`backend`, `catalog`, `mypage`

## 협업

- **팀장:** CSV import 후 데이터 검증
- **3번(Commerce):** 주문 상태 ↔ 리뷰 자격

## 데이터 확인 명령

```bash
python scripts/fetch_csv_data.py
python scripts/seed_db.py
python scripts/import_csv.py
python hspace_server.py
```
