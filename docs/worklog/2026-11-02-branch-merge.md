# 2026-11-02 — 브랜치 셋 합치기와 기록 번호 다시 매기기

에이전트: 메인(클라우드 세션) 직접. 하위 에이전트 호출: 없음.
커밋·push: 사용자 요청("브랜치 합쳐줘")으로 함 — 작업 브랜치 `ccr-c6ac578b-w4b0vj`에. main 병합과 원격 브랜치 삭제는 사용자가 한다.

## 한 일
- 합친 브랜치 셋(병합 커밋 셋, 날짜 순서로 기록 끝에 붙임):

| 브랜치 | 일 | 원래 번호 | 새 번호 | 배치 |
|---|---|---|---|---|
| `claude/busy-mccarthy-yzak4q` (10-28) | 수능 국어 회차 분석 | p105–p121 | p107–p123 | 35 그대로, p121의 36 → 38 |
| `claude/inspiring-edison-igoees` (10-29) | movie_game 전체 줄거리(비평·고증) | p107–p112 | p124–p129 | 37 그대로 |
| `claude/amazing-carson-owssej` (11-02) | exam_grader 풀이지 | p107–p114 | p130–p137 | 37 → 39 |

- busy-mccarthy는 10-28 main 병합이 되돌려져(`a05b28e`) 있어 git 병합만으로는 기록이 빠진다. 그래서 `dispatches.toml`·`docs/AGENT-LOG.md`는 병합 전 판 + 그 브랜치 기록(번호 바꿈)으로 다시 썼다. 같은 번호의 같은 일인 p104는 그 브랜치의 실측 판으로 바꿨다(main에는 '모름'으로 남아 있었다).
- 번호는 그 브랜치에서 들어온 글의 그 브랜치 번호 범위만 바꿨다: 기록, AGENT-LOG 배치 35·37, `docs/worklog/2026-10-29-movie-game-story-plot.md`, `docs/worklog/2026-11-02-exam-grader-kkulmo-s2-02.md`, `domains/movie_game/CLAUDE.md`의 새 줄, `domains/agent_usage/knowledge.toml`의 S_main_self 메모. 각 묶음 앞에 원래 번호를 주석으로 남겼다.
- 루트 `CLAUDE.md` 충돌(inspiring-edison이 movie_game 줄에 스토리 한 문장을 더함)은 정리본을 따랐다. 같은 내용이 `domains/movie_game/CLAUDE.md`에 들어왔다.
- **C_small_codebase → C_small_codebase_v2로 쪼갬**(따로 커밋). busy-mccarthy를 넣으면 방향 시험이 반박(있음/없음 ×5.97)으로 뒤집혀 `audit` 오류가 났다 — 10-28에 되돌린 까닭과 같다. 조건 있음 39건 중 수능 분석 19건과 movie_game 글 일 8건이 코드 없는 일(S_no_code=예)이었고, 코드 일만 보면 ×0.54로 방향이 맞았다. 조각의 이유(찾을 코드가 적고 확인이 즉시 끝난다)가 코드 일에만 해당하므로 조건 흐림 → S_no_code≠예를 더해 쪼갰다. `fit final --write`로 다시 맞춰도 범위는 그대로(×0.313–0.624).
- 문서: agent_usage CLAUDE.md의 기록 수·전제 1 측정 번호(p105·p106·p124·p130)·다음 정리 후보, 루트 "다음 할 일" 0번 지움, 테스트의 쪼갠 조각 목록에 v2.
- 도구: 기록 블록을 번호 바꿔 붙이는 일회용 스크립트(세션 스크래치, 저장소에 넣지 않음).

## 확인한 것 (어떻게)
- `python -m domains.agent_usage.dispatches` → 기록 문제 없음(262건). `grep '^id = ' … | sort | uniq -d` → 겹치는 번호 없음.
- `python -m unittest discover -s tests -t .` → 109개 통과(쪼개기 커밋 뒤). 병합 커밋 셋에서는 `test_audit_has_no_errors_now` 하나가 실패한다(C_small_codebase 방향) — 쪼개기 커밋에서 풀린다.
- `python -m proviso audit agent_usage` → 오류 0, 경고 22(병합 전과 같은 수).
- `python -m proviso check agent_usage` → C_small_codebase_v2: 방향 지지 1/1(×0.38), 크기 3/12.
- 쪼개기 근거: 같은 방향 비교를 기록 묶음별로 다시 돌림 — 전부 ×5.97(반박), 수능 빼고 ×0.77, 코드 일만 ×0.54, 병합 전 main ×0.82(모두 지지).

## 확인 못 한 것
- 수능 분석 22건(배치 35·38)의 작업 보고서가 수능 저장소에 있는지(이 저장소에는 없다).

## 알려진 문제
- C_small_codebase_v2의 '지지'는 쪼개게 만든 기록(p102–p123)이 시험 기록에도 들어 있어 사후 설명이다. 계산 조각은 seen_until을 p05 하나로 맞추므로(`fit`) 지난 쪼개기(C_fix_existing_v2·C_turns_no_check_v2)와 같은 방식을 따랐다. 진짜 시험은 p137 다음 기록부터. 크기 3/12는 남은 쪼개기 후보(agent_usage CLAUDE.md "다음 정리에서 할 것" 4).
- AGENT-LOG에 배치 38(p123)·배치 39(p130–p137)의 줄이 없다 — 그 세션들이 적지 않았다. 품질은 각 기록의 `review.reason`에 있다. 지어내지 않고 비워 둠.
- 기록 순서가 날짜순이 아니다(10-28 기록이 10-29 기록 p105·p106 뒤에 있다).

## 다음 작업자에게
- 사용자가 지울 원격 브랜치: `claude/busy-mccarthy-yzak4q`, `claude/inspiring-edison-igoees`, `claude/amazing-carson-owssej`(셋 다 이 브랜치에 병합 커밋으로 들어옴). 이 브랜치를 main에 합친 뒤 지우면 된다.
- 그 브랜치에서 일하던 세션이 다시 붙으면 이 브랜치(또는 합친 main)에서 새로 시작해야 한다 — 번호가 바뀌었다.
