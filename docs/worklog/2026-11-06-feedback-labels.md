# 2026-11-06 — 피드백 정답 모으기 (메인 전부 읽기 · searched · hit · missed · labels)

에이전트: 구현 작업자 (Opus 5.5, effort는 메인이 정함). 하위 에이전트 호출: 없음.
커밋·push: 안 함.

읽은 피드백: `feedback/main/` 15개 파일 전부(76항목), 백서 F014·F051·F078·F102·F103·F104.

## 한 일
사용자 결정(2026-11-06): 나중에 피드백 찾기 모델을 시험할 정답을 쌓는다. 2026-11-07부터 보낸 기록·직접 한 일에 아래 칸이 필수이고, 그 전 기록은 지금 규칙 그대로 검사된다(날짜 경계 `dispatches.FEEDBACK_ALL_FROM = "2026-11-07"`, batman 기록 제외).

- `domains/agent_usage/dispatches.py`
  - `feedback_errors`를 둘로 나눔: `feedback_send_errors`(보낼 때 적는 `[…feedback]` 표)와 `feedback_review_errors`(끝난 뒤 review). `feedback_errors`는 둘을 합친 것(validate·validate_direct는 그대로 이걸 부른다). 날짜 판단은 `on_or_after(d, since)`(batman 제외)로 모음.
  - (가) read: 11-07부터 메인 파일 **전부**가 없으면 오류("…가 빠짐 — 2026-11-07부터 메인 피드백은 전부…"). 그 전 날짜는 예전대로 `topics(task)`가 고른 파일.
  - (나) searched: 색인 낱말(`feedback.VOCAB`) 목록, 한 개 이상. 11-07부터 필수. 칸이 있으면 날짜와 상관없이 모양을 본다.
  - (다) hit: F 번호 목록, 모두 백서에 있어야 함, 겹치면 오류. 빈 목록이면 `hit_none = "이유"`(5자 이상) 필수. hit가 있는데 hit_none도 있거나 hit 없이 hit_none만 있으면 오류. 11-07부터 필수.
  - (마) review.missed: F 번호 목록(백서에 있음) 또는 `"없음: 이유"`(review.feedback과 같은 꼴). 11-07부터 끝난 기록에 필수. hit와 겹치면 오류.
  - **지시서 밖(정의에서 나온 것)**: missed가 이번에 새로 올린 번호(review.feedback)와 겹쳐도 오류 — "missed는 보낼 때 이미 있던 항목"이라는 정의를 검사로. hit·missed 안의 중복 번호도 오류.
- `domains/agent_usage/record.py`
  - `_feedback_read` → `_feedback_table`: 11-07부터 막는 기준이 메인 파일 전부 + searched·hit(`feedback_send_errors`로). 기록에 `read`·`searched`·`hit`·`hit_none`을 `[dispatch.feedback]`/`[direct.feedback]`에 옮김(자리는 예전처럼 decide 뒤·actual 앞).
  - 보낸 뒤 출력(`feedback_lines` + 새 `search_lines`): 읽은 메인의 F 줄(25줄 넘으면 번호·제목) → "키워드가 고른 메인 파일(참고)" → "백서에서 찾은 항목 (낱말: …) N개"와 항목마다 `F0xx · 제목 — 자리 …` → "이번 일에 걸린다고 본 항목(hit)". `record direct`도 같은 출력.
  - `finish … --missed "F014,F051 | 없음: 이유"` → `review.missed`(값 해석은 `--feedback`과 같은 `feedback_value`). **기록 파일에 아무것도 쓰기 전에** 검사해서(`_check_missed`) hit와 겹치거나 백서에 없는 번호면 막는다. 안 주면 11-07부터 '남은 일'에 review.missed가 뜬다.
  - 모듈 사용법 글(맨 위) 고침.
- `feedback/__init__.py`: `labels(dispatch_path, direct_path)`와 `labels_write(out)` — `feedback.hit` 칸이 있는 기록마다 `{id, kind, project, date, task, read, searched, hit, missed}`. missed는 목록이면 그대로, `"없음: 이유"`면 `[]`, 아직 없으면(안 끝난 기록) `null`. 기록 파일은 `tomllib`로 바로 읽는다(domains.agent_usage를 불러오면 서로 불러오는 고리가 생긴다). 기본 출력 `out/feedback/labels.jsonl`(git 제외).
- `feedback/__main__.py`: `labels [--out 경로]` 명령. `topics`는 고른 파일을 "참고"로 찍고, 붙일 `read = [...]` 줄은 메인 파일 전부로. `find`는 붙일 `searched = [...]` 줄도 찍는다.
- 테스트 `tests/test_feedback.py` +11개: `GroundTruth`(전부 읽기 날짜 경계, 11-06은 예전 규칙, batman 제외, validate에 끼워짐 / searched 없음·빈 목록·목록 밖 낱말 / hit 없음·F999·중복·빈 목록과 hit_none 짧음·좋음·같이 있음 / missed 없음·안 끝난 기록·짧은 이유·빈 목록·F999·hit와 겹침·새로 올린 번호와 겹침 / 직접 한 일도 같은 칸), `GroundTruthRecord`(임시 기록 파일로 `record send` 11-07: topics만·searched 없음·hit 없음은 막히고 아무것도 안 붙음, 통과하면 표가 그대로 옮겨지고 출력에 찾은 항목·참고 줄·hit / `hit = []`+hit_none / `finish --missed`가 hit와 겹치면 막히고 파일이 그대로, 안 주면 남은 일, 목록·'없음' 글 / `record direct` 11-07), `Labels`(가짜 기록 셋 + 직접 하나 → hit 있는 셋만, 칸 값, JSONL 왕복, CLI `labels --out`). 기존 `Record`의 준비 부분을 `RecordFiles`로 떼어 두 묶음이 같이 씀(테스트가 두 번 돌지 않게).
- **지시서 밖**: `tests/test_decide.py`의 가짜 보낼 일 파일 둘에 `date = "2026-11-06"`을 박음(같은 글을 `test_measure`도 읽어 씀). 까닭: 날짜를 안 적으면 **오늘 날짜**로 보내서 내일(11-07)부터 새 검사에 깨진다(어제 p240이 11-06 경계로 같은 일을 겪음). 같은 파일의 `late.toml`/`early.toml` 만들기는 `batch = 999` 뒤에 date를 더하던 것을 date 줄 바꾸기로 고침(키가 두 번 되지 않게).
- 문서: 루트 `CLAUDE.md`(표의 feedback 줄, 체크리스트 1과 6′), `feedback/CLAUDE.md`(키워드 줄, 명령에 topics 참고·find·labels, 강제에 '정답 모으기' 절·직접 한 일·코드 이름, 다른 폴더 관계의 단계 번호 1·6′), `domains/agent_usage/CLAUDE.md`(고리의 피드백 읽기, 놓친 피드백 줄 새로), `docs/dispatch.md`(지시서에 넣을 피드백), `README.md`(명령 목록), `domains/agent_usage/direct.toml` 머리 주석(기록은 안 건드림).

## 확인한 것 (어떻게)
- `python -m unittest tests.test_feedback` → 23개 통과. `python -m unittest tests.test_decide` → 7개 통과.
- `python -m unittest discover -s tests -t .` → 191개 중 실패 1: `tests.test_computable.Devices.test_audit_has_no_errors_now`(C_turns_files_scale 방향 주장 2/9 — 지시서가 말한 알려진 실패). 그 밖은 다 통과(131.7초).
- `python -m domains.agent_usage.dispatches` → "기록 문제 없음 (371건)".
- `python -m feedback check` → "문제 없음 (백서 항목 104개, 메인 파일 15개)".
- `python -m feedback find 문서 지시서`, `python -m feedback topics "구현: 기록 검사"` — 새 안내 줄이 찍히는 것을 봄. `python -m feedback labels --out <scratchpad>/labels.jsonl` → 0줄(아직 hit 칸이 있는 기록이 없다).
- 전제를 데이터로: 메인 파일 15개 · F 줄 76개 · 18,794바이트(`grep -c`, `wc -c`). `[dispatch.feedback]`이 있는 기록 6건, `[direct.feedback]` 2건, 모두 11-06 이하이고 searched·hit는 아무 데도 없다 → 새 규칙에 걸리는 지난 기록 0건.
- `record send/finish/direct`는 진짜 기록 파일에 돌리지 않았다(테스트의 임시 폴더로만). `python -m domains.agent_usage.record`는 인자 없이 한 번 — 코드에서 인자 둘 미만이면 사용법만 찍고 끝나는 것을 먼저 확인하고 돌림.

## 확인 못 한 것
- 내일 날짜(11-07)에 전체 테스트를 실제로 돌려 보지는 않았다. 날짜 없이 보내는 테스트(`rc.send`·`rc.direct`를 부르는 곳)는 `grep`으로 셋(test_decide·test_measure·test_feedback)뿐임을 확인하고 모두 날짜를 박았다.
- `eda` 내보내기는 `[dispatch.feedback]`의 새 목록 칸을 평평하게 펴는 기존 코드로 다룬다 — test_eda 통과만 봤고 새 칸이 든 기록으로 CSV를 열어 보지는 않았다.

## 알려진 문제 / 메인이 정할 것
1. **`dispatches.toml` 머리 주석(73줄 review.feedback, 112–114줄 feedback)은 옛 규칙 그대로다** — 지시서가 그 파일을 건드리지 말라 해서 두었다(다른 일의 finish가 곧 덧붙인다). 그 finish 뒤에 메인이 `searched`·`hit`·`hit_none`·`review.missed` 설명을 더해야 한다(문구는 `direct.toml` 머리 주석에 쓴 것을 그대로 쓰면 된다).
2. **"일 글(task + 지시서)을 임베딩"하려면 지시서 글이 기록에 없다.** 기록에는 `task` 한 줄만 있고 지시서 본문은 저장하지 않는다(로그에서 `named_*` 숫자만 뽑음). labels는 지금 task만 담는다. 지시서도 쓰려면 보낼 때 지시서 파일 경로나 본문을 기록에 남기는 칸이 필요하다 — 결정이 필요해 만들지 않았다.
3. 날짜는 `record send`가 UTC로 정한다: 한국 시간 11-07 오전 9시 전에 보내면 date가 11-06이라 옛 규칙(topics)으로 통과한다. 정답을 빠짐없이 모으려면 그날 아침에는 보낼 일 파일에 `date`를 적거나 그냥 새 칸을 채운다(칸이 있으면 날짜와 상관없이 모양은 검사된다).
4. hit는 "백서에 있는 번호"만 검사하고, 읽은 메인이나 find 결과 안에서 골랐는지는 보지 않는다(결정 C 문장대로: 메인이든 백서든). 좁혀야 하면 `feedback_send_errors` (다)에 한 줄.
5. 다른 저장소(gemmin `docs/subagents.md` 등)에 옛 규칙("topics가 고른 파일")이 적혀 있으면 그쪽 세션이 고쳐야 한다 — 이 작업은 다른 저장소를 안 봤다.

## 다음 작업자에게
- 보낼 일 파일 꼴(11-07부터):
  ```toml
  [feedback]
  read = ["api", "brief", …메인 15개 전부…]   # `python -m feedback topics "…"`가 붙일 줄을 찍어 준다
  searched = ["기록", "지시서"]                 # `python -m feedback find 기록 지시서`가 붙일 줄을 찍어 준다
  hit = ["F052", "F103"]                        # 없으면 hit = [] 와 hit_none = "이유"
  ```
  끝나면 `record finish <id> <로그> --feedback "…" --missed "F014"`(또는 `--missed "없음: 이유"`).
- 정답 뽑기: `python -m feedback labels` → `out/feedback/labels.jsonl`.
