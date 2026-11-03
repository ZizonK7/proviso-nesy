# 2026-11-03 — 레포만 주고 절차를 찾을 수 있나(콜드 리드 점검)

에이전트: 점검 (Opus 5.5, high). 하위 에이전트 호출: 없음. 커밋·push: 안 함.

가정: 나는 다른 저장소(수학 풀이지를 만드는 `exam_grader`)에서 일하는 세션이고, 사용자가 "논리집 레포 읽어 보고, 이 일을 하위 에이전트한테 맡겨 줘: 14번 풀이지 14.html 새로 쓰기(본뜰 풀이지 13.html 있음, 렌더해서 png로 확인). 13번까지 써 온 에이전트가 이 세션에 아직 살아 있어."라고만 말했다. 실제로 보내지 않고, 이 레포만 읽고 절차를 찾을 수 있는지 본다.

## 한 일

### 읽은 순서
1. 루트 `CLAUDE.md` — 세션 시작 때 자동으로 읽힘. "하위 에이전트 운영"의 체크리스트 8단계가 뼈대라는 것을 여기서 앎.
2. `README.md` — 사람용 소개. 절차는 없음(분야 목록이 셋으로 낡음).
3. `docs/dispatch.md` — 루트가 "자세한 절차"라고 가리킴. 열자 `docs/CLAUDE.md`가 같이 읽힘.
4. `domains/agent_usage/CLAUDE.md` — 루트 체크리스트 2번이 "고리"를 가리킴. 열자 `domains/CLAUDE.md`가 같이 읽힘. 205줄, 4.7만 자로 가장 길고 실제 절차의 대부분이 여기 "고리"에 있다.
5. `docs/worklog/CLAUDE.md` — 보고서 양식.
6. `scripts/CLAUDE.md` — 실측 도구와 대화 기록 위치.
7. `domains/agent_usage/dispatches.toml` 머리 주석(칸 설명) → `exam_grader`로 검색해 지난 풀이지 기록 p130–p144를 읽음(13번 = p141).
8. `docs/worklog/2026-11-02-exam-grader-kkulmo-s2-02.md` — 지난 exam_grader 세션 보고서(회차별 교훈).
9. `docs/AGENT-LOG.md` 끝부분 — 배치 줄 양식.
10. `docs/worklog/2026-11-02-branch-merge.md`, `docs/worklog/2026-11-02-procedure-cleanup.md` — 다른 저장소 세션의 기록이 이 레포에 어떻게 들어왔는지(브랜치 병합).
11. 코드 머리말: `domains/agent_usage/predict.py`, `analog.py`, `scripts/agent_usage.py`, `dispatches.py`의 검사 부분, `knowledge.toml`의 R_preflight·R_say_numbers.

### 찾은 절차 (17단계)

예시 숫자는 이 점검에서 실제로 돌린 결과다. 기록 id는 지금 파일의 다음 빈 번호(p146이 이 점검이라 p147)를 가정했다.

**보내기 전**

| # | 할 일 | 무엇을, 어디에 | 근거 |
|---|---|---|---|
| 1 | 보내는 방식 정하기: **같은 작성 에이전트에 이어서**(SendMessage), 한 회차 | 관련 구현은 한 에이전트가 끝까지 맡고 후속은 이어 보낸다(까닭: 비용이 아니라 일관성). 14번은 할 일이 다 적힌 '정해진 일'이라 찾기·고치기 두 회차로 나눌 일이 아니다. 회차 번호는 지난 기록의 작업 설명에서 센다: 작성 에이전트 p130(1회차)…p144(13회차) → 14회차 | `docs/dispatch.md` "역할과 언제 쓰나"(구현은 한 에이전트에 몰아서, 섞인 일은 같은 에이전트에 두 회차로) |
| 2 | 보내기 전 점검 넷(R_preflight) | ① 이어 보낼 에이전트 id를 대화 기록과 대조(`subagents/agent-*.meta.json`의 설명으로) ② 지시문에 생각 과정 보고를 요구하지 않음 ③ `which node` 등 렌더 도구 확인, 없으면 +2분 ④ 글 규칙(teacher.md의 풀이지 규칙)을 지시서에 | `domains/agent_usage/CLAUDE.md` "고리" 1, "지금 쓰는 규칙 요약" 6; `knowledge.toml` R_preflight |
| 3 | 지시서 쓰기 | 목표 / 범위(`solutions/14.html`, png·pdf, `session.md` 14번 줄, teacher.md 수업 논리 1줄) / 하지 말 것(커밋·push, 다른 풀이지 수정, sheet.css 전역 변경)과 승인이 필요한 일 / 완료 조건과 확인 방법(render.js로 렌더, png를 Read로 눈으로 확인, A4 한 쪽) / **보고서 경로** / 하위의 하위 금지 / 저장소 규칙(일상어, 공개 저장소, 사실은 코드로). 만들 것·고칠 곳은 목록으로(일의 크기를 셀 수 있게). exam_grader 교훈: 지시서를 부정문('A하지 않고 B')으로 쓰지 않는다, '핵심 상자 하나·손글씨 2개'를 매번 요구하지 않는다(채우려고 만든다) | 루트 `CLAUDE.md` 체크리스트 1; `docs/dispatch.md` "지시서"; `docs/worklog/2026-11-02-exam-grader-kkulmo-s2-02.md` 회차 5·11–14 |
| 4 | 계산기 돌리기 | 상황 값 파일(project + `[situation]` 상태 = 값 + `analog`)을 만들어 `python -m domains.agent_usage.predict <파일>`. 이번 결과: 스위치만 '다른 일' 10.9–21.8분, 빗댄 기록 계산 '잠깐' 2.1–4.2분 → `[dispatch.calc]` `told`·`minutes`에 (스위치만 쪽) | `domains/agent_usage/CLAUDE.md` "고리" 1 첫 줄, "지금 쓰는 규칙 요약" 0 |
| 5 | 손 예측 | 규칙 요약에서 고름: R_turns_analogy_v2(빗댄 p141: 13번, 그림 포함, 2.4분·14턴·4.1M), R_third_pass(세 번째 이상), R_time_turns_v2, R_resume_ctx_v2, R_say_numbers_v3. 예: 11–18턴, 1.5–3분, 3–5.5M(T1). 가운데 값 √(1.5×3)≈2.1분 → '잠깐' | `domains/agent_usage/CLAUDE.md` "지금 쓰는 규칙 요약" 1–4, 6 |
| 6 | 기록 덧붙이기 | `domains/agent_usage/dispatches.toml` 끝에 `[[dispatch]]`: id, `project = "exam_grader"`, batch, date, task, `size`, **`agent`·`round`**, `[dispatch.situation]`, `[dispatch.predicted]`(written_before, told, minutes, turns, tokens_m, tokens_class, rules — 규칙 id만·가설 id 금지, analog, reason), `[dispatch.calc]` | `domains/agent_usage/CLAUDE.md` "고리" 1; `dispatches.toml` 머리 주석 |
| 7 | 빗댄 기록 규칙 보기 | `python -m domains.agent_usage.analog <새 id>` — 기록을 덧붙인 뒤에만 돈다(상황 파일은 안 받음). 시험 중이라 참고만 | `domains/agent_usage/CLAUDE.md` "고리" 1 넷째 줄, "빗댄 기록 규칙" v2 |
| 8 | 사용자에게 말하기 | 아래 문장. 말한 구간을 `predicted.told`에 | 루트 체크리스트 2; `domains/agent_usage/CLAUDE.md` "역할", R_say_numbers_v3 |
| 9 | 보내기 | 같은 에이전트에 SendMessage. 도중에 지시를 더 보내면 그 기록의 `S_mid_notes = "예"` | `docs/dispatch.md`; `domains/agent_usage/CLAUDE.md` "고리" 2 |

사용자에게 할 말(예):

> 14번 풀이지는 13번까지 쓴 작성 에이전트에 이어서 맡길게요. **잠깐 기다려 주세요** — 1.5–3분쯤, 응답 11–18번, 토큰 300만–550만쯤으로 봅니다. 이유: 같은 에이전트가 13번(그림 포함)을 2.4분·14번 응답에 썼고, 이어서 쓰는 풀이지 한 장은 지금까지 1.4–2.4분이었어요. 계산기는 '다른 거 하고 있어'(11–22분)라고 하지만 계산기는 일의 크기를 모르고 이 풀이지 시리즈에서는 늘 높게 잡았습니다.

**끝난 뒤 — 사용자에게 결과를 말하기 전에 기록부터**

| # | 할 일 | 무엇을, 어디에 | 근거 |
|---|---|---|---|
| 10 | 실측 | `python scripts/agent_usage.py "<대화 기록>/subagents/agent-<id>.jsonl" --actual --after <앞 회차 끝 시각>` → 나온 `[dispatch.actual]`(status, minutes, turns, tokens_m, **start, end**)를 그 기록에. 이어 보낸 회차의 분은 완료 알림의 실행 시간으로 고친다 | 루트 체크리스트 3; `domains/agent_usage/CLAUDE.md` "고리" 3; `scripts/CLAUDE.md` |
| 11 | 턴 길이 표 | 같은 로그에 `--turns --toml --after <앞 회차 끝 시각>` → `[dispatch.turns]` 블록을 기록 끝에. 이어 보낸 회차라는 것은 skip 사유가 아니다. 정말 못 재면 `skip = "이유"` 한 줄 | 루트 체크리스트 4; `domains/agent_usage/CLAUDE.md` "고리" 3 |
| 12 | 보고서 | 작업자의 보고서를 확인하고 경로를 `review.report`에(이 레포면 `docs/worklog/...md`, 다른 저장소면 `"exam_grader:경로"`). 없으면 쓰게 하고 나서 | 루트 체크리스트 5; `domains/agent_usage/CLAUDE.md` "고리" 3 |
| 13 | 돌아보기 | `python -m domains.agent_usage.dispatches`, `python -m proviso check agent_usage`. 맞든 틀리든 `review.reason`. 말한 구간이 빗나가면 `review.wrong`(틀린 조각 id) + `review.why`(조건 흐림 / 이유 틀림 / 바깥 상황 / 까닭 모름). 어느 조각인지는 출력의 갈래(턴이 맞았으면 속도, 틀렸으면 양)로. '까닭 모름'이면 wrong은 비워도 되고 사용자에게 숫자와 함께 넘겨 답을 `review.user`에 | 루트 체크리스트 6; `domains/agent_usage/CLAUDE.md` "고리" 4 |
| 14 | 고치기(필요할 때) | 이유가 새 주장이면 가설 + `checks.py` 검사와 `SEEN_UNTIL`. 규칙을 고치면 이전 버전은 `retired` + `replaced_by`, 쪼갤 때는 더한 조건을 `conditions`에 | `domains/agent_usage/CLAUDE.md` "고리" 4 끝, 5 |
| 15 | 배치 줄 | `docs/AGENT-LOG.md`에 배치 머리(메인·에이전트 설명) + 표 한 줄(모델·effort·난이도·예상/실제 시간과 토큰·품질 1–5·메모) + 교훈 | 루트 체크리스트 7 |
| 16 | 검사·테스트 | `python -m proviso validate agent_usage`, `python -m proviso audit agent_usage`, `python -m unittest discover -s tests -t .` | `domains/agent_usage/CLAUDE.md` "고리" 6 |
| 17 | 결과 검토 → 커밋·push(메인) → 사용자에게 결과 | exam_grader 쪽 결과물(14.html·png)은 그 저장소 관례대로, 기록은 이 레포에 | 루트 체크리스트 8 |

### 기록을 남기는 곳
- 이 레포(`proviso-nesy`)에: 기록 `domains/agent_usage/dispatches.toml`(`project = "exam_grader"`), 배치 줄 `docs/AGENT-LOG.md`, 보고서는 이 레포 `docs/worklog/YYYY-MM-DD-<주제>.md` 또는 exam_grader 쪽 파일(`review.report = "exam_grader:경로"`). 지난 exam_grader 세션은 이 레포의 `docs/worklog/2026-11-02-exam-grader-kkulmo-s2-02.md` 한 파일에 회차를 이어 썼다.
- 다른 저장소에서 일할 때: 문서에 직접 적힌 방법은 없다. 지난 예로 짐작하면, exam_grader 세션이 이 레포를 따로 붙여(클론) 작업 브랜치(`claude/amazing-carson-owssej`)에 기록을 커밋했고, 나중에 메인이 브랜치를 합치며 번호를 다시 매겼다(p107–p114 → p130–p137, `docs/worklog/2026-11-02-branch-merge.md`). batman만 따로 길이 있다(그 저장소 STATUS의 "proviso sync pending"을 PC 세션이 옮김, `domains/agent_usage/CLAUDE.md` "역할").

## 확인한 것 (어떻게)
모두 저장소 루트에서. 레포 파일은 바꾸지 않았다(`git status --short` → 비어 있음, 이 보고서 전).
- 상황 값 파일 `/tmp/claude-0/-home-user-proviso-nesy/6c8c5998-0b60-5e26-9333-f6f489e9a581/scratchpad/coldread/p14.toml`(p141의 상황 값을 그대로, `analog = "p141"`)을 만들고
  `PYTHONIOENCODING=utf-8 python -m domains.agent_usage.predict <그 파일>` → 스위치만 '다른 일' 10.9–21.8분·51–102턴·25–50M(T2), 비유 계산 '잠깐' 2.10–4.19분·10–19턴·4.8–9.6M(T1).
- `PYTHONIOENCODING=utf-8 python -m domains.agent_usage.predict p141` → 같은 상황으로 '다른 일' 10.9–21.8분. 그런데 p141 기록에 적힌 계산기 답은 '신경 끄기' 45.6–91.2분이다(아래 알려진 문제 7).
- `PYTHONIOENCODING=utf-8 python -m domains.agent_usage.analog p141` → "반드시 같은 답으로 찾음, 동점 1건 — p135 1.7분 × 0.6–1.2 → 1.0–2.0분 → 잠깐, 실측 2.4분(잠깐)".
- `PYTHONIOENCODING=utf-8 python -m domains.agent_usage.analog p14` → 오류가 아니라 **이미 있는 기록 p14**(Haiku 기록)를 보여 줌: "동점 4건이라 규칙이 가리지 못함". 상황 파일 이름이 기록 id와 겹친 것.
- `PYTHONIOENCODING=utf-8 python -m domains.agent_usage.dispatches` → "기록 문제 없음 (271건)", 끝 기록 p146(이 점검, `status = "unknown"`). 말한 구간 맞음 87 / 빗나감 53, '사용자에게 넘길 것' 없음.
- `PYTHONIOENCODING=utf-8 python -m proviso check agent_usage` → 504줄 출력, R_turns_analogy_v2·R_third_pass 성적 보임.
- `python scripts/agent_usage.py "<이 세션>/subagents/agent-*.jsonl" --actual` → 기록 둘에 `[dispatch.actual]`(status·minutes·turns·tokens_m·start·end) 출력. `agent`·`round`는 안 나온다(손으로 적어야 함).
- `python scripts/agent_usage.py <로그 하나> --turns --toml` → `[dispatch.turns]` 블록 출력(동작마다 n·sum_s·turn_s·tool_s·out_chars·ctx_k).
- `dispatches.py` 검사 코드: turns·report 필수는 2026-11-03부터(`FORM_REQUIRED_FROM`), 시작·끝 시각과 agent·round 필수는 2026-11-04부터(`TIMES_REQUIRED_FROM`). `skip`은 문장 하나인지만 보고 사유는 안 본다.

## 확인 못 한 것
- 실제 보내기·SendMessage·`--after`로 이어 보낸 회차만 가르기(이 컨테이너에는 이어 보낸 에이전트 기록이 없다).
- `predicted.rules`에 이전 버전 규칙 id(R_say_numbers_v2 등)를 넣으면 검사·테스트가 막는지. `dispatches.py`는 종류(규칙인지)만 보는 것으로 읽었다.
- 테스트 전체(`python -m unittest ...`)는 돌리지 않았다.
- 다른 저장소 세션이 이 레포에 push할 권한·방법(클라우드 세션의 저장소 붙이기)은 문서에도 없고 시험도 안 했다.
- exam_grader 저장소 쪽 문서(teacher.md, 그 저장소 CLAUDE.md)에 이 절차가 적혀 있는지.

## 알려진 문제 (새 세션이 이 레포만 보고 따라 하면 빠뜨리기 쉬운 순서)
1. **다른 저장소에서 기록을 이 레포에 남기는 방법이 없다.** 루트 "다른 저장소 다루기"는 이 레포 세션이 남의 저장소를 고칠 때의 이야기다. 반대 방향(남의 저장소 세션이 이 레포에 기록)은 branch-merge 보고서를 읽어야 짐작된다: 이 레포를 따로 클론 → 브랜치에 커밋 → 나중에 번호 다시 매김. 그래서 기록 번호가 세 번 겹쳤다(p40–p64, p79–p83, p107–).
2. **AGENT-LOG 배치 줄(체크리스트 7)은 검사가 없다.** 실제로 exam_grader 배치 39·40과 배치 38이 AGENT-LOG에 없다(branch-merge 보고서도 확인). 루트 "꼭 할 단계는 검사가 막게 한다"에 아직 안 걸린 단계.
3. **이어 보낸 회차의 턴 길이 표.** `domains/agent_usage/CLAUDE.md`는 "로그가 한 파일에 쌓인 것은 skip 사유가 아니다, `--after`를 써라"라고 하는데, 검사는 skip 문장을 막지 않고, 본뜰 만한 바로 앞 기록(p138·p140·p141·p143·p144)이 모두 바로 그 사유로 skip했다. 지난 기록을 베끼면 틀린 쪽을 따라간다. 또 `--after`에 줄 '앞 회차 끝 시각'이 앞 기록(p144)에 없다(시각 칸이 생기기 전) — 이번처럼 시리즈 중간에 새 규칙이 들어오면 앞 회차 끝 시각을 어디서 얻는지 안내가 없다.
4. **회차 번호와 에이전트 대조.** `agent`·`round` 칸은 11-04부터 필수인데 p130–p144에는 없다. 14번이 몇 회차인지는 작업 설명 문장("같은 작성 에이전트 13회차")에서 세야 하고, R_preflight ①의 '에이전트 id 대조'도 기록에 id가 없어 대화 기록의 meta.json 설명으로 해야 한다.
5. **빗댄 기록 규칙(`analog`)은 기록을 덧붙인 뒤에만 돈다.** 상황 파일을 받지 않는다. 루트 체크리스트와 `docs/dispatch.md`에는 이 단계가 없고 `domains/agent_usage/CLAUDE.md` "고리" 1에만 있다. 이름이 기록 id와 겹치면 엉뚱한 기록을 보여 준다(p14).
6. **루트 체크리스트에 없는 보내기 전 단계가 많다**: 계산기를 `[dispatch.calc]`에 적기는 있지만, R_preflight 점검 넷, analog 돌리기, `proviso check`, 도중 지시 때 `S_mid_notes`, 끝난 뒤 validate·audit·테스트(고리 6)는 `domains/agent_usage/CLAUDE.md`에만 있다. 루트만 보면 빠진다.
7. **계산기 답이 기록과 다르다.** p138–p144의 `[dispatch.calc]`는 모두 '신경 끄기' 45.6–91.2분인데, 지금 같은 상황 값으로 돌리면 '다른 일' 10.9–21.8분이다. 그때 상황 값이 달랐는지, 다른 기록의 답을 옮겨 적었는지 확인 못 함. 앞 기록의 calc를 베끼면 안 된다는 경고가 없다.
8. **문서끼리 어긋난 곳**
   - 말하기 규칙: `dispatches.toml` 머리 주석 `predicted.told`는 "걸치면 긴 쪽(R_say_numbers_v2)", `domains/agent_usage/CLAUDE.md` "지금 상태"의 계산기 설명도 "걸치면 긴 쪽" — 같은 파일 "역할"·"고리"와 `predict.py`는 v3(가운데 값).
   - 본보기 기록 p141의 `rules`는 R_say_numbers_v2(지금은 이전 버전).
   - `docs/dispatch.md` "끝나면" 첫 문단은 옛 명령 `--md`로 실측을 넣으라고 하고, 같은 절 둘째 문단·루트·agent_usage는 `--actual`.
   - `docs/dispatch.md` "끝나면"의 링크 넷(`docs/worklog/CLAUDE.md`, `domains/agent_usage/CLAUDE.md`, `docs/AGENT-LOG.md`, `scripts/CLAUDE.md`)이 `docs/` 안에서 루트 기준 경로로 적혀 있어 깨진다(같은 파일 맨 위는 `../`로 맞음).
   - 이어 보낸 회차의 분: `scripts/CLAUDE.md`·`--actual` 주석은 "알림의 실행 시간으로 고친다", `domains/agent_usage/CLAUDE.md`는 `--after`로 그 회차만 센다고만 적어 어느 쪽 분을 쓰는지 한 곳에 없다.
9. **exam_grader 일 고유의 교훈이 이 레포 보고서에만 있다**: 지시서 부정문 금지, 핵심 상자·손글씨 개수 요구 금지, '작성(high) → 새 검토 에이전트(xhigh) → 같은 작성 에이전트가 수정' 한 바퀴 구조(사용자 제안, 12·13번에서 '구조 유지'). 새 세션은 14번 뒤에 검토 에이전트를 따로 보내야 하는지 모를 수 있다(검토도 별도 기록).
10. 상황 값 목록(상태 36개)을 처음부터 채우는 법은 안내가 없다. 실제로는 가장 비슷한 지난 기록(p141)의 `[dispatch.situation]`을 복사해 바꾸는 것이 쉬웠다.
11. `README.md` 분야 목록이 셋뿐(이미 알려진 것, procedure-cleanup 보고서).

## 다음 작업자에게
- 가장 큰 구멍은 1·2·3번이다. 1번은 루트 "다른 저장소 다루기"에 '다른 저장소 세션에서 기록할 때' 한 단락(이 레포 클론, 브랜치, 다음 빈 번호와 병합 때 번호 다시 매김)을 두면 풀린다. 2번은 끝난 기록의 배치 번호가 AGENT-LOG에 있는지 `dispatches`가 보게 하면 검사로 막을 수 있다. 3번은 skip 문장에 '이어'·'누적'이 있으면 경고하거나, 이어 보낸 회차 첫 기록에 앞 회차 끝 시각을 얻는 방법(`--actual`을 `--after` 없이 돌린 끝 시각 등)을 적으면 된다.
- 어긋난 문장(8번)은 고치기 쉬운 것들이다: 머리 주석의 v2 → v3, dispatch.md의 `--md` 문단과 링크.
- 이 점검 자체의 기록은 p146(`status = "unknown"`)으로 이미 있다. 이 보고서 경로를 그 기록의 `review.report`에 넣으면 된다.
