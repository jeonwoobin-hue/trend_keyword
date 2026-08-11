# TrendFit 정보구조도 (IA)

## 메타
| 항목 | 내용 |
|------|------|
| 서비스명 | TrendFit (나에게 맞는 트렌드 및 관심사 인사이트 서비스) |
| 플랫폼 | 웹 (Streamlit/Dash 기반 반응형 웹) |
| 대상 사용자 | 마케팅·콘텐츠 제작·소비 등 목적으로 관심 분야의 최신 트렌드와 급상승 키워드를 파악하려는 일반 사용자 |
| 작성일 | 2026-08-08 |
| 문서 버전 | v1.3 |

> **v1.1 변경 이력(2026-08-12)**: ONBOARD-001의 관심 분야 예시를 네이버 주제 필터 기준 20개
> 확정 목록으로 갱신. 상세는 [srs.md](srs.md) v1.1 변경 이력 참고.

> **v1.2 변경 이력(2026-08-11)**: 사이드바 15개 화면 평면 나열을 상단 호버 드롭다운 메뉴(홈/
> 트렌드/인사이트/마이페이지/관리자)로 개편한 것을 반영. 화면 목록·콘텐츠 흐름 계층도는 그대로
> 유지하고, 실제 클릭 경로를 보여주는 "상단 메뉴 구조" 절과 다이어그램을 새로 추가. 비밀번호
> 재설정을 COM-002의 부가 기능에서 별도 화면(COM-004)으로 승격. 관리자 화면(ADMIN-001/002)은
> 이제 로그인 여부가 아니라 관리자 역할(`AuthUser.role`) 세션에서만 메뉴에 노출됨. 상세는
> [Feature_Roadmap.md](../docs/Feature_Roadmap.md) 참고.

> **v1.3 변경 이력(2026-08-11)**: `CURATE-002`(콘텐츠 상세)를 구현하고 "미착수" 각주를 제거.
> `pages/15_📄_콘텐츠_상세.py`, `CURATE-001` 카드의 "상세보기"에서 진입. 상단 메뉴 "인사이트"
> 그룹에도 추가.

## 화면 목록

| 화면ID | 화면명 | Depth | 상위화면 | 주요 콘텐츠 | 주요 기능 | 데이터 소스 | 접근권한 |
|--------|--------|-------|----------|-------------|-----------|-------------|----------|
| COM-001 | 랜딩 | 1 | Root | 서비스 소개, 핵심 가치 문구, 대표 트렌드 미리보기 | 시작하기, 로그인 이동 | Static | G |
| COM-002 | 로그인 | 1 | COM-001 | 이메일/비밀번호 입력폼, 소셜 로그인 버튼 | 로그인, 회원가입 이동, 비밀번호 찾기 | API | G |
| COM-003 | 회원가입 | 1 | COM-002 | 가입 폼, 약관 동의 | 이메일 인증, 가입 완료 | API | G |
| COM-004 | 비밀번호 재설정 | 2 | COM-002 | 이메일 인증 단계, 새 비밀번호 입력 폼 | 인증번호 발급/확인, 새 비밀번호 설정 | API | G |
| ONBOARD-001 | 관심사·조건 설정 | 1 | COM-003 | 관심 분야(여행/패션/뷰티/푸드/IT테크 등 20개), 목적, 연령대·성별, 선호 플랫폼, 탐색 기간 | 관심 분야 선택, 목적 선택, 프로필 입력, 조건 저장 | API | U |
| ONBOARD-002 | 맞춤 설정 완료 | 2 | ONBOARD-001 | 선택 조건 요약, 추천 키워드 미리보기 | 설정 확인, 대시보드 이동 | API | U |
| DASH-001 | 트렌드 대시보드(홈) | 1 | Root(TAB1) | 분야별 핫 키워드 목록, 언급량 그래프, Spike Score 랭킹 | 분야 필터, 기간 필터(24시간/1주/1개월), 키워드 상세 이동 | API | G/U |
| DASH-002 | 키워드 상세 | 2 | DASH-001 | 검색량 추이 그래프, 긍·부정 감성 비율, 연관 키워드, 연령·성별 관심도 가중치 | 기간 변경, 급상승 알림 등록, 관련 콘텐츠 이동 | API | U |
| REPORT-001 | 인사이트 리포트 목록 | 1 | Root(TAB2) | 조건별 리포트 카드(생성일, 분야, 요약) | 리포트 생성 요청, 리포트 필터 | API | U |
| REPORT-002 | 리포트 상세 | 2 | REPORT-001 | 최신 이슈 요약, Word Cloud, 키워드 연관성 Network Graph | 리포트 저장, 공유, PDF 다운로드 | API | U |
| ALERT-001 | 급상승 알림 설정 | 1 | Root(TAB3) | 등록된 관심 키워드 목록, Spike 임계치 설정 | 키워드 등록/삭제, 수신 방식 설정(이메일/인앱) | API | U |
| ALERT-002 | 알림함 | 2 | ALERT-001 | 알림 히스토리(키워드, 폭증 지수, 시각) | 알림 읽음 처리, 알림 상세(키워드 상세) 이동 | API/Local | U |
| CURATE-001 | 콘텐츠 큐레이션 피드 | 1 | Root(TAB4) | 인기 게시물·뉴스 카드(썸네일, 제목, 출처 플랫폼) | 플랫폼 필터, 무한 스크롤 | API | U |
| CURATE-002 | 콘텐츠 상세 | 2 | CURATE-001 | 콘텐츠 미리보기, 원문 링크, 연관 키워드 태그 | 원문 이동, 스크랩 | API | U |
| MY-001 | 마이페이지 | 1 | Root(TAB5) | 프로필 정보, 등록 관심 키워드, 스크랩 목록 | 관심 분야 수정, 스크랩 관리, 설정 이동 | API | U |
| MY-002 | 계정 설정 | 2 | MY-001 | 계정 정보, 알림 수신 설정, 기본 탐색 기간 | 정보 수정, 비밀번호 변경, 회원 탈퇴 | API | U |
| ADMIN-001 | 관리자 대시보드 | 1 | Root(Admin) | 데이터 수집 현황(API 호출량, 오류율), 사용자·키워드 통계 | 데이터 소스 상태 모니터링, 배치 작업 확인 | API | A |
| ADMIN-002 | 사용자·키워드 관리 | 2 | ADMIN-001 | 사용자 목록, 등록 키워드 통계, 신고 내역 | 사용자 정지, 키워드 블랙리스트 관리 | API | A |

## 콘텐츠 흐름 계층도

화면이 콘텐츠상 어디에서 이어지는지(어떤 화면에서 들어가는지)를 나타낸다. `TAB1~5`/`Admin`은
실제 UI 요소가 아니라 화면군을 묶어 보여주기 위한 표기다. 실제 클릭 가능한 전역 메뉴 구조는
아래 "상단 메뉴 구조" 절을 따로 참고 — v1.2부터 두 구조는 서로 다르다(예: `ALERT-002`는
콘텐츠상 `ALERT-001`에서 이어지지만, 메뉴상으로는 마이페이지 그룹에 있다).

```mermaid
graph TD
  Root[TrendFit] --> Auth[공통/인증]
  Root --> Onboard[관심사 설정]
  Root --> TAB1[트렌드 대시보드]
  Root --> TAB2[인사이트 리포트]
  Root --> TAB3[급상승 알림]
  Root --> TAB4[콘텐츠 큐레이션]
  Root --> TAB5[마이페이지]
  Root --> Admin[관리자]

  Auth --> COM001[COM-001 랜딩]
  Auth --> COM002[COM-002 로그인]
  Auth --> COM003[COM-003 회원가입]
  Auth --> COM004[COM-004 비밀번호 재설정]

  Onboard --> ONBOARD001[ONBOARD-001 관심사·조건 설정]
  ONBOARD001 --> ONBOARD002[ONBOARD-002 맞춤 설정 완료]

  TAB1 --> DASH001[DASH-001 트렌드 대시보드]
  DASH001 --> DASH002[DASH-002 키워드 상세]

  TAB2 --> REPORT001[REPORT-001 리포트 목록]
  REPORT001 --> REPORT002[REPORT-002 리포트 상세]

  TAB3 --> ALERT001[ALERT-001 알림 설정]
  ALERT001 --> ALERT002[ALERT-002 알림함]

  TAB4 --> CURATE001[CURATE-001 큐레이션 피드]
  CURATE001 --> CURATE002[CURATE-002 콘텐츠 상세]

  TAB5 --> MY001[MY-001 마이페이지]
  MY001 --> MY002[MY-002 계정 설정]

  Admin --> ADMIN001[ADMIN-001 관리자 대시보드]
  ADMIN001 --> ADMIN002[ADMIN-002 사용자·키워드 관리]

  style Root fill:#4F46E5,color:#fff
  style Auth fill:#7C3AED,color:#fff
  style Onboard fill:#7C3AED,color:#fff
  style TAB1 fill:#0891B2,color:#fff
  style TAB2 fill:#059669,color:#fff
  style TAB3 fill:#D97706,color:#fff
  style TAB4 fill:#DC2626,color:#fff
  style TAB5 fill:#475569,color:#fff
  style Admin fill:#475569,color:#fff
```

## 상단 메뉴 구조 (v1.2, 2026-08-11 개편)

사이드바에 15개 화면을 평면 나열하던 것을 상단 호버 드롭다운 메뉴 5개 그룹으로 대체했다
(`components/top_nav.py`). 마우스를 그룹에 올리면 하위 화면이 드롭다운으로 펼쳐진다. 로그인·
회원가입(COM-002/003)은 메뉴에 없고 랜딩(COM-001)의 버튼과 로그인 화면 내부 링크로만
진입한다. 관리자 그룹은 `AuthUser.role`이 관리자(`config.ADMIN_EMAILS` 화이트리스트 기반)인
세션에서만 보인다.

```mermaid
graph TD
  Nav[상단 메뉴] --> Home[홈]
  Nav --> Trend[트렌드]
  Nav --> Insight[인사이트]
  Nav --> MyPage[마이페이지]
  Nav --> Admin["관리자 (관리자 역할만 노출)"]

  Home --> N_COM001[COM-001 랜딩]

  Trend --> N_DASH001[DASH-001 트렌드 대시보드]
  Trend --> N_DASH002[DASH-002 키워드 상세]
  Trend --> N_ALERT001[ALERT-001 급상승 알림 설정]

  Insight --> N_REPORT001[REPORT-001 인사이트 리포트]
  Insight --> N_REPORT002[REPORT-002 리포트 상세]
  Insight --> N_CURATE001[CURATE-001 콘텐츠 큐레이션]
  Insight --> N_CURATE002[CURATE-002 콘텐츠 상세]

  MyPage --> N_MY001[MY-001 마이페이지]
  MyPage --> N_ONBOARD001[ONBOARD-001 관심사 설정]
  MyPage --> N_MY002[MY-002 계정 설정]
  MyPage --> N_COM004[COM-004 비밀번호 재설정]
  MyPage --> N_ALERT002[ALERT-002 알림함]

  Admin --> N_ADMIN001[ADMIN-001 관리자 대시보드]
  Admin --> N_ADMIN002[ADMIN-002 사용자·키워드 관리]

  style Nav fill:#4F46E5,color:#fff
  style Home fill:#0891B2,color:#fff
  style Trend fill:#0891B2,color:#fff
  style Insight fill:#059669,color:#fff
  style MyPage fill:#475569,color:#fff
  style Admin fill:#DC2626,color:#fff
```
