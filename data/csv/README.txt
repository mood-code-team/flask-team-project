Mood Code — CSV 데이터 폴더
============================

frontend 브랜치에는 CSV·이미지가 포함되어 있습니다 (git pull).

data-analysis 브랜치 최신본으로 갱신하려면:

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
