Mood Code — 인테리어 셀렉션 쇼핑몰
====================================

Flask 풀스택 | SQLite


■ 실행

  실행_서버.bat
  또는
    cd 프로젝트_2
    pip install -r requirements.txt
    python scripts\seed_db.py
    python hspace_server.py

  http://127.0.0.1:5000/


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


■ 테스트 계정

  python scripts\seed_db.py
  admin / admin1234
