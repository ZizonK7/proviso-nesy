# 2026-10-20 — Flowlog 진행 중 타이머를 PC 웹 앱과 공유 (앱 쪽)

에이전트: 타이머 동기화 구현 (Opus 5.5, effort high). 하위 에이전트 호출: 없음. 커밋·push: 안 함.

대상: `/home/user/Flowlog`, 브랜치 `ccr-2a22e640-e8dn8n`, 기준 커밋 `adaec31`(하드닝 병합 뒤). 바뀐 파일은 모두 커밋하지 않은 작업 트리에 있다.

## 한 일

### 설계: 한 곳에서 올린다
폰 타이머의 단일 진실은 그대로 `TimerStateStore`(SharedPreferences)다. 진행 중 타이머를 바꾸는 함수는 이 저장소의 세 개뿐(`saveActiveTimer`·`pauseActiveTimer`·`clearActiveTimer`)이므로, **이 세 함수 끝에서 서버 문서를 쓰게 했다**(`RemoteTimerSync.publishLocalChange`). 화면(ViewModel)이든 알람 수신기든 되돌리기든 같은 함수를 지나므로 빠지는 경로가 없다. 웹에서 온 변경을 적용할 때는 `publish = false`로 불러 다시 올리지 않는다.

### 타이머 상태를 바꾸는 경로 전수 조사
`grep -rn "TimerStateStore\.\(saveActiveTimer\|pauseActiveTimer\|clearActiveTimer\)"`와 `"timer_state"` 직접 편집을 찾아 모두 확인했다(직접 편집은 양치·간식 키뿐이라 해당 없음).

| 경로 | 위치 | 저장소 호출 | 서버 문서 |
|---|---|---|---|
| 메인 버튼 시작(바로가기 START_TIMER, `restartActivity` 포함) | `ActivityViewModel.startActivity` | `saveActiveSession` → `saveActiveTimer` | running |
| 자동 버튼 지금 시작(학교·회사 외) | `startScheduledAutoButtonNow` | 같음 | running |
| 할 일·루틴·캘린더 조각·추천 할 일·흐름 추천 시작 | `startTodoActivity`, `startDailyCueRoutineActivity`, `startCalendarPetiteActivity`, `startRecommendedTodoActivity`, `startFlowRecommendation`(앞 셋에 위임) | 같음 | running |
| 진행 중 제목 변경 | `setRunningActivityTitle` | 같음 | running(새 제목) |
| 정지·저장 | `stopActivityAndSave` → `clearActiveSession` | `clearActiveTimer` | stopped |
| 저장/취소(대기 기록) | `saveActivity`, `cancelPendingActivity` → `clearPendingActivity` | `clearActiveTimer` | stopped (UI에서 부르는 곳 없음) |
| 멈춤 | `stopActivity` | `pauseActiveTimer` | paused (UI에서 부르는 곳 없음) |
| 자동 버튼 알람 시작·끝 | `AutoButtonAlarmReceiver.handleStart/handleEnd` | `saveActiveTimer` / `clearActiveTimer` | running / stopped |
| 공부 계획 자동 시작·끝 | `StudyPlanAutoStartReceiver` | 같음 | running / stopped |
| 자동 버튼 되돌리기 | `AutoButtonUndoReceiver` | `clearActiveTimer` 뒤 `saveActiveTimer` | stopped 뒤 running(이전 타이머) |
| 학교·회사 겹침 타이머 | `startOverlappingActivity`, `savePinnedTimer` 경로 | 고정(pinned) 타이머 | **공유 안 함**(별도 저장 칸, 문서는 하나) |
| 계정 삭제 | `DeviceDataWiper.wipe` | 저장소를 거치지 않고 파일째 지움 | **문서 삭제**(아래) |

- 진행 중 **분류 변경 기능은 폰에 없다**(코드에서 `currentCategory`를 바꾸는 곳은 시작·종료뿐). 웹에서 바꾼 분류는 따라간다.
- 폰에는 **일시정지·재개가 없다.** `pauseActiveTimer`는 화면에서 부르지 않는 `stopActivity`만 쓴다. 그래서 웹의 `paused`는 같은 `startTime`의 running으로 따라간다(아래 규칙).

### 새 파일
- `app/src/main/java/com/example/flowlog/data/sync/TimerSyncPolicy.kt` — 순수 로직(안드로이드·Firebase 없음). `decide(로컬, 원격, 내 deviceId, 마지막으로 끝낸 타이머의 startTime)` → 무시(이유) / 원격대로 시작(로컬을 갈아끼우는지) / 같은 타이머의 분류·제목 갱신 / 로컬 취소 / 내 상태 다시 올리기. 문서 필드 만들기(`documentFields`)와 읽기(`remoteFrom`)도 여기.
- `.../data/sync/RemoteTimerSync.kt` — 쓰기(`publishLocalChange`: 병합 쓰기 `set(merge)` + `updatedAt = serverTimestamp()`, Firestore 오프라인 큐에 맡기고 실패는 로그만), 듣기(`listen`: `addSnapshotListener`), 적용(기존 수신기와 같은 시작 단계: 저장소 → 위젯 → 진행 알림), 계정 삭제 때 문서 삭제(`deleteForWipe`, 3초까지 기다림). `deviceId`는 설치마다 한 번 만든 UUID(SharedPreferences `flowlog_timer_sync`). 로그에 제목·uid 없음.
- `app/src/test/.../data/sync/TimerSyncPolicyTest.kt` — 17개.

### 고친 파일
- `TimerStateStore.kt`: 세 함수에 `publish: Boolean = true` 인자와 끝의 올리기, `clearActiveTimer`는 지우기 전 상태를 읽어 `stopped`로 올리고 "마지막으로 끝낸 타이머"를 기록.
- `MainActivity.kt`: 듣기를 **캘린더 구독과 같은 생명주기**에 붙였다(`startCalendarSubscription` 안에서 `startRemoteTimerSync`, `stopCalendarSubscription` 안에서 해제). 그래서 로그인 뒤 시작, 앱이 화면 밖(onStop)·로그아웃·삭제 예약 확인 중(`accountDeletionGate`)·계정 삭제 때 해제된다. 자정 재구독은 같은 uid라 다시 붙이지 않는다.
- `DeviceDataWiper.kt`: 맨 앞에서(아직 로그인 상태) `RemoteTimerSync.deleteForWipe`.
- `ActivityViewModel.kt`: 1초마다 저장소를 보는 감시(`syncActiveSessionFromStore`)의 비교에 제목을 더함. 원래는 분류·시작 시각·연결만 비교해서, 웹에서 바꾼 제목이 화면과 저장되는 기록에 안 들어갔다.
- 규칙 사본 `docs/study-integration/firestore.proposed.rules`: `users/{uid}/flowlog/timer` 쓰기는 `validSharedTimer`(필드 9개만, status 세 값, `updatedAt == request.time`, 칸별 형식·길이), 읽기는 **소유자만**(관리자 읽기에서 `document != path('timer')`로 제외). 삭제는 소유자 허용.
- `tools/study-integration/rules-test.cjs`: 검사 10개 추가(허용 2, 다른 필드 거절, 잘못된 status 거절, 폰 시계 `updatedAt` 거절, 타인 쓰기 거절, 본인 읽기 허용, 타인 읽기 거절, 관리자 읽기 거절, 관리자의 다른 flowlog 문서 읽기는 그대로 허용). 33 → 43.
- 문서: README("Sync and Web" 한 줄, "Data & Sync" 한 단락, 경로 목록), CHANGELOG, `docs/RELEASE_CHECKLIST.md`(구독 구현 절 "PC 앱 타이머 공유 완료(앱 쪽)" + 남은 일 둘, 규칙 검사 수 43), `docs/study-integration/IMPLEMENTATION_STATUS.md`(검사 수), `tools/account-deletion/selection.js` 주석(timer 경로 — `flowlog` 하위 전체가 지워지므로 동작 변경 없음).

### 적용 규칙 (`TimerSyncPolicy.decide`)
1. 문서 없음: 로컬이 돌고 있으면 내 상태 올리기, 아니면 무시. 캐시에서만 본 "없음"은 처리 전에 버린다.
2. `hasPendingWrites`(내 쓰기가 아직 가는 중) → 무시. `isFromCache` → 무시.
3. `updatedBy == "web"`이고 `deviceId`가 내 것이 아닐 때만 따른다. 내 deviceId 문서(메아리)는 로컬과 같으면 무시, **다르면 내 상태를 다시 올린다**(로그아웃 중 바뀐 타이머, 사라진 쓰기를 메움). 다른 폰(`updatedBy == "app"`, 다른 deviceId)은 무시.
4. status가 세 값이 아니거나 분류가 비었거나 `startTime`·`updatedAt`이 없으면 무시.
5. 원격 `stopped`: 로컬이 같은 `startTime`이면 **기록 없이 로컬 취소**(알림·루틴 알람·위젯 정리). 다른 타이머면 무시.
6. 원격 `running`/`paused`:
   - 로컬 없음 → 원격대로 시작. 단 그 `startTime`이 이 폰이 마지막으로 끝낸 타이머면 오래된 문서로 보고 무시.
   - 같은 `startTime` → 분류·제목이 다르면 그것만 갱신, 같으면 무시.
   - 다른 타이머 → **나중 것이 이김**: 원격 `updatedAt`(서버 시각) > 로컬 시작 시각이면 로컬을 기록 없이 취소하고 원격 시작, 아니면 무시하고 내 상태를 다시 올림.

## 확인한 것 (어떻게)
환경: `ANDROID_HOME=/tmp/claude-0/-home-user/7c40c1dc-b607-5f78-9497-ffe487ef55d0/scratchpad/android-sdk`, `cd /home/user/Flowlog`.
- `bash ./gradlew :app:compileDebugKotlin -PofflineValidation=true --console=plain` → BUILD SUCCESSFUL.
- `bash ./gradlew :app:testDebugUnitTest -PofflineValidation=true --console=plain` → BUILD SUCCESSFUL. 결과 XML 집계 **165개 통과, 실패 0, 오류 0** = 기존 148 + `TimerSyncPolicyTest` 17(메아리 무시, 사라진 쓰기 다시 올리기, 대기 중 쓰기·캐시 무시, 내 deviceId 단 웹 쓰기, 다른 폰 무시, 멈춘 폰이 원격 시작, paused를 running으로, 같은 타이머 정지 → 기록 없이 취소, 다른 타이머 정지 무시, 늦은 웹 시작 승리, 이른 웹 시작 패배 → 다시 올리기, 오래된 원격 무시, 같은 타이머 제목 갱신/무시, 잘못된 문서 무시, 문서 없음, 문서 필드 모양, 원격 필드 방어적 읽기).
- 규칙: `node tools/study-integration/prepare-rules.cjs` 뒤 `app/build/study-validation`에서 `/tmp/claude-0/-home-user/7c40c1dc-b607-5f78-9497-ffe487ef55d0/scratchpad/web-tools/node_modules/.bin/firebase emulators:exec --only firestore --project demo-flowlog-study --config firebase.json "node rules-test.cjs"` → `43 Firestore authorization/revision assertions passed`.
- `tools/account-deletion`에서 `node --test` → 10개 통과(주석만 바꿈).
- `git diff --stat`(새 파일 3개 제외): 11 files changed, 112 insertions(+), 9 deletions(-). 새 파일: `TimerSyncPolicy.kt`, `RemoteTimerSync.kt`, `TimerSyncPolicyTest.kt`.

## 확인 못 한 것
- **기기와 실제 Firestore**: 설치·실행 안 함. 실제 문서 쓰기, 스냅샷 듣기, 오프라인 큐, 알림·위젯이 원격 시작·취소를 따라가는지, ViewModel 화면이 1초 안에 따라오는지 전부 미확인. `RemoteTimerSync`(안드로이드·Firebase 부분)는 단위 테스트가 없다 — 테스트는 순수 로직뿐.
- 웹 앱(`/app/`)이 같은 필드·같은 규칙으로 쓰는지, 웹이 `stopped`를 받았을 때 기록을 만들지 않는지(폰이 정지하며 이미 기록을 만듦)는 웹 쪽 일이라 확인 못 함.
- 웹 저장소의 **원본 규칙에는 아직 안 넣었다**(이 저장소 사본만). 배포 전 원본에 같은 조항이 필요하다.
- 릴리즈 빌드(R8)에서의 동작.

## 알려진 문제
- **앱이 화면에 있을 때만 듣는다**(캘린더 구독과 같은 생명주기, 배터리 때문). 앱이 꺼져 있는 동안 웹에서 정지하면 폰 진행 알림은 남아 있다가 앱을 열 때 맞춰진다. 그 사이 폰에서 먼저 정지하면 웹과 폰 양쪽에 기록이 생길 수 있다. 앱을 연 직후 서버 스냅샷이 오기 전(보통 1초 안)에 정지해도 같다.
- 원격 취소가 저장소에 들어간 뒤 ViewModel 감시가 따라오기까지 최대 1초. 그 사이 정지를 누르면 중복 기록이 생길 수 있다.
- "나중 것이 이김"은 서버 시각(`updatedAt`)과 폰 시계(`startTime`)를 비교한다. 폰 시계가 크게 틀리면 판정이 밀린다.
- 원격 시작으로 갈아끼울 때 진행 중이던 집중 모드와 운동 세트 입력 메모리 상태는 정리하지 않는다(저장소 쪽 운동 세트는 지워짐).
- 삭제 예약 확인을 기다리는 동안(`accountDeletionGate`)에도 타이머 변경은 문서에 쓴다(듣기는 멈춤). 영구 삭제 작업이 `flowlog` 하위를 통째로 지우므로 남지는 않는다.
- 다른 폰(같은 계정의 두 번째 폰)의 타이머는 지시대로 따르지 않는다.
- `linkedTodoId`는 폰의 할 일 번호(`todos/{id}` 문서 id와 같음)를 문자열로 쓴다. 웹 캘린더 할 일(`linkedTodoCalendarSourceId`)은 보내지 않는다.
- 웹이 `pausedElapsedMs`를 쓰더라도 폰은 일시정지가 없어 쓰지 않는다.

## 다음 작업자에게
- 웹 앱과 맞출 것: 웹 쓰기는 `updatedBy: "web"`, 자기 `deviceId`, `updatedAt: serverTimestamp()`, 필드 9개만. 정지는 `status: "stopped"`에 정지한 타이머의 `startTime`을 그대로 둬야 폰이 같은 타이머로 알아본다. 웹은 폰이 쓴 `stopped`(updatedBy app)를 보고 기록을 만들면 안 된다.
- 규칙 원본(웹 저장소)에 `validSharedTimer`와 관리자 읽기 제외(`document != path('timer')`)를 옮기고 배포. 사본 검사 43개가 기준.
- 동기화 안전장치: 이 작업은 `RemotePullCursor`(증분 끌어오기)·계정 삭제 예약·복원 흐름을 건드리지 않았다. 타이머 문서는 끌어오기 대상이 아니다. 새 타이머 쓰기 경로를 만들면 `TimerStateStore`의 세 함수를 지나게 해야 공유된다(저장소 파일을 직접 고치지 말 것).
- 기기 확인 순서 제안: 폰 시작 → 웹 표시, 웹 시작(폰 멈춤) → 폰 시작·알림, 웹 정지 → 폰 기록 없이 종료, 폰과 웹 거의 동시 시작 → 늦은 쪽이 남는지, 비행기 모드에서 폰 정지 → 다시 연결되면 웹 갱신.
