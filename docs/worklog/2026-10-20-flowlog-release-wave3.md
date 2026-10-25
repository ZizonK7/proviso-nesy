# 2026-10-20 — Flowlog 출시 준비 3차 (App Check, 규칙 사본 보강과 규칙 테스트)

에이전트: 출시 준비 구현 3차 (Opus 5.5, effort high). 하위 에이전트 호출: 없음. 커밋·push: 안 함.

대상: `/home/user/Flowlog`, 브랜치 `ccr-2a22e640-e8dn8n`, 2차 커밋 d359e05 위의 작업 트리. 두 묶음 모두 했다. git 상태를 바꾸는 명령은 쓰지 않았다(이번엔 실수 없음).

## 한 일

### A. Firebase App Check (Play Integrity)
- `gradle/libs.versions.toml`에 `firebase-appcheck-playintegrity`, `firebase-appcheck-debug`를 버전 없이 등록했다. BoM 34.7.0이 둘 다 19.0.1로 정한다.
- `app/build.gradle.kts`에 `implementation(libs.firebase.appcheck.playintegrity)`, `debugImplementation(libs.firebase.appcheck.debug)`를 더했다.
- **지시서와 다르게 한 것**: 지시서는 `BuildConfig.DEBUG`로 분기하라고 했지만, 디버그 라이브러리가 `debugImplementation`이라 릴리즈 빌드에는 `DebugAppCheckProviderFactory` 클래스가 없다. 그래서 공통 코드에서 이름을 부르면 릴리즈가 컴파일되지 않는다. 대신 빌드 종류별 소스 폴더로 나눴다.
  - `app/src/debug/java/com/example/flowlog/appcheck/AppCheckProviders.kt` → `DebugAppCheckProviderFactory`
  - `app/src/release/java/com/example/flowlog/appcheck/AppCheckProviders.kt` → `PlayIntegrityAppCheckProviderFactory`
  - 공통 `app/src/main/java/com/example/flowlog/appcheck/FlowlogAppCheck.kt`의 `install()`은 `runCatching`으로 감싸 실패하면 로그만 남긴다. google-services.json이 없어 `FirebaseApp`이 없을 때도 앱이 죽지 않는다.
- Application 클래스가 없어서 `MainActivity.onCreate`의 `super.onCreate` 바로 다음, Crashlytics 줄 앞에서 부른다. `FirebaseApp`은 그보다 먼저 `FirebaseInitProvider`가 초기화한다.
- README "Firebase Setup" 9번: App Check에 앱 등록(Play Integrity), 디버그 토큰 등록, "콘솔에서 적용(enforce)을 켜기 전까지는 아무 영향 없음".

### B. 규칙 사본 보강 + 규칙 테스트
`docs/study-integration/firestore.proposed.rules`(저장소 사본)에서 바꾼 것. 줄마다 이유 주석을 달았다.

1. **`flowlogSurveyResponses`**:
   - 허용 조건: `request.auth != null`, 문서 id = `request.auth.uid`(1인 1건, 수정은 관리자만이라 두 번째 응답은 거절).
   - 필드는 `keys().hasOnly(['userId','answers','note','createdAt'])`로 묶었다. `userId`는 본인, `answers`는 문자열 목록 10개 이하·각 2,000자 이하, `note`는 선택·2,000자 이하, `createdAt`은 서버 시각이다.
   - 주석에 두 가지를 적었다: 웹이 비로그인 응답을 받으면 익명 로그인이 필요하다는 것, **필드 목록은 웹 양식과 맞춰야 한다는 것**(웹 저장소가 없어 실제 필드를 확인하지 못했다).
2. **`users/{userId}/flowlog/...` 일반 쓰기**:
   - 문서 하나·기록 하나의 최상위 필드를 100개 이하로 막았다. 앱이 쓰는 문서는 config·metadata 몇 개, 활동·할 일류 기록 약 25개라 깨지지 않는다.
   - 문자열 길이 상한은 필드를 모르는 일반 경로에서 걸 수 없어 넣지 않았다.
   - 할 일(todos)은 별도 허용 규칙이 있어서 이 상한이 적용되지 않는다(규칙은 OR로 합쳐진다).
   - `flowlog/account` 문서는 `deletionRequestedAt`, `deletionRequestedBy` 두 필드만 받는다. `deletionRequestedAt`은 서버 시각(`request.time`)이어야 하고, `deletionRequestedBy`는 'app' 또는 나중의 웹 요청용 'web'이다. 두 필드를 지운 빈 문서(=취소)도 통과한다.
3. **uid 리터럴 → 자리표시자**:
   - 사본의 관리자·직원 uid를 `"__FLOWLOG_ADMIN_UID__"`, `"__FLOWLOG_WORK_STAFF_UID__"`로 바꿨다.
   - `tools/study-integration/prepare-rules.cjs`가 에뮬레이터용 사본에서 이를 환경변수 `FLOWLOG_ADMIN_UID`/`FLOWLOG_WORK_STAFF_UID`로 채운다. 값이 없으면 시험용 `test-admin-uid`/`test-work-staff-uid`를 쓴다.
   - 기존 테스트가 관리자 uid 리터럴을 쓰던 한 줄은 같은 기본값을 읽는 `adminUid`로 바꿨다. 실제 uid는 새로 쓰지 않았다.
- `tools/study-integration/rules-test.cjs`에 18개를 더해 15 → **33**이 됐다.
  - 서버 시각 필드는 `:commit`의 `REQUEST_TIME` 변환으로 시험한다(`FieldValue.serverTimestamp()`와 같은 경로).
  - 설문 8개: 비로그인 거절, 로그인 허용, 두 번째 응답 거절, 남의 id 거절, 2,001자 답·메모 거절, 모르는 필드 거절, 다른 사용자 허용.
  - account 5개: 예약 허용, 취소(빈 문서) 허용, 다른 필드 거절, 폰 시각 거절, 남의 계정 거절.
  - 크기 상한 4개: metadata·eventLog 정상 허용, 101필드 거절.
  - 2차의 내용 없는 삭제 표시(title "", note null 등)가 `validActivity`를 통과하는지 1개.
- 문서:
  - README Firebase Setup에 "규칙 원본은 웹 저장소, 사본 위치, 자리표시자"를 한 단락으로 적었다.
  - `docs/study-integration/IMPLEMENTATION_STATUS.md` 실행 방법에 자리표시자와 검사 33개를 한 줄로 적었다.
  - `CHANGELOG.md` Unreleased 맨 위에 두 항목.

### 바뀐 파일
`git diff --stat`: 9 files changed, 108 insertions(+), 9 deletions(-).
- 바뀐 파일: CHANGELOG.md, README.md, app/build.gradle.kts, MainActivity.kt, docs/study-integration/IMPLEMENTATION_STATUS.md, docs/study-integration/firestore.proposed.rules, gradle/libs.versions.toml, tools/study-integration/prepare-rules.cjs, tools/study-integration/rules-test.cjs.
- 새 파일:
  - `app/src/main/java/com/example/flowlog/appcheck/FlowlogAppCheck.kt`
  - `app/src/debug/java/com/example/flowlog/appcheck/AppCheckProviders.kt`
  - `app/src/release/java/com/example/flowlog/appcheck/AppCheckProviders.kt`

## 확인한 것 (어떻게)
- `bash ./gradlew :app:compileDebugKotlin -PofflineValidation=true --console=plain` → BUILD SUCCESSFUL. 새 라이브러리 두 개는 프록시로 받아졌다.
- `bash ./gradlew :app:dependencies --configuration debugRuntimeClasspath -PofflineValidation=true` → appcheck-debug·playintegrity 모두 19.0.1.
- `bash ./gradlew :app:testDebugUnitTest -PofflineValidation=true --console=plain` → 결과 XML 합산 **143개 통과**, 실패 0.
- 릴리즈 소스 폴더 확인: `bash ./gradlew :app:compileReleaseKotlin -PofflineValidation=true -x processReleaseGoogleServices` → 오류는 **기존의** `R.string.default_web_client_id` 없음 1개뿐이었다(오프라인 플래그가 디버그에만 대체값을 넣음). 릴리즈 `AppCheckProviders.kt`는 오류 없이 해석됐다.
- 규칙 에뮬레이터:
  - 도구 준비: 스크래치 폴더(저장소 밖)에 `npm install firebase-tools@13.29.1`, 에뮬레이터 jar는 프록시로 받아졌다.
  - 실행: `node tools/study-integration/prepare-rules.cjs` → `app/build/study-validation`에서 `firebase emulators:exec --only firestore --project demo-flowlog-study --config firebase.json "node rules-test.cjs"` → "33 Firestore authorization/revision assertions passed".
  - 바꾸기 전 기준선: 같은 방법으로 15개 통과를 먼저 확인했다.
  - 새 테스트가 실제로 무언가를 잡는지: 2차 커밋의 옛 규칙(관리자 uid만 시험값으로 치환)으로 돌리면 "signed-out survey write must be rejected"에서 실패했다.
- 저장소에 node_modules·lock 파일 없음. 자리표시자 사본에 실제 uid가 남지 않았는지 `grep`으로 확인했다.

## 확인 못 한 것
- **기기 미확인**: App Check 토큰이 실제로 발급되는지, 디버그 토큰이 logcat에 찍히는지, Play Integrity가 Play 배포본에서 통과하는지.
- 실제 Firebase 콘솔 등록과 적용(enforce). 적용 뒤 웹 대시보드(App Check를 안 붙였다면)가 막히지 않는지도 미확인이다. 웹에도 App Check(reCAPTCHA)를 붙이거나 Firestore 적용을 미뤄야 한다.
- `flowlogSurveyResponses`의 실제 웹 필드와 저장 방식(하루 한 번 체크인이라면 "1인 1건"과 충돌). 웹 저장소를 못 봤다. 이 사본은 배포본이 아니다.
- 릴리즈 빌드 전체(`assembleRelease`)와 lint.

## 알려진 문제
- **uid 리터럴이 남은 곳(남김)**: `docs/study-integration/firestore.original.rules`(배포본 그대로의 기록), `app/src/main/java/com/example/flowlog/data/local/UserRoleStore.kt`(앱의 개발자 역할 판정, 코드 동작이라 범위 밖). 둘 다 이번에 새로 쓴 것은 아니다.
- 자리표시자 사본을 웹 저장소로 옮길 때 실제 uid로 채우지 않으면 관리자 읽기가 모두 막힌다(주석에 적음).
- 설문 규칙은 "필드 목록 확정 전 초안"이다.
- App Check를 Firestore에 적용하면 등록하지 않은 디버그 빌드와 오프라인 검증 빌드는 서버 접근이 막힌다(의도된 동작).

## 다음 작업자에게
- 콘솔 순서 추천:
  1. App Check에 Android 앱 등록(Play Integrity, Play Console 앱 서명 SHA-256 필요).
  2. 디버그 토큰 등록.
  3. 몇 주 "모니터링"으로 정상 요청 비율 확인.
  4. 웹 대시보드에도 App Check를 붙인 뒤 Firestore 적용.
- 규칙 사본을 웹 저장소에 반영할 때: 자리표시자를 실제 값으로 바꾸고, 설문 필드를 웹 양식에 맞춘 뒤, 웹 쪽 테스트도 돌린다.
- 에뮬레이터는 이 환경에서 돈다. firebase-tools를 저장소 밖에 설치해 쓰면 된다.
