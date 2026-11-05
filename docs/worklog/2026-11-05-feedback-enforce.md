# 2026-11-05 — 피드백 읽기·쓰기 강제 (feedback 모듈 + record/dispatches 검사)

에이전트: 구현 (Opus 5.5, high). 하위 에이전트 호출: 없음.
커밋·push: 안 함 (지시서대로 메인이 한다).

## 한 일
- **새로 씀**
  - `feedback/__init__.py` — 라이브러리. `VOCAB()`(CLAUDE.md "## 색인 낱말" 아래 쉼표 줄을 읽음, 코드에 낱말을 박지 않음), `entries()`(백서 `### F… · 제목` 블록 → 여섯 칸, 색인은 목록), `mains()`(파일마다 stem·키워드·읽는 때·`(F 번호, 줄)`), `check()`, `index()`·`index_write()`, `topics(글)`(대소문자 무시 부분 문자열, 늘 `common`, 정렬), `find(낱말)`, `main_files()`. 검사 함수는 경로를 인자로 받아 테스트가 임시 폴더로 돌린다.
    - `check()`가 보는 것: 칸 여섯이 다 있고 비지 않음(칸이 아닌 줄·같은 칸 두 번도 오류) / 색인 낱말이 목록 안 / 색인 목록 자체의 중복 / F 번호 중복·파일 순서대로 증가 / `자리`가 `메인 <stem>`(실제 파일)·`검사로 졸업`·`백서만` / 메인 파일마다 ≤10, `키워드:`·`읽는 때:` 줄, `common.md` 있음, 같은 파일 안 번호 중복 / 메인 줄 번호가 백서에 있고 자리가 바로 그 파일 / 거꾸로 `자리: 메인 X`는 모두 main/X.md에 / 색인 표가 `index()`와 같음.
  - `feedback/__main__.py` — `python -m feedback check | index [--write] | topics "<글>" | find <낱말>...`. check는 문제가 있으면 종료 코드 1. topics는 파일 경로와 보낼 일 파일에 붙일 `[feedback] read = [...]` 줄을 찍는다. find는 목록 밖 낱말이면 알려 준다.
  - `tests/test_feedback.py` — 12개: 저장소 `check() == []` / 메인 파일에 11개 넘게 → 오류 / 색인 밖 낱말 → 오류 / 칸 이름 틀림·자리 어긋남 → 오류 / 색인 표를 비우면 오류 → `index_write` 뒤 통과(두 번째는 안 바뀜, 낱말마다 한 줄) / `topics("웹 조사 지시서를 쓴다")`에 common·research·brief / dispatches 검사(2026-11-06 기록에 read 없음·review 없음 → 오류, common 없음·없는 파일·task가 고른 파일 빠짐 → 오류, `"없음: 이유"`·`["F001"]` 통과, `["F999"]`·짧은 이유·빈 목록 → 오류, 11-05·batman·안 끝난 기록은 안 걸림, 칸이 있으면 날짜 상관없이 모양) / 직접 한 일도 같은 두 칸 / `record send`를 임시 기록 파일로: read 없으면·docs 빠지면 막힘(메시지에 `feedback/main/docs.md`와 "읽고"), 통과하면 `[dispatch.feedback]`이 `[dispatch.decide]` 뒤·`[dispatch.actual]` 앞에, 출력에 F 줄 / 11-05 날짜는 read 없이 보냄 / `record finish`가 `--feedback` 없으면 '남은 일'에 review.feedback, `feedback_value`·`_put_review`로 목록 넣기·바꾸기.
- **고침**
  - `feedback/whitepaper.md` — `python -m feedback index --write`로 색인 표를 채움(43낱말, 0건인 낱말 없음). 항목 글은 안 건드림. **모양 오류는 0건이었다** — 메인이 손으로 맞춘 F 번호·자리·색인 낱말이 모두 맞았다.
  - `domains/agent_usage/dispatches.py` — `FEEDBACK_REQUIRED_FROM = "2026-11-06"`(다른 `*_REQUIRED_FROM` 옆, 같은 주석 투), `FEEDBACK_NONE = "없음: "`, `FEEDBACK_NONE_MIN = 5`, `feedback_errors(d, root, prefix)`. `validate()`와 `validate_direct()`에 끼움. batman 기록은 제외(다른 검사와 같게). 메인 자신의 일(`S_main_self`)은 제외하지 않았다(읽기는 메인에게도 해당).
  - `domains/agent_usage/record.py` — `send`·`direct`: `[feedback] read` 검사(`_feedback_read`) → 기록에 `[dispatch.feedback]`/`[direct.feedback]`을 decide 뒤에, 출력 끝에 "읽은 메인 피드백: …"과 그 파일들의 F 줄(25줄 넘으면 번호와 제목만). `finish`: `--feedback "F102,F103 | 없음: 이유"` → `review.feedback`(번호만이면 TOML 배열, 아니면 글; 있으면 바꿈). 안 주면 날짜 ≥ 11-06일 때 '남은 일' 맨 앞에 review.feedback. 모듈 설명(사용법)도 고침.
  - `domains/agent_usage/dispatches.toml` 머리 주석 — `review.feedback`(review.report 다음)과 `feedback`(cloud 다음) 설명.
  - `domains/agent_usage/CLAUDE.md` — 고리 1 묶음 명령 문단 뒤에 "피드백 읽기", 고리 3 보고서 줄 뒤에 "피드백 쓰기" 한 줄씩. "파일" 절의 `record finish` 인자에 `[--feedback]`.
  - `feedback/CLAUDE.md` "명령"·"강제" 절 — 코드와 맞춤: check가 보는 것 목록과 종료 코드, index의 `--write` 없을 때, topics 매칭 방식과 찍는 줄, 강제의 batman 제외·코드 이름, 보낸 뒤 출력, '없음' 이유 5자 이상, `record finish --feedback`. 구조·철학 문장은 안 건드림.
  - **지시서 밖**: `tests/test_decide.py`의 가짜 보낼 일 파일에 `[feedback] read = [...]`를 넣고, finish 두 곳에 `feedback="없음: 시험용 가짜 기록"`을 넘김. 까닭: 그 파일들은 날짜를 안 적어 **오늘 날짜**로 보낸다 — 2026-11-06부터는 새 검사에 막혀 `Bundle` 테스트 넷과 `test_measure.test_send_then_finish_in_a_temp_repo`(같은 파일을 글로 읽어 씀)가 깨진다. 테스트가 보는 동작은 그대로다. `FEEDBACK_REQUIRED_FROM`을 11-01로 당겨 두 묶음을 돌려 내일도 통과하는 것을 확인했다(아래).

## 확인한 것 (어떻게)
- `PYTHONIOENCODING=utf-8 python -m feedback check` → 처음엔 "백서의 색인 표가 최신이 아님" 1건(표가 비어 있었음), `python -m feedback index --write` 뒤 → "피드백 검사: 문제 없음 (백서 항목 101개, 메인 파일 15개)", 종료 코드 0.
- `PYTHONIOENCODING=utf-8 python -m feedback topics "웹 조사 지시서를 쓴다"` → `읽을 메인 피드백: brief, common, research`.
- `PYTHONIOENCODING=utf-8 python -m domains.agent_usage.dispatches` → "기록 문제 없음 (365건)", 종료 코드 0 (메인이 그새 커밋한 p240 포함, 지난 기록은 새 검사에 안 걸림).
- `python -m proviso validate agent_usage` → "문제 없음".
- `PYTHONIOENCODING=utf-8 python -m unittest discover -s tests -t .` → **174개 중 173 통과, 실패 1 = `test_audit_has_no_errors_now`**(C_turns_files_scale 방향, 지금 1/7 — 알려진 문제 그대로). 보내기 전 162개에 새 12개.
- 내일 날짜 흉내: `dp.FEEDBACK_REQUIRED_FROM = '2026-11-01'`로 바꾸고 `tests.test_decide.Bundle`·`tests.test_measure.GitNumbers` → 8개 통과.
- 실제 사용 예: scratchpad의 기록 파일·AGENT-LOG 복사본으로 `record send`(task "웹 조사 지시서를 쓴다", date 2026-11-06, read = brief·common·research) → 기록에 `[dispatch.feedback]\nread = ["brief", "common", "research"]`가 decide 뒤에 붙고, 출력에 세 파일 경로와 F 줄 20개. 저장소의 기록 파일은 안 건드림(`git status`로 확인 — `dispatches.toml`의 변경은 머리 주석뿐).
- 마지막에 `feedback/CLAUDE.md` 명령·강제, `domains/agent_usage/CLAUDE.md` 고리, `dispatches.toml` 머리를 코드와 다시 대 봄.

## 확인 못 한 것
- 실제 `record finish … --feedback`을 명령줄(`main`)로 돈 것은 안 했다 — 함수(`finish(feedback=…)`, test_decide)와 `_put_review`로만.
- 2026-11-06 이후 실제 보낸 기록 — 아직 없다.

## 알려진 문제
- `test_audit_has_no_errors_now` 실패(지시서에 적힌 알려진 문제, 이 작업과 무관).
- `direct.toml` 머리 주석에는 두 칸 설명을 안 넣었다(지시서 범위 밖). 검사는 direct에도 걸린다.

## 메인 판단 필요 (3건)
1. **키워드가 너무 넓다** — `topics()`는 지시서대로 단순 부분 문자열인데, 몇 키워드가 거의 모든 일에 걸린다. 2026-11-01 이후 기록 111건의 task에 대 보면 한 일에 평균 **5.8개** 메인 파일을 읽어야 한다. 그 키워드 하나만으로 걸린 수: cloud `세션` 47(예: '메인 세션'), predict `분` 46('분야'·'분석'·'부분'), review `검토` 39, api `생성` 29, docs `검사` 29, parallel·professor_king `회차` 27씩. 영문 `UE`(movie_game)는 'queue'·'issue'·'value'에 걸린다. main/*.md 문장은 고치지 말라 해서 그대로 뒀다 — 키워드를 좁히거나(`분` → `예측 분` 등) 짧은 키워드는 낱말 경계로 맞추는 안 중 고를 것.
2. **메인 자신의 일(`S_main_self = 예`)도 `feedback.read`를 요구한다** — `files`와 달리 빼지 않았다(읽기는 메인에게도 해당한다고 봄). 빼야 하면 `feedback_errors`의 `late` 조건에 한 줄.
3. **'없음' 이유 최소 5자**(`FEEDBACK_NONE_MIN`) — 지시서의 값이다. `"없음: 해당 없음"`(5자)처럼 형식만 채우는 글은 못 막는다. 재발을 재려면 나중에 "없음"이 많은 기록을 집계하는 쪽이 낫겠다.

## 다음 작업자에게
- 새 피드백을 올릴 때: 백서 끝에 `### F102 · 제목` + 여섯 칸 → `python -m feedback index --write` → (메인에 올리면) main/<파일>.md에 `- **F102** …` 줄과 백서 `자리: 메인 <파일>` → `python -m feedback check`. 메인 파일이 10개를 넘으면 check가 막는다.
- 루트 `CLAUDE.md` 체크리스트(보내기 전 1, 끝나면 6′)는 고치지 않았다(지시서가 금지). 읽어 보니 코드와 어긋나는 곳은 없다 — 다만 `record finish --feedback` 인자는 거기 안 적혀 있다(필요하면 메인이 한마디 더한다).
