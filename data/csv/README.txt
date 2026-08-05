Mood Code — CSV 데이터 폴더
============================

스크래핑 CSV는 Git main/dvelop 브랜치에 포함되지 않습니다.
data-analysis 브랜치에서 아래 명령으로 가져옵니다.

  python scripts/fetch_csv_data.py

가져온 뒤 DB import:

  python scripts/seed_db.py
  python scripts/import_csv.py

미리보기 (DB 변경 없음):

  python scripts/import_csv.py --dry-run

CSV 카테고리 (7종 × 약 100개 = 700개 상품):

  output_sofa/          → SOFA
  output_lighting/      → LIGHTING
  output_diffuser/      → DIFFUSER
  output_living_table/  → LIVING_TABLE (Side Table)
  output_dining_table/  → DINING_TABLE
  output_bed/           → BED
  output_balcony/       → BALCONY

담당: 백엔드 팀장 (import 파이프라인), 4번 (카탈로그 검증)
