에이전트: 웹 통계 비용 구현 (Opus 5.5, effort high). 하위 에이전트 호출: 없음. 커밋·push: 안 함.

# 2026-10-20 — Flowlog 웹 Firestore 읽기 비용 줄이기 (pfkfks-main)

대상: 비공개 웹 저장소 `/home/user/pfkfks-main`, 브랜치 `ccr-2a22e640-e8dn8n` 작업 트리(커밋 안 함).

## 한 일

### 먼저 바로잡을 사실 (지시서의 전제와 다른 점)
- **"메인(랜딩) 페이지"에는 대시보드가 없다.** Flowlog 사이트의 `/`(`public-flowlog/index.html`)는 앱 소개 페이지이고, `flowlog.js`가 그리려는 칸(`data-maturity-banner`, `data-early-chapter`)이 HTML에 없다. 그런데 `flowlog.js`는 로그인한 방문자에게 Firestore를 읽고 아무것도 그리지 않았다(읽기만 낭비). 어제 상세·30일 추세 그래프가 실제로 보이는 곳은 **`/statistics/`**(`statistics/index.html`에 그 칸이 있음)다.
- **숫자 `startTime`에 Date로 범위를 거는 쿼리는 아무것도 못 읽는다.** 앱은 `startTime`을 숫자(ms)로 쓰고 규칙도 숫자를 강제한다. 랜딩의 30일 폴백과 "오늘 원본" 쿼리, `summary.js`의 `fetchRawActivitiesForDay`는 Date를 넘겨서 항상 0건이었다(에뮬레이터에서 같은 모양의 쿼리로 0건 확인). 통계·활동 페이지는 원래 숫자를 써서 문제없다.
- 일별·월별 요약은 정말 아무도 못 쓰고 있었다: 규칙 에뮬레이터 테스트에서 클라이언트의 `summary/daily/*`·`summary/monthly/*` 쓰기가 403. 앱도 쓰지 않는다(Flowlog 앱 코드에 `summary` 경로 없음).
- 옛 서버 개요는 날짜를 함수 서버 시간대(UTC)로 셌다(`new Date(ms).getDate()`). 이번에 KST로 바뀐다.

### A. 요약 함수 날짜별 증분 (`functions/activity-summary.js` 새로 씀, `functions/index.js` 배선)
- 활동이 바뀌면 그 활동이 걸친 KST 날짜만(전·후 버전 모두, 자정을 넘기면 다음 날도, 최대 3일) 그 날짜 창(날짜 시작 −48시간 ~ 날짜 끝, `startTime` 범위 + 겹침 필터 — 웹 `fetchRawActivitiesForDay`와 같은 창)의 원본만 읽어 다시 계산한다. 이웃한 날짜는 한 쿼리로 묶는다. 숫자형과 옛 Timestamp형 `startTime`을 둘 다 질의한다.
- 서버가 `summary/daily/{날짜}`를 쓴다. 계산은 웹 `calculateDailySummary`를 그대로 옮긴 것(KST, 같은 자정 분할). 차이: 삭제된 활동 제외, 할 일 개수 두 칸은 안 씀(읽는 곳 없음, 할 일 변경은 이 함수를 깨우지 않음). 시간대 분포의 그날 몫(`dist`)을 같이 저장한다. 기록 없는 날의 문서는 지운다.
- `summary/monthly/{달}`은 그 달 일별 문서(≤31)로 계산(웹 `computeMonthlySummary` 모양 + `firstLogDate`·`lastLogDate`·`trailingLoggedDays`·`dist`).
- 개요 `flowlog/summary`는 월별 문서로 계산: `loggedDays`, `allTimeLoggedDays`(랜딩이 읽는 이름), `streak`, `totalMinutes`, `categoryTotals`, `monthSeries`, `firstLogDate`, `lastLogDate`, `summaryVersion: 2`, `updatedAt`. 연속 기록(streak)은 최신 기록 달의 일별 문서만 읽고, 그 이전의 꽉 찬 달은 월별 `trailingLoggedDays`로 센다(처음엔 일별을 거꾸로 훑었더니 300일 연속 사용자에서 저장 1건에 359 읽기가 나와 바꿈).
- 시간대 분포 캐시 `userDistCaches/{uid}` = 월별 `dist`의 합. 숫자는 옛 `computeDistCache`와 같다(테스트로 비교).
- 10분 제한·dirty·flush 구조 유지. 미뤄진 쓰기는 `dirtyDates`에 날짜를 쌓고, 400일을 넘거나 버전이 없으면 `dirtyFull`로 전체 재계산 1회.
- 안전망: 전체 재계산 `recomputeAll` — (1) 개요에 `summaryVersion: 2`가 없으면(배포 전 사용자, 새 사용자) 그 사용자의 첫 활동 변경 때 자동 1회(마이그레이션), (2) 새 예약 함수 `reconcileActivitySummaries`(일요일 04:30 KST, 540초, 모든 인증 사용자, 계정 삭제 중·삭제된 계정 제외)가 주 1회. 바뀐 문서만 쓴다. Flowlog를 안 쓰는 사용자에겐 문서를 만들지 않는다.
- 옛 `computeActivitySummary`·`computeDistCache`와 보조 함수는 `index.js`에서 지웠다. `_rebuildGlobalDistCache`는 새 모듈의 `makeDistBucket`·`addDistBuckets`를 쓴다.

### 웹 요약 모듈 (`public-flowlog/shared/summary.js`)
- 쓰기 코드(SyncManager, UploadQueue, DirtySummaryQueue, UploadStatus/resolveUploadStatus, upload*, syncDirtySummaries) 삭제. 계산 두 개, 경로 헬퍼, `fetchRawActivitiesForDay`(숫자 범위로 고침)는 남김. 이 모듈을 import하던 곳은 `flowlog.js` 하나뿐이었다(만들기만 하고 메서드는 안 불렀음).

### B. 랜딩 (`public-flowlog/flowlog.js`)
- **대시보드 칸이 없으면 로그인해도 Firestore를 읽지 않는다**(지시서 밖, 위 사실 때문에 추가). 지금 `/`에서는 읽기 0.
- 칸이 있는 경우의 경로도 지시대로 바꿈: 요약 조건을 "24시간 안 갱신"에서 "`summaryVersion >= 2`"로. 요약 경로 = 개요 1 + 일별 문서 28일(그제까지, 날짜 범위 쿼리) + 어제·오늘 원본(그제 0시 ~ 내일 0시, limit 150) + 최근 기록 4건. 그래프 끝 두 칸과 어제 비교는 원본으로 계산. 삭제된 활동 제외. 화면에 안 쓰이던 할 일(최대 50/250)·월별 요약(6) 읽기 제거. 폴백은 30일 원본 limit 300(숫자 범위).
- 지시서 밖: 메인 사이트의 옛 사본 `public/flowlog.js`(`/flowlog.html`, 역시 대시보드 칸 없음)가 로그인 방문자에게 **활동·할 일 전체를 제한 없이** 읽던 것도 같은 방식으로 막음.

### C. 루틴 화면 (`public-flowlog/routine/routine.js`, `index.html` 버전 `20261020-01`)
- 활동은 최근 30일(`startTime >= 오늘−29일 0시`). 차트 시작점 플래그("30일보다 오래된 루틴 기록이 있나")는 `sourceType == DAILY_CUE_ROUTINE`, `sourceId in [루틴 id ≤30개씩]`, `startTime < 경계`, `limit(1)` 쿼리로만, 그리고 창 안에 루틴 기록이 있을 때만. 인덱스 `activitySessions(sourceType, sourceId, startTime)`을 `firestore.indexes.json`에 추가.
- dailyGoalItems는 `createdAt` 31일(하루 여유). petites(캘린더 문서 사본, 캘린더 문서의 할 일 수만큼)와 dailyCues(루틴 정의, 루틴 수만큼)는 날짜 칸이 없거나 범위를 걸면 연결이 끊길 수 있어 그대로 전체.
- 캘린더 분포의 "더 오래된 활동" 플래그는 원래 화면에서 쓰이지 않아(그리는 함수가 받기만 함) 영향 없음.

### 그 밖 (지시서 밖)
- `/statistics/` 개인 화면: 요약 문서가 없거나 31일이 비면 **활동 전체를 읽던 폴백**을 "최근 300건"으로 바꿈. 통계 진입 모듈 버전 `20261020-1`로 두 HTML(import map) 함께 올림.
- `tests/flowlog-rules.emulator.cjs`에 월별 요약 클라이언트 쓰기 거절 한 줄 추가.

### D. 문서
- `README.md`: Functions 목록에 요약 함수 셋, 요약 설명과 통계 읽기 설명 갱신.
- `docs/flowlog-release-plan.md`: 6절 5·6번에 "2026-10-20 반영", 3절 끝에 "요약 함수 증분화 배포"(순서·마이그레이션), 7절에 이번 변경 요약.

## 읽기 수 추정 (기록 3,000건, 하루 10건, 300일 사용자)

| 동작 | 전 | 후 | 근거 |
|---|---|---|---|
| 활동 1건 저장(10분 제한 밖) | 약 3,001 (활동 전체 + 개요) | 약 61 (에뮬레이터 측정 59 + 트랜잭션 2) | 측정 |
| 활동 묶음 저장(10분 안 여러 건) | 3,001 + 30분 뒤 flush 3,001 | 61 + flush 때 쌓인 날짜만 (날짜 수 × 약 30 + 약 30) | 코드 |
| 주 1회 정합성 | 없음 | 약 3,316 (활동 3,000 + 일별 300 + 월별 11 + 개요 1 + 삭제 확인 2), 쓰기는 바뀐 것만(측정 0) | 측정 3,313 + 2 |
| 최초 1회 마이그레이션 | — | 약 3,003 읽기, 일별 300 + 월별 11 쓰기 | 측정 |
| 사이트 첫 화면 `/` 1회(로그인 상태) | 약 74 (개요·빈 일별·빈 월별·0건 원본 각 1 + 최근 20 + 할 일 ≤50) 또는 폴백 약 252 | 0 | 코드 |
| (대시보드 칸이 있을 때의 랜딩) | 위와 같음 | 1 + ≤28 + 약 20~30 + 4 ≈ 60 | 코드 |
| 루틴 화면 1회 | 3,000 + 루틴 정의 N + 캘린더 1 + petites P + 목표 항목 전체 G | 약 300 + N + 1 + P + 31일 목표 항목 + 1 | 코드 |
| 통계 `/statistics/` 1회 | 31일 원본 약 310 + 기타(31일이 비면 3,000) | 같음(약 310), 비면 최대 300 | 코드 |

쓰기: 저장 1건마다 전 3(점유·개요·분포) → 후 약 5(점유·일별·월별·개요·분포).

## 배포 순서와 마이그레이션
1. `firebase deploy --only firestore:indexes` (루틴 인덱스; 만들어지는 동안 루틴 차트의 그 쿼리만 실패).
2. `firebase deploy --only functions:updateActivitySummary,functions:flushDirtyActivitySummaries,functions:reconcileActivitySummaries`.
3. Hosting(`main` push가 두 대상 모두 배포).
- 기존 사용자의 일별 문서가 생기는 때: 함수 배포 뒤 그 사용자의 활동이 처음 바뀔 때(그 한 번은 전체 재계산), 또는 첫 일요일 04:30 KST. 바로 만들려면 배포 직후 Cloud Scheduler에서 `reconcileActivitySummaries`를 한 번 수동 실행.
- 웹이 먼저 나가도 깨지지 않는다(개요에 `summaryVersion`이 없으면 원본 범위 읽기).

## 확인한 것 (어떻게)
모두 `/home/user/pfkfks-main`에서. 함수 의존성은 저장소 밖(`<scratchpad>/fn-deps`, `npm ci --omit=dev`)에 설치하고 `NODE_PATH`로 썼다. Playwright는 `<scratchpad>/web-tools/pw-wrapper`(이 환경의 Chromium), 경로가 박힌 두 브라우저 테스트는 require 경로만 바꾸는 preload로 실행.
- `node --check functions/index.js` · `node --check functions/activity-summary.js` → 통과.
- `firebase emulators:exec --only firestore --project demo-flowlog-summary "node tests/activity-summary.emulator.cjs"` → 통과. 검사 내용: 웹 `calculateDailySummary`·`computeMonthlySummary`와 계산 일치(웹 파일을 그대로 불러 비교), 자정 분할 60/420분, 연속 기록(60일 경계, 미래 날짜, 여러 달 연속에서 최신 달만 읽음), 옛 개요 → 전체 재계산 1회, 추가·수정·자정 넘김·날짜 이동·소프트 삭제(빈 날·빈 달 문서 삭제)·하드 삭제·무관한 수정 무시·묶음 저장 미룸과 flush·늦게 미뤄진 쓰기 보존·중간 실패 복구·옛 Timestamp형 시작 시간, **매 단계 뒤 전체 재계산을 돌려 결과가 같고 다시 쓸 문서가 0개인지**, 분포가 옛 `computeDistCache`와 같은지, 주간 정합성의 건너뛰기(비사용자·삭제 중), Date 범위 쿼리가 숫자 필드에 0건인지, 3,000건 사용자 읽기 수(출력: 최초 3,003 / 주간 3,313·쓰기 0 / 저장 1건 59 읽기·2 쓰기).
- `firebase emulators:exec --only firestore --project demo-flowlog-rules "node tests/flowlog-rules.emulator.cjs"` → 32개 통과(월별 요약 쓰기 거절 추가분 포함).
- `node tests/statistics-entry-once.browser.cjs` → PASS. `node tests/condition-survey.browser.cjs` → PASS. `node tests/statistics-activity-edit.browser.cjs` → PASS.
- `node --test --experimental-test-isolation=none tests/condition-model.test.mjs` → 3개 통과(이 환경 Node 22.22는 지시서의 `--test-isolation=none`을 모르고 `--experimental-…`만 받음).
- `node --test tests/flowlog-account-deletion.test.cjs tests/statistics-study-links.test.cjs` → 12개 통과.
- 저장소 밖 임시 브라우저 검사(Firebase를 가짜로 바꿔 쿼리 모양을 기록): 실제 `/`는 쿼리 0개 / 대시보드 칸을 넣은 페이지에서 요약 경로의 쿼리가 일별 날짜 범위(29일 전~2일 전)·원본 숫자 범위 limit 150·최근 4, 어제 일별 문서 값(가짜 9999분)은 무시되고 원본으로 계산, 삭제 활동 제외, 폴백은 원본 1쿼리 limit 300 / 루틴 화면은 활동 30일 범위 + 오래된 루틴 존재 확인 `limit(1)` 1회, 차트가 30일 전부터 시작. 루틴 쿼리 모양(`==` + `in` + `<` + limit)은 에뮬레이터에서도 결과 확인(1/0/0).
- `git status --short`(최종): `M` README.md, docs/flowlog-release-plan.md, firestore.indexes.json, functions/activity-summary.js, functions/index.js, public-flowlog/flowlog.js, public-flowlog/routine/index.html, public-flowlog/routine/routine.js, public-flowlog/shared/summary.js, public-flowlog/statistics/admin/index.html, public-flowlog/statistics/index.html, public-flowlog/statistics/statistics.js, public/flowlog.js, tests/activity-summary.emulator.cjs, tests/flowlog-rules.emulator.cjs. 새 파일 없음(테스트가 tests/에 남긴 스크린샷은 지웠고, 이후 `TEMP`를 임시 폴더로 지정해 실행).

## 확인 못 한 것
- 실제 Firebase 배포·실데이터·실기기. 운영 인덱스 생성(에뮬레이터는 복합 인덱스를 강제하지 않는다). 루틴 인덱스가 정말 이 모양이어야 하는지는 배포 후 콘솔 오류로만 확인 가능.
- `reconcileActivitySummaries`의 예약 실행과 540초 안에 전체 사용자가 끝나는지(사용자 수를 모름; 480초에서 멈추고 다음 주에 이어 감 — 순서가 같아서 뒤쪽 사용자는 계속 밀릴 수 있다).
- 실제 함수 런타임에서 트리거(`onDocumentWritten`) 경로 전체 — 테스트는 같은 함수를 직접 부른다.
- ESLint(함수 폴더에 설정 파일이 없음).
- 랜딩 대시보드 경로는 지금 실제 페이지에 칸이 없어 임시 페이지로만 확인.

## 알려진 문제
- **사용자가 실제로 보는 `/statistics/`는 그대로 31일 원본(약 310 읽기/회)을 읽는다.** 지시서의 B("어제·오늘 원본 + 28일 요약")를 이 페이지에 적용하지 않았다. 이 페이지는 2주치 원본으로 운동 주간 패널·운동 이름·최근 운동 목록·주간 차트를 만들고, 기준일을 "어제부터 60일 안의 마지막 기록일"로 찾고, 타임라인에서 활동 편집·스터디 연결을 한다. 바꾸려면 화면 설계 결정이 필요해 메인에 넘긴다(아래 제안).
- 의미가 조금 바뀐 값: `loggedDays`가 "KST 날짜별로 잘린 분이 0보다 큰 날 수"(전: UTC 기준 시작 날짜 수), `categoryTotals`가 웹의 17분류(전: 7분류, 읽는 곳 없음), `streak`이 KST 기준.
- 증분 경로가 못 보는 것: `startTime` 없이 `start_time`/`start`만 있는 옛 문서, 48시간보다 긴 활동의 3일째 이후. 주 1회 전체 재계산이 맞춘다(그 사이 일별 문서와 차이가 날 수 있음).
- 같은 사용자에게 증분과 주간 전체 재계산이 동시에 돌면 같은 날짜 문서를 서로 다른 시점 읽기로 쓸 수 있다(다음 변경이나 다음 주에 맞춰짐).
- `public/statistics/statistics.js`(메인 사이트 옛 통계 사본)는 요약 문서가 없으면 개인 활동 전체를 읽는 경로가 남아 있다. 관리자 "전체" 범위(collectionGroup limit 5000)도 그대로. 둘 다 손대지 않음.
- `assistant.js`와 함수의 완료 할 일·calendarEvents 전체 읽기(계획 6절 5번 뒷부분)는 이번 범위 밖.

## 다음 작업자에게
- `/statistics/` 제안: 개인 범위에서 (1) 원본은 최근 15일(이번 주·지난주 운동 패널과 주간 차트가 쓰는 범위, 약 150 읽기)로 줄이고, (2) 30일 추세의 나머지 15일은 `summary/daily` 날짜 범위 쿼리(≤15)로, (3) 기준일이 15일 안에 없을 때만 일별 문서로 기준일을 찾아 그 날짜와 전날 원본을 추가로 읽는다. 사용자 결정대로 "어제·오늘만 원본"까지 가려면 운동 패널을 `category == EXERCISE` 14일 쿼리(기존 `category`+`startTime` 인덱스)로 따로 읽고, 주간 차트를 일별 문서로 그려야 한다. `buildDashboardModel`은 `today-flow-engine.js`에 있고 관리자 화면도 같은 모듈을 쓴다.
- 함수 배포 뒤 Cloud Scheduler에서 `reconcileActivitySummaries`를 한 번 돌리면 모든 사용자가 바로 요약 경로로 옮겨진다.
- 서버 일별 계산은 웹 `calculateDailySummary`의 사본이다. 웹 쪽을 고치면 서버도 고치고 에뮬레이터 테스트의 "matches the web" 검사가 잡아 준다.
- 이 환경에서 테스트 돌리기: Node 22는 `--experimental-test-isolation=none`. 브라우저 테스트 일부는 `tools/study-build` Playwright 경로가 박혀 있다. 조건 설문 브라우저 테스트는 `TEMP`가 없으면 `tests/`에 PNG를 남긴다.
