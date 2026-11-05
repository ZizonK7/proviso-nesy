# scripts/ — 저장소 운영 도구

proviso 본체(코어·분야)가 아니라 작업을 굴리는 데 쓰는 도구. 표준 라이브러리만.

- `agent_usage.py`: 하위 에이전트 대화 기록(JSONL)을 사용량 숫자로 요약 → `domains/agent_usage/dispatches.toml`의 `actual`에 옮겨 적는다(분, 턴, 합계 토큰은 백만 단위). batman 지휘 모델의 기록도 같은 방법으로. batman 저장소에서 가져옴(UTF-8 읽기, meta.json 설명을 이름으로 쓰도록 수정).
  - 이 PC의 기록 위치: `C:/Users/minii/.claude/projects/<프로젝트>/<세션>/subagents/agent-*.jsonl` (+ 같은 이름의 `.meta.json`). Git Bash의 `/c/...` 경로는 Python이 못 읽으니 `C:/...`로 넘긴다.
  - 클라우드 세션의 기록 위치: `/root/.claude/projects/<작업 폴더>/<세션>/subagents/agent-*.jsonl`. 세션 도중 작업 폴더가 바뀌면 `<작업 폴더>` 이름도 바뀌어 기록이 두 폴더에 나뉜다(2026-10-19: `-home-user-proviso-nesy`와 `-home-user`). 컨테이너가 회수되면 사라지니 끝나는 대로 바로 옮긴다.
  - 이어 보낸 에이전트는 한 파일에 회차가 쌓인다: `--rounds`로 회차마다 시작·끝 시각을 보고, 그 회차 시작 시각을 `--after`에 줘서 `--actual`·`--turns --toml`을 돌린다(그 회차만 센다). 분은 완료 알림의 실행 시간이 있으면 그것을 쓴다(로그 전체의 시작–끝에는 회차 사이 쉬는 시간이 끼어 있다).
  - `--turns` (2026-10-26): 턴마다 동작 종류·턴 길이·도구 시간·출력 글자·맥락을 뽑아 동작별 중앙값 표로 낸다. agent_usage 논리집의 전제 1(턴은 비슷한 크기다)을 가설 대신 측정으로 치우기 위한 것 — [domains/agent_usage/CLAUDE.md](../domains/agent_usage/CLAUDE.md) "전제 1 시험". Bash는 실제 동작 낱말(앞의 `cd <폴더> &&`·환경 변수·time 등을 뗀 첫 낱말, 2026-11-05 p238부터 — 그 전 표는 첫 낱말 그대로)만 쓰고 본문은 출력하지 않는다.
  - `--turns --toml` (2026-11-02): 같은 숫자를 `dispatches.toml` 기록 끝에 그대로 붙일 `[dispatch.turns]` 블록으로. 2026-11-03부터 끝난 기록에 필수(검사가 막는다). `--after <시각>`은 그 뒤에 시작한 턴만 — 이어 보낸 에이전트는 한 파일에 회차가 쌓이므로 앞 회차 끝 시각을 준다(ISO 시각 또는 UTC `HH:MM:SS`).
  - `--until <시각>` (2026-11-03): 그 시각까지만 센다 — 메인이 직접 한 일처럼 기록이 그 뒤로 이어질 때, `--rounds`로 본 그 요청의 시작·끝을 `--after`·`--until`에 준다(`record finish <m…>`가 쓴다).
  - `--rounds` (2026-11-03): 회차 경계(답한 뒤에 들어온 지시마다 새 회차)와 회차마다 시작·끝 시각·응답 줄 수. 이어 보낸 회차의 `--after`에 줄 시각을 여기서 얻는다(앞 회차 기록에 끝 시각이 없어도 된다).
  - `--actual` (2026-11-03): 실측을 `dispatches.toml`의 `[dispatch.actual]` 줄로(분·턴·토큰 + 시작·끝 시각 `start`/`end`, UTC ISO). 2026-11-04부터 끝난 기록에 시각이 필수 — 빗댄 기록 규칙(`domains/agent_usage/analog.py`)이 '보낼 때 끝나 있던 기록'을 가르는 데 쓴다.
  - `--log` (2026-11-05): 로그에서 싸게 얻는 숫자 전부(`LOG_KEYS`: 파일·읽기·명령·맥락·생각 시간·지시 길이 등, 뜻은 `log_numbers` 설명). `--toml`이면 `[dispatch.log]` 블록 — `record finish`가 붙이고 2026-11-06부터 끝난 기록에 필수. 실측이지 예측 입력이 아니다.
  - `brief_text(로그, after, until)` (2026-11-05): 창 안의 첫 지시 글을 돌려준다(출력·저장하지 않음). `domains/agent_usage/measure.named`가 지시서에 적힌 파일의 크기를 재는 데만 쓴다(`[dispatch.git]` named_*).
  - 대화 내용은 출력하지 않는다. 숫자만.
  - 기록 파일은 세션 폴더에 남지만, 정리될 수 있으니 배치가 끝나면 바로 기록한다.
- `claude_http.py` (2026-11-03): Claude API를 표준 라이브러리(urllib)로 부른다(외부 패키지 없음 규칙). 키는 환경 변수 `API`에서만 읽고 출력·저장하지 않는다(공개 저장소). `cost(usage, batch=)`는 claude-opus-5-5 가격으로 usage를 달러로(배치는 절반). 쓰는 곳: `domains/far_fields`.
