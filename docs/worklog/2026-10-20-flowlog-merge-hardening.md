# 2026-10-20 — Flowlog 하드닝 브랜치 병합 (ccr-1cb50339-vdsr0x → ccr-2a22e640-e8dn8n)

에이전트: 하드닝 브랜치 병합 (Opus 5.5, effort high). 하위 에이전트 호출: 없음. 커밋·push: 병합 커밋만, push 안 함. (병합 커밋 `cd91e8b`, 병합 뒤 손질 커밋 `adaec31` — 지시서가 허용한 "충돌 해결 커밋")

## 한 일

Flowlog 저장소(`/home/user/Flowlog`) 브랜치 `ccr-2a22e640-e8dn8n`(이번 세션 커밋 7개, 끝 `6e27a36`) 위로 2026-10-13 하드닝 브랜치 `origin/ccr-1cb50339-vdsr0x`(`93a2e7b`, 212파일)를 합쳤다. 두 브랜치는 같은 `98b3039`에서 갈라졌다.

### 겹치는 파일 (양쪽이 모두 바꾼 파일, 8개)

`git diff --name-only 98b3039 origin/ccr-1cb50339-vdsr0x`(212개)와 `git diff --name-only 98b3039 HEAD`(64개)의 교집합:

- `CHANGELOG.md`
- `README.md`
- `app/build.gradle.kts`
- `app/src/main/AndroidManifest.xml`
- `app/src/main/java/com/example/flowlog/MainActivity.kt`
- `app/src/main/java/com/example/flowlog/data/remote/FirestoreSyncRepository.kt`
- `app/src/main/java/com/example/flowlog/data/sync/FirebaseRestoreDataSource.kt`
- `app/src/main/java/com/example/flowlog/notification/PlannedTodoReminderReceiver.kt`

예상했던 겹침 중 `notification/`은 `PlannedTodoReminderReceiver.kt` 하나만 실제로 겹쳤다(그쪽 `ActivityTimerNotifier.kt`, 우리 `AlarmRescheduler`·`ExactAlarmPermission*`은 서로 안 건드림). `data/sync/`도 `FirebaseRestoreDataSource.kt` 하나(+ `data/remote/FirestoreSyncRepository.kt`). 그쪽 `FirebaseSyncSupport.kt`·`StudySyncDataSource.kt`·`RemotePullCursor.kt`는 우리 쪽이 안 건드려 그대로 들어왔다. 나머지 204개는 그쪽만 바꾼 파일(대부분 drawable·타일 삭제와 WebP).

### 파일별 결정

| 파일 | git 결과 | 결정 |
|---|---|---|
| `MainActivity.kt` | 충돌 2곳 | **정확 알람은 우리 쪽**: `ExactAlarmPermission.status/shouldPrompt` + 설명 다이얼로그(`answerExactAlarmPrompt`)를 남기고, 그쪽 `requestExactAlarmPermission()`(설치당 한 번 설정 화면 열기) 함수와 호출, 그쪽 SharedPreferences 키(`flowlog_permission_prompts` / `exact_alarm_prompted`) 상수를 버렸다. 키는 우리 것(`exact_alarm_permission` / `prompted`)으로 통일. **그쪽 밝은 고정 팔레트는 받음**: `enableEdgeToEdge(SystemBarStyle.light(...))`, `FlowlogTheme(darkTheme = false, dynamicColor = false)` |
| `PlannedTodoReminderReceiver.kt` | 충돌 4곳 | **경고 로그는 우리 문장**(`todoId=...`, 제목 없음). 그쪽도 제목만 뺀 문장이라 정보가 더 있는 우리 쪽을 택함. 그쪽 잠금화면 공개본(`VISIBILITY_PRIVATE` + `setPublicVersion`)은 자동 병합으로 들어옴 |
| `CHANGELOG.md` | 충돌 1곳 | 양쪽 Unreleased 항목을 모두 남김(우리 쪽 먼저). 그쪽 항목의 "정확 알람 설정 화면은 설치당 한 번" 문장은 지금 동작과 달라 지우고 "자정 동기화 알람은 부정확 알람이라 정확 알람 권한이 필요 없다"로 바꿈. 그쪽 경고 로그 문장에 "id를 남긴다(위 항목)" 참조를 붙임 |
| `app/build.gradle.kts` | 자동 | 그쪽 `isMinifyEnabled = true`, `isShrinkResources = true` + 우리 App Check 의존성 두 줄 둘 다 들어감. debug/release 소스셋(`appcheck/`)은 그대로 |
| `app/proguard-rules.pro` | 그쪽만 | 그쪽 규칙 그대로(줄 번호 유지, `Log.v/d/i` 제거). **keep 규칙은 추가하지 않음** — 아래 "R8 판단" |
| `AndroidManifest.xml` | 자동 | 그쪽 `networkSecurityConfig`, 위젯 `FLOW_STATUS_REFRESH` 액션을 intent-filter에서 뺀 것 + 우리 `ExactAlarmPermissionReceiver` 수신기 모두 있음(확인함) |
| `FirestoreSyncRepository.kt` | 자동 | 그쪽 `markSynced`(flowlog/metadata 쓰기) 제거, `calendarEvents`를 `update()`로(없으면 NOT_FOUND 무시) + 우리 tombstone 내용 비우기(`ActivityRevisionContent.forUpload`) 모두 있음 |
| `FirebaseRestoreDataSource.kt` | 자동 | 그쪽 증분 끌어오기(`incremental`, `RemotePullCursor`) + 우리 uid 없는 로그(`restore start — signed in`) 모두 있음 |
| `README.md` | 자동 | 그쪽 증분 동기화 문단 들어옴. 경로 목록의 `flowlog/metadata`를 "예전 빌드만 썼고 지금은 안 씀"으로 고침(병합 커밋에 포함) |

### 동기화 쪽 맞물림 확인 (코드 읽기)
- **계정 삭제**: `DeviceDataWiper.clearAppPreferences`가 SDK 접두어(`com.google.`, `firebase` 등)만 빼고 앱 SharedPreferences를 전부 비우므로, 증분 커서 파일 `flowlog_remote_pull_cursor`도 삭제 때 지워진다. 재로그인 뒤 삭제 취소·복원은 `restoreFromFirestore` → `restoreActivities(userId)`(기본값 `incremental = false`, 전체 읽기)라 커서와 무관. 로그인 직후 삭제 예약 검사 코드(`MainActivity` 418행 근처)는 병합에서 바뀌지 않음.
- **tombstone**: 우리 `forUpload`는 제목·메모·태그·운동 세트만 비우고 `modifiedTime`은 건드리지 않는다. 로컬 삭제가 `updatedAt = MAX(now, updatedAt+1)`로 올리므로(`ActivityRevisionDao` 49행) 삭제 tombstone도 다른 기기의 증분 끌어오기(`modifiedTime >= 커서-24시간`)에 잡힌다.
- **웹 편집**: 웹 저장소의 활동 편집 경로(`public-flowlog/statistics/study-link-store.js`)가 `modifiedTime = now`를 쓰는 것은 확인. 웹의 다른 쓰기 경로와 study link `updatedAt`·decision `createdAt` 갱신은 확인 못 함.

### 병합 뒤 손질 커밋 `adaec31` (지시서를 조금 넘어선 일)
- `app/src/main/res/raw/keep.xml` 추가: 리소스 축소가 켜졌는데 알림 소리 `flowlog_ding`은 `R.raw`가 아니라 **이름**으로 부른다(`KakaoStyleAlertPlayer.soundUri` → `android.resource://<패키지>/raw/flowlog_ding`, 알림 채널·타이머·양치 알림이 씀). 축소기의 문자열 추측에 맡기지 않고 `tools:keep="@raw/flowlog_ding"`으로 명시. 지우면 릴리즈에서 알림 소리가 무음/기본음으로 바뀔 수 있는 자리.
- `tools/account-deletion/selection.js` 주석 한 줄: `flowlog/metadata`는 예전 빌드만 썼다(영구 삭제 대상에는 그대로 남김 — 예전 기기가 쓴 문서가 서버에 있을 수 있음).
- 그 밖에 병합 커밋에 `docs/RELEASE_CHECKLIST.md` 두 줄 정리: 로그 항목에 "릴리즈는 R8로 debug/info/verbose 제거 + 남은 일: 릴리즈 빌드를 기기에서 확인", 다크 모드 항목에 "지금은 라이트 팔레트 고정".

### R8 판단 (keep 규칙을 더하지 않은 이유)
- Firestore는 전부 Map 접근(`toObject` 없음, grep 확인), `Class.forName`·Gson·`getIdentifier` 없음.
- `@Serializable` 클래스(ActivitySession, MainButtonConfig, TodoItem, DailyGoalRepository 안 3개)는 kotlinx-serialization 1.6.0이 자체 R8 규칙을 싣고 오고, 필드 이름은 컴파일러 플러그인이 정하므로 난독화와 무관.
- Room·WorkManager·Firebase(App Check Play Integrity·debug 포함)는 각자 consumer 규칙을 싣는다. App Check 공급자는 소스셋으로 고르고 리플렉션을 쓰지 않음.
- 그래서 추가 keep은 넣지 않았다. **실제로 R8을 돌려 본 것은 아니다**(아래).

## 확인한 것 (어떻게)
환경: `ANDROID_HOME=/tmp/claude-0/-home-user/7c40c1dc-b607-5f78-9497-ffe487ef55d0/scratchpad/android-sdk`, `cd /home/user/Flowlog`.
- `git diff --name-only 98b3039 origin/ccr-1cb50339-vdsr0x` / `... HEAD` 교집합 → 8개(위 목록).
- `git merge --no-ff --no-commit origin/ccr-1cb50339-vdsr0x` → 충돌 3파일(CHANGELOG.md, MainActivity.kt, PlannedTodoReminderReceiver.kt), 나머지 자동 병합.
- 해결 뒤 충돌 표시(`<<<<<<<`) 0개 확인.
- `bash ./gradlew :app:compileDebugKotlin -PofflineValidation=true --console=plain` → BUILD SUCCESSFUL.
- `bash ./gradlew :app:testDebugUnitTest -PofflineValidation=true --console=plain` → BUILD SUCCESSFUL. 결과 XML 집계: **148개 통과, 실패 0, 오류 0, 건너뜀 0, 테스트 클래스 20개**. 148 = 우리 143 + 그쪽 `RemotePullCursorTest` 5개. 손질 커밋 뒤 두 명령을 다시 돌려 통과.
- `bash ./gradlew :app:compileReleaseKotlin -PofflineValidation=true` → `:app:processReleaseGoogleServices`에서 실패(`google-services.json`이 없음, 예상대로). Kotlin 컴파일까지 못 감.
- 같은 명령에 `-x processReleaseGoogleServices`를 붙여 다시 시도 → `compileReleaseKotlin`까지 가서 **오류 1개만**: `MainActivity.kt:775 Unresolved reference 'default_web_client_id'`(google-services 플러그인이 만드는 문자열이라 없는 게 정상). 즉 릴리즈 소스셋(App Check Play Integrity 쪽)을 포함한 나머지 Kotlin 코드는 컴파일 오류가 없었다.

## 확인 못 한 것
- **릴리즈 R8·리소스 축소 결과**: `minifyReleaseWithR8`·`shrinkReleaseRes`는 `google-services.json` 없이는 돌릴 수 없어 한 번도 실행되지 않았다. keep 규칙 누락(직렬화·Room·WorkManager·App Check), 리소스 축소로 빠지는 리소스는 여기서 잡히지 않는다.
- **기기 동작**: 설치·실행 안 함. 정확 알람 다이얼로그, 라이트 고정 화면, 잠금화면 알림 숨김, 위젯 60초 갱신, 증분 동기화, 계정 삭제 뒤 재로그인 전부 기기 미확인.
- 그쪽 브랜치 빌드를 실제 폰에 깔았던 적이 있는지: 깔았다면 그쪽 키(`exact_alarm_prompted`)는 이제 안 읽으므로 우리 설명 다이얼로그가 한 번 더 뜬다(해롭지 않음).
- 웹 쪽 study link `updatedAt`·decision `createdAt`이 편집 때마다 갱신되는지(증분 끌어오기의 전제).

## 알려진 문제
- 증분 끌어오기는 휴대폰·브라우저가 적은 시각(클라이언트 시계)에 기댄다. 24시간 겹침과 주 1회 전체 읽기로 막지만, 시계가 하루 넘게 틀린 기기의 편집은 최대 일주일 늦게 들어올 수 있다(그쪽 설계 그대로).
- `PlannedTodoReminderReceiver.kt` 46행 근처 빈 줄 두 개(우리 쪽 원래 상태).

## 다음 작업자에게
- **타이머 동기화 작업은 이 병합 위(`adaec31`)에 올라간다.** 동기화를 건드릴 때: 정기 동기화는 `FirebaseSyncCoordinator.refreshStudy`에서 `incremental = true`로 끌어오고, 재설치 복원·충돌 해결·삭제 취소 복원은 전체 읽기다. 새 원격 컬렉션을 정기 끌어오기에 넣으면 `RemotePullCursor`에 키를 새로 만들고, 서버 문서에 클라이언트 시각 칸(`modifiedTime`/`updatedAt`)을 꼭 갱신해야 증분에 잡힌다. 커서는 모든 문서를 적용했을 때만 전진시킨다(`recordSuccess` 주석).
- 업로드 뒤 `flowlog/metadata`는 더 이상 쓰지 않는다. 그 문서를 읽는 기능을 새로 만들지 말 것.
- 출시 전 반드시: `google-services.json`이 있는 PC에서 `bundleRelease`(또는 `assembleRelease`)를 돌려 R8·리소스 축소가 통과하는지, 그 빌드로 로그인·동기화·위젯·알림 소리·App Check가 도는지 확인(RELEASE_CHECKLIST에 항목 추가해 둠). 문제가 나면 `app/proguard-rules.pro`에 keep을 더한다.
- push는 안 했다. main 병합은 사용자 판단.
