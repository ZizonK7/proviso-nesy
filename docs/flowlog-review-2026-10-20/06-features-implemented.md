# Flowlog 새 기능 3개 — 구현 결과 (2026-10-20)

대상: `/home/user/Flowlog` (브랜치 `ccr-2a22e640-e8dn8n`, 버전 0.5.9 그대로). 커밋·push는 하지 않았다. 파일만 바뀐 상태로 두었다.

세 기능(A 지난 활동 직접 추가, B 기록 내보내기, C 앱 바로가기)을 모두 넣었다. 뺀 기능은 없다.

한 줄 요약: 컴파일 성공, 단위 테스트 115개 모두 통과(원래 있던 89개 + 새로 쓴 26개, 후속 1회차 포함). 실제 휴대폰에서는 돌려 보지 못했다. 그래서 화면 모양, 저장 위치 고르기 창, 바로가기 표시는 확인하지 못했다.

---

## A. 지난 활동 직접 추가

**무엇을**: 타이머를 켜는 걸 잊은 활동을 나중에 손으로 넣는다. 카테고리, 날짜(오늘 / 어제 / 다른 날), 시작·끝 시각, 제목(선택), 메모(선택)를 고른다.

**어디서 어떻게 쓰나**
- 홈 화면 "최근 기록" 제목 오른쪽, "되돌리기" 버튼 옆에 **"직접 추가"** 버튼이 생겼다.
- 누르면 "지난 활동 추가" 창이 뜬다.
  - 카테고리: 기록 수정 창과 같은 칩 목록을 쓴다. 메인 버튼이 앞에 오고, 나머지 카테고리는 그 뒤에 붙는다.
  - 날짜: "오늘", "어제" 칩이 있다. "다른 날"을 누르면 달력이 열린다(오늘 이후 날짜는 고를 수 없다).
  - 시각: "시작"이나 "끝" 칸을 누르면 시각 선택 시트가 열린다. 루틴 관리에서 쓰는 바퀴식 시·분 선택기를 그대로 다시 썼다.
  - 끝 시각을 시작보다 이른 시각으로 고르면 다음 날로 넘어간 것으로 본다. 예를 들어 23:30 → 07:00 수면이면 끝 칸에 "(다음 날)"이 붙는다.
  - 제목 추천: 타이머에서 쓰는 추천(최근에 자주 쓴 제목 5개)을 같은 방식으로 보여 준다.
- **막는 경우**(빨간 글씨, 저장 버튼이 꺼진다):
  - 끝이 시작보다 뒤가 아닐 때
  - 길이가 24시간을 넘을 때
  - 끝 시각이 아직 오지 않은 미래일 때
- **경고만 하는 경우**(주황 글씨, 저장은 된다): 이미 있는 기록과 시간이 겹칠 때. 몇 개가 겹치는지 알려 주고 앞의 3개를 "제목 시작–끝" 꼴로 보여 준다.
- 저장하면 "지난 활동을 추가했어요." 토스트가 뜬다. 어제 이전 날짜면 "10월 18일 기록에 저장했어요."처럼 날짜를 알려 준다. "최근 기록" 목록은 오늘 시작한 기록만 보여 주기 때문이다(후속 1회차). 바로 "되돌리기"로 지울 수도 있다.

**저장 방식(타이머 정지 저장과 같은 뒤처리)**: 코드에서 확인한 대로 따랐다.
- 따른 것:
  - `repository.insertActivity`: Room에 PENDING 상태로 저장하고, 이벤트 로그 `ACTIVITY_SAVED`를 함께 남긴다.
  - `rememberLastAddedActivity`: 되돌리기 칸에 넣는다.
  - `dailyGoalRepository.ensureTodayTimePlan`: 오늘 시간 계획을 점검한다.
  - `syncAfterActivitySaveIfNeeded`: 10분 이상이면 바로 동기화한다.
  - 기록 종류는 `sourceType = MANUAL`.
- 일부러 뺀 것:
  - 식사 뒤 양치 알림 예약(`scheduleToothbrushReminder`): 이미 끝난 식사라서 지금 알림을 거는 게 맞지 않다.
  - "한동안 기록 없음" 알림: 타이머가 돌고 있지 않고, 이 기록이 지금까지 알려진 마지막 활동보다 늦게 끝났을 때만 옮긴다.
  - 위젯 갱신을 직접 부르지는 않았다. 위젯은 지금 도는 타이머를 보여 주는데, 손으로 넣은 기록은 그걸 바꾸지 않는다. 그리고 기록이 바뀌면 추천 관찰 코드가 위젯 갱신을 이미 부른다(`ActivityViewModel.kt` 360행).
  - Todo 연결, 운동 세트 입력은 넣지 않았다.

**왜 골랐나 (Flowlog 철학과의 관계)**: "가볍게 기록"은 타이머를 잊은 순간에 깨진다. 빠진 시간을 메울 길이 없으면 하루 통계가 실제보다 비어 보인다. 반대로 무엇이든 넣게 두면 "정직한 돌아보기"가 흐려진다. 그래서 미래 시각과 24시간 넘는 기록은 막았다. 겹치는 기록은 실제로 동시에 한 일일 수도 있어서, 막지 않고 알리기만 한다.

**어떻게 확인했나**: 순수 검사 로직을 `ui/viewmodel/ManualActivityValidator.kt`로 따로 빼고, `ManualActivityValidatorTest` 11개를 붙였다. 다룬 경우:
- 정상 입력
- 끝 ≤ 시작
- 정확히 24시간은 통과, 1분이라도 넘으면 거절
- 미래 시각, 그리고 정확히 지금 끝나는 경우
- 겹침은 경고만
- 끝과 시작이 딱 맞닿은 경우와 길이 0인 기록은 겹침으로 세지 않음
- 겹친 기록의 정렬
- 다음 날로 넘어가기, 시작과 끝이 같은 시각

모두 통과했다.

**확인 못 한 것**:
- 실제 화면 모양.
- 대화창 위에 시각 선택 시트가 제대로 겹쳐 뜨는지.
- 달력에서 날짜를 고르는 동작.
- 저장 후 토스트와 되돌리기.

**남은 일·알려진 문제**:
- 운동(EXERCISE)을 세트 없이 직접 넣으면, 나중에 그 기록을 "기록 수정" 창에서 고칠 때 세트를 하나 넣어야 저장된다(`EditActivityDialog.kt` 91행의 기존 규칙). 그 규칙은 고치지 않았다.
- 시간대는 기기 기본 시간대를 쓴다.

---

## B. 기록 내보내기 (CSV·JSON 파일)

**무엇을**: 이 기기에 저장된 활동 기록 전체를 CSV(표 계산 프로그램용) 또는 JSON(프로그램용) 파일로 저장한다. 지운 기록은 뺀다. 지금 로그인한 계정의 기록만 들어간다(로그인 전이면 "anonymous" 기록).

**어디서 어떻게 쓰나**
1. 설정을 연다. 로그인했으면 프로필 사진 → 설정, 로그인하지 않았으면 "로그인" 버튼 옆 톱니 버튼(후속 1회차).
2. 맨 아래 "기록" 묶음의 **"기록 내보내기"**에서 "CSV로 저장"이나 "JSON으로 저장"을 누른다.
3. 안드로이드 파일 저장 창이 열린다. 기본 이름은 `flowlog-activities-YYYYMMDD.csv`(또는 `.json`)이다. 위치를 고르면 저장된다.
4. 끝나면 "기록 N개를 내보냈어요." 또는 "기록을 내보내지 못했어요." 토스트가 뜬다.

- CSV 열: id, category, title, start, end, durationMinutes, note, tags(세미콜론 구분), linkedTodoId, sourceType, exerciseSets(JSON 글자).
- 시각은 기기 시간대의 ISO 8601이다. 예: `2026-10-20T09:30:00+09:00`.
- 쉼표·따옴표·줄바꿈이 든 칸은 따옴표로 감싸고, 안의 따옴표는 두 번 쓴다(CSV 표준 RFC 4180). 줄 끝은 CRLF.
- 오래된 기록부터 쓴다.
- **지시서에 없던 추가**: CSV 파일 맨 앞에 UTF-8 BOM(파일이 UTF-8이라고 알려 주는 3바이트)을 붙였다. 이게 없으면 윈도우 엑셀에서 한글 제목이 깨지기 쉽다. JSON에는 붙이지 않는다.
- JSON은 앱 안의 기록 모델(`ActivitySession`)을 그대로 배열로 쓴다. 그래서 동기화용 내부 칸(modifiedTime, remoteRevision, localActivityId 등)도 함께 나간다.

**왜 골랐나**: 기록이 앱과 웹 대시보드 안에만 갇혀 있으면 "내 데이터로 정직하게 돌아보기"가 앱이 보여 주는 화면까지로 한정된다. 원본을 사용자가 직접 가져가 엑셀 등에서 볼 수 있게 하는 것이 같은 방향이다. 분석을 앱이 약속하지 않고 사용자에게 맡긴다는 점에서, 과장 금지 원칙에도 맞는다.

**어떻게 확인했나**: 순수 변환기 `ui/viewmodel/ActivityExportFormatter.kt`에 `ActivityExportFormatterTest` 9개를 붙였다. 다룬 경우:
- 빈 목록
- 기본 한 줄과 분 계산
- 시간대에 따라 시각이 바뀌는지(서울 ↔ UTC)
- 이스케이프(쉼표, 따옴표, LF, CR, 빈 값)
- 메모 줄바꿈·태그·Todo 번호
- 운동 세트 JSON을 CSV에서 꺼내 다시 읽기
- 오래된 순 정렬
- JSON 왕복(쓰고 다시 읽으면 같은 값)
- 기본 파일 이름의 날짜·확장자

모두 통과했다.

**확인 못 한 것**:
- 파일 저장 창이 실제로 뜨는지.
- 파일이 실제로 쓰이는지.
- 엑셀에서 한글이 제대로 보이는지.
- 기록이 아주 많을 때 걸리는 시간.

**남은 일·알려진 문제**:
- 설정 창 내용이 길어져서 그 Column에 세로 스크롤을 붙였다(작은 화면에서 잘리지 않게).

---

## C. 앱 바로가기 (아이콘 길게 눌러 타이머 시작)

**무엇을**: 홈 화면에서 Flowlog 아이콘을 길게 누르면 "공부 시작", "업무 시작" 같은 바로가기가 최대 4개 뜬다. 메인 버튼 순서대로 앞의 4개 카테고리다. 누르면 앱이 열리면서 그 타이머가 바로 시작된다.

**어떻게 동작하나**
- 메인 버튼 설정이 바뀔 때마다(앱 시작 때 포함) `ShortcutManagerCompat.setDynamicShortcuts`로 다시 등록한다(`shortcut/TimerShortcutPublisher.kt`).
- 아이콘: 기존 카테고리 아이콘(`ic_activity_*`)을 카테고리 색 바탕 위에 흰색으로 그린다. 그 아이콘들은 알림용 흰색 그림이라, 바탕 없이 쓰면 밝은 런처에서 안 보이기 때문이다. 그림을 못 읽으면 앱 아이콘을 쓴다.
- 인텐트: action `com.example.flowlog.action.START_TIMER` + extra `category`. 앱이 새로 열릴 때(`onCreate`)와 이미 열려 있을 때(`onNewIntent`) 둘 다 처리한다.
- **외부 인텐트 방어**: MainActivity는 런처 진입점이라 다른 앱도 인텐트를 보낼 수 있다. 그래서 정확한 action이고, category가 알려진 카테고리 목록(`MainButtonConfig.ALL_SELECTABLE_CATEGORIES`)에 있을 때만 받는다. 그 밖에 이런 경우는 무시한다:
  - 최근 앱 목록에서 다시 연 경우(같은 인텐트가 다시 들어와 타이머가 또 켜지는 것 방지)
  - 화면 회전 등으로 다시 만들어진 경우
- 타이머가 이미 돌고 있으면 새로 시작하지 않는다. 대신 "이미 타이머가 돌고 있어요. 지금 타이머를 먼저 끝내 주세요." 토스트를 띄우고, 홈의 타이머 위치로 이동한다.
- 타이머 시작은 홈의 메인 버튼이 쓰는 `ActivityViewModel.startActivity(category)`를 그대로 부른다. 새 시작 경로는 만들지 않았다.

**왜 골랐나**: 기록이 빠지는 가장 큰 이유는 "앱을 열고 → 버튼을 찾는" 몇 걸음이다. 아이콘을 길게 누르는 한 번으로 줄이면 "가볍게 기록"에 바로 도움이 된다. A(빠뜨린 기록 메우기)와 짝을 이루는 예방책이다.

**어떻게 확인했나**: 순수 규칙 `shortcut/TimerShortcutRules.kt`에 `TimerShortcutRulesTest` 5개를 붙였다. 다룬 경우:
- 버튼 순서를 따르고 4개에서 멈추는지
- 모르는 카테고리·중복 제외
- 올바른 요청은 받는지
- 다른 action, null action, 모르는 값, 소문자, SNACK, extra 없음은 거절하는지
- 최근 앱에서 다시 연 경우는 무시하는지

모두 통과했다.

**확인 못 한 것** (기기 필요):
- 바로가기가 실제로 뜨는지.
- 아이콘 모양.
- 누르면 타이머가 시작되는지.
- 앱이 이미 열려 있을 때의 동작.
- 런처마다의 차이.

**남은 일**:
- 메인 버튼을 아직 설정하지 않은 상태에서는 바로가기가 없다.
- 안드로이드 7.0(API 24)에서는 동적 바로가기가 없으므로 아무 일도 하지 않는다(7.1부터 지원).

---

## 확인한 명령과 결과

```
export ANDROID_HOME=/tmp/claude-0/-home-user/7c40c1dc-b607-5f78-9497-ffe487ef55d0/scratchpad/android-sdk
export ANDROID_SDK_ROOT=$ANDROID_HOME
cd /home/user/Flowlog
bash ./gradlew :app:compileDebugKotlin -PofflineValidation=true --console=plain   → BUILD SUCCESSFUL, 오류 0
bash ./gradlew :app:testDebugUnitTest -PofflineValidation=true --console=plain    → BUILD SUCCESSFUL
```
- 테스트 결과(`app/build/test-results/testDebugUnitTest/*.xml` 합계): 16개 묶음, **114개 테스트, 실패 0, 오류 0, 건너뜀 0**. 후속 1회차 뒤 다시 돌려 **115개, 실패 0**(같은 날짜 판정 테스트 1개 추가).
- 고치기 전 기준선(같은 명령): **89개, 실패 0**. 새로 25개 늘었다(11 + 9 + 5).
- 메인이 먼저 돌린 테스트(`logs/unit-tests.log`)는 테스트 결과가 아니었다. Maven Central에서 KSP 플러그인을 못 받아(`EXIT=1`) 실패한 기록이다. 다시 돌렸을 때도 Maven Central이 `429 Too Many Requests`(요청이 너무 많다는 거절)를 몇 번 돌려줬다. 그래서 실패하면 45초 쉬고 다시 시도하는 감싸개(`scratchpad/bin/gradle-retry.sh`)로 돌렸다. 저장소 설정은 바꾸지 않았다.

## 바뀐 파일

수정 8개 (후속 1회차 포함 `git diff --stat` 기준 372줄 추가, 16줄 삭제):
- `README.md`: Features 3줄, Architecture에 `shortcut/` 한 줄.
- `CHANGELOG.md`: Unreleased 맨 위에 3항목.
- `MainActivity.kt`: 바로가기 인텐트 처리와 등록, 설정 창의 내보내기 묶음, 설정 창 스크롤.
- `ActivityViewModel.kt`: `addManualActivity`, `exportActivities` 추가.
- `HomeScreen.kt`: 직접 추가 창 연결.
- `RecentRecordsSection.kt`: "직접 추가" 버튼.
- `EditActivityDialog.kt`: 카테고리 칩·입력칸 색 함수 2개를 `private` → `internal`로 바꿔 다시 쓸 수 있게 했다. 동작은 그대로다.
- `strings.xml`: 새 문구 33개.

새 파일 8개:
- `ui/viewmodel/ManualActivityValidator.kt`
- `ui/viewmodel/ActivityExportFormatter.kt`
- `ui/screen/home/ManualActivitySection.kt`
- `shortcut/TimerShortcutRules.kt`
- `shortcut/TimerShortcutPublisher.kt`
- 테스트 3개

버전(`versionName` 0.5.9, `versionCode` 26)은 바꾸지 않았다. 의존성도 바꾸지 않았다(새 라이브러리 없음).
