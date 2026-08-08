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

### 4. 테스트 계정 (일반 쇼핑몰)

| 항목     | 값                 |
| -------- | ------------------ |
| 아이디   | `admin`            |
| 이메일   | `admin@shop.local` |
| 비밀번호 | `admin1234`        |

> `seed_db.py` 최신 버전에서는 관리자 계정이 아래 **운영 관리자 계정**으로 통일됩니다.
> 로그인이 안 되면 **5. 관리자 페이지** 계정을 사용하세요.

---

## 5. 관리자 페이지 (Admin)

쇼핑몰 **운영자용** 화면입니다. 상품·주문·공지·FAQ·1:1 문의·회원을 브라우저에서 관리합니다.

| 항목     | 값                          |
| -------- | --------------------------- |
| 주소     | http://127.0.0.1:5000/admin |
| 아이디   | `gygs1010`                  |
| 이메일   | `gygs1010@gmail.com`        |
| 비밀번호 | `dnjsdlf@102360`            |

> ⚠️ **팀 공유용 비밀번호**입니다. 외부에 공개하지 마세요.
> 로그인 후 상단 **로그아웃** · 작업 종료 시 서버 창 **Ctrl+C** 권장.

### Windows — `실행_관리자.bat` 실행 방법

1. 프로젝트 폴더(`flask-team-project` 또는 `프로젝트_2`)를 연다.
2. **`실행_관리자.bat`** 파일을 **더블클릭**한다.
3. 검은 창(터미널)이 뜨고 아래처럼 표시되면 성공:
   ```
   Mood Code Admin Server
   http://127.0.0.1:5000/admin
   ID: gygs1010
   ```
4. 브라우저가 자동으로 **`/admin/`** 을 연다. (안 열리면 주소를 직접 입력)
5. 로그인 화면에서 **아이디 `gygs1010`**, **비밀번호** 입력 → 관리자 대시보드 진입
6. 종료: 터미널 창에서 **Ctrl+C** → 창 닫기

**`실행_관리자.bat`이 자동으로 하는 일**

| 순서 | 동작                                                 |
| ---- | ---------------------------------------------------- |
| 1    | 5000 포트에 이미 켜진 서버가 있으면 종료 (충돌 방지) |
| 2    | Python · venv 확인/생성 (`scripts/ensure_venv.py`)   |
| 3    | DB 없으면 `seed_db.py` 실행                          |
| 4    | 관리자 계정(`gygs1010`) 시드                         |
| 5    | 서버 시작 + 브라우저를 `/admin/` 으로 연결           |

### Mac / Linux (관리자)

배치 파일(`.bat`)은 Windows 전용입니다.

```bash
pip install -r requirements.txt
python scripts/seed_db.py          # 최초 1회
python hspace_server.py
```

브라우저에서 http://127.0.0.1:5000/admin 접속 → 위 **관리자 계정**으로 로그인

### 관리자 메뉴 요약

| 메뉴      | URL                 | 용도                    |
| --------- | ------------------- | ----------------------- |
| 대시보드  | `/admin/dashboard`  | 매출·주문·문의 현황     |
| 주문 관리 | `/admin/orders`     | 주문 상태 변경          |
| 상품 관리 | `/admin/products`   | 상품 등록·수정·노출     |
| 카테고리  | `/admin/categories` | 소분류별 상품 개수 확인 |
| 1:1 문의  | `/admin/inquiries`  | 고객 문의 답변          |
| 공지사항  | `/admin/notices`    | 공지 작성               |
| FAQ       | `/admin/faqs`       | FAQ 작성                |
| 회원 관리 | `/admin/users`      | 회원 검색·비활성화      |

### `실행_관리자.bat`이 안 될 때

| 증상                                       | 원인                           | 해결                                                                                                             |
| ------------------------------------------ | ------------------------------ | ---------------------------------------------------------------------------------------------------------------- |
| **`Python not found`**                     | Python 미설치 또는 PATH 미등록 | [python.org](https://www.python.org/downloads/) 에서 Python 3.10+ 설치, **Add Python to PATH** 체크 후 PC 재시작 |
| **`venv setup failed`**                    | venv 생성 실패                 | 프로젝트 폴더에서 `py -3 scripts\ensure_venv.py` 수동 실행 → 오류 메시지 확인                                    |
| **`seed_db.py failed`**                    | DB·시드 오류                   | `venv\Scripts\python.exe scripts\seed_db.py` 수동 실행                                                           |
| **브라우저가 `/admin`이 아닌 다른 페이지** | 자동 열기 실패                 | 주소창에 `http://127.0.0.1:5000/admin` 직접 입력                                                                 |
| **로그인 후 403 Forbidden**                | 일반 회원 계정으로 로그인      | **관리자 계정**(`gygs1010`)으로 다시 로그인                                                                      |
| **아이디/비밀번호 오류**                   | 예전 시드 계정 사용            | 터미널에서 아래 **관리자 계정 재설정** 실행                                                                      |
| **`5000 포트 사용 중`**                    | 다른 서버가 5000 사용          | `실행_서버.bat`·다른 Flask 창 **Ctrl+C** 종료 후 다시 실행 (bat이 자동 종료 시도)                                |
| **창이 바로 닫힘**                         | 시작 직후 오류                 | **탐색기 주소창에 `cmd` 입력 후 Enter** → `cd 프로젝트경로` → `실행_관리자.bat` 입력해 오류 문구 확인            |

**관리자 계정 재설정 (로그인 안 될 때)**

```bash
venv\Scripts\python.exe -c "from app import create_app; from scripts.seed_db import seed_admin; app=create_app(); ctx=app.app_context(); ctx.push(); seed_admin(); ctx.pop(); print('OK')"
```

이후 **아이디 `gygs1010` / 비밀번호 `dnjsdlf@102360`** 으로 다시 로그인.

**터미널에서 직접 실행 (bat 대신)**

```bash
cd flask-team-project
venv\Scripts\python.exe scripts\seed_db.py
set MOODCODE_OPEN_URL=/admin/
venv\Scripts\python.exe hspace_server.py
```

---

## GitHub `frontend` 브랜치에 포함된 것

| 항목              | 경로                               | 설명                                      |
| ----------------- | ---------------------------------- | ----------------------------------------- |
| CSV 데이터        | `data/csv/output_*/`               | 스크래핑 CSV 7종 + 이미지 548개           |
| DB                | `database/shop.db`                 | 상품 670개+ 반영된 SQLite                 |
| 상품 이미지       | `static/images/products/imported/` | import된 상품 썸네일                      |
| 스크래핑 스크립트 | `data-analysis/*.py`               | IKEA 크롤링 · CSV 정제                    |
| import 수정       | `scripts/import_csv.py`            | CSV → DB 변환 (external_id · DINING 매핑) |

## 각자 PC에서만 만드는 것

| 항목    | 방법                                                         |
| ------- | ------------------------------------------------------------ |
| `.env`  | `.env.example` 복사 (`실행_서버.bat` / `run.sh`가 자동 생성) |
| `venv/` | 선택 사항                                                    |

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

| 확인        | URL / 명령                                             |
| ----------- | ------------------------------------------------------ |
| 홈          | http://127.0.0.1:5000/                                 |
| 검색        | http://127.0.0.1:5000/search?q=GLOSTAD                 |
| 카테고리    | http://127.0.0.1:5000/category/sofa                    |
| import 점검 | `python scripts/import_csv.py --dry-run` → `errors: 0` |

---

## CSV · DB 데이터 안내

### 포함된 CSV 카테고리 (7종 · 449행)

| 폴더                   | 카테고리    |
| ---------------------- | ----------- |
| `output_sofa/`         | 소파        |
| `output_lighting/`     | 조명        |
| `output_diffuser/`     | 디퓨저      |
| `output_living_table/` | 거실 테이블 |
| `output_dining_table/` | 식탁        |
| `output_bed/`          | 침대        |
| `output_balcony/`      | 발코니      |

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

| 증상                         | 해결                                                    |
| ---------------------------- | ------------------------------------------------------- |
| `ModuleNotFoundError: flask` | `pip install -r requirements.txt`                       |
| 상품이 비어 있음             | `frontend` 브랜치인지 확인 후 `git pull team frontend`  |
| import `errors: 35`          | `import_csv.py` 최신 pull (`DINING` 매핑 포함)          |
| import 전부 skip             | `import_csv.py` 최신 pull (`resolve_external_id` 포함)  |
| `5000 포트 사용 중`          | 실행 중인 서버 `Ctrl+C` 종료                            |
| Mac에서 `.bat` 안 됨         | `./run.sh` 사용                                         |
| 관리자 로그인 실패           | README **5. 관리자 페이지** → 계정 재설정 명령 실행     |
| `/admin` 403                 | `gygs1010` 관리자 계정으로 로그인 (일반 회원 계정 불가) |

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

## 인테리어 갤러리

| 페이지                      | URL                                                         |
| --------------------------- | ----------------------------------------------------------- |
| 메인 하단 링크              | http://127.0.0.1:5000/ (스크롤 ↓ GALLERY PREVIEW)           |
| 무드 갤러리                 | http://127.0.0.1:5000/gallery                               |
| BLOOM / CLEAR / CALM / CHIC | `/gallery?category=fresh` · `vibrant` · `cozy` · `chic_key` |
| 공간별                      | http://127.0.0.1:5000/spaces                                |

상세: [`docs/GALLERY_TEAM_SEONYEONG.txt`](docs/GALLERY_TEAM_SEONYEONG.txt)

---

## 주요 기능

- 메인 · 시즌 · 카테고리 · 검색 · 상품 상세
- 회원가입 · 로그인 · 마이페이지
- 장바구니 · 주문 · 토스페이먼츠 결제
- 위시리스트 · 쿠폰 · 포인트 · 리뷰 · Q&A
- 고객센터(FAQ · 1:1 문의) · 공지사항
- **관리자 백오피스** (`/admin`) — 상품·주문·공지·문의·회원 관리

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

| 파일                                                   | 내용                                  |
| ------------------------------------------------------ | ------------------------------------- |
| [docs/TEAM_SETUP.txt](docs/TEAM_SETUP.txt)             | 팀원 clone · 실행 · 협업              |
| [docs/TEAM_DATABASE.md](docs/TEAM_DATABASE.md)         | DB · 시드 · MySQL                     |
| [docs/TEAM_UI_CHANGES.txt](docs/TEAM_UI_CHANGES.txt)   | UI 변경 이력                          |
| [docs/ADMIN_PAGE_GUIDE.txt](docs/ADMIN_PAGE_GUIDE.txt) | 관리자 페이지 · 실행\_관리자.bat 안내 |
| [README.txt](README.txt)                               | 한글 요약                             |

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
