# 2026-10-20 — Flowlog 웹 출시 준비 (계정 삭제 웹 쪽, 영구 삭제 함수, App Check 배선)

에이전트: 웹 출시 준비 구현 (Opus 5.5, effort high). 하위 에이전트 호출: 없음. 커밋·push: 안 함.

대상: 비공개 웹 저장소 `pfkfks-main`(작업 트리만, `main` 기준). 앱 저장소 Flowlog(브랜치 `ccr-2a22e640-e8dn8n`)에서는
지시대로 `tools/account-deletion/README.md` 한 파일만 고쳤다. git 상태를 바꾸는 명령은 쓰지 않았다.
비공개 저장소라 코드·계정 ID·키는 여기 옮기지 않는다(파일 이름과 종류만).

## 한 일

묶음 A–F를 모두 했다.

- **A. 규칙** (`firestore.rules`, `tests/flowlog-rules.emulator.cjs`)
  - `users/{uid}/flowlog/account` 전용 조항: 소유자만, 필드는 `deletionRequestedAt`(timestamp, 서버 시각과 같아야 함)과
    `deletionRequestedBy`(`app`/`web`)만, 두 필드는 같이 있거나 같이 없어야 함. 취소는 두 필드 삭제(앱 방식) 또는 문서 삭제.
  - 일반 `flowlog/{documentId}` 쓰기 조항과 그 하위 조항에서 `account`를 뺐다(같은 경로의 규칙은 "또는"으로 합쳐지므로,
    빼지 않으면 일반 조항이 아무 필드나 허용한다).
  - **지시서보다 더 한 것**: 관리자·직원 계정은 예약을 못 쓰게 했다(규칙에 이미 있는 관리자·직원 판정 함수 사용, 새 ID 없음).
    빈 문서로 만드는 취소와 문서 삭제는 허용. 이유: 운영 계정이 실수로 예약되는 걸 함수보다 먼저 막는다. 앱은 예약 쓰기가
    실패하면 폰 데이터를 지우지 않으므로(앱 코드에서 확인) 관리자가 앱에서 눌러도 잃는 것이 없다.
  - 에뮬레이터 검사 16개 추가(15 → 31): 앱·웹 예약 허용, 본인 읽기, 다른 요청자 값·다른 필드·클라이언트 시각·
    요청자 없는 시각·타인·로그아웃 상태 거절, `account` 아래 하위 문서 거절, 앱식 취소(두 필드 삭제)·재예약·
    본인 문서 삭제 허용, 타인 삭제 거절, 관리자 예약 거절(관리자 ID는 테스트가 규칙 파일에서 읽는다 — 테스트에 새로 적지 않음).
    서버 시각은 에뮬레이터 REST의 `:commit` + `REQUEST_TIME` 변환으로 넣는다.
- **B. 삭제 요청 웹 페이지** (`public-flowlog/account/delete/`: `index.html`, `delete.js`, `delete.css`, `deletion-policy.js`)
  - 머리·꼬리·`flowlog.css`는 처리방침 페이지와 같게, Firebase 초기화는 `shared/firebase.js`, Google 로그인은 routine 페이지 방식.
  - 상태: 로그인 전(설명 + Google로 로그인) / 예약 없음(설명 + 예약 버튼 → "삭제" 입력해야 확정 버튼이 켜짐 →
    서버 시각과 `"web"` 쓰기) / 예약 중("남은 기간 n일", 끝나는 날짜, 예약 취소 = 두 필드 삭제) / 14일 지남("삭제 처리 중").
    관리자 계정이면 읽기 전에 "운영자 계정은 삭제할 수 없음"만 보여 준다. 계정이 바뀌면 이전 계정의 늦은 응답은 버린다.
  - 남은 일수는 앱 `AccountDeletionPolicy`와 같은 규칙(14일, 올림, 서버 시각이 폰 시계보다 앞서면 14일)의 순수 함수
    `deletion-policy.js`. 검사 `tests/flowlog-account-delete-page.test.mjs` 6개(함수 쪽 14일과 같은지 포함).
  - `firebase.json` flowlog 타깃에 `/account/delete` → `/account/delete/index.html` 다시 쓰기.
  - "계정 삭제" 꼬리 링크: 처리방침 페이지와 **랜딩 페이지**. 통계 페이지는 꼬리(footer)가 아예 없어서 지시서의 "통계 페이지 꼬리"
    대신 링크 목록이 있는 랜딩 페이지에 넣었다(지시서와 다름).
  - **지시서보다 더 한 것**: 링크가 하나 늘자 랜딩 페이지 꼬리가 390px 폭에서 가로로 넘쳤다(320px은 원래도 넘쳤음).
    `flowlog.css` 모바일 규칙에 꼬리 링크 줄바꿈을 더했다.
- **C. 개인정보처리방침** (`public-flowlog/privacy/index.html`): "정보 삭제 요청"을 실제 흐름으로 교체 — 앱 설정 또는 웹 페이지에서 요청,
  앱 요청은 폰 기록도 지움 / 웹 요청은 폰 기록이 남음, 14일 유보와 취소, 14일 뒤 하루 한 번 서버 작업이 기록·요약 통계·로그인 계정을
  영구 삭제하고 완료 시각만 남김, 같은 로그인 계정을 쓰는 블로그·스터디의 로그인과 그쪽 기록도 함께 삭제, 지운 활동은 서버에
  삭제 표시·식별자·분류·시작/종료 시각만 남고 제목·메모·태그·운동 세트는 지워짐(앱 업로드 코드에서 남는 칸 확인), 내보내기(CSV·JSON),
  연락처 대안. 최종 수정일 2026년 10월 20일.
- **D. 영구 삭제 함수** (`functions/flowlog-account-deletion.js`, `functions/index.js`, `tests/flowlog-account-deletion.test.cjs`, `firestore.indexes.json`)
  - 앱 저장소 초안의 `selection.js`·`purge.js`를 한 파일로 옮기고, Firebase 의존 없이 `createAccountPurgeJob({...})`로 묶었다
    (기존 `activity-summary.js`의 주입 방식과 같음). `index.js`에서 `exports.purgeDeletedFlowlogAccounts = onSchedule(...)`,
    리전 `asia-northeast3`, 매일 04:00 Asia/Seoul, 최대 1개 인스턴스, 540초.
  - 지우는 순서: `users/{uid}` 아래 컬렉션 전부(실행 때 목록을 받아서 — 나중에 생긴 컬렉션도 지워짐; flowlog 제외) → flowlog 아래
    문서 전부(account 제외) → `users/{uid}` 문서 → `userDistCaches/{uid}` → Auth 사용자 → `deletionLog/{uid}`(시각만) → 예약 문서 마지막.
    규칙과 코드에서 모은 경로 목록은 파일 머리 주석에(flowlog 하위, activityStudyLinks, interactionDecisions, studyCourses, studyRecords,
    previewCards, previewUsage, aiStudySessions, aiStudySessionDeletes, aiStudyUsage). 초안은 고정 목록 6개라 AI 학습 컬렉션을 빠뜨렸다.
  - 관리자·직원 거부: 함수 쪽 기존 관리자 집합 + 환경변수 `FLOWLOG_ADMIN_UIDS`(쉼표 구분). 직원 ID는 함수 코드에 없어서
    환경변수로만 막힌다(새 ID를 코드에 적지 않음). 거부된 예약은 그대로 두고 경고만(ID 없이) 남긴다.
  - **지시서보다 더 한 것 (버그 예방)**: 활동 기록을 지우면 기존 트리거 `updateActivitySummary`가 요약을 다시 계산해
    `flowlog/summary`와 `userDistCaches/{uid}`를 **되살린다**(코드에서 확인). 그래서 트리거가 "완전 삭제(문서가 사라짐)"일 때만
    예약 문서 또는 `deletionLog`가 있는지 보고, 있으면 건너뛰게 했다(`isPurgingOrPurged`). 클라이언트는 활동을 지울 수 없으므로
    평소 쓰기에는 읽기가 늘지 않는다. → `updateActivitySummary`도 다시 배포해야 한다.
  - 단위 테스트 11개(가짜 Firestore·Auth): 14일 경계, 중복·취소 제외, 시각 형식, 경로 판별, 환경변수 파싱, 지우는 순서와
    예약 마지막, Auth 사용자가 이미 없을 때, 실패 시 예약 유지, 질의 뒤 취소된 예약 건너뛰기, 요약 재계산 억제 판정,
    보호 계정 거부와 로그에 ID 없음, 한 계정 실패 시 나머지 처리 후 실행 실패로 보고.
  - 인덱스: 컬렉션 그룹 `flowlog`의 `deletionRequestedAt` 단일 필드(`fieldOverrides`, 기존 `dirtyAt` 항목과 같은 모양: COLLECTION·COLLECTION_GROUP 오름차순).
  - Flowlog `tools/account-deletion/README.md` 맨 위에 "배포본은 pfkfks-main의 `functions/flowlog-account-deletion.js`" 한 줄.
- **E. App Check 배선 (꺼져 있음)** (`public-flowlog/shared/appcheck.js`, `public/shared/appcheck.js`, 두 `shared/firebase.js`)
  - reCAPTCHA v3 공급자, CDN 10.12.5, 사이트 키 상수가 빈 문자열이면 아무것도 안 함, 오류가 나도 페이지를 깨지 않음.
    `getPfkfksFirebaseApp()`의 앱 초기화 직후 호출.
  - 두 호스팅 대상은 서로의 파일을 불러올 수 없어서 `public/shared/appcheck.js`에 같은 내용의 복사본을 뒀다(지시서는 한 파일).
  - 이 경로를 안 거치는 초기화(건드리지 않음): `public/football/auth.js`, `public/fm24/datasource.js`(각자 `initializeApp`).
    `admin/debug.js`, `admin/export_data.js`는 Node용 Admin SDK 스크립트라 App Check 대상이 아니다. `admin/`에 웹 모듈은 없다.
  - `tests/statistics-entry-once.browser.cjs`의 SDK 가짜 목록에 `firebase-app-check.js`를 더했다. 안 더하면 통계 페이지가 빈 모듈을 받아
    멈춘다(빼고 돌려서 실패하는 것 확인).
  - README에 "Flowlog 계정 삭제 (`/account/delete/`)와 App Check" 절(켜는 순서: 콘솔에서 reCAPTCHA v3로 등록 → 사이트 키 두 파일에 →
    지표 확인 → 모든 웹 진입점이 덮인 뒤 Firestore 적용), 경로 표와 컬렉션 표에 한 줄씩.
- **F. 계획 문서** (`docs/flowlog-release-plan.md`): 4.1절을 "14일 유보 예약으로 바뀜 + 이유 + 이번에 들어간 것 + 남은 일(소유자)"로
  다시 썼고, 4.3절 삭제 URL, 7절에 "pfkfks-main (2026-10-20)" 항목. 1·2절은 그대로.

바뀐 파일(`git status --short`, pfkfks-main):
```
 M README.md
 M docs/flowlog-release-plan.md
 M firebase.json
 M firestore.indexes.json
 M firestore.rules
 M functions/index.js
 M public-flowlog/flowlog.css
 M public-flowlog/index.html
 M public-flowlog/privacy/index.html
 M public-flowlog/shared/firebase.js
 M public/shared/firebase.js
 M tests/flowlog-rules.emulator.cjs
 M tests/statistics-entry-once.browser.cjs
?? functions/flowlog-account-deletion.js
?? public-flowlog/account/          (index.html, delete.js, delete.css, deletion-policy.js)
?? public-flowlog/shared/appcheck.js
?? public/shared/appcheck.js
?? tests/flowlog-account-delete-page.test.mjs
?? tests/flowlog-account-deletion.test.cjs
```
Flowlog: ` M tools/account-deletion/README.md`. 두 저장소에 node_modules 없음.

## 확인한 것 (어떻게)

도구는 저장소 밖 `<scratchpad>/web-tools/`에 설치(firebase-tools 14, playwright 1.48.2, npm의 Chromium 패키지).

- 규칙: `cd pfkfks-main && <web-tools>/node_modules/.bin/firebase emulators:exec --only firestore --project demo-flowlog-rules "node tests/flowlog-rules.emulator.cjs"`
  → `31 Flowlog Firestore rules assertions passed`(기존 15 + 새 16).
- 새 단위 테스트: `node --test tests/flowlog-account-deletion.test.cjs` → 11개 통과. `node --test tests/flowlog-account-delete-page.test.mjs` → 6개 통과.
- 저장소 단위 테스트 전체: `node --test tests/*.test.cjs tests/*.test.mjs` → 124개 통과(새 17 포함). README의 `--test-isolation=none`은
  이 환경의 Node 22.22에 없는 옵션이라 `--experimental-test-isolation=none`으로도 돌려 124개 통과.
- 문법: `node --check functions/index.js functions/flowlog-account-deletion.js` → 통과.
- 함수 모듈 불러오기: `functions/`를 저장소 밖으로 복사해 `npm ci` 후 `require("./index.js")` → `purgeDeletedFlowlogAccounts`가
  함수로 내보내지고 리전 asia-northeast3, 일정 `0 4 * * *` Asia/Seoul로 등록됨(내보내기 17개).
- **실제 Admin SDK로 삭제 작업**(지시서 밖 추가 확인, 임시 스크립트): Firestore + Auth 에뮬레이터(저장소 `firebase.json`에 Auth 에뮬레이터 설정이
  없어 임시 설정 파일 사용)에서 사용자 4명(15일 지난 예약, 보호 계정 예약, 오늘 예약, 예약 없음)을 만들고 `createAccountPurgeJob` 실행 →
  `{candidates:2, done:1, refused:1, failed:0}`, 지난 예약 계정은 `users/{uid}` 아래·문서·`userDistCaches`·Auth 사용자 모두 없어지고
  `deletionLog`는 `completedAt` 한 칸만, 나머지 셋은 그대로. 컬렉션 그룹 질의와 `listCollections`/`recursiveDelete`가 실제로 동작함.
- 삭제 페이지 브라우저 확인(임시 스크립트, Firebase SDK만 가짜, 1280px와 390px): 로그인 전 화면 → 로그인 → 예약 없음 → "삭"만 입력하면 확정 버튼 꺼짐 →
  쓰기 실패 시 오류 문구와 문서 없음 → "삭제" 입력 후 예약 → 쓴 문서의 칸이 두 개, 요청자 `web`, "남은 기간 14일" → 3.5일 지난 예약은 "11일" →
  취소하면 두 칸 사라짐 → 15일 지난 예약은 "삭제 처리 중"·버튼 없음 → 관리자 계정은 안내만 → 로그아웃. 사이트 키가 비어 있어 App Check 초기화 0회.
  페이지 오류 0, 390px 가로 넘침 없음. 모바일 스크린숏을 눈으로 확인.
- 꼬리 링크 폭: `/`, `/privacy/`, `/account/delete/`를 320·390·1280px로 열어 가로 넘침 0(수정 전 랜딩 390px에서 25px, 320px에서 95px 넘침).
- 기존 브라우저 테스트(위 Chromium, `PLAYWRIGHT_MODULE`로 대체): `statistics-entry-once` 통과, `statistics-activity-edit` 통과.

## 확인 못 한 것

- 실제 프로젝트 배포와 운영 데이터: 규칙·인덱스·함수·Hosting 모두 배포 안 함. 인덱스가 실제로 만들어지는지, 예약 함수가 운영에서 도는지 확인 못 함.
- `updateActivitySummary`의 건너뛰기 연결: 판정 함수는 단위·에뮬레이터로 확인했지만, Functions 에뮬레이터에서 트리거가 실제로 건너뛰는지는 확인 못 함
  (`index.js`는 문법 검사와 불러오기만).
- 실제 Google 로그인 팝업, 실제 Firestore SDK로 웹 페이지가 쓰고 지우는 것(브라우저 확인은 가짜 SDK). 다만 같은 모양의 쓰기는 규칙 에뮬레이터에서 확인.
- App Check를 실제로 켠 동작(사이트 키 없음).
- `tests/activity-summary.emulator.cjs`: `functions/node_modules`가 저장소 안에 있어야 돌아가서 안 돌림(그 파일은 안 바꿈).
- `tests/condition-survey.browser.cjs`: Playwright 경로가 코드에 고정돼 있어 이 환경에서 못 돌림(바뀐 파일을 불러오지 않는 테스트).
- `tests/blog-public.browser.cjs`: 이 환경에서 실패하지만, 바꾸기 전 `public/shared/firebase.js`로 되돌려도 똑같이 실패해서 환경(외부 CDN) 문제로 판단.
- Android 앱에서 웹으로 한 예약을 보고 취소하는 흐름(앱 쪽은 이번 범위 밖).

## 알려진 문제

- 직원 계정은 함수 코드에 ID가 없어 `FLOWLOG_ADMIN_UIDS` 환경변수를 넣어야 함수에서 막힌다. 규칙은 이미 막으므로 새로 예약될 수는 없지만,
  규칙 배포 전에 생긴 예약이 있으면 환경변수 없이는 지워질 수 있다.
- 삭제되지 않는 계정 연결 데이터: `flowlogSurveyResponses`(마감된 관심 조사), `previewResponses`(`userId` 칸으로만 연결). 지울지 소유자 결정.
- 웹에서 예약하면 폰에 남은 기록은 그대로다(페이지와 처리방침에 적음). 그 폰이 다시 로그인하면 예약 취소를 제안받는다(앱 동작).
- `deletionLog/{uid}`는 영구히 남는다(시각만). 보존 기간을 정할지 결정 필요.
- `appcheck.js` 두 복사본은 손으로 같이 고쳐야 한다(파일 주석에 적음).
- App Check SDK 모듈은 키가 비어 있어도 모든 웹 페이지에서 한 번 내려받는다(켰을 때 첫 요청부터 토큰이 붙게 하려고 정적 import를 택함).

## 다음 작업자에게

- 배포 순서: `firebase deploy --only firestore:indexes` → `firestore:rules` → `functions:purgeDeletedFlowlogAccounts,functions:updateActivitySummary` → Hosting(`main` 푸시).
  규칙을 배포하기 전에는 웹 페이지의 예약 쓰기가 옛 규칙(필드 제한 없음)으로 통과한다 — 순서를 지킬 것.
- `functions/.env`(커밋 금지)에 `FLOWLOG_ADMIN_UIDS`로 직원 ID. 테스트 계정으로 한 번 끝까지(예약 → 콘솔에서 시각을 15일 전으로 → 다음 실행 로그 `[account-deletion] finished`).
- 14일은 세 곳(앱 `AccountDeletionPolicy`, 웹 `deletion-policy.js`, 함수 `GRACE_DAYS`) — 웹·함수 쪽은 테스트가 서로 같은지 검사한다.
- Play Console 데이터 보안 양식 삭제 URL: `https://flowlog.pfkfks.org/account/delete/`.
- 브라우저 테스트를 이 클라우드 환경에서 돌리려면 Playwright의 브라우저 다운로드 주소가 막혀 있으니, npm 레지스트리의 Chromium 패키지 + `PLAYWRIGHT_MODULE` 래퍼를 쓰면 된다
  (`--single-process`는 페이지를 여러 개 열면 브라우저가 죽으니 빼야 함). 패키지가 브라우저를 `/tmp/chromium`에 푼다.
