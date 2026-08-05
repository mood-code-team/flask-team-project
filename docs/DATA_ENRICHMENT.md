# Mood Code — 데이터 보강 가이드

> CSV + DB를 **실제 쇼핑몰(오늘의집/IKEA)** 처럼 보이게 만드는 방법

---

## 현재 vs 목표

| 항목 | import 직후 | enrich 후 |
|------|------------|-----------|
| 할인 상품 | ~7개 | ~150개 (30%) |
| filter_color/style | 대부분 비어 있음 | 이름·카테고리 기반 자동 추론 |
| is_popular/new/best | 거의 없음 | 카테고리별 분배 |
| 리뷰 | 0 | 데모 3건+ |
| Q&A | 0 | 15건 (답변 포함) |
| 이미지 | IKEA CDN URL | 로컬 캐시 가능 |

---

## 전체 파이프라인 (권장 순서)

```bash
# 1. CSV 가져오기 (data-analysis 브랜치)
python scripts/fetch_csv_data.py

# 2. 카테고리·관리자 시드
python scripts/seed_db.py

# 3. CSV → products 테이블
python scripts/import_csv.py

# 4. 할인·필터·뱃지 보강
python scripts/enrich_products.py

# 5. (선택) IKEA 이미지 로컬 저장 — 느림, 네트워크 필요
python scripts/download_product_images.py --limit 100

# 6. 리뷰·Q&A·샘플 주문
python scripts/seed_demo_content.py

# 7. 서버 실행
python hspace_server.py
```

한 번에:

```bash
python scripts/fetch_csv_data.py && python scripts/seed_db.py && python scripts/import_csv.py && python scripts/enrich_products.py && python scripts/seed_demo_content.py
```

---

## CSV에 추가하면 좋은 컬럼 (팀이 직접 채우기)

기존 CSV에 아래 컬럼을 **추가**하면 import 시 자동 반영됩니다.
(`scripts/import_csv.py` + `scripts/product_enrichment.py`)

| 컬럼 | 예시 | 설명 |
|------|------|------|
| `filter_space` | `living` | 거실/침실/주방/발코니 |
| `filter_style` | `spring` | Spring/Summer/Fall/Winter |
| `filter_color` | `beige` | white, beige, gray, wood, black... |
| `discount_rate` | `15` | 할인율 % (discount_price 자동 계산) |
| `discount_price` | `119000` | 할인가 직접 지정 |
| `is_popular` | `true` | 인기 뱃지 |
| `is_new` | `true` | NEW 뱃지 |
| `is_best` | `true` | BEST 뱃지 |
| `mood_code` | `winter` | filter_style 별칭 |

컬럼이 **비어 있으면** 스크립트가 상품명에서 색상 추론, 카테고리별 할인/뱃지 자동 부여.

### filter 값 목록 (코드와 동일)

- **space:** `living`, `bedroom`, `kitchen`, `balcony`
- **style:** `spring`, `summer`, `fall`, `winter`
- **color:** `white`, `beige`, `gray`, `wood`, `black`, `pink`, `yellow`, `green`, `blue`

---

## 팀 역할별 데이터 작업

| 담당 | 데이터 작업 |
|------|------------|
| **팀장** | CSV import 파이프라인, enrich 실행, MySQL 공유 DB |
| **4번 Catalog** | CSV 컬럼 보강 (filter, discount), 카테고리별 검증 |
| **data-analysis** | 스크래핑 CSV 품질, `mood_code`/필터 컬럼 추가 |
| **3번 Commerce** | 데모 주문/결제 테스트 데이터 |

---

## 데모 계정

| 용도 | 이메일 | 비밀번호 |
|------|--------|----------|
| 관리자 | admin@shop.local | admin1234 |
| 데모 회원 | demo1@shop.local | demo1234 |

---

## DB만 다시 만들 때

```bash
# SQLite DB 삭제 후 재시드
del database\shop.db          # Windows
python scripts/seed_db.py
python scripts/import_csv.py
python scripts/enrich_products.py
python scripts/seed_demo_content.py
```

---

## 앞으로 더 실제같이 만들려면

1. **CSV 컬럼 확장** — `discount_rate`, `filter_color`, `mood_code` 팀이 채우기
2. **이미지 로컬화** — `download_product_images.py` 전체 실행
3. **리뷰 늘리기** — `seed_demo_content.py` 템플릿 추가 또는 Admin API (Phase 2)
4. **MySQL 팀 공용** — `docs/TEAM_DATABASE.md` 참고
