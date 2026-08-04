# Mood Code — 인테리어 셀렉션 쇼핑몰

Flask 풀스택 쇼핑몰 (SQLite / MySQL)

**팀 저장소:** https://github.com/mood-code-team/flask-team-project

---

## 빠른 시작

### 1. 코드 받기

```bash
git clone https://github.com/mood-code-team/flask-team-project.git
cd flask-team-project
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
python scripts/seed_db.py    # 최초 1회 (DB 없을 때)
python hspace_server.py
```

### 3. 브라우저

http://127.0.0.1:5000/

### 4. 테스트 계정

| 항목 | 값 |
|------|-----|
| 아이디 | `admin` |
| 이메일 | `admin@shop.local` |
| 비밀번호 | `admin1234` |

---

## GitHub에서 받았는데 실행이 안 될 때

GitHub에는 **코드만** 올라갑니다. 아래는 **각자 PC에서** 만들어야 합니다.

| 항목 | GitHub | 로컬 |
|------|--------|------|
| `database/shop.db` | ❌ | `seed_db.py` 실행 |
| `.env` | ❌ | `.env.example` 복사 (bat/run.sh가 자동 생성) |
| `venv/` | ❌ | 선택 사항 |

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
scripts/seed_db.py  DB 초기화 · 샘플 데이터
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
