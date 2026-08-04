# Notion ↔ Mood Code 연결 가이드

기획 페이지: [Mood Code (Notion)](https://app.notion.com/p/Mood-Code-3aa8246defc680c79bdfc0acb523a9ec)

---

## 1. 왜 연결이 안 될 때가 있나?

Cursor Notion Integration은 **공유된 페이지만** 읽을 수 있습니다.  
현재 연결된 워크스페이스: **김원일님의 워크스페이스**

Mood Code 페이지가 **다른 워크스페이스**에 있거나 **Integration 미공유**면 404가 납니다.

---

## 2. 연결 방법 (5분)

### ① Cursor에서 Notion MCP 연결
1. Cursor → Settings → MCP → **Notion** → Connect
2. Notion 계정 로그인·승인

### ② Mood Code 페이지에 Integration 추가
1. Notion에서 [Mood Code 페이지](https://app.notion.com/p/Mood-Code-3aa8246defc680c79bdfc0acb523a9ec) 열기
2. 우측 상단 **`···`** → **Connections** / **연결**
3. **Cursor** 또는 사용 중인 Integration 선택 → **Confirm**

### ③ Cursor Agent에게 다시 요청
> "Notion Mood Code 페이지 읽고 구현해줘"

---

## 3. 팀원 역할 (Notion 기준)

| Notion 섹션 | 담당 | 코드 반영 위치 |
|-------------|------|----------------|
| 상품목록 / 카테고리 | DB | `scripts/catalog_data.py` |
| 필터 기준 | DB + 프론트 | `products.filter_*`, `search_filters.py` |
| 홈 / 시즌 | 프론트 | `home_content.py`, `templates/index.html` |
| 장바구니·결제 | 백엔드 | `routes/cart.py`, `routes/payment.py` |
| 마이페이지 | 백엔드 | `routes/mypage.py` |

기획 변경 시:
1. Notion 수정
2. `catalog_data.py` 또는 Admin(추후) 반영
3. `python scripts/seed_db.py`

---

## 4. 현재 코드에 반영된 기획 (Notion 연결 전 기준)

- ✅ 사이드 메뉴 7대분류 + 소분류 (DB)
- ✅ 필터: 정렬 · 공간 · 스타일 · 컬러 · **브랜드**
- ✅ 헤더 계절 ↔ 스타일 필터 연동
- ✅ 상품 33개 + 필터 속성 DB 저장
- ✅ 상품 상세 스펙 (브랜드·공간·스타일·컬러)

---

## 5. Notion API 직접 사용 (선택)

```bash
set NOTION_TOKEN=secret_xxx
python scripts/notion_fetch_spec.py --save docs/NOTION_MOOD_CODE.md
```

Integration Token: https://www.notion.so/my-integrations
