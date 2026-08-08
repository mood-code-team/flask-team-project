"""
2차 데이터 정제 CSV → DB 반영 (육안 검수 결과 적용).

팀원이 CSV에 입력한 filter_color, filter_style/mood_code, mood_code_number,
is_popular/is_new/is_best 값을 쇼핑몰 DB에 반영합니다.
enrich_products.py 는 실행하지 않습니다 (수동 값 덮어쓰기 방지).

사용:
  python scripts/apply_reviewed_csv.py
  python scripts/apply_reviewed_csv.py --dry-run
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PYTHON = sys.executable


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply 2nd-pass reviewed CSV to DB")
    parser.add_argument("--dry-run", action="store_true", help="Preview without DB writes")
    parser.add_argument(
        "--csv-dir",
        type=Path,
        default=ROOT / "data" / "csv",
        help="CSV root directory",
    )
    args = parser.parse_args()

    cmd = [PYTHON, str(ROOT / "scripts" / "import_csv.py"), "--update", "--skip-seed"]
    if args.dry_run:
        cmd.append("--dry-run")
    if args.csv_dir:
        cmd.extend(["--csv-dir", str(args.csv_dir.resolve())])

    print("2차 검수 CSV → DB 반영")
    print("  - filter_color / filter_style(mood_code) / mood_code_number")
    print("  - is_popular / is_new / is_best")
    print("  ※ enrich_products.py 는 실행하지 않습니다.\n")

    result = subprocess.run(cmd, cwd=ROOT, check=False)
    if result.returncode != 0:
        sys.exit(result.returncode)

    if args.dry_run:
        print("\n[DRY-RUN] 미리보기만 완료. 실제 반영: python scripts/apply_reviewed_csv.py")
    else:
        print("\n[DONE] 반영 완료. 서버 재시작 후 상품 상세·필터·뱃지를 확인하세요.")


if __name__ == "__main__":
    main()
