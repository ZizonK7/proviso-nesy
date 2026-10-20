에이전트: 방향·유지보수·아이디어 조사 (Opus 5.5, effort high). 하위 에이전트 호출: 없음. 커밋·push: 안 함.

# 2026-10-20 — Flowlog 방향·유지보수·기능 아이디어 조사

## 한 일
- 결과물(저장소 밖): `/tmp/claude-0/-home-user/7c40c1dc-b607-5f78-9497-ffe487ef55d0/scratchpad/reports/05-direction-maintenance-ideas.md` (약 600줄, 섹션 A–E).
  - A. 플랫폼 변화 13항목: 무엇이 바뀌었나 / Flowlog `파일:줄` / 해야 할 일 / 기한 / 출처.
  - B. 유지보수 7항목: CI(GitHub Actions yml 초안), Dependabot·Renovate 설정 초안, 릴리즈 경로 비교 표, 테스트 전략, Crashlytics, 문서 역할 평가, 버전·브랜치. 각각 비용·효과.
  - C. 기능 아이디어 22개(표 + 상세), "신박" 3개 표시(C7 계획 대 실제 거울, C8 기록 정확도 무작위 점검, C9 어제 재구성 5분). 지시서 씨앗 중 뺀 것과 이유.
  - D. 웹 대시보드 방향(README만 근거).
  - E. 3·6·12개월 로드맵 21단계, 단계마다 "왜 이 순서".
- `/home/user/Flowlog`는 읽기만 했다. 파일 수정 없음.

## 확인한 것 (어떻게)
- Flowlog 코드 사실은 `grep`/`sed`로 직접 확인: 정확 알람 사용 8곳, 매 실행 권한 요청(`MainActivity.kt:172`, HEAD 기준), 권한 변경 수신기 없음, 타이머 알림에 정지 액션·`setDeleteIntent` 없음, `exportSchema = false`, `tags`는 데이터 칸만 있고 항상 빈 목록, lifecycle 버전 2.10.0/2.8.7 섞임, `.github/` 없음, git 태그 0개, `runCatching` 256곳.
- `git ls-files -s gradlew` → `100644`(실행 권한 없음). 리눅스 CI에서 `./gradlew`가 실패할 것.
- 공식 문서는 WebFetch로 열어 읽음: developer.android.com의 Play targetSdk 요구, Android 14·15·16·17 동작 변경, 정확 알람, Live Update, 16KB, 엣지 투 엣지, predictive back, Health Connect, Glance·Room·credentials·material3 릴리즈 노트, 빠른 설정 타일, 바로가기, NFC, Gemini Nano, Play Integrity, 개발자 인증(+FAQ), Room 마이그레이션 시험, Compose 스크린샷 시험. Firestore 요금은 `curl`로 cloud.google.com 페이지를 받아 무료 할당 문구를 직접 확인.
- 줄 번호는 커밋 `98b3039` 기준. `git show HEAD:…/MainActivity.kt | grep -n`으로 대조함.

## 확인 못 한 것
- **네트워크 제한**: firebase.google.com, developers.google.com, docs.github.com, f-droid.org, support.google.com(Play 정책), 앱 회사 사이트, 논문 사이트(ncbi, 대학 PDF)는 접속 불가. 이 출처들은 보고서에 "(검색 결과로만, 열지 못함)"으로 표시했다. 특히 App Check의 Play 밖 배포 지원 여부, Firebase BoM 최신 버전, Dependabot/Renovate 문법, F-Droid 정책, Play 정확 알람 정책은 메인이 다시 확인해야 한다.
- 빌드 금지라 APK에 `.so`가 있는지(16KB), CI 초안이 실제로 도는지, lint 결과는 확인 못 함.
- 사용자가 폰에 debug와 release 중 무엇을 깔아 쓰는지(Crashlytics가 debug에선 꺼짐) — 사용자에게 물어야 함.
- 웹 저장소(pfkfks-main) 코드와 현재 배포된 Firestore 규칙은 볼 수 없었다.
- `clearCredentialState` 권장은 공식 페이지 본문에서 직접 읽지 못했다(요약 도구가 일반 지식이라고 밝힘).
- 한국의 개발자 인증 시행 시점, ML Kit GenAI 지원 기기·한국어 지원.

## 알려진 문제
- 조사 도중 같은 Flowlog 작업 트리에 다른 에이전트의 미커밋 변경(직접 추가·내보내기·바로가기, 8개 파일 수정 + 새 파일)이 생겼다. 결과물 C3·C5·로드맵에 반영 표시만 했고 그 코드는 검토하지 않았다. 작업 트리 기준으로는 `MainActivity.kt`·`ActivityViewModel.kt` 줄 번호가 밀려 있다.
- 단위 테스트 수: 상태 문서는 98개, 지금 `@Test` grep은 89개. 원인은 확인 못 함(시험 기능 삭제로 추정).
- Android 17 페이지는 아직 베타로 보이며, API 37 Play 요구 시점(2027 여름)은 관례 기반 추정이다.

## 다음 작업자에게
- 가장 급한 3개: (1) 정확 알람 정리(A1 — 매 실행 권한 화면 제거, 자정 동기화를 WorkManager로, 권한 변경 수신기), (2) 타이머 알림 정지 버튼·지움 감지·Live Update(A2/C1), (3) 키스토어 백업 + 개발자 인증 대비(A3, 2027 전 세계 확대; ADB 설치는 면제).
- CI를 넣을 때 `gradlew` 실행 권한부터(`git update-index --chmod=+x gradlew`).
- Room 스키마 내보내기·마이그레이션 시험은 다음 스키마 변경(시험 기능 잔재 삭제) **전에**.
- 사용자 판단이 필요한 것: 백업 규칙(무엇을 클라우드 백업할지), Health Connect용 minSdk 26 상향, 남에게 배포할 계획 여부, 신박 아이디어 C7–C9 중 무엇을 원하는지.
- 공개 저장소 주의: 관리자 uid 문자열이 `UserRoleStore.kt:11`과 `tools/study-integration/rules-test.cjs:19`에 있다(값은 보고서에 옮기지 않음). 비밀값은 아니지만 Flowlog의 PROJECT_CONTEXT 원칙과 맞는지 사용자 판단.
