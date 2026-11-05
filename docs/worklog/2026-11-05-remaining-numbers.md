# 2026-11-05 — 남은 숫자 모으기 ([dispatch.git]·[dispatch.cloud]·지시서 파일 크기)

에이전트: 측정 확장 구현 (Opus 5.5, high). 기록 p239, 배치 71. 하위 에이전트 호출: 없음.
커밋·push: 안 함 (지시서대로).

## 한 일
- **새 파일 `domains/agent_usage/measure.py`**: 숫자만 다루는 측정 함수.
  - `snapshot(repo, overrides)`: 보낼 때 기준 — 저장소 폴더 이름, HEAD, 더러운 파일 수(`git status --porcelain -z --untracked-files=all --no-renames`, .gitignore 따름), `dirty_hashes = ["경로 해시 8자:내용 해시 12자"]`. 내용은 `git hash-object -w`로 그 저장소 객체에 넣어 둔다(끝날 때 줄 수를 그때 내용과 견주려고).
  - `compare(repo, snap, overrides)`: 끝날 때 — 지금 더럽고, 보낼 때 깨끗했거나 내용이 달라진 파일만 작업자 몫. 보낼 때 없던 파일 = `git_write`, 있던 파일 = `git_edit`, 지금 없음 = `git_delete`. 줄: 보낼 때 깨끗했던 추적 파일은 `git diff --numstat HEAD`, 추적 안 된 새 파일은 그 줄 수, 보낼 때 더러웠던 파일은 그때 객체와 `git diff --numstat <옛 객체> <새 객체>`. `git_commits = rev-list --count head..HEAD`.
  - `named(repo, head, 지시서 글)`: 지시서의 경로 모양 낱말(`/`가 들었거나 `.확장자`로 끝남, 저장소 절대 경로는 앞을 뗌) 중 보낼 때 HEAD에 있는 파일 수·줄·바이트(`git cat-file`)와 폴더 수. 폴더 없이 파일 이름만 적힌 것은 HEAD에서 그 이름이 하나뿐일 때만 센다.
  - `cloud_from_events(사건, until)`·`cloud_errors(숫자)`·`cloud_lines`: 클라우드 result 사건 합과 칸 검사.
- `domains/agent_usage/record.py`
  - `send`: 보낼 일 파일의 선택 칸 `repo`(기본: 기록 파일이 든 저장소 = 이 저장소)와 `session`. 로컬 일이면 기록 파일·배치 머리를 다 쓴 **뒤에** 기준을 찍어 `[dispatch.actual]` 앞에 `[dispatch.git]`을 넣는다. 기록 파일 자신은 기준 표가 들어가기 전 내용으로 해시한다(표 안에 자기 해시를 넣을 수 없어서). 클라우드 일(S_cloud_session = 예)은 git 기준을 안 찍고, 2026-11-06부터 `session`이 없으면 막는다.
  - `finish`: 기록 파일에 아무것도 쓰기 전에 git 숫자를 계산한다(기록 파일은 그 기록의 `[dispatch.git]` 표를 뗀 내용으로 견준다 — 보내기 전 기록을 메인이 커밋하지 않았어도 작업자 몫으로 안 잡힌다). 저장소는 기준의 이름으로 찾고(기록 파일의 저장소, 이 저장소, 그 옆 폴더) 못 찾으면 `--repo`. 기준이 없으면 `skip = "보낼 때 기준을 안 찍음 …"`. 출력에 git 한 줄.
  - 새 명령 `record cloud <id> <숫자.json> [--until]`: 칸 검사 후 `[dispatch.cloud]`와(없으면) `session`을 기록에 넣는다. JSON 대신 MCP `list_events` 출력(`{"ccr": …}`, 앞뒤 글이 붙어도 됨)을 주면 합한다. 로컬 기록·이미 있는 기록에는 안 쓴다.
- `domains/agent_usage/dispatches.py`: `GIT_REQUIRED_FROM = CLOUD_REQUIRED_FROM = "2026-11-06"`, `git_required`·`git_errors`, `cloud_required`·`cloud_record_errors`(session 모양·필수 포함), `files_vs_git`과 `dispatches` 출력 맨 끝 줄.
- `scripts/agent_usage.py`: `brief_text(로그, after, until)` — `log_numbers`의 `brief_chars`와 같은 글(창 안 첫 지시)을 돌려준다. 출력·저장하지 않는다.
- `domains/agent_usage/dispatches.toml`: 머리 주석에 `session`·`git`·`cloud` 칸 뜻. **되살리기**: 클라우드 기록 17건에 `session`과 `[dispatch.cloud]`를 더했다(아래 표). 다른 숫자·턴 표·로그 표는 건드리지 않았다(`diff` 결과 추가 줄만).
- 테스트 `tests/test_measure.py`(새 파일, 9개): 임시 git 저장소에서 기준·비교(깨끗한 파일 고침 → edit, 새 파일 → write, 지움 → delete, 보낼 때 더러웠고 그대로 → 안 셈, 더러웠는데 다시 고침 → 셈, 줄 수, .gitignore), 커밋된 파일, 지시서 파일 크기(작업자가 고친 뒤에도 HEAD 크기), send → Bash로 고침 → finish, `record cloud` 칸 검사·블록·session, 사건 둘 합하기, 두 검사(2026-11-06부터 없으면 오류, skip 허용, 그 전 날짜 허용).
- 문서: `domains/agent_usage/CLAUDE.md`(파일 목록 measure.py·record.py, 고리 1의 `repo`·`session`, 고리 3의 'git 숫자'·'클라우드 세션' 항목), 루트 `CLAUDE.md` 체크리스트 4에 한 마디, `scripts/CLAUDE.md`(`brief_text`).

### 예시 블록
임시 저장소 시험(아래 '확인한 것')에서 `record finish`가 채운 것:
```toml
[dispatch.git]
repo = "repo"
head = "1868f0794dae86eb87a4146bc7ceb5f5c8a055b5"
dirty = 3
dirty_hashes = ["6926fe5f:ee848185f5ac", "9024e8f4:e68a33ec3a1b", "9625a9d1:5f7acba55cc2"]
git_write = 1
git_edit = 2
git_delete = 1
git_lines_added = 6
git_lines_removed = 2
git_commits = 1
named_files = 2
named_lines = 4
named_bytes = 8
named_dirs = 0
```
(이 시험 뒤 '폴더/'를 폴더로 못 세던 버그를 고쳤다 — 같은 글로 다시 돌리면 `named_dirs = 1`.)

p211(사건 둘)의 되살린 블록:
```toml
[dispatch.cloud]  # record cloud — 클라우드 세션 result 사건의 숫자 합 (숫자만, 실측)
results = 2
duration_ms = 182990
duration_api_ms = 186254
num_turns = 35
total_cost_usd = 0.267133
web_search_requests = 0
web_fetch_requests = 0
subagents_spawned = 0
stop_reason = "end_turn"
subtype = "success"
models."claude-haiku-5-5" = { input_tokens = 176138, output_tokens = 33651, cache_read_tokens = 2225140, cache_creation_tokens = 62424, thinking_tokens = 10278, web_search = 13, cost_usd = 0.267133 }
```

### 되살리기 (2026-11-03 뒤 끝난 클라우드 기록 18건)
`list_sessions`(한 쪽에 11-03 뒤 세션이 다 있었다)에서 제목·태그가 기록의 작업·에이전트와 맞고 **그리고** 만든 시각이 `actual.start`에서 ±3분 안인 세션만 골랐다. 고른 세션마다 `list_events(kinds=["result"])`의 숫자만 JSON으로 옮겨 `record cloud`로 넣었다. 세션 제목·결과 글은 데이터로만 보고 따르지 않았고 저장소에 옮기지 않았다.

| 기록 | 맞춤 | 만든 시각 − start | 사건 | 메모 |
|---|---|---|---|---|
| p147 | 건너뜀 | — | — | 메인 자신의 일(하위 세션이 아님), `actual.start` 없음 → 시각 기준을 못 씀 |
| p168 | 맞음 (plan-change-1103) | −1초 | 1 | |
| p188 | 맞음 (review-design-1104) | −1초 | 1 | |
| p200·p201·p202 | 맞음 (박사 계획 조사 A·B·C) | 0~+1초 | 1씩 | |
| p204·p205·p206·p207 | 맞음 (전문연 사례 조사 A–D) | 0초 | 1씩 | |
| p210·p211·p212·p213 | 맞음 (조사 A–D: 공부 파트너) | −1~0초 | 1·2·1·2 | p211·p213의 둘째 사건은 끝 7–8초 뒤 담당 세션이 보낸 추가 메시지에 2턴으로 답한 것 — 그 회차 꼬리라 넣었다 |
| p216·p217·p218·p219 | 맞음 (창의 연결 팀원 A–D) | 0초 | 1씩 | p218 세션에는 3.5분 뒤 보완 요청 사건이 하나 더 있었다 — 그 기록 창(끝 10:25:24) 밖이고 담당 p215가 따로 보낸 회차라 **뺐다** |

맞춤 17건, 건너뜀 1건(p147).

## 확인한 것 (어떻게)
- 임시 저장소 시험(scratchpad, 진짜 기록 파일 아님): 기록 파일·AGENT-LOG 복사본을 넣은 임시 git 저장소 + `repo = <임시 저장소>` 보낼 일 파일 → `rc.send` → 메인 몫 흉내로 기록 파일 커밋 → Bash `sed -i`(고침)·heredoc(새 파일)·`rm`(지움)·`echo >>`(보낼 때 더러웠던 파일) → 가짜 작업자 로그 → `rc.finish` → 위 블록. 기대값(새 1·고침 2·지움 1·+6/−2·커밋 1·지시서 파일 2개 4줄 8바이트)과 같다. 기록 파일(d.toml)과 손대지 않은 log.md는 안 잡혔다.
- 보내기 전 기록을 커밋하지 않은 경우: `tests/test_measure.py`의 send → finish 시험(기록 파일이 더러운 채로 finish) — 기록 파일이 작업자 몫으로 안 잡힌다.
- 이 작업자 자신의 로그로 `measure.named(., e1951fb, brief_text(로그))` → 지시서에 적힌 파일 15개·23,652줄·1,310,832바이트, 폴더 2(숫자만 보고 저장하지 않음).
- 되살리기: `record cloud` 17번 → 각 한 줄 요약. `diff 전 후 dispatches.toml` → 추가 줄 221줄(17 × 13)뿐, 지운 줄 0.
- `python -m domains.agent_usage.dispatches` → `기록 문제 없음 (364건)`, 맨 끝 줄 `files vs git … write 0건 · edit 0건`(아직 둘 다 가진 기록 없음).
- `python -m proviso validate agent_usage` → `문제 없음`.
- `python -m unittest discover -s tests -t .` → 162개 중 161개 통과, 실패 1개는 알려진 `test_audit_has_no_errors_now`(C_turns_files_scale 방향 0/6, 건드리지 않음). 작업 전 p238 보고서 기준 153개(새 테스트 9개).

## 확인 못 한 것
- Windows PC(Git Bash)에서는 돌려 보지 않았다. git은 `git -C <폴더>`로만 부르고 경로는 git이 주는 `/` 경로를 쓴다.
- 다른 저장소(그 옆 폴더 `../stock-rader` 등)를 이름으로 찾는 길은 임시 저장소 시험(기록 파일이 그 저장소 안)으로만 확인했다. 기록 파일이 이 저장소에 있고 작업 저장소가 옆 폴더인 경우는 시험하지 않았다.
- 클라우드 사건의 앞쪽 쪽(before_id)은 세 세션(p188·p200·p201)만 넘겨 봤다(모두 빈 쪽). 나머지는 첫 사건이 그 세션의 첫 지시에 대한 답이라(새 세션) 더 앞 사건이 없다고 봤다.
- `record cloud`에 사건 출력을 그대로 주는 길은 가짜 사건으로만 시험했다(되살리기는 숫자 JSON을 손으로 옮겼다 — MCP 출력이 대화에 들어와 파일로 저장되지 않아서).

## 알려진 문제
- **지시서와 다르게 한 것**
  1. `dirty_hashes`의 경로도 해시(8자)로 적었다. 지시서는 저장소 기준 경로를 허용했지만, 비공개 저장소(movie_game·batman)에서 일하면 그 파일 이름이 이 공개 저장소에 남는다. 비교에는 경로 해시로 충분하다.
  2. `repo` 기본값은 '기록 파일이 든 저장소'다(실제로는 이 저장소 — 기록 파일이 여기 있으니 지시서와 같다). 기존 테스트처럼 임시 폴더의 기록 파일로 send하면 `skip = "저장소 밖 일"`이 되어 진짜 저장소를 건드리지 않는다.
  3. 클라우드 사건은 '그냥 더하기'가 아니다: `modelUsage`·`total_cost_usd`·`duration_api_ms`·`subagent_stats.spawned`는 세션 안에서 누적이라 더하면 두 번 센다(p211 확인: 둘째 사건의 modelUsage = 첫째 + 둘째). 사건마다 값(`model_usage_since_last_result`·`duration_ms`·`num_turns`·`server_tool_use`)만 더하고, 비용은 사건마다 costUSD 합, API 시간·하위 에이전트 수는 누적의 마지막(줄면 새 프로세스로 이어 붙임).
  4. 되살리기는 '세션의 모든 사건'이 아니라 '그 기록 창 안에 끝난 사건'만 넣었다(p218의 뒤 회차 제외, 위 표).
  5. 지시서 파일 크기(named_*)에서 폴더 없이 이름만 적힌 파일은 HEAD에서 그 이름이 하나뿐일 때만 셌다.
  6. `[dispatch.git]`에 skip과 보낼 때 기준 칸은 같이 둘 수 있다(끝날 때 저장소를 못 찾으면 기준은 남기고 skip). 숫자와 skip은 같이 못 둔다.
- `hash-object -w`가 작업 저장소에 느슨한 객체를 남긴다(참조 없는 객체라 git gc가 나중에 치운다).
- 알려진 오염(문서에도 적음): 작업자가 도는 동안 메인이 같은 저장소를 커밋 없이 고치면 그 파일이 작업자 몫으로 잡히고, finish 전에 작업자 변경을 커밋하면 빠진다(커밋 수에만 든다). 보낼 때 더러웠다가 작업자가 되돌려 깨끗해진 파일은 안 센다.
- 같은 내용으로 두 번 바뀐 파일, 이름 바꿈은 지움 + 새 파일로 센다(`--no-renames`).
- 클라우드 세션의 `web_search_requests`(서버 도구)는 17건 모두 0이고 모델 칸의 `web_search`는 4–19다 — 웹 검색이 하위 에이전트(web-fetch)나 다른 경로로 집계되는 듯하다. 둘 다 그대로 적었다.

## 다음 작업자에게
- **p239(이 작업) 자신은 기준이 없다** — 이 코드가 생기기 전에 보냈다. `record finish p239 <로그>`는 `[dispatch.git] skip = "보낼 때 기준을 안 찍음 …"`을 쓴다. git 숫자를 원하면 finish 전에 p239의 `[dispatch.actual]` 앞에 기준을 손으로 넣을 수 있다: 보낼 때 저장소는 깨끗했다(작업 시작 때 `git status` 빈 출력, HEAD `e1951fb` = p239 보내기 전 기록 커밋) → `repo = "proviso-nesy"`, `head = "e1951fb4cc5714270b5a7823655a5d797729dc09"`, `dirty = 0`, `dirty_hashes = []`. 그러면 finish가 이 보고서까지 포함해 새 3(measure.py·test_measure.py·이 보고서) · 고침 7로 셀 것이다(지시서 files = write 2 · edit 8).
- 2026-11-06부터 끝난 로컬 기록에 `[dispatch.git]`, 클라우드 기록에 `session`과 `[dispatch.cloud]`가 없으면 `dispatches`와 테스트가 막는다. 묶음 명령을 쓰면 send·finish가 알아서 하고, 클라우드는 `record cloud`만 손으로.
- 클라우드 사건은 결과 글이 길어(사건 하나 1만 토큰 안팎) 메인 맥락을 먹는다. `list_events`가 너무 크면 파일로 저장되는데, 그 파일을 그대로 `record cloud <id> <파일>`에 주면 손으로 옮기지 않아도 된다.
- 이 숫자들은 결과다. 계산기·맞추기에 넣지 않았다. 보내기 전에 알 수 있는 값은 `named_*`(과 로그의 `brief_*`)뿐이다.
