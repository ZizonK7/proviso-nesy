에이전트: 웹 통계 페이지 구현 (Opus 5.5, effort high). 하위 에이전트 호출: 없음. 커밋·push: 안 함.

# 2026-10-20 — Flowlog `/statistics/`를 어제·오늘 원본 + 일별 요약으로 (pfkfks-main)

대상: 비공개 웹 저장소 `/home/user/pfkfks-main`, 브랜치 `ccr-2a22e640-e8dn8n`. 시작 시점은 커밋 e27e897(앞 작업 커밋). 작업 트리만 고쳤고 커밋하지 않았다.

## 한 일

### 데이터 경로 (`public-flowlog/statistics/statistics.js`)
개인 화면에서 서버 요약 개요가 있으면(`summaryVersion >= 2`) 아래처럼 읽는다.
- **원본은 어제·오늘만**: `startTime >= 어제 0시 − 48시간`(숫자 ms, `limit(300)`) 한 쿼리. 그중 어제·오늘과 겹치는 기록만 남기고, 삭제된 기록은 뺀다.
- **30일 추세에서 그제까지(오늘−30 ~ 오늘−2)**: `summary/daily` 날짜 범위 쿼리 하나(≤29건)로 읽는다. 어제 칸은 원본으로 계산하고, 오늘은 원래대로 추세에 넣지 않는다.
- **기준일**: 어제 시작한 기록이 있으면 어제다. 이때 카드·타임라인·분류 도넛은 원본으로 그리고, 블록은 수정할 수 있다.
- 어제 기록이 없으면 60일 안의 마지막 기록일을 일별 문서에서 찾는다. 불러온 29일에 기록이 없을 때만 1건짜리 쿼리(`date < 경계`, 내림차순, `limit(1)`)를 더 보낸다.
- 어제가 아닌 기준일은 요약 값으로만 보여 준다(카드·도넛). 타임라인 자리에는 "이 날짜는 하루 요약만 불러와요…" 문구를 띄우고, 수정할 수 있는 블록은 없다.
- 기록 일수와 연속 기록은 개요 문서 값을 쓴다.
- **서버 요약이 아직 없는 사용자**(마이그레이션 전)는 예전처럼 31일 원본, 그게 비면 최근 300건으로 동작한다. 이 경로에서는 원본 창 쿼리와 일별 쿼리가 먼저 한 번 헛돌아 약 36건이 더 읽힌다.
- 일별 쿼리가 실패해도 화면은 그대로 그린다. 오류는 콘솔 경고로만 남기고 추세는 0으로 표시된다.
- `today-flow-engine.js`의 `buildDashboardModel`에 요약 경로를 추가했다(`options.dailySummaries`가 배열일 때, `baseFromSummary` 칸 포함). 원본만 있는 경로는 손대지 않았다. 로그인 전 미리보기와 관리자 화면은 그대로 원본 경로를 쓴다. statistics.js는 엔진을 `?v=20261020-1`로 불러온다.

### 없앤 것
- **주간 누적 차트**(`WeeklyStackedChart`)와 그 안의 운동 개요 줄을 없앴다.
- **운동 패널 전체**를 없앴다: `ExerciseLogSection` 아래의 이번 주 운동 요약·종목 집계(`ExerciseWeekPanel`)와 최근 운동 목록(`RecentExerciseList`), 그리고 운동 아이콘 상수.
- 위 화면이 쓰던 문구를 없앴다: `statistics-copy.js`의 weekly 5개, exercise 8개, 한·영 합쳐 26줄. `exerciseMoreBtn`은 남겼다.
- 위 화면이 쓰던 CSS를 `statistics.css`에서 없앴다: stacked·exercise·agg·set·intensity·timer 관련 규칙과 모바일 규칙. 이 CSS를 함께 쓰는 관리자·활동 페이지가 이 클래스들을 쓰지 않는 것은 확인했다. 운동 페이지는 자기 `style.css`를 쓴다.
- 쓰지 않게 된 import를 지웠다.
- 빈자리에는 버튼 두 개("운동 일지 보러가기 →" `/statistics/exercise/`, "전체 활동 보기")와 최근 기록 4개 칸을 놓았다. 클래스 `stats-links`·`stats-recent`를 새로 만들었다. `index.html`의 CSS 버전은 `20261020-1`.
- **지시서에 없던 결과**: 서버 요약 경로에서는 "오늘의 흐름 미리보기"의 **과거 기반 예상 블록**이 나오지 않는다. 기준 요일 날, 14일·60일 시간대 패턴은 과거 원본이 있어야 계산되는데 이제 불러오지 않기 때문이다. 어제 하루만으로 예측하면 어제를 그대로 베낀 결과가 나와서 끄는 쪽을 택했다. 오늘 실제 기록, 루틴 체크, 고정 일정, 추천 할 일 블록은 그대로 나온다. 원본만 있는 경로에서는 예측도 예전처럼 나온다.

### 남는 페이지 구성 (개인, 로그인 후)
1. 데이터 성숙도 배너(기록 일수: 개요 값).
2. 오늘의 흐름 미리보기: 오늘 기록과 루틴 체크, 고정 일정·추천 할 일 블록. 오늘 기록은 수정 가능.
3. 다음 수업 카드.
4. 최근 리듬:
   - 기준일 카드 4개.
   - 기준일 타임라인. 어제면 원본이라 수정 가능하고, 그 밖의 날은 요약 문구만 보인다.
   - 분류 합계 도넛.
   - 30일 평균 3개와 연속 기록.
   - 30일 추세 3개(생산·수면·휴식).
   - 운동 일지·전체 활동 링크, 최근 기록 4개.
5. 컨디션 체크인 대화상자.

### 테스트
- **새 파일** `tests/statistics-summary-path.browser.cjs`. Firebase를 가짜로 바꾸되 where·orderBy·limit를 실제로 적용하고 쿼리를 기록하게 했다. 세 경우를 본다.
  - 어제 기록 있음:
    - 원본 쿼리가 1개이고 조건은 `startTime >= 어제−48h` 하나, limit이 있다.
    - 일별 쿼리는 1개이고 범위가 정확하다.
    - 어제 카드가 8h 30m이다(자정 넘은 수면 7h + 공부 1.5h, 삭제된 휴식 5h는 빠짐).
    - 어제 블록이 수정 가능하고, 사흘 전 원본은 빠진다.
    - 수면 추세에 일별 문서 값(5h2m)과 어제 원본 값(7h)이 함께 들어간다.
    - 주간·운동 화면이 없고 링크 두 개가 있다. 기록 일수는 개요 값이다.
  - 5일 전만 기록 있음: 날짜 표시, 3h 20m, 요약만 문구가 나오고 수정 블록 0, 추가 쿼리 없음.
  - 45일 전만 기록 있음: 1건 추가 조회의 모양이 맞고 1h 15m가 표시된다.
- `tests/statistics-activity-edit.browser.cjs`: 가짜 `getDoc`이 `summaryVersion: 2` 개요를 돌려주게 해서 요약 경로로 돌게 했다. 어제 타임라인에 수정 가능한 블록이 있는지 확인하는 줄 하나를 더했다.
- `tests/statistics-entry-once.browser.cjs`: 가짜 저장소에 `summaryVersion: 2` 개요를 넣어 요약 경로로 돌게 했다.
- `tests/README.md`에 새 테스트 설명을 추가했다.
- `condition-survey.browser.cjs`와 `statistics-study-links.test.cjs`는 이 데이터 경로를 타지 않아 고칠 것이 없었다(그대로 통과).

### 문서
- `README.md` `/statistics/` 절:
  - 데이터 경로, 기준일 규칙, 수정 범위, 마이그레이션 전 폴백을 지금 동작대로 다시 썼다.
  - 화면 구성표를 갱신했다. 코드에 없던 "장기 패턴" 행은 지웠다(heatmap 등이 statistics.js에 없음).
  - 제거 사실을 적고, 예상 블록이 원본만 있는 경로에서만 나온다고 적었다.
- `docs/flowlog-release-plan.md`: 6절 5번에 `/statistics/` 반영 내용, 7절에 읽기 수와 테스트를 적었다.

## 읽기 수 (기록 3,000건, 하루 10건 사용자, 통계 1회 열기) — 코드 기준 추정

| 항목 | 전 (e27e897) | 후 |
|---|---|---|
| 개요 | 1 | 1 |
| 활동 원본 | 31일 약 310 | 어제 0시−48h부터 약 30~40 (그중 어제·오늘 것만 사용) |
| 일별 요약 | 0 | ≤29 (+ 드물게 1) |
| 할 일(미완료)·추천 1·루틴 정의·캘린더 1·추천 항목 | 같음 | 같음 |
| **활동 관련 합계** | **약 310** | **약 60~70** |

서버 요약이 아직 없는 사용자는 약 310 + 36이다(헛도는 두 쿼리). 마이그레이션이 끝나면 없어진다.

## 확인한 것 (어떻게)
모두 `/home/user/pfkfks-main`에서 실행했다. Playwright는 이 환경의 Chromium 래퍼(`PLAYWRIGHT_MODULE`)로 돌렸다. `tools/study-build` 경로가 박힌 두 테스트는 require 경로만 바꾸는 preload를 붙였고, `TEMP`는 임시 폴더로 지정했다.
- `node tests/statistics-summary-path.browser.cjs` → PASS. 개요를 `summaryVersion: 1`로 바꾼 사본으로 돌리면 "one raw activity query"에서 실패해, 이 테스트가 요약 경로를 실제로 가른다는 것도 확인했다(사본은 지움).
- `node tests/statistics-entry-once.browser.cjs` → PASS.
- `node tests/statistics-activity-edit.browser.cjs` → PASS.
- `node tests/condition-survey.browser.cjs` → PASS.
- `node --test --experimental-test-isolation=none tests/condition-model.test.mjs` → 3개 통과.
- `node --test tests/statistics-study-links.test.cjs` → 1개 통과.
- `node --check --input-type=module`으로 statistics.js, today-flow-engine.js, statistics-copy.js를 검사해 통과했다.
- 로그인 전 미리보기(원본 경로)는 임시 사본 테스트로 오류 없이 그려지는 것을 확인했다(사본은 지움).
- 앞 작업의 저장소 밖 랜딩·루틴 검사도 다시 통과했다.
- `git status --short`:
  - `M` README.md, docs/flowlog-release-plan.md, tests/README.md
  - `M` public-flowlog/statistics/index.html, statistics-copy.js, statistics.css, statistics.js, today-flow-engine.js
  - `M` tests/statistics-activity-edit.browser.cjs, tests/statistics-entry-once.browser.cjs
  - `??` tests/statistics-summary-path.browser.cjs

## 확인 못 한 것
- 실제 Firestore와 실데이터, 실기기 화면. 테스트의 Firebase는 모두 가짜다.
- 운영 인덱스: 일별 쿼리는 같은 필드의 범위와 정렬이라 자동 단일 필드 인덱스로 될 것으로 보지만, 배포해서 확인하지는 않았다.
- 자정 직전·직후에 열 때의 경계, 그리고 KST가 아닌 시간대의 브라우저. 날짜는 브라우저 시간 기준이고, 서버 일별 문서는 KST 기준이다.
- 화면을 사람 눈으로 본 확인(스크린숏 비교)은 하지 않았다.

## 알려진 문제
- 서버 요약 경로의 "오늘의 흐름 미리보기"에서 과거 기반 예상 블록이 사라졌다(위 "지시서에 없던 결과"). 사용자 확인이 필요하다.
- 캐시: Hosting이 js를 1시간 캐시한다. statistics.js·엔진·CSS는 버전을 올렸지만, `statistics-copy.js`(statistics-utils.js가 버전 없이 불러옴)는 배포 후 최대 1시간 옛 파일일 수 있다. 그동안 요약만 있는 기준일에는 새 문구 대신 기존 "타임라인 없음" 문구가 보인다(대체 문구로 막음).
- 일별 문서의 분류 이름은 웹 17분류를 `normalizeCategory`로 통계 화면 분류에 합친다. 화면에 없는 분류는 기타로 들어간다.
- 기준일이 어제가 아닐 때 도넛·카드 값은 서버 일별 문서 기준이다(자정에서 잘린 분, 삭제 제외). 예전 원본 계산과 몇 분 차이가 날 수 있다.
- 원본 창(−48h)에서 그제·그끄제 기록을 읽고 버리는 만큼은 비용으로 남는다(지시대로 창 유지).
- `today-flow-engine.js`의 예측 함수들은 원본 경로에서 아직 쓰여서 지우지 않았다.

## 다음 작업자에게
- 예상 블록을 다시 살리려면 서버에 시간대별 패턴 문서가 필요하다. 일별 문서의 `dist`는 분류 묶음별 시간대 합이라 그대로는 못 쓴다. 아니면 예측할 때만 14일 원본을 따로 읽는 방법이 있는데, 그러면 읽기가 다시 늘어난다.
- `statistics-copy.js`를 고칠 때는 `statistics-utils.js`의 import에도 버전을 붙이는 편이 안전하다. 관리자 모듈도 utils를 불러오므로 두 경로가 같은 URL을 쓰게 맞출 것(CLAUDE.md의 statistics.js 두 번 실행 사례 참고).
- 함수 배포 뒤 Cloud Scheduler에서 `reconcileActivitySummaries`를 한 번 돌리면, 모든 사용자가 바로 이 요약 경로로 옮겨지고 폴백의 헛도는 읽기가 없어진다.
