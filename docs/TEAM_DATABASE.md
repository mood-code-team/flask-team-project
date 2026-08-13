# Mood Code — 팀 DB 협업 가이드

> Notion 기획: [Mood Code](https://app.notion.com/p/Mood-Code-3aa8246defc680c79bdfc0acb523a9ec)  
> (Notion Integration 연결 시 기획서와 코드를 1:1 대조할 수 있습니다)

---

## 1. 팀 역할 분담 (오늘의집형 쇼핑몰)

| 담당 | 하는 일 | 주요 파일 |
|------|---------|-----------|
| **DB / 백엔드** | 테이블·모델·시드·API | `models/`, `database/schema.sql`, `scripts/seed_db.py` |
| **프론트** | HTML/CSS/JS, 화면 | `templates/`, `static/` |
| **기획** | Notion 페이지, 필터·메뉴 정의 | Notion Mood Code |
| **공통** | Flask 실행, 설정 | `app.py`, `config.py`, `.env` |

### 데이터 흐름

```
Notion 기획 → catalog_data.py (또는 Admin) → seed_db.py → MySQL/SQLite
data-analysis → fetch_csv_data.py → import_csv.py ────────┘
                                                      ↓
              브라우저 ← templates ← routes ← services ← models/DB
```

### CSV 실데이터 import (스크래핑 700개 상품)

```bash
python scripts/fetch_csv_data.py   # data-analysis 브랜치에서 CSV 가져오기
python scripts/seed_db.py          # 카테고리·관리자 시드
python scripts/import_csv.py       # CSV → products 테이블
python scripts/import_csv.py --dry-run   # 미리보기
```

CSV 위치: `data/csv/output_*/` (gitignore 대상, 각자 로컬에서 fetch)

---

## 2. DB 종류별 사용법

### 개발 (혼자 / 로컬) — SQLite

```bash
cd flask-team-project
python scripts/seed_db.py
python hspace_server.py
```

- DB 파일: `database/shop.db`
- 별도 MySQL 설치 불필요

### 팀 공유 — MySQL (권장)

1. MySQL 설치 후 DB 생성:

```bash
mysql -u root -p < database/schema.sql
```

2. `.env` 설정:

```env
DATABASE_URL=mysql+pymysql://USER:PASSWORD@localhost:3306/moodcode_shop
```

3. 패키지 설치:

```bash
pip install pymysql
```

4. 시드 실행:

```bash
python scripts/seed_db.py
```

5. 연결 테스트:

```bash
python database/db.py
```

---

## 3. 페이지별 DB 매핑 (Notion ↔ 웹)

| 웹 페이지 | URL | DB 테이블 | 설명 |
|-----------|-----|-----------|------|
| **홈** | `/` | `products`, `categories` | 히어로·시즌은 `home_content.py`, 상품은 DB |
| **카테고리** | `/category/light` | `categories`, `products` | 대분류 + 하위 포함 조회 |
| **검색** | `/search?q=` | `products`, `categories` | 이름·설명 LIKE 검색 |
| **상품 상세** | `/product/<slug>` | `products`, `reviews`, `product_questions` | |
| **장바구니** | `/cart` | `cart` | 회원만 DB, 비회원은 세션 |
| **주문/결제** | `/payment` | `orders`, `order_items` | Toss 결제 연동 |
| **마이페이지** | `/mypage/*` | `orders`, `wishlist`, `coupons`, `points` | |
| **사이드 메뉴** | 햄버거 → 상품목록 | `categories` (parent/child) | `side_menu_service.py`가 DB에서 로드 |
| **필터** | 카테고리·검색 상단 | `products.filter_*` | 공간·스타일·컬러·제품정보 |

### 상품 필터 컬럼 (`products` 테이블)

| 컬럼 | 값 예시 | UI 필터 |
|------|---------|---------|
| `filter_space` | living, bedroom, kitchen, balcony | 공간 |
| `filter_style` | spring, summer, fall, winter | 스타일 (헤더 계절과 연동) |
| `filter_color` | white, beige, gray, … | 컬러 |
| `is_new` / `is_best` / `is_popular` | true/false | 제품정보 |
| `brand` | Mood Code | (추후 브랜드 필터) |

---

## 4. 카탈로그 구조 (사이드 메뉴 = DB)

대분류 `categories` (parent_id = NULL):

- Lighting, Sofa, Side Table, Diffuser, Dining Table, Bed, Balcony

소분류 `categories` (parent_id = 대분류 id):

- 예: Lighting → 테이블 램프, 플로어 램프, …

상품 `products.category_id` → **소분류**에 연결  
대분류 페이지(`/category/light`)는 **하위 상품 전체** 표시

시드 데이터: `scripts/catalog_data.py`  
수정 후:

```bash
python scripts/seed_db.py
```

---

## 5. 팀 Git 협업 규칙

1. **DB 스키마 변경** → `models/` 수정 + `database/schema.sql` 동기화 + 팀원에게 공지
2. **샘플 상품 추가** → `scripts/catalog_data.py`에 추가 → `seed_db.py` 실행
3. **`.env` / `shop.db`는 커밋 금지** (`.gitignore` 적용됨)
4. **충돌 방지**: DB 담당이 `models/` PR 먼저 머지 → 프론트가 pull 후 작업

---

## 6. 자주 쓰는 명령

```bash
# DB + 샘플 데이터 초기화
python scripts/seed_db.py

# 서버 실행
python hspace_server.py

# MySQL 연결 확인
python database/db.py
```

관리자 계정 (시드): `gygs1010` / `dnjsdlf@102360` (이메일: gygs1010@gmail.com)

---

## 7. 아직 Notion 전체 자동 반영은?

Notion 페이지가 Integration에 연결되면 기획 변경 → `catalog_data.py` / Admin UI로 옮기는 작업을 이어가면 됩니다.  
**오늘의집급 전체**(집들이, 셀러, 배송 추적, Admin CRUD)는 Phase 2로 분리하는 것을 권장합니다.

현재 Phase 1 완료 범위:

- [x] 카테고리 계층 + 사이드 메뉴 DB 연동
- [x] 상품 필터 DB 컬럼
- [x] 7대분류 · 30+ 샘플 상품 시드
- [x] MySQL schema.sql + 팀 가이드
- [x] 회원·장바구니·주문·결제·마이페이지 (기존)
