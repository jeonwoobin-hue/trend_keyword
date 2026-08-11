# Deployment.md — 배포 가이드

> SRS §2.3 운영 환경: 클라우드 인프라(컨테이너 기반), Streamlit/Dash 애플리케이션 서버 + 별도 배치 서버.
> 인프라가 아직 확정되지 않아 템플릿 상태입니다. 실제 배포 환경이 정해지면 각 항목을 채웁니다.

## 배포 대상

- [ ] 프론트엔드(Streamlit 앱)
- [ ] 백엔드 API(FastAPI)
- [ ] 배치 워커(스케줄러)
- [x] DB(Supabase/PostgreSQL — 2026-08-11 확정, 2026-08-12 연결+검증 완료. 전용 프로젝트가 아니라
  블로그 프로젝트(`blog_dashboard_data`)를 공유하고 `trendfit` 스키마로 격리 — 무료 플랜 프로젝트
  한도로 인한 결정, [product/CHANGELOG.md](../product/CHANGELOG.md) 2026-08-12 참고. `trendfit.profiles`
  테이블까지 마이그레이션 적용 완료(`supabase/migrations/`), REST API 조회 검증 완료)
- [x] 인증(Supabase Auth) — 2026-08-12 `services/auth_service.py` 실제 연동 완료(로그인/회원가입/
  비밀번호 재설정/변경/회원 탈퇴). 회원 탈퇴(`delete_account()`)는 `service_role` Admin API로
  `auth.users` 계정을 실제로 삭제 — 테스트 계정 생성→삭제로 `auth.users`·`trendfit.profiles`
  cascade까지 실제 확인 완료.
  - [x] 이메일 발송 — Supabase 기본 메일러는 커스텀 SMTP 없이는 템플릿(본문) 편집 자체가
    막혀 있어(대시보드 배너로 확인), Resend를 커스텀 SMTP로 연결(`smtp.resend.com`, 포트 465,
    Sender `onboarding@resend.dev` — Resend에 도메인 미검증 상태라 이 발신자만 허용됨. 도메인
    검증하면 자체 도메인 발신자로 교체 가능). "Confirm signup"·"Reset Password" 템플릿을
    `{{ .Token }}`(6자리 코드) 방식으로 교체 완료
  - [x] 실제 이메일(`jeonwoobin@gmail.com`)로 회원가입 → 코드 수신 → `complete_signup()`까지
    전체 플로우 실제 검증 완료(2026-08-12). 그 과정에서 `maybe_single().execute()`가 행이 없을
    때 `None`을 그대로 반환하는 걸 놓쳐 최초 가입 시 크래시 나던 버그를 발견해 수정
  - [ ] Authentication → Sessions의 JWT 만료 시간이 NFR-SEC-003(24시간) 기준과 맞는지(기본값은
    보통 1시간)
  - [ ] 소셜 로그인(FR-AUTH-002, P2)은 아직 미착수(OAuth 프로바이더 설정 필요)
  - [ ] Resend 발신 도메인 검증(실제 서비스 오픈 전 — 지금은 `onboarding@resend.dev`로만 발송 가능)

## 환경변수/시크릿 체크리스트

시크릿 값 자체는 절대 이 문서나 git에 커밋하지 않습니다 — 실제 값은 각 환경(로컬 `.streamlit/secrets.toml`,
배포 환경의 시크릿 매니저)에만 보관합니다.

| 항목 | 용도 | 위치(로컬 기준) |
|---|---|---|
| 외부 트렌드/소셜/뉴스 API 키 | [docs/API_Design.md](../docs/API_Design.md) §8 연동 현황 참고 | `.streamlit/secrets.toml` |
| DB 접속 정보 | Supabase 등 | `.streamlit/secrets.toml` |
| JWT 시크릿 | 인증 토큰 서명 | 환경변수 |
| OAuth 클라이언트 ID/Secret | 구글/카카오 소셜 로그인 | 환경변수 |
| 이메일 발송(Resend SMTP) 자격증명 | 회원가입/비밀번호 재설정 인증 메일(Supabase Auth 내장 발송) | Supabase 대시보드(Authentication → Emails → SMTP Settings)에 직접 저장 — 앱 코드/secrets.toml에는 없음 |

## 배포 체크리스트 (초안)

1. [ ] `docs/Coding_Convention.md` 기준 테스트 통과 확인
2. [ ] 배치 워커 중복 실행 방지 락 동작 확인
3. [ ] 신규 외부 연동이 있다면 [docs/API_Design.md](../docs/API_Design.md) §8에 반영됐는지 확인
4. [ ] 배포 후 `product/CHANGELOG.md`에 기록
