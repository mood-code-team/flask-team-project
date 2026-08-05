## Summary

백엔드 팀장 담당 — 앱 인프라, DB 스키마, CSV import 파이프라인, PR 리뷰 및 팀 통합.

## 담당 파일

- `app.py`, `config.py`, `extensions.py`, `routes/__init__.py`
- `database/schema.sql`, `services/db_schema.py`
- `scripts/seed_db.py`, `scripts/import_csv.py`, `scripts/fetch_csv_data.py`
- `docs/BACKEND_TEAM.md`, `docs/TEAM_DATABASE.md`

## 할 일

- [ ] CSV import 파이프라인 검증 (`fetch_csv_data.py` → `import_csv.py`)
- [ ] 팀 MySQL 공용 DB 연결 가이드 작성 및 `.env.example` 점검
- [ ] 스키마 변경 규칙 팀 공유 (model → schema.sql → db_schema.py)
- [ ] GitHub Issue 4개 등록 및 담당자 배정
- [ ] 모든 `backend/*` PR 리뷰 및 `dvelop` merge
- [ ] 팀원 onboarding: clone → seed → import → 실행 확인

## 완료 기준

- [ ] `python scripts/import_csv.py --dry-run` 성공
- [ ] import 후 상품 600개+ DB 반영 확인
- [ ] 팀원 3명 각자 로컬 실행 성공 (http://127.0.0.1:5000/)
- [ ] `docs/BACKEND_TEAM.md` 팀 공유 완료

## Labels

`backend`, `team-lead`, `infra`
