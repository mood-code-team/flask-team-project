# Mood Code — 인테리어 셀렉션 쇼핑몰

Flask 풀스택 쇼핑몰 (SQLite / MySQL)

**팀 저장소:** https://github.com/mood-code-team/flask-team-project

---

## 빠른 시작

### 1. 코드 받기

```bash
git clone https://github.com/mood-code-team/flask-team-project.git
cd flask-team-project
git checkout frontend
git pull team frontend
```

`team` remote가 없으면:

```bash
git remote add team https://github.com/mood-code-team/flask-team-project.git
git pull team frontend
```

### 2. 실행

**Windows** — `실행_서버.bat` 더블클릭

**Mac / Linux**

```bash
chmod +x run.sh
./run.sh
```

**터미널 (공통)**

```bash
pip install -r requirements.txt
python hspace_server.py
```

> `frontend` 브랜치에는 **CSV · DB · 상품 이미지**가 포함되어 있습니다.  
> `seed_db.py` / `fetch_csv_data.py` 없이도 바로 실행할 수 있습니다.

### 3. 브라우저

http://127.0.0.1:5000/

### 4. 테스트 계정

| 항목 | 값 |
|------|-----|
| 아이디 | `admin` |
| 이메일 | `admin@shop.local` |
| 비밀번호 | `admin1234` |

---

## GitHub `frontend` 브랜치에 포함된 것

| 항목 | 경로 | 설명 |
|------|------|------|
| CSV 데이터 | `data/csv/output_*/` | 스크래핑 CSV 7종 + 이미지 548개 |
| DB | `database/shop.db` | 상품 670개+ 반영된 SQLite |
| 상품 이미지 | `static/images/products/imported/` | import된 상품 썸네일 |
| 스크래핑 스크립트 | `data-analysis/*.py` | IKEA 크롤링 · CSV 정제 |
| import 수정 | `scripts/import_csv.py` | CSV → DB 변환 (external_id · DINING 매핑) |

## 각자 PC에서만 만드는 것

| 항목 | 방법 |
|------|------|
| `.env` | `.env.example` 복사 (`실행_서버.bat` / `run.sh`가 자동 생성) |
| `venv/` | 선택 사항 |

---

## 팀원 적용 방법 (프론트엔드 · CSV · DB)

### 처음 받는 사람

```bash
git clone https://github.com/mood-code-team/flask-team-project.git
cd flask-team-project
git checkout frontend
pip install -r requirements.txt
python hspace_server.py
```

Windows는 `실행_서버.bat` 더블클릭으로 동일합니다.

### 이미 clone 해둔 사람 (최신화)

```bash
git checkout frontend
git pull team frontend
python hspace_server.py
```

### 잘 됐는지 확인

| 확인 | URL / 명령 |
|------|------------|
| 홈 | http://127.0.0.1:5000/ |
| 검색 | http://127.0.0.1:5000/search?q=GLOSTAD |
| 카테고리 | http://127.0.0.1:5000/category/sofa |
| import 점검 | `python scripts/import_csv.py --dry-run` → `errors: 0` |

---

## CSV · DB 데이터 안내

### 포함된 CSV 카테고리 (7종 · 449행)

| 폴더 | 카테고리 |
|------|----------|
| `output_sofa/` | 소파 |
| `output_lighting/` | 조명 |
| `output_diffuser/` | 디퓨저 |
| `output_living_table/` | 거실 테이블 |
| `output_dining_table/` | 식탁 |
| `output_bed/` | 침대 |
| `output_balcony/` | 발코니 |

### DB · CSV를 새로 만들고 싶을 때

```bash
python scripts/fetch_csv_data.py   # data-analysis 브랜치 최신 CSV
python scripts/seed_db.py
python scripts/import_csv.py --dry-run
python scripts/import_csv.py
```

### 적용된 import 수정 (2026-08-06)

- CSV에 `external_id`가 없을 때 → `image_name`(예: `104.890.09.jpg`)으로 ID 생성
- `category_code`가 `DINING`인 행 → `table` 카테고리로 매핑

---

## 자주 막히는 경우

| 증상 | 해결 |
|------|------|
| `ModuleNotFoundError: flask` | `pip install -r requirements.txt` |
| 상품이 비어 있음 | `frontend` 브랜치인지 확인 후 `git pull team frontend` |
| import `errors: 35` | `import_csv.py` 최신 pull (`DINING` 매핑 포함) |
| import 전부 skip | `import_csv.py` 최신 pull (`resolve_external_id` 포함) |
| `5000 포트 사용 중` | 실행 중인 서버 `Ctrl+C` 종료 |
| Mac에서 `.bat` 안 됨 | `./run.sh` 사용 |

---

## GitHub에서 받았는데 실행이 안 될 때 (구버전 안내)

> **2026-08-06 이후:** `frontend` 브랜치에 CSV · DB · 이미지가 포함되어 pull만으로 실행 가능합니다.

구버전 README를 보고 있다면:

```bash
git checkout frontend
git pull team frontend
```

자세한 팀 안내: [`docs/TEAM_SETUP.txt`](docs/TEAM_SETUP.txt)

---

## 주요 기능

- 메인 · 시즌 · 카테고리 · 검색 · 상품 상세
- 회원가입 · 로그인 · 마이페이지
- 장바구니 · 주문 · 토스페이먼츠 결제
- 위시리스트 · 쿠폰 · 포인트 · 리뷰 · Q&A
- 고객센터(FAQ · 1:1 문의) · 공지사항

---

## 프로젝트 구조

```
app.py              Flask 앱
hspace_server.py    서버 실행
routes/             URL 라우트
services/           비즈니스 로직
models/             DB 모델
templates/          HTML
static/             CSS, JS, 이미지
data/csv/           스크래핑 CSV + 이미지
database/shop.db    상품 DB
data-analysis/      스크래핑 · CSV 정제 스크립트
scripts/            seed · import · fetch 스크립트
```

---

## 문서

| 파일 | 내용 |
|------|------|
| [docs/TEAM_SETUP.txt](docs/TEAM_SETUP.txt) | 팀원 clone · 실행 · 협업 |
| [docs/TEAM_DATABASE.md](docs/TEAM_DATABASE.md) | DB · 시드 · MySQL |
| [docs/TEAM_UI_CHANGES.txt](docs/TEAM_UI_CHANGES.txt) | UI 변경 이력 |
| [README.txt](README.txt) | 한글 요약 |

---

## 팀 협업

`main` 브랜치는 PR로만 merge됩니다.

```bash
git pull
git checkout -b feature/작업명
# ... 수정 ...
git commit -m "작업 설명"
git push -u origin feature/작업명
```

GitHub에서 Pull Request 생성 → merge
