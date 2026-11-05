# 2026-11-05 — 작업자 로그에서 숫자 더 뽑기 ([dispatch.log])

에이전트: 측정 확장 구현 (Opus 5.5, high). 기록 p238, 배치 70. 하위 에이전트 호출: 없음.
커밋·push: 안 함 (지시서대로).

## 한 일
- `scripts/agent_usage.py`
  - `log_numbers(path, after, until)`: 작업자 로그 하나에서 숫자만 뽑는다. 창(after·until)은 `--actual`과 같다 — 그래서 `summarize`의 줄 고르기를 `_window`로 떼어 내 둘이 같이 쓴다(동작은 그대로; 기존 테스트와 p237 `--actual` 숫자가 같음을 확인). 칸 이름은 `LOG_KEYS`, 뜻은 함수 설명과 `dispatches.toml` 머리 주석.
  - `log_toml(n, header)`: `[dispatch.log]` 블록(직접 한 일은 `[direct.log]`).
  - `--log` 플래그(`--toml`이면 블록, 아니면 JSON 한 줄). `--after`·`--until`을 같이 받는다.
  - `bash_verb(cmd)`: Bash 동작 이름. 앞의 `cd <폴더> &&`·`cd <폴더>;`, 따로 선 대입(`X=값;`·`export X=값 &&`), 환경 변수 앞붙이(`X=값 명령`), `X=$(명령 …)`의 안쪽, 감싸는 명령(time·nohup·env·sudo·exec·`timeout N`), 여는 `(`·`{`를 떼고 첫 낱말의 파일 이름. `--turns`의 `_action`이 이것을 쓴다. 문서 설명(머리 docstring)도 고쳤다.
  - `is_scratch(path)`: 임시 파일 = `/tmp/`·`/var/tmp/`, 홈의 `.claude/`(`/root`·`/home/<이름>`·`C:/Users/<이름>`, 그리고 실행하는 사람의 `~`), Windows `AppData/Local/Temp/`. 저장소 안의 `.claude/` 폴더는 임시가 아니다.
- `domains/agent_usage/record.py`: `finish`가 턴 표 뒤에 `[dispatch.log]`를 붙인다(실측과 같은 창). 이미 있으면 다시 쓰지 않는다. 직접 한 일(`finish m… <메인 로그> --after --until`)도 같은 창으로 `[direct.log]`를 붙인다 — 칸이 같고 창만 다르므로 깔끔하게 들어갔다. 기록 사이 빈 줄은 그대로 둔다.
- `domains/agent_usage/dispatches.py`
  - `LOG_REQUIRED_FROM = "2026-11-06"`, `log_required`(= `form_required`와 같은 모양: 끝났고 실측 분이 있고 날짜가 그날 이후), `log_errors`. 턴 표 검사를 그대로 본떴다: 없으면 오류, `skip = "이유"` 한 줄 허용(다른 칸과 같이 쓰면 오류), 이어 보낸 회차(round ≥ 2)는 클라우드 세션이 아니면 skip 못 함. 턴 표 검사에는 batman·메인 자신 면제가 없어서 여기에도 없다. 칸이 있으면 날짜와 상관없이 모양(LOG_KEYS가 다 있고, 모르는 칸 없고, 0 이상의 수)을 본다.
  - `validate_direct`도 `[direct.log]`가 있으면 모양만 본다(필수는 아님 — 직접 한 일에는 턴 표 필수도 없어서 본뜰 것이 없다).
  - `files_vs_log(records)`와 `dispatches` 출력 맨 끝 한 줄: 지시서에서 센 `files`와 로그의 `write`·`edit`를 둘 다 가진 기록에서 칸마다 같음 / 로그가 많음 / 로그가 적음.
  - `LOG_KEYS`는 `scripts/agent_usage.py`에서 가져온다(칸 이름을 한 곳에만 둔다).
- `domains/agent_usage/dispatches.toml`: 머리 주석에 `log` 칸 설명과 Bash 이름이 바뀐 시점을 더했다. **p237에 `[dispatch.log]`만 더했다**(아래). 다른 기록·숫자·턴 표는 건드리지 않았다.
- 테스트: `tests/test_agent_usage.py`(가짜 로그 픽스처 + 3개), `tests/test_agent_usage_domain.py`(검사 1개), `tests/test_decide.py`(기존 finish 테스트 둘에 log 확인 줄).
- 문서: `domains/agent_usage/CLAUDE.md`(고리 3에 '로그 숫자' 항목, 파일 목록의 record.py, 전제 1 시험의 도구 설명), 루트 `CLAUDE.md` 체크리스트 4에 한 마디, `scripts/CLAUDE.md`(`--turns` 설명의 Bash 이름, `--log` 항목 — 지시서에 없던 파일이지만 '첫 낱말만'이라는 설명이 틀리게 되어 같이 고침).

### 칸 (LOG_KEYS)
`responses` 서로 다른 응답 수 · `blocks` 응답 줄 수(= `actual.turns`) · `write` Write로 쓴 파일(Write와 Edit 둘 다 받으면 write) · `edit` Edit·NotebookEdit(·MultiEdit)만 받은 파일 · `scratch_files` 쓰거나 고친 임시 파일 · `write_chars`·`edit_chars`·`write_lines` (임시 파일 뺌) · `read_calls`·`read_files`·`read_chars`(Read 결과 글자, 그림 뺌)·`images`(모든 도구 결과의 그림) · `bash_calls`·`bash_out_chars` · `grep_calls`·`glob_calls`·`web_search`·`web_fetch`·`agent_calls`(Agent·Task)·`other_tool_calls` · `tool_errors` · `repeat_cmds` · `ctx_start_k`·`ctx_max_k`·`ctx_end_k`(응답마다 입력 + 캐시 생성 + 캐시 읽기, 천 토큰, 반올림) · `thinking_blocks` · **`thinking_s`** · `brief_chars`·`brief_lines`(창 안 첫 지시. 붙어 오는 안내 줄 `isMeta`는 지시로 안 친다).

### p237의 블록 (실제 로그에서, `record finish`로)
```toml
[dispatch.log]  # scripts/agent_usage.py --log --toml (숫자만, 실측 — 예측 입력 아님)
responses = 74
blocks = 163
write = 2
edit = 1
scratch_files = 1
write_chars = 73424
edit_chars = 231
write_lines = 762
read_calls = 40
read_files = 19
read_chars = 36283
images = 38
bash_calls = 60
bash_out_chars = 274507
grep_calls = 0
glob_calls = 0
web_search = 0
web_fetch = 0
agent_calls = 0
other_tool_calls = 1
tool_errors = 1
repeat_cmds = 0
ctx_start_k = 62
ctx_max_k = 452
ctx_end_k = 452
thinking_blocks = 55
thinking_s = 292.8
brief_chars = 11198
brief_lines = 50
```
지시서에서 센 `files = { write = 2, edit = 1 }`과 같다. 생각 시간 292.8초는 실행 21.8분의 22 %.

## 확인한 것 (어떻게)
- `python3 -I <프로토타입> <p237 로그>` → 응답 74 · 줄 163 · Write 3(저장소 안 2) · Edit 1 · 읽은 파일 19 · 읽은 글 36,283자 · 그림 38 · 도구 오류 1. 새 함수가 같은 수를 냈다(Write 글자는 프로토타입 80,321 = 임시 파일 포함, 새 함수 73,424 = 임시 파일 뺌).
- `python scripts/agent_usage.py <p237 로그> --actual` → turns 163 = `log.blocks` 163.
- `python scripts/agent_usage.py <p237 로그> --turns --toml` → Bash 줄이 `cat 16 · sed 13 · grep 7 · python3 7 · python 5 · git 4 · mkdir 3 · awk 2 · ls·for·curl 1`(옛 표: `cd 11 · out; 4 · explainer; 3 · PYTHONPATH=. 2 · scratchpad; 1 · export 1` 등). 기록의 표는 바꾸지 않았다.
- 임시 복사본에서: `dispatches.toml`을 scratchpad에 복사 → `record.finish('p237', <로그>, path=<복사본>)` → `diff` 결과는 `[dispatch.log]` 30줄 추가뿐(실측 줄은 같은 숫자로 다시 써져 차이 없음). 그다음 진짜 파일에 같은 `finish`를 돌리고 `cmp 진짜 복사본` → 같음.
- `python -m domains.agent_usage.dispatches` → `기록 문제 없음 (363건)`, 맨 끝 줄 `쓰는 파일 수 — … write 1건(같음 1) · edit 1건(같음 1)`.
- `python -m proviso validate agent_usage` → `문제 없음`.
- `python -m unittest discover -s tests -t .` → 153개 중 152개 통과, 실패 1개는 알려진 `test_audit_has_no_errors_now`(C_turns_files_scale 방향 0/5, 건드리지 않음). 작업 전에는 149개 중 같은 1개 실패(새 테스트 4개). 첫 전체 실행에서 새 검사 테스트가 오류(가짜 기록에 `predicted` 칸이 없어 `validate`가 넘어짐) — 칸을 채워 고친 뒤 다시 돌린 결과다.

## 확인 못 한 것
- Windows PC 로그(`C:\Users\…` 경로, Git Bash)에서는 돌려 보지 않았다. 역슬래시는 `/`로 바꿔 보지만 실제 PC 로그로는 시험하지 않았다.
- `[direct.log]`는 가짜 메인 로그 테스트로만 확인했다. direct.toml의 실제 기록에는 붙이지 않았다(지시서 범위 밖).
- `record finish`의 명령줄 입구(`python -m domains.agent_usage.record finish …`)는 진짜 파일에 돌리지 않고 함수를 불렀다(같은 함수 + 끝의 검사 출력만 다름). 검사는 따로 `dispatches`로 돌렸다.

## 알려진 문제
- **지시서와 다르게 한 것**: `thinking_s`(생각 시간 합, 초) 칸을 더했다. 로그 줄마다 `thinkingDurationMs`가 있어서 싸게 얻고, 생각 블록이 0글자로 남아 "생각하는 양은 글자로 못 잰다"(전제 1 시험)는 빈틈을 직접 메운다. 필수 칸에 들어 있으니 빼려면 `LOG_KEYS`에서 지우고 p237 블록의 한 줄을 지우면 된다.
- Bash 이름: `cd`·대입·감싸는 명령만 뗀다. `mkdir -p x && python …`은 `mkdir`, `for …; do …`는 `for`, `source venv && …`는 `source`로 남는다.
- `read_chars`는 Read 결과 그대로라 줄 번호 앞붙이(cat -n 모양)가 들어 있다 — 파일 글자 수보다 크다.
- `write_chars`·`write_lines`는 Write 호출마다 더한다 — 같은 파일을 두 번 통째로 쓰면 두 번 센다(파일 수 `write`는 한 번).
- 맥락은 응답의 첫 줄 사용량으로 잰다(같은 응답의 줄마다 사용량이 반복된다).
- `repeat_cmds`는 글자까지 똑같은 명령만 센다(공백만 다른 것은 다르게 친다; 앞뒤 공백은 뗀다).
- 창 앞에 시작한 도구 호출의 결과가 창 안에 들어오면 어느 도구인지 몰라 `read_chars`·`bash_out_chars`에 안 들어간다(그림·오류 수에는 들어간다).

## 다음 작업자에게
- 2026-11-06부터 끝난 기록에 `[dispatch.log]`가 없으면 `dispatches`와 테스트가 막는다. `record finish`가 알아서 붙이므로 묶음 명령을 쓰면 된다. 손으로 할 때는 `python scripts/agent_usage.py <로그> --log --toml [--after <그 회차 시작>]`.
- 이 숫자들은 결과다. 계산기(`predict.py`)·맞추기(`fit.py`)·홀드아웃에 넣지 않았다. 예측 입력으로 쓰려면 보내기 전에 알 수 있는 값인지부터 가른다 — `brief_chars`·`brief_lines`만 그렇다.
- `files_vs_log`가 쌓이면 '지시서에서 센 파일 수'가 실제와 얼마나 어긋나는지 보인다(지금 p237 1건, 둘 다 같음). 비율 조각(C_turns_files_scale) 시험이 실측 파일 수로도 돌 수 있는지 볼 만하다.
- 턴 표의 Bash 이름은 p238부터 실제 동작이다. 동작별 중앙값을 기록끼리 합칠 때 p237 이전 표의 `Bash:cd` 등은 따로 다뤄야 한다.
