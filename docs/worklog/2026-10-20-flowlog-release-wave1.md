# 2026-10-20 — Flowlog 출시 준비 1차 (AI 문구, 민감 로그, 정확 알람 권한)

에이전트: 출시 준비 구현 (Opus 5.5, effort high). 하위 에이전트 호출: 없음. 커밋·push: 안 함.

대상: `/home/user/Flowlog`, 브랜치 `ccr-2a22e640-e8dn8n`(작업 트리만 고침). 배경은 Flowlog `docs/RELEASE_CHECKLIST.md`의 "정확 알람 권한", "Flowlog AI 문구 제거", "로그 정리" 세 항목. 체크리스트의 체크 표시는 메인 판단으로 남겨 두었다.

## 한 일

### 1. "Flowlog AI" 문구 제거
앱 전체(`app/src/main`)에서 사용자에게 보이는 AI 약속 문구는 두 곳뿐이었다(`grep -rn "Flowlog AI"`, `grep -rnE 'AI|인공지능|코칭|분석'`으로 확인).

| 위치 | 전 | 후 |
|---|---|---|
| `ui/screen/home/RecommendationSection.kt` 메인 버튼 고르기(온보딩) 설명 | "자주 쓰는 활동을 추려봤어요. 필요하면 바꿀 수 있어요.\n나중에 Flowlog AI가 더 맞는 버튼을 추천해 드려요." (코드에 박힌 문자열) | "…\n기록이 쌓이면 Flowlog가 기록을 바탕으로 더 맞는 버튼을 제안해 드려요." (`strings.xml`의 `onboarding_main_buttons_desc`) |
| `MainActivity.kt` 제안 시트(`AiMessengerSheet`) 머리 제목 | "Flowlog AI" (코드에 박힌 문자열) | "Flowlog 제안" (`main_activity_suggestion_sheet_title`). 아래 부제 "활동 패턴 기반 제안"은 그대로 |

건드리지 않은 것: 시트를 여는 아이콘의 접근성 설명 "AI 메신저"(`main_activity_ai_messenger_content_desc`)는 지시서가 예로 든 기능 이름이라 그대로 두었다. 다만 화면 낭독기 사용자에게는 이것도 "AI"로 들린다 — 바꿀지는 메인 판단.

### 2. 민감 로그 정리
`grep -rnE 'Log\.(d|i|w|e|v)\(' app/src/main/java` 전체 157줄을 훑었다. 민감 값(할 일·활동·강의 제목, uid)이 든 로그는 **전 19줄 → 후 0줄**. 로그 자체는 남기고 값만 바꿨다(`BuildConfig.DEBUG` 감싸기는 쓰지 않음).

| 파일 | 줄 수 | 바꾼 방식 |
|---|---|---|
| `notification/PlannedTodoReminderReceiver.kt` | 9 | `title=$snapshotTitle` → `todoId=${item.todoId}`. 로그에만 쓰이던 `snapshotTitle` 변수 삭제 |
| `ui/viewmodel/ActivityViewModel.kt` | 2 | 할 일 제목 → `titleLength`/`newTodoTitleLength`(글자 수) |
| `data/sync/FirebaseSyncDataSource.kt` | 4 | `userId=$userId` → "signed in" 또는 삭제 |
| `data/sync/FirebaseCalendarPullDataSource.kt` | 3 | uid 2줄 → "signed in"/"for the signed-in user", 강의 이름 `course=` → `courseTitleLength` |
| `data/sync/FirebaseRestoreDataSource.kt` | 1 | uid → "signed in" |

그대로 둔 것: `SleepFillDialog`의 `pickerTitle`(화면 고정 라벨, 사용자 내용 아님), 동기화 실패 로그의 `e.message`와 문서 id.

### 3. 정확 알람 권한: "설명 후 한 번"
- **이전 동작**: `MainActivity.onCreate`가 `requestExactAlarmPermission()`을 불러, Android 12+에서 권한이 없으면 앱을 열 때마다 설명 없이 시스템 설정 화면을 띄웠다. 이 함수는 삭제했다.
- **a. 설명 다이얼로그 한 번**: 권한이 없고 아직 묻지 않았으면 앱 안 다이얼로그(`ExactAlarmPromptDialog`)를 띄운다. 문구는 지시서대로("알림이 제시간에 울리려면 '알람 및 리마인더' 권한이 필요합니다. 끄면 알림이 몇 분 늦을 수 있습니다.") + "켜지 않아도 앱은 그대로 쓸 수 있고, 설정 창의 '정확한 알림'에서 언제든 켤 수 있어요." 버튼 [설정으로] / [나중에]. 어느 쪽을 누르든, 바깥을 눌러 닫든 SharedPreferences(`exact_alarm_permission`/`prompted`)에 "물었음"을 적고 다시 묻지 않는다. 답하기 전에 화면이 돌아가면(재생성) 다시 뜬다. 다른 경로로 권한이 켜진 채 돌아오면 `onResume`이 다이얼로그를 거둔다.
- **b. 거절해도 정상 동작**: 기존 스케줄러는 모두 이미 부정확 알람 폴백이 있었다. 코드를 바꾸지 않았다.

  | 스케줄러 | 권한 없을 때 |
  |---|---|
  | `AutoButtonScheduler` | `canScheduleExactAlarms()` 검사 → `setAndAllowWhileIdle` → `set` |
  | `StudyPlanAutoStartScheduler` | 같음 |
  | `PlannedTodoReminderScheduler` | 같음 |
  | `RoutineGoalAlarmScheduler` | 같음 |
  | `FocusModeScheduler` | 같음 |
  | `InactivityReminderScheduler` | 검사 → `setAndAllowWhileIdle`, 실패 시 `set` |
  | `ReminderScheduler`(양치·식사) | `setAlarmClock` 실패(SecurityException) → `setExactAndAllowWhileIdle` 실패 → `setAndAllowWhileIdle` → `set`. 예외로 내려가는 방식 |
  | `FirebaseSyncAlarmScheduler`(자정 동기화, `FirebaseSyncSupport.kt`) | `canExact` 분기 → `setAndAllowWhileIdle` |
  | `FlowStatusWidgetProvider`(위젯 새로고침) | 처음부터 `set`(부정확), 권한 무관 |

- **c. 설정 창 줄**: HeaderActions 설정 창의 "알림 설정" 묶음 끝(예정 시간 알림 아래, 집중 모드 위)에 "정확한 알림" 줄. 켜짐/꺼짐 문구 + 아이콘(Alarm/AlarmOff) + [설정 열기]. 상태는 `MainActivity.onResume`에서 다시 읽어 시스템 설정에서 돌아오면 바로 바뀐다. Android 12 미만에서는 줄을 숨긴다.
- **d. 권한 변경 수신기**: `notification/ExactAlarmPermissionReceiver.kt`가 `AlarmManager.ACTION_SCHEDULE_EXACT_ALARM_PERMISSION_STATE_CHANGED`를 받아 알람을 다시 잡는다. 매니페스트에 `exported="true"`로 등록하고 부팅 수신기와 같은 이유를 주석으로 적었다. 재예약 로직은 새 `notification/AlarmRescheduler.kt`로 뽑았다: `rescheduleAutoButtonGroup`(자동 버튼·공부 계획·양치 알림, 기존 `AutoButtonBootReceiver` 내용), `reschedulePlannedTodoReminders`(기존 `PlannedTodoReminderBootReceiver` 내용), 둘을 합친 `rescheduleAll`. goAsync 처리는 `BroadcastReceiver.launchAlarmReschedule` 확장 함수 하나로 모았다. 두 부팅 수신기와 새 수신기가 같은 함수를 쓴다. 부팅 수신기의 동작(무엇을 다시 잡는가)은 그대로이고, 실패 로그의 태그만 `AlarmRescheduler`로 바뀌었다.
- **e. 순수 판단 로직**: `notification/ExactAlarmPromptPolicy.kt` — `ExactAlarmStatus`(NOT_REQUIRED / ALLOWED / DENIED), `status(sdkInt, canScheduleExactAlarms)`, `shouldPrompt(status, alreadyAsked)`. 안드로이드 쪽 일(현재 상태 읽기, "물었음" 기록, 설정 화면 열기)은 `notification/ExactAlarmPermission.kt`. 테스트는 `app/src/test/java/com/example/flowlog/notification/ExactAlarmPromptPolicyTest.kt`에 6개(12 미만은 묻지 않음, 12+ 상태 구분, 꺼짐·처음이면 물음, 이미 물었으면 안 물음, 켜져 있으면 안 물음, NOT_REQUIRED는 안 물음).

### 문서
- `CHANGELOG.md` `## Unreleased` 맨 위에 세 항목(정확 알람 흐름, 민감 로그, AI 문구).
- `README.md` "Reminders and Focus" 절에 한 줄: Android 12+에서 한 번만 설명하고 묻고, 없어도 알림은 몇 분 늦게 울릴 수 있으며, 설정의 "정확한 알림"에서 언제든 켤 수 있음.

### 바뀐 파일
`git diff --stat`(작업 트리 기준, 13 files changed, 186 insertions(+), 78 deletions(-)):
```
 CHANGELOG.md                                       |  14 ++
 README.md                                          |   4 +
 app/src/main/AndroidManifest.xml                   |  12 ++
 .../main/java/com/example/flowlog/MainActivity.kt  | 142 ++++++++++++++++++---
 .../data/sync/FirebaseCalendarPullDataSource.kt    |   6 +-
 .../flowlog/data/sync/FirebaseRestoreDataSource.kt |   2 +-
 .../flowlog/data/sync/FirebaseSyncDataSource.kt    |   8 +-
 .../flowlog/notification/AutoButtonBootReceiver.kt |  21 +--
 .../PlannedTodoReminderBootReceiver.kt             |  19 +--
 .../notification/PlannedTodoReminderReceiver.kt    |  19 ++-
 .../ui/screen/home/RecommendationSection.kt        |   4 +-
 .../flowlog/ui/viewmodel/ActivityViewModel.kt      |   4 +-
 app/src/main/res/values/strings.xml                |   9 ++
```
새 파일 5개:
- `app/src/main/java/com/example/flowlog/notification/AlarmRescheduler.kt`
- `app/src/main/java/com/example/flowlog/notification/ExactAlarmPermission.kt`
- `app/src/main/java/com/example/flowlog/notification/ExactAlarmPermissionReceiver.kt`
- `app/src/main/java/com/example/flowlog/notification/ExactAlarmPromptPolicy.kt`
- `app/src/test/java/com/example/flowlog/notification/ExactAlarmPromptPolicyTest.kt`

## 확인한 것 (어떻게)
- `bash ./gradlew :app:compileDebugKotlin -PofflineValidation=true --console=plain` → BUILD SUCCESSFUL.
- `bash ./gradlew :app:testDebugUnitTest -PofflineValidation=true --console=plain` → BUILD SUCCESSFUL. `app/build/test-results/testDebugUnitTest/*.xml`을 합산하니 121개(기존 115 + 새 6), 실패 0, 오류 0, 건너뜀 0. `TEST-com.example.flowlog.notification.ExactAlarmPromptPolicyTest.xml`가 생긴 것도 확인.
- 민감 로그 남은 수: `grep -rnE 'Log\.(d|i|w|e|v)\(.*(\$userId|\$\{?uid|snapshotTitle|\.title\}|newTodo\.title\}|\$courseTitle|memo|note)' app/src/main/java | wc -l` → 0. 여러 줄에 걸친 Log 호출 3곳(`FlowlogAlertChannel`, 캘린더 받기 완료, 복원 완료)도 열어 보았고 개수만 찍는다.
- "Flowlog AI": `grep -rn "Flowlog AI"` → 앱 코드에서 0건(체크리스트 문서에만 남음).
- 새 코드에 개인정보·비밀값·실제 uid 없음(직접 읽어 확인). 의존성·`gradlew` 권한·`google-services.json`은 건드리지 않았다.

## 확인 못 한 것
- **기기·에뮬레이터에서 전부 미확인.** 다이얼로그가 실제로 한 번만 뜨는지, 알림 권한(POST_NOTIFICATIONS) 시스템 창과 겹칠 때 보이는 순서, [설정으로]가 "알람 및 리마인더" 화면을 여는지, 돌아왔을 때 설정 창 줄이 켜짐으로 바뀌는지, 권한을 켰을 때 `ExactAlarmPermissionReceiver`가 실제로 불리는지.
- Android 12 미만 기기에서 아무것도 묻지 않는지(코드와 테스트로만 확인).
- 릴리즈 빌드(`assembleRelease`)와 lint는 돌리지 않았다. 새 수신기의 `ACTION_SCHEDULE_EXACT_ALARM_PERMISSION_STATE_CHANGED`는 API 31 상수라 lint가 InlinedApi 경고를 낼 수 있다(컴파일 시 문자열로 들어가 동작에는 문제 없음, minSdk 24에서는 방송이 오지 않을 뿐).

## 알려진 문제
- 권한을 켰을 때 다시 잡는 범위는 부팅 수신기와 같다(자동 버튼, 공부 계획, 양치·식사, 타임테이블 할 일). 루틴 목표·집중 모드 끝·비활동 알림·자정 동기화는 부팅 때도 다시 잡지 않는 기존 구조라 여기서도 다시 잡지 않는다. 권한을 켜기 전에 부정확하게 잡힌 것은 다음에 새로 잡힐 때부터 정확해진다.
- "물었음" 기록은 SharedPreferences라 자동 백업으로 새 폰에 넘어갈 수 있다(백업 규칙 결정은 체크리스트에 따로 있음). 넘어가면 새 폰에서는 묻지 않지만 설정 창에서 켤 수 있다.
- 시트 열기 아이콘의 접근성 설명 "AI 메신저"는 남아 있다(위 1절).
- 체크리스트가 말하는 "용도 선언"(Play Console의 정확 알람 사용 신고)은 앱 코드 밖이라 하지 않았다.
- 설정 창 문구 중 다이얼로그만 "~합니다"체(지시서 문구 그대로), 나머지는 기존처럼 "~요"체.

## 다음 작업자에게
- 기기 확인 순서 추천: Android 14 기기에 새로 설치 → 첫 실행에 알림 권한 창 + 설명 다이얼로그 → [나중에] → 앱 재실행 시 안 뜨는지 → 설정 창 "정확한 알림" 꺼짐 → [설정 열기]로 켬 → 돌아와 켜짐 표시 → `adb logcat -s AlarmRescheduler` 로 실패 로그가 없는지.
- 다시 묻게 하려면 앱 데이터 삭제 또는 `exact_alarm_permission` 환경설정 파일 삭제.
- 재예약 대상을 늘리려면 `AlarmRescheduler`에 함수를 더하면 부팅·권한 수신기 둘 다 따라간다(부팅 수신기는 묶음별로 나뉘어 있어 어느 수신기에서 부를지 정해야 함).
- 정확 알람을 쓰는 Play 정책상 근거(알람·리마인더 앱 핵심 기능인지)는 체크리스트의 "용도 선언"에서 따로 판단해야 한다. 안 되면 `USE_EXACT_ALARM` 대신 지금처럼 `SCHEDULE_EXACT_ALARM` + 폴백 유지가 맞다.
