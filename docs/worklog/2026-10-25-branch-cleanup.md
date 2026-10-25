# 2026-10-25 — 브랜치 정리: 10-20 세션 두 브랜치 병합, 옛 역사 브랜치 태그 보존

에이전트: 메인(클라우드 세션). 하위 에이전트 호출: 없음.
커밋·push: 사용자 요청("브랜치 정리")으로 함 — main에 직접.

## 한 일
- `origin/ccr-2a22e640-e8dn8n`(2026-10-20 Flowlog 전체 점검·출시 준비·PC 웹 앱 세션, 28커밋) 병합.
  - 그대로 들어온 것: `docs/flowlog-review-2026-10-20/` 보고서 6개, `docs/worklog/2026-10-20-*.md` 19개, 루트 CLAUDE.md의 "Flowlog 전체 점검" 상태 문단.
  - 번호를 바꾼 것: agent_usage 기록 p06–p24·배치 4–7 → **p40–p58·배치 18–21** (main이 같은 번호를 language_learning 조사에 썼다). `dispatches.toml`·`docs/AGENT-LOG.md` 끝에 붙이고 주석으로 원래 번호를 남김. 그 세션의 돌아보기는 `domains/agent_usage/CLAUDE.md` 끝에 절로 붙임.
- `origin/claude/relaxed-babbage-11l0ha`(2026-10-20 강의 자료 정리본 여섯, 2커밋) 병합.
  - 번호를 바꾼 것: p06–p11·배치 4 → **p59–p64·배치 22**.
  - 고친 것: 여섯 기록의 `project`를 `"proviso"` → `"professor_king"`. 일은 강의 정리본 저장소에서 했고(과제 본문 "다른 비공개 저장소"), main의 같은 종류 기록(p33–p39)이 쓰는 값이다. `"proviso"`로 두면 `from_project`가 S_small_codebase=예로 추론해 C_small_codebase의 방향 성적이 반박되고 `audit`이 오류를 냈다.
  - 받지 않은 것: `tests/test_computable.py`의 seen_until 테스트 수정 — main이 같은 문제를 다른 방식으로 이미 고쳐 두었다(`"시험(p05 다음부터)"` 허용). main 쪽을 유지.
- 테스트 기대 갱신: `test_used_check_reads_predictions_written_before`에서 R_integration은 "시험 전"이었는데, 병합된 p54(원래 p20, 보내기 전에 R_integration으로 예측한 212파일 병합 작업)가 첫 시험 기록이 되어 판정("반박됨 1/1")이 난다. 테스트는 판정이 나고 p54를 읽는지로 바꿈.
- 루트 CLAUDE.md "지금 상태"의 기록 수를 189건(p01–p64)으로 갱신하고 병합 사실을 적음.
- `origin/claude/inspiring-planck-m43xto` = `origin/claude/jolly-mayer-jzwd7u`(같은 커밋 39499ea, 10-14~10-19 옛 역사 80커밋)는 main과 공통 조상이 없어 병합하지 않는다. 태그 `archive/old-history-2026-10-19`(39499ea)를 만들었지만 **이 환경에서는 태그 푸시가 조용히 막혀 원격에 올라가지 않았다** — 사용자가 PC에서 `git tag -a archive/old-history-2026-10-19 39499ea -m 보존 && git push origin archive/old-history-2026-10-19`로 찍은 뒤에 두 브랜치를 지운다. main의 첫 커밋은 이 끝 상태에서 `domains/nonfiction_games`·`experiments/retrieval_v0`과 관련 문서를 뺀 것과 같다.

## 확인한 것 (어떻게)
- `python -m unittest discover -s tests -t .` → 104개 통과.
- `python -m proviso validate agent_usage` → 문제 없음. `python -m proviso audit agent_usage` → 오류 없음(경고: 바깥 상황 예외 p06·p07, 조건 칸 없는 개정 9건 — 병합 전과 같음).
- 기록 id 중복 없음(`grep '^id = ' | sort | uniq -d` 비어 있음), `dispatches.load()` 189건.
- `git merge-tree`로 충돌 파일을 미리 확인: 두 브랜치 모두 `dispatches.toml`·`AGENT-LOG.md`·`agent_usage/CLAUDE.md`(+ babbage는 테스트 1개)만 충돌 — 모두 양쪽이 끝에 덧붙인 것이라 main 판 + 번호 바꾼 덧붙임으로 풀었다.

## 확인 못 한 것
- p59–p64가 실제로 어느 저장소의 일이었는지는 과제 본문과 날짜로 추정했다(Professor_King 수업정리가 10-19·10-20에 여섯 편 만들어짐).
- 병합된 10-20 기록 25건이 계산 조각 성적에 미치는 영향은 테스트·audit 통과까지만 봤다. 다음 정리에서 R_integration 반박(p54)과 ccr 세션의 교훈 4가지(`domains/agent_usage/CLAUDE.md` 끝)를 가설·조건으로 옮겨야 한다.

## 알려진 문제
- 기록 순서가 날짜순이 아니다: p40–p64는 10-20 일인데 10-24 기록(p39) 뒤에 있다. SEEN_UNTIL·홀드아웃이 파일 순서를 쓰므로 "세운 뒤 기록"으로 시험되는 것은 맞지만, 날짜로 읽을 때는 주의.
- 원격 브랜치 삭제와 태그 푸시는 이 클라우드 환경에서 막혀 있다(`git push --delete`는 연결 끊김, 태그 푸시는 'up-to-date'라면서 올라가지 않음, API는 프록시 403). 브랜치 푸시만 된다. 사용자가 PC에서 한다.

## 다음 작업자에게
- 병합된 두 브랜치와 태그로 보존한 옛 역사 브랜치는 사용자가 삭제한다: `ccr-2a22e640-e8dn8n`, `claude/relaxed-babbage-11l0ha`, `claude/inspiring-planck-m43xto`, `claude/jolly-mayer-jzwd7u`, (이미 병합돼 있던) `claude/professor-king-agent-usage`.
- nonfiction_games·retrieval_v0을 다시 쓰려면 `archive/old-history-2026-10-19`에서 18개 파일을 옮겨 심고 루트 CLAUDE.md에 분야·실험 항목을 다시 적는다(dG1–dG6 사용량 기록은 main 번호 체계로 옮겨 적어야 한다).
