# scripts/ — 저장소 운영 도구

proviso 본체(코어·분야)가 아니라 작업을 굴리는 데 쓰는 도구. 표준 라이브러리만.

- `agent_usage.py`: 하위 에이전트 대화 기록(JSONL)을 사용량 숫자로 요약 → `domains/agent_usage/dispatches.toml`의 `actual`에 옮겨 적는다(분, 턴, 합계 토큰은 백만 단위). batman 지휘 모델의 기록도 같은 방법으로. batman 저장소에서 가져옴(UTF-8 읽기, meta.json 설명을 이름으로 쓰도록 수정).
  - 이 PC의 기록 위치: `C:/Users/minii/.claude/projects/<프로젝트>/<세션>/subagents/agent-*.jsonl` (+ 같은 이름의 `.meta.json`). Git Bash의 `/c/...` 경로는 Python이 못 읽으니 `C:/...`로 넘긴다.
  - 대화 내용은 출력하지 않는다. 숫자만.
  - 기록 파일은 세션 폴더에 남지만, 정리될 수 있으니 배치가 끝나면 바로 기록한다.
