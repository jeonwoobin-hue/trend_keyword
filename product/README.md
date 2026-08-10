# product/ — 서비스 개선 관리

개발 규칙(`docs/`)과 달리, 이 폴더는 **"무엇을, 왜, 언제" 만들지**를 관리합니다.

| 파일 | 용도 |
|---|---|
| [Backlog.md](Backlog.md) | P1 이후 백로그 — SRS의 P2/P3 요구사항 + 새로 제안된 개선 아이디어 |
| [CHANGELOG.md](CHANGELOG.md) | 버전/배포 단위 변경 이력 |
| [KPI_Dashboard.md](KPI_Dashboard.md) | 서비스 실측 지표 트래킹 (가입자수, DAU, 알림 발송 성공률 등) |

- 새 기능 아이디어가 생기면 우선 `Backlog.md`에 등록합니다.
- 실제 지표 정의/계산식은 [../docs/KPI_Definitions.md](../docs/KPI_Definitions.md)를 따르고, 여기서는
  **실측값 기록**만 합니다(정의와 실측을 분리).
- 배포/릴리즈가 있을 때마다 `CHANGELOG.md`에 한 줄이라도 남깁니다.
