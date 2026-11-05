# eda/ — 논리집 데이터 탐색(EDA)

## 역할
저장소에 쌓인 논리집 데이터를 표(CSV)로 펼쳐 pandas·노트북으로 둘러보게 한다(2026-11-05 사용자 요청 "현재 있는 논리집 데이터로 eda 해보려고 하는데 세팅좀").
분석 결과를 지식에 넣는 곳이 아니다 — 여기서 본 것이 가설·피드백이 되면 그 분야 `knowledge.toml`이나 `feedback/`에 출처 붙여 적는다.

## 파일
- `export.py` — `python -m eda.export [--out 폴더]`. 표준 라이브러리만. 읽기 전용으로 아래를 읽어 `out/eda/*.csv`(git 제외)에 쓴다. 쓰기 전에 그 폴더의 CSV를 지운다(F064).
- `start.ipynb` — 시작 노트북. 첫 셀에서 `export()`를 다시 돌려 늘 최신 표를 읽는다. **출력을 지우고 커밋**한다(공개 저장소에 표가 그대로 박히지 않게, diff가 커지지 않게).
- `requirements.txt` — 노트북에만 필요한 패키지(pandas·matplotlib·jupyterlab). 내보내기와 테스트는 이것 없이 돈다.

## 표 (한 행이 무엇인가)
| 표 | 한 행 | 읽는 곳 |
|---|---|---|
| `nodes` | 노드 하나(목표·상태·사실·관찰·가설·규칙). 공통 칸 + 분야 칸 전부, 목록 칸은 `\|`로 잇고 `n_<칸>`에 개수, `in_degree`/`out_degree`, 가설이면 `alive`·`n_checks`·`n_judgments` | `proviso.schema.load` (나눈 파일 포함, `part`에 파일 이름) |
| `edges` | 참조 하나 `src --field--> dst` | `schema.REFS`의 칸 |
| `effects` | 효과 칸 하나 | `[[rule.effect]]`·`[[hypothesis.effect]]` |
| `judgments` | 판정 기록 하나 | `[[judgment]]` |
| `dispatches` | 보낸 일 기록 하나. 중첩은 `actual.minutes`처럼 점, `[하한, 상한]`은 `_lo`·`_hi`, `hit.<양>` = 실측이 예측 구간 안인가 | `domains/agent_usage/dispatches.toml` |
| `dispatch_rules` | 기록 × 규칙 (role: 예측에 씀·틀림 지목 등) | 같은 파일 |
| `dispatch_turns` | 기록 × 도구 종류의 턴 길이 | `[dispatch.turns]` |
| `direct` | 직접 한 일 기록 | `direct.toml` |
| `feedback`·`feedback_index`·`feedback_main` | 백서 항목 / 항목 × 색인 낱말 / 메인 파일 × 항목 | `feedback.entries()`·`mains()` |

## 지킬 것
- 원본 파일은 읽기만 한다. 내보낸 CSV와 노트북 출력은 `out/`에만.
- 새 데이터 파일(새 분야, 새 기록 칸)은 대부분 저절로 따라온다(칸 이름을 하드코딩하지 않음). 새 *종류*의 파일을 표로 만들면 위 표와 `tests/test_eda.py`를 같이 고친다.
- `far_fields`(AI가 만든 조각 1만여 개)는 크기가 다른 분야를 압도하고 판정이 AI뿐이다(F074) — 분야를 섞어 세는 통계는 따로 떼어 본다.
- 기록 숫자로 보는 상관은 인과가 아니다. 상황 값과 결과가 같이 움직여도 선택 편향(F084)일 수 있다.

## 다른 폴더와의 관계
- `proviso/`(코어)·`feedback/`의 읽기 함수를 그대로 쓴다 — 칸 해석을 여기서 따로 만들지 않는다.
- 코어의 '외부 패키지 없음' 규칙은 지키고(내보내기는 표준 라이브러리), 분석 도구(pandas 등)는 노트북에만 둔다.
