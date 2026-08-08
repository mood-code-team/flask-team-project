Mood Code — 인테리어 셀렉션 쇼핑몰
====================================

Flask 풀스택 | SQLite

팀 저장소: https://github.com/mood-code-team/flask-team-project


■ 실행 (frontend 브랜치)

  git checkout frontend
  git pull team frontend

  Windows: 실행_서버.bat (더블클릭)
  Mac/Linux: ./run.sh

  또는 터미널:
    pip install -r requirements.txt
    python hspace_server.py

  http://127.0.0.1:5000/

  ※ frontend 브랜치에 CSV · DB · 상품 이미지 포함 (pull만 하면 실행 가능)
  ※ GitHub 상세 안내: README.md, docs/TEAM_SETUP.txt


■ 주요 기능

  - 메인·시즌·카테고리·검색·상품 상세
  - 회원가입·로그인·마이페이지
  - 장바구니·주문·토스페이먼츠 결제
  - 위시리스트·쿠폰·포인트·리뷰·Q&A
  - 고객센터(FAQ·1:1 문의)·공지사항


■ 구조

  app.py / routes/ / services/ / models/
  templates/ / static/ / database/shop.db


■ 데모 URL

  메인          http://127.0.0.1:5000/
  고객센터      http://127.0.0.1:5000/support/
  마이페이지    http://127.0.0.1:5000/mypage/


■ 테스트 계정 (일반)

  python scripts\seed_db.py
  admin / admin1234  (이메일: admin@shop.local)
  ※ 최신 seed는 관리자 계정 gygs1010 으로 통일됨


■ 관리자 페이지

  Windows: 실행_관리자.bat (더블클릭)
  URL: http://127.0.0.1:5000/admin

  아이디   : gygs1010
  이메일   : gygs1010@gmail.com
  비밀번호 : dnjsdlf@102360

  안 될 때:
    - Python PATH 확인
    - 5000 포트 다른 서버 종료 (Ctrl+C)
    - 로그인 실패 → docs/ADMIN_PAGE_GUIDE.txt 참고
    - 상세: README.md "5. 관리자 페이지" 섹션
