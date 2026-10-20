# 2026-10-20 — Flowlog PC 웹 앱 (`/app/`)

에이전트: PC 웹 앱 구현 (Opus 5.5, effort high). 하위 에이전트 호출: 없음. 커밋·push: 안 함.

대상: 비공개 웹 저장소(`pfkfks-main`), 브랜치 `ccr-2a22e640-e8dn8n`, 작업 트리만. Flowlog 앱 저장소는 읽기만 했다
(작업 트리와 `origin/ccr-1cb50339-vdsr0x`). 비공개 저장소의 코드·uid·키는 여기에 옮기지 않았다.

## 한 일
- **옮기기**: `public/test1/` 미리보기 시안(가짜 데이터)을 지우고 `public-flowlog/app/`에 실제 앱으로 만들었다 —
  `index.html`, `app.js`(화면·동작, 시안의 PC·휴대폰 두 화면 구조 유지), `app-store.js`(서버 읽기·쓰기, 새 파일),
  `app.css`, `app-pc.css`. `firebase.json`: main 타깃의 `/test1` rewrite 삭제, flowlog 타깃에 `/app`·`/app/**`.
  Firebase는 공용 `shared/firebase.js`(App Check 배선 포함)로 초기화.
- **로그인**: 통계 페이지와 같은 Google 팝업 로그인. 로그아웃 상태는 "로그인하면 폰의 기록이 보입니다" 안내 화면만
  (가짜 데이터·서버 읽기 없음). 계정 버튼 → 로그아웃.
- **오늘 탭**: 오늘 0시 −48시간 창의 활동(어제 같은 시각 비교용 포함) + 타이머 문서 `onSnapshot`. 시작·정지·취소·
  제목·분류 변경이 모두 타이머 문서 트랜잭션. 정지 = 같은 트랜잭션에서 활동 문서 revision 1 생성 + 문서 `stopped`.
  30초 미만은 기록 안 함(시안 그대로). 할 일 ▶ = 분류 `TODO`, `linkedTodoId`(할 일 문서 id). 폰에서 멈춘(paused) 문서는
  "일시정지"로 보이고 "이어서" 가능. 빠른 타이머(양치·간식)·집중 모드는 이 창에서만 세고, 빠른 타이머는 끝나면 기록.
  시안의 고정 루틴 블록(가짜)은 빼고 반복 루틴 페이지 링크로, "추천 흐름"은 "어제 이 시간에 한 일"로 바꿨다.
- **기록 탭**: 최근 30일 쿼리(`startTime` 숫자 ≥, 내림차순, 500건), 날짜별 묶음, 정렬·검색·분류 거르기 유지.
  수정은 통계 페이지 코드(`statistics/study-link-store.js`의 load·save, revision +1, 연결 수업 구간 확인) 그대로,
  삭제는 앱과 같은 tombstone(`isDeleted`·`deletedAt`, 제목·메모·태그·운동 세트 비움 — 앱 `ActivityRevisionContent.forUpload`로 확인),
  즐겨찾기도 revision +1. 직접 추가(날짜·시작·끝, 끝이 이르면 다음 날) = revision 1. 되돌리기는 서버에 역동작을 쓴다.
- **할 일 탭**: 미완료 할 일 읽기, 추가(앱 `TodoItem.toRemoteMap` 13개 필드, `id: 0`), 완료(`isCompleted`·`completedAt`·
  `updatedAt`), 삭제(앱처럼 문서 삭제), 쌓인 시간(`accumulatedSeconds`) 표시와 정지 때 더하기. 앱 할 일에는 활동 분류가 없어
  종류(일반·오늘·과제·복습)와 날짜로 열을 나눴다. Daily Cues는 읽기 전용(▶ 시작만).
- **통계 탭**: `summary/daily` 날짜 범위 쿼리(30일 전 ~ 어제) + 오늘 원본. 요약이 없으면 "앱에서 기록이 올라오면 보입니다".
- **규칙**: `users/{uid}/flowlog/timer` 조항 — 소유자만 읽기·쓰기·삭제, 아홉 필드만·모두, 상태 세 값, `updatedAt == request.time`,
  `updatedBy` app/web. 일반 쓰기 조항 둘에서 `timer` 제외, 관리자 읽기에서도 제외(`document[0] != 'timer'`).
- **테스트**: 새 `tests/flowlog-app.browser.cjs`(가짜 Firestore), 규칙 에뮬레이터 검사 21개 추가.
- **문서**: README 페이지 표·폴더 트리, `tests/README.md`, `docs/flowlog-release-plan.md` 4.4(타이머 문서 모양·뜻·폰 쪽 남은 일·
  가져오기 표)와 7절 항목.
- 지시서 밖: 같은 날 Flowlog 작업 트리에 폰 쪽 타이머 공유 코드(`2026-10-20-flowlog-timer-sync.md`)가 이미 있는 것을 보고,
  4.4에 두 쪽의 맞물림(웹 정지 → 폰은 기록 없이 끔, 폰 정지 → 웹은 다시 읽기만)과 규칙 사본 차이를 적었다.

## 확인한 것 (어떻게)
도구: `S=/tmp/claude-0/-home-user/7c40c1dc-b607-5f78-9497-ffe487ef55d0/scratchpad`, `PLAYWRIGHT_MODULE=$S/web-tools/pw-wrapper`,
`TEMP=$S/apptest`, `NODE_PATH=$S/fn-deps/node_modules`, 웹 저장소 루트에서.
- `node tests/flowlog-app.browser.cjs` → `PASS ... 63 checks`(로그인 전 1280·390, 오늘 창 쿼리, 타이머 문서 아홉 필드·서버 시각,
  정지 = 트랜잭션 1회로 활동 revision 1, 되돌리기 → 타이머 복귀·기록 tombstone revision 2, 취소, paused·이어서,
  할 일 연결(옛 할 일은 숫자 id, 앱 할 일은 null, 초 더하기), 할 일 추가·완료·삭제, 30일 쿼리·검색·정렬, 수정 revision 2·
  삭제 tombstone 3·되돌리기 4, 즐겨찾기, 직접 추가, 요약 쿼리·차트, 요약 없음 안내, 390 휴대폰 화면·가로 넘침 없음, 페이지 오류 0).
- `$S/web-tools/node_modules/.bin/firebase emulators:exec --only firestore --project demo-flowlog-rules "node tests/flowlog-rules.emulator.cjs"`
  → `52 Flowlog Firestore rules assertions passed`(기존 31 + 타이머 21).
- 기존 브라우저 테스트: `statistics-activity-edit`, `statistics-entry-once`, `statistics-summary-path` PASS,
  `node -r $S/pw-preload.cjs tests/condition-survey.browser.cjs` PASS(이 테스트는 Playwright 경로가 고정이라 preload로 바꿔 끼움).
- `node --test tests/*.test.cjs tests/*.test.mjs` → 124개 통과(condition-model 3, 계정 삭제 11, 삭제 페이지 6, study-links 1 포함).
- `node --check`: `app.js`, `app-store.js`, 두 테스트 파일 통과. JSON 파싱: `firebase.json` 통과.
- 화면: 1280(오늘·통계), 390(할 일) 스크린샷을 눈으로 확인(테스트에서는 아이콘 글꼴을 막아 아이콘이 글자로 보임).
- 폰이 웹 변경을 가져오는지: Flowlog `FirebaseRestoreDataSource`, `FirebaseSyncSupport`, `RemotePullCursor`, `MainActivity`,
  `ActivityViewModel`/`TodoViewModel` 호출부를 읽어 판단(작업 트리와 `origin/ccr-1cb50339-vdsr0x`의 `data/sync/*`는 로그 문구 외 같음).

| 웹에서 한 일 | 폰이 가져오나 | 언제·어느 코드 |
|---|---|---|
| 활동 새로 만들기 | 가져온다 | `refreshStudy` → `restoreActivities(incremental)`: `modifiedTime ≥ 커서 − 24h`. 로그인 직후·앱을 열어 네트워크 콜백·자정 알람(`syncEligible`, 15분에 한 번, 폰 타이머 RUNNING이면 미룸), 10분 이상 활동 저장·할 일 동작 뒤(`syncAll`, 매번) |
| 활동 수정·삭제(tombstone)·되돌리기 | 가져온다 | 같은 경로, 원격 revision이 크고 폰에 안 올린 수정이 없을 때 |
| 할 일 새로 만들기·완료·삭제·시간 더하기 | **안 가져온다 — 앱 쪽 수정 필요** | `restoreTodos`는 새 설치(폰의 활동·할 일 0개) 로그인과 계정 삭제 취소 때만. 폰이 그 할 일을 다시 올리면 웹 변경이 덮이고, 웹에서 지운 할 일이 되살아난다 |
| 진행 중 타이머 | 커밋된 코드는 안 읽음, 작업 트리(미커밋)는 앱이 화면에 있을 때 읽음 | `RemoteTimerSync.listen` |

## 확인 못 한 것
- 실제 Firebase(로그인 팝업, 실제 Firestore 쓰기·트랜잭션·`onSnapshot`, 오프라인, App Check)와 실제 브라우저 글꼴. 가짜 어댑터는
  규칙·네트워크 재시도를 흉내 내지 않는다(규칙은 에뮬레이터로 따로 확인).
- 배포된 `flowlog.pfkfks.org/app/` 동작(배포 안 함), Hosting rewrite 실제 적용.
- 폰과 함께 쓰는 흐름(웹 시작 → 폰 표시, 폰 정지 → 웹 갱신 등) — 폰 쪽 코드는 미커밋이고 기기 없음.
- 폰이 웹에서 만든 활동을 실제로 받는지(코드 읽기로만 판단). Android의 네트워크 콜백이 등록 즉시 불리는지도 기기 미확인.
- 900–1060px 같은 중간 폭, 키보드 단축키 전부, 자정 넘김(`refreshSlow`) 동작.

## 알려진 문제
- 폰은 웹에서 만든·완료한·지운 할 일을 가져오지 않는다(위 표). 웹에서 할 일을 고치면 폰과 어긋나고, 폰이 다시 올리면 웹 변경이 사라진다.
- 활동의 `linkedTodoId`는 숫자만(앱이 `getLong`으로 읽음). 앱 전용 할 일(`id: 0`)에 연결해 기록하면 활동에는 연결이 남지 않는다
  (타이머 문서와 할 일의 쌓인 시간에는 남음).
- 폰 쪽 타이머 쓰기는 트랜잭션 없는 병합이라, 폰이 웹 변경을 받기 전에 정지하면 기록이 두 개 생기거나 웹 타이머가 덮일 수 있다.
  웹이 다른 활동을 시작하면 폰에서 돌던 타이머를 웹이 기록으로 닫는다(폰의 메모·운동 세트는 빠짐).
- 빠른 타이머·집중 모드는 그 창에서만(창을 닫으면 사라짐). Daily Cue 완료 표시는 읽기 전용.
- 되돌리기는 이 창에서 한 동작만, 서버에 역동작을 쓰는 방식이라 그 사이 다른 기기가 바꿨으면 실패하거나 덮을 수 있다.
- 기록 수정은 통계 페이지 저장 코드를 그대로 써서 수업·복습 데이터(`studyCourses`, `studyRecords`)를 매번 읽고 연결 문서도 다시 쓴다.
- 규칙 원본(`validTimer`, `document[0] != 'timer'`)과 Flowlog 저장소 사본(`validSharedTimer`, `document != path('timer')`)의 표현이 다르다(뜻은 같음).
- 웹이 다른 창에서 정지된 걸 알아채는 건 `deviceId`가 다를 때만이다(같은 브라우저의 두 창은 같은 id).

## 다음 작업자에게
- 배포 순서: `firebase deploy --only firestore:rules` 먼저, 그다음 Hosting(`main` 푸시가 두 타깃 배포). 규칙 없이 Hosting만 나가면
  타이머 문서가 일반 조항으로 모양 검사 없이 써진다. 인덱스 추가는 필요 없다(단일 필드 범위·정렬만 씀).
- 폰 앱: 할 일 가져오기(주기 동기화에 `todos` 증분 — `updatedAt` 기준 `RemotePullCursor` 같은 방식)와, 정지할 때 타이머 문서를
  트랜잭션으로 확인하는 것을 권한다. 타이머 문서 모양은 `docs/flowlog-release-plan.md` 4.4가 기준.
- 웹 화면의 "폰 앱 연동은 준비 중" 안내(`index.html`의 `.app-note`)는 폰 쪽이 배포되면 고친다.
- 구독 기능(결제)은 이번 범위 밖. `/app/`은 로그인한 누구나 쓸 수 있다.
- `tests/condition-survey.browser.cjs` 등 일부 옛 테스트는 `PLAYWRIGHT_MODULE`을 안 읽는다 — 이 환경에선 `node -r $S/pw-preload.cjs`로 돌린다.
