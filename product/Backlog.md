# Backlog.md — P1 이후 백로그

> P1(1차 출시) 범위는 [../docs/Feature_Roadmap.md](../docs/Feature_Roadmap.md) 참고. 아래는
> [../TrendFit-ux-docs/srs.md](../TrendFit-ux-docs/srs.md)의 P2/P3 요구사항을 초기 백로그로 옮겨온 것입니다.
> 새 아이디어는 표 맨 아래에 추가합니다.

| ID | 항목 | 우선순위 | 관련 요구사항 | 상태 | 비고 |
|---|---|---|---|---|---|
| BL-001 | 소셜 로그인(구글/카카오) | P2 | FR-AUTH-002 | 완료 | `pages/0_로그인` — 구글/카카오 버튼 → `login_with_social_provider()`. 실제 OAuth 연동 전 단계로 버튼 클릭 시 즉시 로그인 처리하는 목업 |
| BL-002 | 비밀번호 재설정 | P2 | FR-AUTH-004 | 완료 | `pages/13_비밀번호_재설정` — 이메일 인증 → 새 비밀번호 설정 3단계 구현. 실제 이메일 발송 전 단계로 인증번호를 화면에 노출, 새 비밀번호는 저장하지 않음 |
| BL-003 | 연령/성별 관심도 가중치 보정 | P2 | FR-DASH-005 | 진행중 | `pages/4_키워드_상세` — 연령/성별 가중치 표시 UI와 `DemographicWeights` 모델은 구현됨. 다만 `dashboard_service._build_demographic_weights()`가 `rng.uniform()` 난수를 정규화해 보여주는 것뿐이라 실제 보정 산식은 여전히 미정 — [KPI_Definitions.md](../docs/KPI_Definitions.md) 참고 |
| BL-004 | 리포트 PDF 저장/링크 공유 | P2 | FR-REPORT-004 | 완료 | `pages/10_리포트_상세` — `build_report_pdf()`(fpdf 기반 실제 PDF 생성) 다운로드 버튼과 `build_share_link()` 공유 링크 표시 구현. 공유 링크는 백엔드 없는 표시용 목업 URL |
| BL-005 | 유사 관심사 비교 추천 키워드 | P2 | FR-REPORT-005 | 완료 | `pages/10_리포트_상세` — 고정 분야 매핑(`SIMILAR_CATEGORIES`) 기반 목 데이터. 산정 방법은 [KPI_Definitions.md](../docs/KPI_Definitions.md) 참고 |
| BL-006 | 알림 임계치 설정 | P2 | FR-ALERT-002 | 완료 | functional-spec의 FR-ALERT-001 등록 플로우(`pages/5_급상승_알림`)에 포함되어 함께 구현됨 |
| BL-007 | 알림 히스토리 조회 | P2 | FR-ALERT-004 | 완료 | `pages/11_알림함` — 실제 발송 배치 워커(FR-ALERT-003)가 없어 등록 키워드 기준 이력을 시뮬레이션 |
| BL-008 | 콘텐츠 플랫폼별 필터 | P2 | FR-CURATE-002 | 완료 | `pages/8_콘텐츠_큐레이션` — 플랫폼 멀티셀렉트가 `get_curated_contents()`에서 실제로 목록을 필터링 |
| BL-009 | 알림 수신 설정(이메일/인앱) | P2 | FR-PROFILE-003 | 완료 | `pages/14_계정_설정` — 알림 채널 멀티셀렉트 저장 구현. 세션 저장만 되고 실제 발송 백엔드 연동 전 단계 |
| BL-010 | 회원 탈퇴 | P2 | FR-PROFILE-004 | 완료 | `pages/14_계정_설정` — 확인 체크박스 + 탈퇴 버튼이 `clear_user_data()`를 호출해 사용자 개인 데이터를 초기화 |
| BL-011 | 관리자 — 사용자/키워드 관리 | P2 | FR-ADMIN-002 | 완료 | `pages/12_사용자_키워드_관리` — 사용자 목록/키워드 통계/신고 내역은 샘플 데이터, 블랙리스트는 실제 CRUD |
| BL-012 | 콘텐츠 스크랩 | P3 | FR-CURATE-003 | 완료 | `pages/8_콘텐츠_큐레이션`, `pages/6_마이페이지` — 스크랩 등록/해제(`add_scrap`/`remove_scrap`)와 마이페이지 목록 표시 구현. 세션 저장만, 영속화 없음 |

## 상태 값

`대기` → `계획중` → `진행중` → `완료` / `보류`
