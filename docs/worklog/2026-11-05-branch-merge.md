# 2026-11-05 — 브랜치 셋 합치기 (gemmin·far_fields 3차·exam_grader)와 번호 다시 매기기

에이전트: 메인(클라우드 세션) 직접. 하위 에이전트 호출: 없음.
커밋·push: 사용자 요청("ㄱㄱ. gemmin 세션 끝났어")으로 함 — 작업 브랜치 `claude/new-data-check-bzz1t3`에. main 병합과 원격 브랜치 삭제는 사용자가 한다.

## 한 일
main(11-04 09:34, p198·배치 60)에 없던 브랜치 셋을 합쳤다. 순서는 겹침이 적은 것부터.

| 브랜치 | 일 | 원래 번호 | 새 번호 | 합친 방법 |
|---|---|---|---|---|
| `claude/laughing-carson-g0n1k6` (gemmin, 11-05) | font 한글 노트, 박사·전문연 조사 팀, Professor_King 확인 문제, 공부 파트너 조사·창의 연결 팀, 은하 물리 보강 | p199–p219 · 배치 61–67 | 그대로 | main 위라 그대로 앞으로 감기(fast-forward) |
| `claude/far-fields-3` (11-03 밤) | 먼 분야 3차 학문·IT·금융 150개 분야·조각 1,800 + 지식 파일 묶음별 20개로 나눔(코어 `schema` load가 `knowledge-*.toml`을 같이 읽음) | p171–p178 · 배치 47 | 그대로(main이 비워 둔 번호) | 병합 커밋 `61d184c` |
| `claude/amazing-carson-owssej` (exam_grader, 11-04–05) | 꿀모 S2 2회 풀이지 14·15·19–22·27·28번 작성 → 검토 → 수정 | p195–p211 · 배치 58 | **p220–p236 · 배치 68** (+25) | 병합 커밋 `2579135` (ours + 번호 바꾼 덧붙임) |

- far-fields-3과 exam_grader 브랜치는 기록 파일(`dispatches.toml`·`docs/AGENT-LOG.md`·worklog)에 **덧붙이기만** 했다(갈라진 뒤 diff가 파일 끝 한 덩어리). 그래서 글자 단위 충돌을 손으로 풀지 않고, 현재 판 + 그 브랜치가 덧붙인 부분으로 다시 썼다.
  - far-fields-3: p171–p178은 p170 뒤(p179 앞)에, 배치 47은 배치 46과 48 사이에 넣었다.
  - exam_grader: 덧붙인 글 안의 p195–p211만 +25 하고 `배치 58`/`batch = 58`을 68로 바꿨다. 글 안의 p138–p144(원래 main의 exam_grader 기록, 빗댄 기록 등)는 그대로. 기록·AGENT-LOG·worklog `2026-11-02-exam-grader-kkulmo-s2-02.md` 각 묶음 앞에 원래 번호 주석.
- 루트 `CLAUDE.md` 충돌: 분야 플러그인 줄은 far-fields-3 글(나눈 지식 파일)에 `study_time`을 더했고, far_fields 줄은 959개·조각 11,525와 3차 검토 없음을 적었다. `domains/far_fields/CLAUDE.md`의 "3차는 브랜치에만 있고 합치기는 사용자 결정 대기"를 합친 날로 바꿨다.
- `domains/agent_usage/CLAUDE.md` 파일 수 비율 조각 단락: 합친 뒤 방향 0/4와 네 기록의 숫자를 덧붙였다(조각은 고치지 않음).
- 도구: 덧붙인 부분을 뽑아 번호를 바꿔 붙이는 일회용 파이썬(세션 스크래치, 저장소에 넣지 않음). 정규식 `(?<![A-Za-z0-9_])p(\d+)(?!\d)`에서 195–211만 바꿈.

## 확인한 것 (어떻게)
- `git rev-list --count HEAD..origin/claude/<브랜치>` → 셋 다 0(브랜치의 커밋이 모두 들어옴).
- `python -m domains.agent_usage.dispatches` → 기록 문제 없음(361건). 파이썬 `tomllib`로 읽어 id 중복 0, p170 → p171…p178 → p179, 끝 p219 → p220…p236.
- `python -m proviso validate <분야>` → 7개 분야 모두 문제 없음(far_fields는 나눈 파일 20개를 같이 읽어서).
- `python -m unittest discover -s tests -t .` → 149개 중 148 통과, 실패 1(`test_audit_has_no_errors_now`, 아래 알려진 문제). main(합치기 전)은 144개 모두 통과였다 — 늘어난 5개는 far-fields-3의 나눈 파일 테스트이고 통과.
- `python -m proviso audit agent_usage` → 오류 1(같은 것), 경고 24.

## 확인 못 한 것
- exam_grader 기록의 품질 숫자·교훈은 그 세션이 적은 그대로다. 번호만 바꿨고 내용은 다시 보지 않았다.
- gemmin 세션이 끝났다는 것은 사용자 말로 확인. 그 브랜치 마지막 커밋은 10:37 p215 실측·돌아보기.

## 알려진 문제
- **비율 조각 `C_turns_files_scale` 방향 0/4** → `audit` 오류, `test_audit_has_no_errors_now` 실패. gemmin 세션이 0/2일 때 일부러 남긴 것이고, 합친 뒤 시험 기록은 p189·p203·p214·p224. 넷 모두 비율이 지나쳤다(p214 ×1/12 → 약 16턴 예측, 실측 63 · p224 ×3 → 45턴 예측, 실측 25). 셋이 조사 일이 아니어서 'S_research로 쪼개기' 짐작으로는 설명이 안 된다. 고칠지·내릴지는 사용자와 정할 일이라 이 작업에서 고치지 않았다.
- 기록 순서가 날짜순이 아니다: p220–p236(11-04–05)이 p219(11-05) 뒤, 배치 68(날짜 11-04)이 배치 67 뒤.
- **이 작업 자체의 보낼까 판단·direct.toml 기록을 하지 않았다**(체크리스트 0번). 결과를 본 뒤 판단 숫자를 지어 넣지 않으려고 비워 뒀다.

## 다음 작업자에게
- 사용자가 지울 원격 브랜치(이 브랜치를 main에 합친 뒤): `claude/laughing-carson-g0n1k6`, `claude/far-fields-3`, `claude/amazing-carson-owssej`. 이미 main에 다 들어 있어 지워도 되는 것: `claude/nice-hawking-ypgudj`, `claude/zen-edison-0omrd7`, `claude/laughing-curie-rrb9ap`, `claude/far-fields-2026-11-03`.
- exam_grader 세션이 다시 붙으면 이 브랜치(또는 합친 main)에서 새로 시작해야 한다 — 그 세션 기록 번호가 바뀌었다(원래 번호 = 새 번호 − 25). 다음 기록은 p237부터.
- 다음 정리: 비율 조각을 비례 대신 약하게 걸지(예: 제곱근) 또는 내릴지. `holdout._scale_scores`가 시험 기록을 고른다.
