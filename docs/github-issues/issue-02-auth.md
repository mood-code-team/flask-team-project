## Summary

인증·회원 도메인 — 로그인, 회원가입, 소셜 OAuth, 비회원 주문 조회.

## 담당 파일

| routes | services | models |
|--------|----------|--------|
| `routes/auth.py` | `auth_service.py` | `models/user.py` |
| | `social_auth_service.py` | |
| | `guest_order_service.py` | |
| | `user_session_service.py` | |
| | `register_options.py` | |

## 할 일

- [ ] 카카오 OAuth 실연동 (demo 모드 → `.env` 키 사용)
- [ ] Apple OAuth 실연동 또는 demo 정리
- [ ] 비회원 → 회원 가입 시 장바구니 merge (`cart_service` 협업)
- [ ] 아이디/비밀번호 찾기 edge case (존재하지 않는 이메일, 만료 토큰)
- [ ] 회원가입 유효성 검사 강화 (전화번호, 이메일 중복)

## 완료 기준

- [ ] 카카오 로그인 E2E 테스트 통과
- [ ] 비회원 장바구니 → 로그인 후 DB cart 유지 확인
- [ ] `/find-id`, `/find-password` 정상 동작
- [ ] PR: `backend/auth-*` → `dvelop`

## Labels

`backend`, `auth`

## 협업

- **3번(Commerce):** 로그인 시 cart merge (`cart_service.merge_session_cart_on_login`)
