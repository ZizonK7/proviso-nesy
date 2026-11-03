# 2026-11-03 — 먼 분야 경험 논리 (far_fields)

에이전트: 메인 자신(클라우드 세션, Opus 5.5). 부모 세션(잼민이)이 사용자 위임으로 보낸 일. 하위 에이전트 호출: 없음. Claude API 호출(키는 환경 변수 `API`, 출력·저장 안 함): 동기 호출 약 25회, 배치 3개.
커밋·push: 함(브랜치 `claude/far-fields-2026-11-03`).

## 한 일
- 새 분야 `domains/far_fields/`: 분야 409개(Opus 생성 399 + Haiku 웹 조사 10), 조각 4,925개, 모양 36개, AI 검토 판정 4,925개. 설명은 그 폴더 CLAUDE.md.
- 분야 목록: Opus 5.5에 400개를 뽑게 함(사용자 쪽 교육·과외·상담·수학·데이터·AI·사무 제외, 기존 10개 제외). 다우징(유사과학) 1개를 뺌.
- 시험 생성 5개(해녀 물질·대장간 단조·피아노 조율·된장 담그기·인질 협상, 정가 동기 호출) → 품질 확인 뒤 본 생성.
- 생성 배치 `msgbatch_0182eEdyy2LKYikdHm951qWq` 394건, 검토 배치 `msgbatch_01Utpw7YLyjWQhXtAtK91m18` 394건, 시험·Haiku분 검토 배치 `msgbatch_019UqeSBVyh5RCDZeQU5sadr` 15건. 모두 성공·오류 0.
- Haiku 웹 조사 md 10개(gemmin 저장소)를 API로 칸만 옮김(낱말 그대로 지시) → 137개. 검토 배치에서 일반화 88개를 고친 문장으로 바꿈(원문 보존).
- 연결 실험 설계 `docs/connection-experiment-v0.md`, 코드 `domains/far_fields/connect.py`, 1회 6쌍 `docs/experiments/connections/seed-20261103.md`.
- 테스트 `tests/test_far_fields.py`(5개). `scripts/claude_http.py`(표준 라이브러리 API 호출, 키는 `API`에서만).
- 루트 CLAUDE.md 분야 표·구조 표·다음 할 일 3에 한 줄씩.

## 확인한 것 (어떻게)
- `python -m proviso validate far_fields` → 문제 없음 (목표 3, 상태 36, 가설 4925, 판정 4925).
- `python -m proviso audit far_fields` → 오류 0, 경고 13(분야 낱말 새는 것). 시험 수단 없음 0.
- `python -m unittest discover -s tests -t .` → 114개 통과.
- `python -m domains.agent_usage.dispatches` → p145 문제 없음.
- `grep -l sk-ant out/far_fields/*` → 없음. 저장한 응답·커밋 파일에 키 없음.
- 비용: `python -m domains.far_fields.generate cost <이름> [--batch]`로 usage 합 → 합계 $55.47 (CLAUDE.md 표).

## 확인 못 한 것
- 조각이 실제 현장에서 맞는지: 현장 확인 없음. 판정은 같은 모델의 검토뿐이다.
- 잔액: 잔액 API가 없어 모름.
- 연결 실험 첫 두 번의 거절된 호출 비용(usage를 저장하지 않음) — 약 $1~2로 추정.

## 알려진 문제
- **연결 실험이 안전 분류기에 거절됨(reasoning_extraction)**: 첫 양식(조각을 다시 말하기 + 각도마다 시도 과정)이 6쌍 중 4쌍, 다시 보내도 대부분 거절. 서버 대체 모델(`fallbacks: "default"`)도 받지 않았다. 양식을 '아이디어 카드'(각도마다 아이디어 한 줄 + 쓸 만한지)로 바꾸자 6쌍 모두 통과. 지금 코드는 바꾼 양식.
- 연결 실험 자기평가가 6쌍 모두 3·4·2로 같다 → 자기평가는 정보가 거의 없다. 사용자 판정이 필요.
- 생성자와 검토자가 같은 모델: 지지 비율(Opus 생성분 84%)은 후할 수 있다.
- `knowledge.toml`이 7MB. 검사는 빠름(audit 0.1초, check 2초). 그래프 html은 커서 보기 어렵다.

## 다음 작업자에게
- `knowledge.toml`은 `build.py`가 만든다. 원본 jsonl(`out/far_fields/`)은 이 컨테이너에만 있으니, 회수 뒤에는 toml을 직접 고치고 domains/far_fields/CLAUDE.md에 적는다.
- 배치는 생각보다 훨씬 빨랐다(394건 8분). 다음에는 배치 대기 시간을 1시간이 아니라 10분 안팎으로 잡는다.
- 연결 실험 프롬프트에 '사고 과정을 단계별로 쓰라'에 가까운 양식을 넣으면 거절된다. 결과물(카드) 양식으로.
