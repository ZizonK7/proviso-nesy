# 2026-10-20 — Flowlog 출시 준비 2차 (JSON 가져오기, 지운 기록 비우기, 계정 삭제, 영구 삭제 작업)

에이전트: 출시 준비 구현 2차 (Opus 5.5, effort high). 하위 에이전트 호출: 없음. 커밋·push: 안 함.

대상: `/home/user/Flowlog`, 브랜치 `ccr-2a22e640-e8dn8n`, 1차 커밋 7f2918b 위의 작업 트리. 네 묶음(A > C > B > D) 모두 했고 뺀 것은 없다.

**실수 하나(되돌림)**: 마지막 확인 중 `git add -N .`(새 파일을 "추가 예정"으로만 표시, 내용은 안 올림)를 실수로 한 번 실행했다. 바로 `git rm --cached --quiet`로 그 표시만 지워 원래 상태(새 파일은 추적 안 됨, 스테이지 비어 있음)로 돌렸다. 확인: `git diff --cached --stat` 출력 없음, 새 파일 5곳은 `??`.

## 한 일

### A. JSON 가져오기
- **순수 파서** `ui/viewmodel/ActivityImportParser.kt`: 내보내기 JSON(`ActivitySession` 배열)을 읽는다(BOM 허용, 모르는 필드는 무시).
  - 깨진 항목으로 세는 것: 필수 필드 없음, 타입 틀림, 분류가 빈칸, 끝이 시작보다 이름, 24시간 넘음, 미래, 길이보다 긴 duration. 시간 검사는 기존 `ManualActivityValidator`를 재사용했다.
  - 중복 판정은 셋이다. (1) 이 기기의 행 중 같은 `localActivityId`이거나 같은 legacy id를 가진 것. 계정·삭제 여부는 따지지 않는다. Room이 같은 키 행을 REPLACE로 덮어써 지운 기록을 되살리거나 다른 계정 행을 가져가 버리는 것을 막기 위해서다. (2) 현재 계정 기록 중 category+start+end가 같은 것. (3) 파일 안의 반복.
  - 결과 요약: 총 / 새 / 중복 / 깨짐 개수와 새 기록의 기간 처음–끝. JSON이 아니거나 배열이 아니면 `NotActivityJson`.
- **지시서와 다르게 한 것 (1): 길이 0 기록**: 시작=끝이어도 duration이 0이면 받는다. 앱이 체크형 기록(`DAILY_CUE_CHECK`, `durationMillis = 0L`)을 실제로 그렇게 저장하므로, "시작<끝"을 그대로 적용하면 자기 내보내기 파일을 깨진 항목으로 버린다.
- **지시서와 다르게 한 것 (2): 파일의 `id`도 유지**: 코드로 확인한 결과, 지시서가 가정한 것과 달리 원격 문서 id는 `localActivityId`가 아니다.
  - 근거: `FirebaseSyncDataSource.syncPendingActivities`의 `docId = entity.legacyId?.toString() ?: entity.activityId`. 평소 저장 경로(`ActivityRepository.insertActivity`)는 새 id를 붙이고, 매퍼가 `activityId = "legacy_activity_<id>"`, `legacyId = id`로 만든다. 그래서 문서 id는 legacy id(숫자)다.
  - 지시서대로 "새 id + 파일 localActivityId"로 넣었다면 생기는 문제: 같은 계정에 다시 올릴 때 **새 문서가 생겨 서버에 중복**이 생긴다. 게다가 나중에 복원하면 `legacy_activity_<새 id>` 행이 하나 더 생겨 폰에도 중복이 된다.
  - 그래서 새 저장 함수 `ActivityRepository.importActivities`는 파일의 `id`와 `localActivityId`를 그대로 두고 `remoteRevision`만 0으로 넣는다(동기화 상태 PENDING, 매퍼 기본).
  - 그 결과 같은 계정에 다시 올리면 원래 문서를 겨냥한다. 서버 내용이 같으면 `ActivityRevisionPolicy`가 쓰지 않고 맞춰 받고(revision 따라잡기), 웹에서 바뀌었으면 기존 충돌 창이 사용자에게 고르게 한다. 덮어쓰기도 중복도 아니다.
  - 파일 id가 0이고 `localActivityId`만 있으면 매퍼가 그 값을 activityId로 쓰고 문서 id도 그 값이 된다.
- **흐름**:
  - 설정 창 내보내기 버튼 아래에 "기록 가져오기(JSON)"를 두었다. `OpenDocument(arrayOf("application/json"))`로 파일을 고르면 `ActivityViewModel.previewActivityImport`가 `openInputStream`으로 읽어 파서를 돌린다.
  - 새 기록이 있으면 확인 창을 띄운다: "M건을 추가합니다. 중복 K건은 건너뜁니다." + 깨짐 수, 파일 안 항목 수, 기간.
  - [추가하기]를 누르면 `commitActivityImport`가 저장 직전에 키를 한 번 더 확인하고 저장한다. 로그인 상태면 바로 `syncAllPendingChanges`를 부른다.
  - 새 기록이 없으면 토스트로 중복·깨짐 수만 알린다.
- DAO에 `getAllActivityIds()`, `getAllLegacyIds()` 조회 두 개를 더했다(스키마 변경 없음).

### C. 지운 기록의 서버 내용 비우기
- `ActivityRevisionContent.forUpload(activity, deletedAt)`: 삭제된 기록이면 title "", note null, tags [], exerciseSets []로 바꾼다. `FirestoreSyncRepository.commitActivityRevision`이 이 값으로 `content`를 만든다. merge 쓰기라 빈 값으로 덮어써야 서버 내용이 지워진다.
- `mutationId`도 비운 형태로 계산한다. 서버의 `lastMutationId`(SHA-256)에 지운 제목의 해시가 남지 않게 하려는 것이다. 기존 테스트는 모두 그대로 통과했다.
- 무엇을 남겼나(근거: `docs/study-integration/firestore.proposed.rules`의 `validActivity` — revision, startTime, endTime, durationMillis(≤ 끝−시작), title(string), category(string), modifiedTime 필수):

  | 필드 | 삭제 표시(tombstone)에서 |
  |---|---|
  | title | `""` (규칙이 string을 요구해 빈 값으로 남김) |
  | note | null |
  | tags | [] |
  | exerciseSets | [] |
  | category, startTime, endTime, durationMillis, modifiedTime | 남김(규칙 필수) |
  | start_time, end_time, durationMinutes | 남김(웹용 별칭, 시각만) |
  | revision, lastMutationId, isDeleted, deletedAt | 남김(동기화 장부) |
  | id, isFavorite, linkedTodoId, linkedPetiteId, sourceType, sourceId, originalCategory | 남김(지시서 범위 밖, 아래 "알려진 문제") |

- 폰의 Room 행은 내용을 그대로 둔다(되돌리기용).
- 할 일(todos): 삭제는 이미 `deleteTodoByDocId`가 **문서째 지운다**(hard delete). 캘린더 연결 할 일은 `calendarEvents`에 완료·삭제 시각만 merge로 쓴다. 고칠 것 없음.
- 테스트 2개 추가: 삭제 tombstone에 내용이 없는지, 삭제된 기록의 mutationId가 지운 글에 영향받지 않는지.

### B. 계정 삭제 (유보 14일)
- **규칙 확인**: `users/{uid}/flowlog/account`는 두 규칙 파일 모두 소유자 쓰기가 된다. original은 `match /users/{userId}/flowlog/{document=**}` write if 본인, proposed는 `match /users/{userId}/flowlog/{documentId}` write if owns(쓸 수 없는 예외는 config의 버튼 수뿐). 경로는 바꾸지 않았다.
- **순수 로직** `data/account/AccountDeletionPolicy.kt`: `GRACE_DAYS = 14`, `state(요청 시각, 지금)` → None / Pending(남은 일수, 올림) / Expired(정확히 14일째부터), `canCancel`, `isExpired`, `isConfirmationTyped("삭제")`. 요청 시각이 폰 시계보다 미래면 "방금 요청"으로 본다. 테스트 6개.
- **서버** `data/account/AccountDeletionRemote.kt`: 삭제 예약 쓰기(`deletionRequestedAt` = 서버 시각, `deletionRequestedBy = "app"`, merge), 읽기, 취소(두 필드 `FieldValue.delete()`).
- **설정 창** "계정" 묶음에 "계정과 데이터 삭제" 줄과 [삭제 요청] 버튼을 두었다(로그인 상태에서만 보인다).
  - 1차 확인: 지시서 문구에 "먼저 내보내기로 파일을 저장해 두세요"를 덧붙였다.
  - 2차 확인: '삭제'를 입력해야 버튼이 켜진다.
- **실행** (`MainActivity.deleteAccountAndData`):
  1. 서버 예약을 먼저 쓴다. 실패하면 폰 데이터도 그대로 두고 "인터넷 연결 확인" 토스트를 띄운다.
  2. 업로드와 캘린더 구독을 막는다(`accountDeletionGate`).
  3. `DeviceDataWiper.wipe`: 알람 취소 → 알림 전부 지움 → Room `clearAllTables`(IO 스레드) → SharedPreferences 비움 → 위젯 갱신. 알람 조회가 현재 계정 행을 읽으므로 로그아웃 전에 한다.
     - 알람 취소는 기존 cancel 함수를 재사용하는 `AlarmRescheduler.cancelAll`이다. 자동 버튼·공부 계획·타임테이블 할 일은 각 스케줄러에 `cancelAll()`(기존 `cancel` 반복)을 더해 쓰고, 양치·식사·간식, 집중 모드, 비활동 알림, 루틴 목표, 자정 동기화는 기존 함수를 그대로 부른다.
     - SharedPreferences는 Firebase·Google·AndroidX 라이브러리 내부 파일만 빼고 비운다. 실행 중인 SDK를 헷갈리게 할 수 있고, Flowlog 기록은 들어 있지 않기 때문이다.
  4. `auth.signOut()` + Credential Manager `clearCredentialState`. 로그인 계정(Auth)은 지우지 않는다.
  5. 토스트 "삭제를 예약했습니다. 14일 안에 다시 로그인하면 되돌릴 수 있습니다."를 띄우고 화면을 새로 시작한다. ViewModel 메모리에 남은 진행 중 타이머를 버리기 위해서다.
- **다시 로그인할 때**: 로그인 직후 작업(익명 기록 이관·복원·업로드·알람·캘린더 구독)을 `runSignedInSetup`으로 묶었다. 그 **앞에서** `account` 문서를 읽는다.
  - 14일 안이면: "삭제 예약이 있습니다(남은 n일). 취소하고 기록을 복원할까요?"
    - [취소하고 복원] → 필드 지움 → `restoreFromFirestore` → 평소 로그인 작업.
    - [그대로 둠] → 로그아웃.
  - 14일이 지났으면: "삭제 처리 중인 계정입니다…" 안내 → [확인] → 로그아웃.
  - 창은 답하기 전에는 닫히지 않는다. 답을 기다리는 동안은 업로드·캘린더 구독을 막는다.
  - 로그인 버튼 경로(`runAccountSync`)가 로그인 직후 따로 업로드하던 것도 예약이 있으면 건너뛴다.

### D. 영구 삭제 예약 작업 (`tools/account-deletion/`)
- `package.json`: firebase-functions ^6.1.0, firebase-admin ^12.7.0, node 20, `npm test` = `node --test`. `.gitignore`로 node_modules 제외.
- `selection.js`(순수): 14일 기준 대상 uid 고르기, Timestamp·Date·숫자 처리, `users/{uid}/flowlog/account` 경로에서만 uid 뽑기, 지울 사용자 컬렉션 목록 `USER_SUBCOLLECTIONS`. README의 "Firestore paths used by the Android app" 목록은 주석에 그대로 적었다.
- 지울 경로:
  - `users/{uid}/flowlog` 아래 전체(account 문서는 맨 마지막).
  - README의 `activityStudyLinks`, `interactionDecisions`.
  - 규칙에 정의된 다른 사용자 컬렉션 `studyCourses`, `studyRecords`, `previewUsage`, `previewCards`.
- `purge.js`: 계정 하나를 지우는 순서. 사용자 컬렉션 → flowlog의 account 외 문서(하위 포함 `recursiveDelete`) → Auth 사용자(이미 없으면 통과) → `deletionLog/{uid}`(`completedAt`만) → **account 문서 맨 마지막**. 그래서 중간에 실패해도 예약이 남아 다음 날 다시 시도된다. 지우기 직전에 예약을 다시 읽어 그새 취소된 계정은 건너뛴다.
- `index.js`: `onSchedule('every day 04:00', Asia/Seoul)`이 collection group `flowlog`에서 `deletionRequestedAt <= 지금−14일`인 문서를 찾는다. 실패는 삼키지 않고 모두 시도한 뒤 예외를 던진다. 로그에는 uid·내용을 남기지 않고 개수만 남긴다.
- `README.md`: 동작 순서, 다중 codebase `firebase.json` 예, **collection group 인덱스(`fieldOverrides`) 필요**, 배포 명령, Blaze 전제, "실제 프로젝트에서 돌려 보지 않음" 주의.
- 테스트 `selection.test.js` 6개, `purge.test.js` 4개(가짜 db/auth로 순서·재시도·취소 확인).

### 문서
- `CHANGELOG.md` Unreleased 맨 위에 네 항목.
- `README.md` Data & Sync에 가져오기 한 단락, tombstone·계정 삭제 한 단락.

### 바뀐 파일
`git diff --stat`: 15 files changed, 685 insertions(+), 34 deletions(-).
- 바뀐 파일: CHANGELOG.md, README.md, MainActivity.kt, RoomActivityLocalDataSource.kt, ActivityDao.kt, ActivityRevisionContent.kt, FirestoreSyncRepository.kt, ActivityRepository.kt, AlarmRescheduler.kt, AutoButtonScheduler.kt, PlannedTodoReminderScheduler.kt, StudyPlanAutoStartScheduler.kt, ActivityViewModel.kt, strings.xml, ActivityRevisionContentTest.kt.
- 새 파일:
  - `app/src/main/java/com/example/flowlog/data/account/AccountDeletionPolicy.kt`
  - `app/src/main/java/com/example/flowlog/data/account/AccountDeletionRemote.kt`
  - `app/src/main/java/com/example/flowlog/data/account/DeviceDataWiper.kt`
  - `app/src/main/java/com/example/flowlog/ui/viewmodel/ActivityImportParser.kt`
  - `app/src/test/java/com/example/flowlog/data/account/AccountDeletionPolicyTest.kt`
  - `app/src/test/java/com/example/flowlog/ui/viewmodel/ActivityImportParserTest.kt`
  - `tools/account-deletion/`의 `.gitignore`, `README.md`, `package.json`, `index.js`, `purge.js`, `selection.js`, `purge.test.js`, `selection.test.js`

## 확인한 것 (어떻게)
- `bash ./gradlew :app:compileDebugKotlin :app:testDebugUnitTest -PofflineValidation=true --console=plain`(ANDROID_HOME은 지시서 경로) → BUILD SUCCESSFUL.
- 결과 XML 합산: **143개**(1차 121 + 새 22: 가져오기 14, tombstone 2, 계정 삭제 정책 6), 실패·오류·건너뜀 0.
- `node --test tools/account-deletion/*.test.js` → 10개 통과.
  - 지시서의 `node --test tools/account-deletion`은 Node 22에서 폴더를 스크립트 경로로 읽어 `index.js`를 실행하려다 실패한다. 그래서 테스트 파일을 직접 넘겼다. 폴더 안에서 `npm test`도 된다.
- npm 설치는 프록시로 됐다. 저장소가 아니라 스크래치 폴더에 복사해 `npm install`(firebase-functions 6.6.0, firebase-admin 12.7.0)했다. `index.js`가 실제 의존성으로 불러와지고 `purgeExpiredAccountDeletions`의 일정이 `every day 04:00` / `Asia/Seoul`로 등록되는 것까지 확인했다. 저장소에는 node_modules·lock 파일을 남기지 않았다.
- 새 코드에서 uid처럼 보이는 28자 이상 문자열을 찾았다 → 함수 이름뿐. 규칙 파일에 있는 관리자 uid는 옮겨 적지 않았다.

## 확인 못 한 것
- **기기에서 전부 미확인**:
  - 파일 선택 창에 내보낸 .json이 보이는지(파일 앱에 따라 MIME이 다르게 잡힐 수 있음).
  - 가져온 기록이 화면·통계에 바로 보이는지.
  - 계정 삭제 뒤 폰이 정말 비고 로그아웃되는지, 다시 로그인했을 때 확인 창과 복원.
  - Credential Manager 초기화 뒤 다음 로그인에서 계정을 다시 고르게 되는지.
- **실제 Firestore·Functions 미확인**: 규칙 아래에서 예약 쓰기·취소가 통과하는지(규칙 문장만 읽음), tombstone 쓰기가 proposed 규칙을 통과하는지(문장 대조만), collection group 인덱스, 예약 작업 배포와 실행.
- 다시 올릴 때 "원래 문서를 겨냥한다"는 것은 코드 경로를 읽어 확인한 것이고 실제 업로드는 안 해 봤다.
- 릴리즈 빌드와 lint는 돌리지 않았다.

## 알려진 문제
- 로그인 직후 예약 확인 읽기가 실패하면(오프라인 등) 평소대로 진행한다. 이때 익명 기록이 이관·업로드될 수 있다. 다음 실행 때 다시 확인한다.
- 답을 기다리는 동안에도 Firebase SDK의 다른 경로(예: 백그라운드 WorkManager 삭제 동기화)는 막지 않았다. 폰을 비운 뒤라 올릴 것이 거의 없다.
- 삭제 직후 SharedPreferences가 비므로 정확 알람 설명 창(1차)도 처음처럼 다시 한 번 뜬다.
- tombstone에 `sourceId`, `linkedPetiteId`, `linkedTodoId`, `originalCategory`가 남는다(식별자·분류). 더 비울지는 메인 판단. 이미 서버에 올라간 옛 tombstone은 다시 올라갈 때만 비워진다. 일괄 정리는 하지 않았다.
- 1.x 버전으로 이미 올라간 삭제 기록이 업로드 성공 뒤 응답 처리만 실패해 PENDING으로 남은 경우: mutationId 계산이 바뀌어 다음 시도 때 충돌 창으로 갈 수 있다(드묾).
- 영구 삭제 작업이 지우지 않는 것:
  - 최상위 `flowlogSurveyResponses`(웹 설문). 사용자 연결 필드를 확인하지 못했다.
  - `users/{uid}` 문서 자체의 필드(하위 컬렉션만 지움).
  - Auth 사용자 삭제는 같은 Firebase 프로젝트의 다른 사이트 기능 로그인도 없앤다(README에 적음).
- 가져오기는 할 일(todos)·설정은 다루지 않는다(내보내기가 활동만 내보냄).

## 다음 작업자에게
- 체크리스트의 "무료 사용자의 기기 이전 = 파일"은 이번 가져오기로 활동 기록만 채워진다. 할 일까지 옮기려면 내보내기 형식부터 넓혀야 한다.
- 웹 삭제 요청 링크와 처리방침 문구(`docs/STORE_RELEASE_DRAFTS.md`의 "구현 뒤")는 웹 저장소 몫이다. 데이터 안전 양식의 "구현 뒤" 표시는 이번 앱 쪽 구현으로 지울 수 있다(배포 뒤).
- 예약 작업 배포 순서: 인덱스 → 함수 → 테스트 계정으로 `deletionRequestedAt`을 15일 전으로 바꿔 한 번 돌려 보기(README "Deploy" 5번).
- 기기 확인 추천 순서: 내보내기 → 기록 하나 삭제 → 가져오기(1건 추가, 나머지 중복) → 로그인 상태에서 계정 삭제 → 같은 계정 재로그인 → 남은 14일 창 → 취소하고 복원 → 기록이 돌아오는지.
