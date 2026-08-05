# Mood Code 백엔드 팀 역할 분담

> **저장소:** https://github.com/mood-code-team/flask-team-project  
> **작업 브랜치:** `dvelop` (PR도 `dvelop`으로)  
> **팀:** 백엔드분류 4명 (팀장 1 + 멤버 3)

---

## 현재 프로젝트 상태

| 항목 | 상태 |
|------|------|
| Flask 백엔드 골격 | ✅ routes 9개, services 28개, models 12개 |
| DB 스키마 | ✅ `database/schema.sql` + SQLite 로컬 |
| 시드 데이터 | ✅ `scripts/catalog_data.py` + `seed_db.py` |
| CSV 실데이터 | ✅ `data-analysis` 브랜치 → `fetch_csv_data.py`로 가져오기 |
| CSV → DB | ✅ `scripts/import_csv.py` |
| 데이터 보강 | ✅ `scripts/enrich_products.py`, `seed_demo_content.py` |
| Admin API | ❌ Phase 2 (미구현) |

> **실제 쇼핑몰처럼 데이터 채우기:** [`docs/DATA_ENRICHMENT.md`](DATA_ENRICHMENT.md)

---

## 역할 분담

```
                    ┌─────────────────────────────┐
                    │  👑 1. 팀장 — 인프라·DB·통합  │
                    └──────────────┬──────────────┘
           ┌───────────────────────┼───────────────────────┐
           ▼                       ▼                       ▼
   ┌───────────────┐      ┌───────────────┐      ┌───────────────┐
   │ 2. 인증/회원   │      │ 3. 주문/결제   │      │ 4. 카탈로그/CX │
   └───────────────┘      └───────────────┘      └───────────────┘
```

### 👑 1. 팀장 — 인프라 · DB · 통합

| 담당 파일 | 할 일 |
|-----------|-------|
| `app.py`, `config.py`, `extensions.py` | 앱 설정, blueprint, 환경변수 |
| `database/schema.sql`, `services/db_schema.py` | 스키마 변경 관리 |
| `scripts/seed_db.py`, `import_csv.py`, `fetch_csv_data.py` | 데이터 파이프라인 |
| PR 리뷰 | 모든 `backend/*` → `dvelop` PR merge |

**1주차:** CSV import 검증, 팀 MySQL 연결 가이드, Issue 배분

---

### 2. 인증 · 회원 (Auth)

| routes | services | models |
|--------|----------|--------|
| `routes/auth.py` | `auth_service.py` | `models/user.py` |
| | `social_auth_service.py` | |
| | `guest_order_service.py` | |
| | `user_session_service.py` | |

**1주차:** 카카오/Apple OAuth 실연동, 비회원→회원 장바구니 merge, 비밀번호 찾기

**브랜치 예:** `backend/auth-kakao-oauth`

---

### 3. 주문 · 결제 · 혜택 (Commerce)

| routes | services | models |
|--------|----------|--------|
| `routes/cart.py` | `cart_service.py` | `models/cart.py` |
| `routes/payment.py` | `order_service.py` | `models/order.py` |
| | `toss_service.py` | `models/coupon.py` |
| | `coupon_service.py` | `models/point.py` |
| | `point_service.py`, `benefits_service.py` | |

**1주차:** Toss 결제 테스트, 주문 상태 전환, 쿠폰+포인트 규칙, 배송비

**브랜치 예:** `backend/order-payment-test`

---

### 4. 카탈로그 · 검색 · 고객경험 (Catalog + CX)

| routes | services | models |
|--------|----------|--------|
| `routes/main.py`, `category.py`, `search.py`, `product.py` | `category_service.py`, `search_service.py` | `category.py`, `product.py` |
| `routes/mypage.py`, `support.py` | `wishlist`, `review`, `mypage`, `inquiry` services | `wishlist`, `review`, `notice` 등 |

**1주차:** CSV import 후 필터/검색 검증, 리뷰 작성 조건, FAQ/문의 API

**브랜치 예:** `backend/catalog-filter-check`

---

## Git 워크플로

```bash
git clone https://github.com/mood-code-team/flask-team-project.git
cd flask-team-project
git checkout dvelop
git pull team dvelop

git checkout -b backend/작업명
# ... 수정 ...
git add .
git commit -m "feat: 작업 설명"
git push -u team backend/작업명
```

→ GitHub에서 **Pull Request: `backend/작업명` → `dvelop`**

---

## 스키마 변경 규칙 (팀장 승인 필수)

1. `models/*.py` 수정
2. `database/schema.sql` MySQL DDL 동기화
3. `services/db_schema.py` SQLite 패치 추가
4. PR에 변경 이유·마이그레이션 방법 기재

---

## 데이터 파이프라인

```
data-analysis 브랜치 (CSV)
        ↓ fetch_csv_data.py
data/csv/output_*/
        ↓ import_csv.py
database/shop.db (products 테이블)
        ↓
routes → services → templates
```

```bash
python scripts/fetch_csv_data.py
python scripts/seed_db.py
python scripts/import_csv.py
python hspace_server.py
```

---

## GitHub Issue

Issue 초안: `docs/github-issues/` 폴더 (4개)

GitHub에 등록:
```bash
gh auth login
gh issue create --title "..." --body-file docs/github-issues/issue-01-team-lead.md
```

또는 GitHub 웹 → Issues → New issue → 파일 내용 붙여넣기

---

## 팀 간 연결점 (충돌 주의)

| 경계 | 공유 지점 |
|------|-----------|
| Auth ↔ Commerce | 로그인 시 session cart → DB cart merge |
| Commerce ↔ CX | 주문 취소 → 쿠폰/포인트 복구, 리뷰 자격 |
| Catalog ↔ All | Product/Category 읽기 (cart, wishlist, search) |
| 스키마 | 모든 model 변경 → 팀장 리뷰 |
