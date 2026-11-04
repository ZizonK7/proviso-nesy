# proviso-nesy — Claude 작업 문서 (루트)

Claude가 세션 시작 시 자동으로 읽는 작업 문서. 사람용 소개는 [README.md](README.md).
**이 파일은 지도와 공통 규칙만 둔다.** 분야·작업의 자세한 것은 그 폴더 `CLAUDE.md`(그 폴더 파일을 열면 같이 읽힌다), 지난 경위는 [docs/history.md](docs/history.md).

## 프로젝트
SELA(자기 진화형 신경-기호 논리 아키텍처) 구현. 원안 논문: [docs/sela-paper-draft.md](docs/sela-paper-draft.md) — 출발점이자 철학의 기준. 원문은 고치지 않고, 바뀐 결정은 이 파일과 docs/에 기록.

## 문서 규칙
- 새 폴더에는 `CLAUDE.md`를 같이 만든다: 역할, 설계 결정과 이유, 지킬 규칙, 다른 폴더와의 관계.
- `CLAUDE.md` = Claude용, `README.md` = 사람용, 메모리 = 사용자와 프로젝트 의도. 내용 중복 금지.
- 구조나 결정이 바뀌면 해당 CLAUDE.md를 같은 작업 안에서 갱신. 이 파일은 시간순 기록이 아니라 **현재 기준**으로 유지.
- 사용자에게는 일상어로 설명. 전문용어는 처음 쓸 때 풀어서.
- **공개 저장소.** 커밋 전 타인 식별자(uid·이메일·이름), 학생 기록, 비밀값을 훑는다. 원본 데이터·실험 원본 출력은 `out/`(git 제외)에만.
- **루트는 짧게** (2026-11-02 사용자 결정: 메인 md를 줄이고 작업마다 다른 곳을 자연스럽게 읽게). 여기는 지도·공통 규칙·확정된 결정·체크리스트만 둔다. 분야의 상태와 할 일은 그 폴더 `CLAUDE.md`(그 폴더 파일을 열면 같이 읽힌다), 하위 에이전트 절차의 자세한 것은 [docs/dispatch.md](docs/dispatch.md), 끝난 경위는 [docs/history.md](docs/history.md)나 분야 폴더의 `history.md`. CLAUDE.md에 날짜별 일기를 쌓지 않는다.
- **꼭 할 단계는 검사가 막게 한다** (2026-11-02). 문서에만 적힌 단계는 빠졌다 — p65 이후 `--turns` 4/53, 검사가 막는 `review.wrong`은 72/73. 새 필수 단계를 만들면 validate·테스트에 같이 넣는다.

## 현재 구조 (2026-11-02)
| 폴더 | 역할 |
|---|---|
| `proviso/` | 코어(분야 모름): 지식 파일 읽기·검사(`schema`), 성적표(`score`), 점검(`audit`), 그래프(`graph`), 조회(`query`), MCP 서버(`mcp_server`, 읽기 전용) |
| `domains/<id>/` | 분야 플러그인: `knowledge.toml` + 가설 검사(`checks.py`) + 분야 전용 코드(agent_usage: 계산기 `predict`·맞추기 `fit`·홀드아웃 `holdout`). 폴더마다 `CLAUDE.md`(지금 상태), 필요하면 `history.md`(경위). 현재 `flowlog`, `music_player`, `agent_usage`, `language_learning`, `movie_game`, `far_fields` |
| `experiments/` | 본체 실험 (논리집 유무에 따른 Claude 답 비교) |
| `docs/` | 원안, 설계 기록, 실험 보고서, 하위 에이전트 절차(`dispatch.md`)와 기록(`AGENT-LOG.md`, `worklog/`), 루트 경위(`history.md`) |
| `scripts/` | 운영 도구 (하위 에이전트 대화 기록 → 사용량 숫자, `agent_usage` 기록에 씀) |
| `tests/` | 표준 라이브러리 unittest |

명령 (저장소 루트): `python -m proviso validate|graph|check|audit <분야>` · `python -m unittest discover -s tests -t .` · `python -m experiments.run_body_v0` · `python -m domains.flowlog.replay <백업>` · `python -m domains.agent_usage.dispatches` · `python -m domains.agent_usage.predict <기록 id | 상황 파일>` · `python -m domains.agent_usage.holdout`. Git Bash에서 한글이 깨지면 `PYTHONIOENCODING=utf-8`. 외부 패키지 없음(Python 3.11+).

## 확정된 설계 결정 (원안 대비 변경 포함)
상세와 경위: [docs/knowledge-format-v0.md](docs/knowledge-format-v0.md)
- **지식 층위**: 목표 / 상태 / 사실(확인 날짜) / 관찰(사용자가 겪은 일) / 가설(주장; 규칙 = 방법이 붙은 가설, 아래). "선호" 층은 폐지 — 사용자 바람은 목표이거나 근거 붙은 방법.
- **규칙 칸**: 목표 · 조건 · 방법 · 이유 · 근거 · 반대 근거 · 결과·부작용 · 예외 · 상태(가설/이전 버전) · 버전 · 검사. 원안 W(Warrant)를 방법과 이유로 분리.
- **규칙·가설은 "성적 붙은 가설" 하나** (2026-10-19 사용자 결정): 규칙은 방법이 붙은 가설이고 '검증됨' 상태는 없다. 모든 가설은 자동 검사와 출처 붙은 판정을 합친 성적표를 받는다(`check`). 이유는 Lean 방향 — 모든 주장에 시험 기록이 붙고, 틀리면 어느 조각이 틀렸는지 짚는다. 논리는 잘 안 틀리고 조건을 흐리게 잡아서 틀리므로, **틀리면 조건을 더해 쪼갠다**(조건 없이 숫자만 넓힌 개정은 audit 경고). 목표·상태·사실·관찰은 가설이 아니다.
- **실패 처리**: 이유가 틀렸으면 규칙을 새 버전으로 고치고 이전 버전 보존. 이유는 맞는데 드문 바깥 상황이면 예외("나중에 발견된 조건, 기본값은 해당 없음"). 원안엔 개정 연산이 없었음.
- **목표는 위계**(큰 목표 ← 하위 목표). 부작용을 다른 목표의 "대가로 수용"한 결정도 기록.
- **판단의 기준은 사용자 실사용 경험.** 증거에는 출처(사용자 / 자동 확인 / AI 판단 / 시뮬레이션 / 실제 기록 재생)를 붙이고 사용자 판단을 가장 무겁게. AI 평가가 전부 좋았는데 실사용에서 아쉬움이 나온 사례 있음.
- **결과 피드백은 결정 단위**(원안은 프로젝트 전체 성공/실패 하나).
- **선택 편향 경계**: 기록에서 규칙을 뽑을 때, 그 방법을 고른 이유가 조건과 겹치면 능력이 아니라 사용 습관일 수 있다.
- **코어는 분야를 모른다**, 분야는 플러그인. 규칙은 같은 낱말을 써야 그래프에서 이어진다.
- **논리를 세우는 것 자체가 점검이다** (사용자 발견). 의도(목표)·말(규칙)·실제(사실, 코드)를 한 양식에 놓으면 어긋남이 실패 전에 드러난다. 엔진의 `audit`이 이걸 자동으로: 목표를 해치는데 대가로 받아들인 기록이 없으면 문제(오류). 조건을 더하지 않은 개정과 시험 수단 없는 가설은 경고. 앱 동작(사실)은 사용자에게 묻지 말고 코드에서 확인, 사용자에게는 의도·판단만.

## 방향: 논리 조각화 (2026-10-14 사용자 제시)
규칙을 앱 이름 없는 작은 **조각**으로 쪼개고, 새 상황을 각 조각에 **대 보고**(예/아니오/일부/모름 또는 값), 켜진 조각의 **조합**으로 결론을 낸다 → 다른 상황으로 유추. 메인은 상용 LLM(쪼개기·대 보기), 논리집은 조각 기억, 엔진은 조합 계산, 로컬 AI는 익숙한 대 보기를 나중에 넘겨받음. 결론마다 근거 → 조각 → 조합 → 결론으로 잇되, **빼면 결론이 바뀌는 조각만** 붙인다.
- **큰 그림 (사용자, 2026-10-19)**: 충분히 잘게 쪼개면 어떤 분야든 기존 논리를 다시 쓸 수 있다. 그래서 조각 이름·문장에 분야·앱 이름을 쓰지 않고, 같은 뜻은 같은 낱말로 쓴다. 다른 분야로 옮긴 조각은 그 분야에서 다시 가설로 시작한다(성적은 분야별로 따로 쌓는다).
- 조각 P1~P6과 상황별 대 보기: [docs/pieces-v0.md](docs/pieces-v0.md). P2·P3·P5·P6은 사용자 검토 반영, P1·P4는 명시 확인 없음. 본체 실험 질문 1·2의 판정을 재현했지만 **사후 설명**이다 — 예측 시험은 아직. 조각은 아직 스키마에 없다.

## 분야와 시험장
지금 상태와 할 일은 각 폴더 `CLAUDE.md`에 있다. 그 분야 일을 하면 그 문서부터 연다.

| 분야 | 무엇 | 자세히 |
|---|---|---|
| `flowlog` | Flowlog 앱의 제목 추천(실제 기록 재생 근거 포함). v2(R_P1a/R_P1b)는 설계만이고 앱은 v1 — 앱 수정은 사용자 요청 시 | [domains/flowlog](domains/flowlog/CLAUDE.md) |
| `music_player` | 알아서 틀기와 재생 순서. 엔진 `audit`이 의도와 다른 동작(같은 곡 재등장)을 잡아 고친 첫 사례 | [domains/music_player](domains/music_player/CLAUDE.md) |
| `agent_usage` | 사용자 목표(2026-10-16): **AI가 하위 에이전트의 시간과 사용량을 예측해서 이유와 함께 말해 준다.** 사용자는 판정하지 않고, AI가 사용자의 쌓는 방식을 따라 스스로 쌓는다. 판정자는 실측. batman 지휘 모델도 쓴다 | [domains/agent_usage](domains/agent_usage/CLAUDE.md) |
| `language_learning` | 사용자 목표(2026-10-22): **일본어를 전혀 모르는 사용자가 일본 여행에서 쓸 일본어를 꾸준히 공부할 시스템.** 결정마다 논리집을 보거나 잘 된 케이스를 조사해 근거를 댄다. 앱은 [ZizonK7/language_learning](https://github.com/ZizonK7/language_learning)(공개) | [domains/language_learning](domains/language_learning/CLAUDE.md) |
| `movie_game` | 셜록 홈즈 추리 게임의 설계 판단(2026-10-26). 게임 저장소 [ZizonK7/movie_game](https://github.com/ZizonK7/movie_game)는 비공개라 코드를 옮겨 적지 않고, 그 저장소의 md는 **제안 → 허락 뒤 수정** | [domains/movie_game](domains/movie_game/CLAUDE.md) |
| `far_fields` | 사용자 목표(2026-11-03): **창의 연결의 재료** — 사용자가 모르고 하지도 않을 먼 분야(809개, 조각 9,725)의 현장 경험칙을 분야 이름 없는 조각으로. 전부 AI가 만들거나 모은 것이라 판정은 AI 검토(가장 가벼운 출처)뿐이고, 2차 400개는 검토 없이 넣었다(사용자 결정). 무작위 두 조각 잇기 실험은 [docs/connection-experiment-v0.md](docs/connection-experiment-v0.md) | [domains/far_fields](domains/far_fields/CLAUDE.md) |
| 시험장 stock-rader | [ZizonK7/stock-rader](https://github.com/ZizonK7/stock-rader)(공개, 이 PC `../stock-rader`): Claude가 혼자 가상 투자(1,000만 원)를 하며 논리 조각화를 시험한다. 판정자는 시장. agent_usage와 같은 방식에 '조사 범위도 논리집에 넣기'를 더했다. 지식 양식·검사는 이 저장소 코어를 쓰고, 코어를 바꿔야 하면 여기서 바꾼다 | 그 저장소 `CLAUDE.md`·`docs/design.md`, 코어 변경은 [proviso/CLAUDE.md](proviso/CLAUDE.md) |

- **사용자 평가 대기**: music_player 새 알아서 틀기 실사용(R_M1b)·폰 셔플 표시(R_S1)·실제 앱 빌드, language_learning 사용자 PC 빌드와 실사용. 판정이 오면 `[[judgment]]` source="user".
- **열린 문제**: 운동 종목 추천에서 이름을 계속 타이핑해야 하는 부담(본체 실험 질문 2).
- **다른 저장소 일의 기준 문서**: Flowlog 출시 준비는 Flowlog 저장소 `docs/RELEASE_CHECKLIST.md`(사용자가 콘솔에서 할 일은 맨 위). 지난 경위는 [docs/history.md](docs/history.md).

## 다음 할 일
1. **조각 층을 스키마에 넣기**: 조각 노드(근거 포함), 규칙의 "이루는 조각" 칸, 상황별 대 보기. 같은 조각이 여러 분야에 걸리고 분야별 성적이 따로 보이게. agent_usage의 계산 조각(효과 칸)이 첫 형태. 그 위에서 **처음 보는 질문으로 예측 시험**(사후 설명이 아닌지 확인).
2. 정리: 가설 검사 결과를 지식에 저장(본체 실험에서 도구가 "지지됨"을 못 보여줌 → 2026-10-19부터 MCP `scorecard`가 성적표를 보여 준다. 결과를 파일에 저장하는 것은 아직), knowledge-format을 확정 양식 문서로 + 원안 대비 변경점 문서. (적용 범위 칸은 조각 층으로 대체)
3. **일반 지식 넣기**(사용자 제안, 첫 묶음 = `far_fields` 2026-11-03: 먼 분야 경험칙. 웹 문헌 출처 등급은 아직 스키마에 없어 가설 `source` 글에 적었다): 통념 · 사용자 생각 · 연구·실험 근거를 조각으로. 출처 종류·근거 강도, 출처 실재 확인 필수, 필요한 것만, 충돌 시 개인 경험 > 일반 원리. 사용자 생각 출처: 각 저장소 DECISIONS.md(뮤직 플레이어에서 효과 확인 — 있었으면 질문 1을 안 틀렸음).
4. 학습 고리 자동화: Episode 로그(질문·조회·답·판정·이유) + 지식 추가 제안 → 사용자 승인 → 저장(원안 commit 도구). `agent_usage`의 `dispatches.toml`(예측 → 실측 → 돌아보기)이 첫 Episode 로그 형태 — 판정자가 사용자가 아니라 실측인 경우.
5. `agent_usage` 이어 가기: 보낼 때마다 아래 체크리스트. 다음 정리에서 할 것은 [domains/agent_usage/CLAUDE.md](domains/agent_usage/CLAUDE.md) 끝. batman 배치 37부터 기록을 옮긴다(STATUS에 "proviso sync pending"이 있으면 PC 세션이 처리).
6. 그 뒤: 로컬 소형 모델(통역), 원안 Stage 2·3

## 하위 에이전트 운영
메인(사용자와 대화하는 모델) = 감독: 방향·설계, 지시서, 결과 검토, 문서를 정직하게 유지, 커밋·push. 하위 에이전트 = 지시서 하나를 구현(지시서에 없으면 커밋·push 안 함). 사용자 = 의도와 판정. 작은 일은 메인이 직접, 조사 물량이 많거나 서로 안 겹치는 큰 구현이면 하위 에이전트. 자세한 절차와 이유: [docs/dispatch.md](docs/dispatch.md).
- **모델**: 기본 Opus 5.5 · effort high(`model: "opus"`, `effort: "high"`, 사용자 지시 2026-10-14). 질보다 양인 일(대량 조사, 같은 고침 반복, 옮겨 적기, 양식 바꾸기)은 Haiku 5.5 · high(2026-10-22). 사용자가 바꾸라고 할 때만 바꾼다.
- **조사**는 되도록 클라우드 환경 `searching`에서, 지시서에 전송 조건을 숫자로 적는다(docs/dispatch.md "조사 보낼 때").

**체크리스트** — '검사'가 붙은 단계는 빠지면 `python -m domains.agent_usage.dispatches`와 테스트가 오류를 낸다.

보내기 전
0. 보낼까: 도구를 대여섯 번 넘게 쓸 일이면 `python -m domains.agent_usage.decide`로 직접 할 때와 보낼 때의 토큰을 견준다(감으로 두면 안 보내는 쪽으로 기운다). 직접 하면 `record direct`로 `direct.toml`에([agent_usage "보낼까 판단"](domains/agent_usage/CLAUDE.md)). 검사: 2026-11-04부터 보낸 기록의 `decide` 칸.
1. 지시서: 목표, 범위(건드릴 폴더·파일), 하지 말 것과 승인이 필요한 일, 완료 조건과 확인 방법, **보고서 경로**(양식 [docs/worklog/CLAUDE.md](docs/worklog/CLAUDE.md)), 하위의 하위 허용 여부, 이 저장소 규칙(일상어, 공개 저장소, 사실은 코드로).
2. 예측(묶음 명령 `python -m domains.agent_usage.record send <보낼 일 파일>`이 아래를 한 번에): `domains/agent_usage/dispatches.toml`에 기록을 먼저 덧붙인다(상황 값은 가장 비슷한 지난 기록에서 복사해 바꾸고, `agent`·`round`와 보낸 `model`·`effort`도 — '기본 설정인가'는 이 둘에서 계산. **쓰는 파일 수 `files`**(새로·통째로 쓰는 write, 일부 고치는 edit)는 실제 지시서에서 센다 — 검사: 2026-11-04부터, [agent_usage "파일 수 비율 조각"](domains/agent_usage/CLAUDE.md)) → 계산기 `predict <id> --calc`(앞 기록의 calc를 베끼지 않는다) → 정해진 일이면 빗댄 기록 규칙 `analog <id>`(시험 중, 참고) → 손 예측 → 사용자에게 구간(걸치면 가운데 값의 구간)·숫자·이유. 보내기 전 점검 넷, 도중 지시, 끝난 뒤 validate·audit·테스트 같은 자세한 단계는 [agent_usage "고리"](domains/agent_usage/CLAUDE.md). 검사: 2026-11-04부터 model·effort(없거나 '기본 설정인가'와 어긋나면 막음). 나머지는 칸 모양만 본다(빠져도 안 막음).

끝나면 — 사용자에게 결과를 말하기 전에 기록부터(컨테이너가 회수되면 대화 기록이 사라진다)

3. 실측(묶음 명령 `record finish <id> <로그> [--after] [--report]`가 3–5를 채운다): `python scripts/agent_usage.py <로그> --actual` → `actual`(시작·끝 시각 포함; 이어 보낸 회차는 `--rounds`로 본 그 회차 시작 시각을 `--after`에). 기록에 `agent`·`round`도. 검사: 끝난 기록의 실측 시간, 2026-11-04부터 시작·끝 시각과 agent·round.
4. 턴 길이: 같은 로그에 `--turns --toml` → 기록 끝에 `[dispatch.turns]`(잴 수 없으면 `skip = "이유"`). 검사(2026-11-03부터).
5. 보고서: 작업자의 보고서를 확인하고 경로를 `review.report`에. 검사(2026-11-03부터).
6. 돌아보기: `review.reason`, 구간이 빗나가면 `review.wrong`·`review.why`. 검사(빗나갔을 때 wrong·why).
7. 배치 줄: [docs/AGENT-LOG.md](docs/AGENT-LOG.md)에 `## 배치 N · 날짜 · 주제` 머리와 모델·effort·품질(1–5)·교훈. 검사(2026-11-04부터, batman 기록은 batman 쪽).
8. 결과 검토 → 커밋·push(메인).

## 다른 저장소 다루기
- 사용자 앱(music_player, Flowlog 등)의 **동작은 코드에서 확인**하고 사용자에게는 의도·판단만 묻는다.
- 고칠 때: 이 PC에 클론이 없으면 임시 폴더에 받아 작업 → 그 저장소 관례(DECISIONS.md 등)대로 기록 → main에 push(사용자 방식). 비공개 저장소 코드는 여기에 옮겨 적지 않는다.
- **다른 저장소에서 일하는 세션이 이 레포에 기록할 때** (2026-11-03, 사용자가 다른 저장소에서 "논리집 레포 읽어 봐"라고만 하는 일이 많다): 하위 에이전트를 보내면 기록은 이 레포에 남긴다 — `domains/agent_usage/dispatches.toml`(`project = "<그 저장소>"`), `docs/AGENT-LOG.md`의 배치 줄, 보고서는 그 저장소에 두고 `review.report = "저장소:경로"`(또는 이 레포 `docs/worklog/`). 이 레포를 그 세션에 붙여(PC는 `../proviso-nesy`, 클라우드는 저장소 붙이기) 그 세션의 작업 브랜치에 커밋·push한다. 기록 id는 이 레포 기본 브랜치의 마지막 번호 다음부터 — 여러 세션이 동시에 적으면 번호가 겹치니, 합칠 때 뒤 묶음을 다시 매기고 머리 주석에 원래 번호를 남긴다([docs/worklog/2026-11-02-branch-merge.md](docs/worklog/2026-11-02-branch-merge.md)). 이 레포를 붙일 수 없으면 그 저장소에 기록 초안과 "proviso sync pending: 배치 N"을 남기고 나중에 이 레포 세션이 옮긴다(batman 방식).
- batman(비공개, 이 PC `../batman`): 지휘 모델이 `agent_usage`로 예측한다(batman CLAUDE.md §7, 2026-10-16). 그 저장소에 다른 세션이 떠 있을 수 있으니, 고칠 때는 공유 폴더를 건드리지 말고 별도 worktree에서 작업한다. 커밋 작성자는 그 저장소의 기존 커밋에 맞춘다(`git log -1 --format='%an <%ae>'`로 확인. 이 PC의 전역 git 이름은 저장소마다 다를 수 있다).

## 보류
- 분야 "AI에게 코딩 맡기는 과정"(ai_company 기록 기반): 사용자가 판단할 수 없어서 보류. 초안은 [docs/rule-drafts-v0.md](docs/rule-drafts-v0.md).

## 환경
- CPU Ryzen 7 7700, GPU RTX 4060(VRAM 8GB로 가정, 미확인), RAM 32GB → 로컬 모델은 4bit 7–8B 추론, QLoRA 학습은 3–4B급이 현실적.
- 클라우드 교사 = Claude. 논리집은 MCP로 노출해 Claude Code(대화형·`claude -p`)와 API 양쪽에서 쓰는 방향.

## 데이터 출처
- Flowlog 백업 JSON: 사용자 Downloads 폴더. **다른 사용자 5명 기록 포함** — `requestedBy` 계정(사용자 본인 확인됨)만 읽는다. 결과는 비율만 기록.
- ai_company DB `C:/Users/minii/Desktop/Folder/Coding/ai_company/data/company.sqlite`: 읽기 전용으로만(실행 중인 서버가 씀). 평가는 AI(총괄 Codex, 주로 GPT-6 Astra) 판단 → 씨앗 데이터로만.

## 원안 논문의 알려진 오탈자
2.2절 `\mathcal{M}*{\text{local}}`, `L*{(1)}`(`_`가 `*`로 깨짐), 3.2절 표 `commit_logic_and_ alignment`(공백).
