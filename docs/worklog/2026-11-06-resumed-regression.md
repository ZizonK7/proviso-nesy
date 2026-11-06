# 2026-11-06 — 이어 보내기와 하위 에이전트 턴 수의 회귀 분석

작업자: 메인 (Claude, 클라우드 세션). 하위 에이전트 호출: 없음. 커밋·push: 메인이 함. 직접 작업 기록: `domains/agent_usage/direct.toml`의 `m003`.

## 질문과 판정

> 앞 회차를 마친 같은 에이전트에게 이어서 보내면(합치는 일이 아니면) 턴이 줄어드나? — `C_turns_resumed_v2`, 계산기 범위 ×0.171–0.333

**방향은 지지된다.** 주 분석에서 이어 보낸 회차의 턴 수는 처음 보낸 일의 **0.456배**(95% 구간 **0.326–0.637**, p < 0.001)였다. 미리 정한 민감도 분석 중 돌릴 수 있었던 것은 모두 구간이 1배 아래에 있다(0.33–0.55배).

**크기는 미리 정한 기준으로는 '맞음'이지만 아슬아슬하다.** 구간 아래끝 0.326이 계산기 범위 위끝 0.333과 조금 겹칠 뿐이다. 추정값 0.46은 계산기 범위(0.17–0.33)보다 위라서, 계산기가 이어 보낸 회차를 조금 세게 깎고 있을 수 있다. 숫자를 다시 맞출지는 정하지 않았다(아래 "다음 작업자에게").

이 작업은 **기존 기록의 탐색 회귀**다. 무작위로 나눈 실험이 아니라서 "이어 보냈기 때문에 줄었다"는 인과까지는 말하지 못한다. 가장 큰 남은 의심은 **이어 보내는 일이 원래 작은 후속 일이라는 점**이다(한계 1).

## 한 일

- 결과(턴·분)를 집단별로 보기 전에 표본·노출·주 분석식·판정 기준·민감도 분석 10개를 `out/resumed_regression_2026-11-06/plan.md`에 고정했다. 그 전에 본 것은 집단별 건수뿐이다.
- 입력은 커밋 `87ab8dc`의 `dispatches.toml`(SHA-256 `0819301ff0954871a68fdcdc1d6a0f6b0caae2e482b95ccc25a5f3ca74b47e37`).
- 분석 환경은 git에서 빠지는 `out/regression-venv/`에 만들었다(Python 3.13, NumPy 2.5.4, pandas 3.1.1, SciPy 1.18.1, statsmodels 0.15.0). 코어 의존성은 바꾸지 않았다.
- 분석 스크립트·결과 표·주 표본·회귀 요약은 `out/resumed_regression_2026-11-06/`에 있다. 클라우드 컨테이너가 회수되면 사라지므로, 주 분석 재현 코드는 이 문서 부록에 남긴다.

## 데이터와 표본

| 단계 | 건수 |
|---|---:|
| 끝남 · 턴 실측 > 0 · 메인 자신의 일 아님 · S_resumed가 예/아니오 | 279 |
| 그중 합치는 일 아님(S_integration ≠ 예, 빈칸 포함 — 계산기의 `!예`와 같다) | 270 |
| 그중 Opus 5.5 high (`dispatches.setup`) | 222 |
| 그중 양쪽 집단이 다 있는 프로젝트 — **주 분석** | **187** (이어 보냄 65 · 처음 122) |

- 노출: 이어 보냄 = S_resumed 예이면서 합치는 일이 아님. 비교 = S_resumed 아니오이면서 합치는 일이 아님.
- 주 분석 프로젝트: batman(처음 46 · 이어 18), proviso(52 · 8), movie_game(11 · 9), gemmin(11 · 3), exam_grader(1 · 24), language_learning(1 · 3). 한쪽 집단만 있는 font·professor_king·suneung(모두 처음 보냄)은 민감도 2에서 넣었다.
- 군집(같은 프로젝트·배치) 67개.
- 지난 분석(설계 고정, 비교 쪽 18건)과 달리 양쪽 집단이 다 넉넉하다.

## 회귀 방법

```text
log(actual.turns) ~ resumed
                  + 프로젝트
                  + 코드 없는 일(S_no_code) + 웹(S_web) + 정해진 입력(S_fixed_input)
                  + 조사(S_research) + 기존 것 고치기(S_fix_existing) + 설계 고정(S_spec_fixed)
                  + 기록일의 선형 추세
```

- 범주 칸은 예 / 아니오 / 그 밖(빈칸·일부·모름)을 따로 둔다. 빈칸을 아니오로 채우지 않았다.
- 보낸 뒤에야 아는 값(실제 파일 수, 도구 호출, 토큰, 시간, S_short, 예측 턴)은 넣지 않았다.
- OLS. `exp(계수)`가 이어 보냄 ÷ 처음의 조건부 기하평균 비다. 표준오차는 `project:batch` 군집 기준(소표본 보정, t 기준).
- 주 분석에서는 설계 행렬의 열이 겹치지 않아 뺀 열이 없다. proviso를 뺀 진단에서만 웹 '예' 열이 상수라 빠졌다.

## 결과

1배 미만이면 이어 보낸 쪽 턴이 적다는 뜻이다.

| 분석 | n (이어/처음) | 배수 | 95% 구간 | p |
|---|---:|---:|---:|---:|
| **주 분석** | **187 (65/122)** | **0.456** | **0.326–0.637** | **<0.001** |
| 1 같은 표본 단순 비교(아무것도 안 맞춤) | 187 | 0.343 | 0.192–0.613 | <0.001 |
| 2 한쪽 집단만 있는 프로젝트도 포함 | 222 (65/157) | 0.458 | 0.327–0.639 | <0.001 |
| 3 다른 모델 포함 · 모델/effort 보정 | 230 (74/156) | 0.497 | 0.363–0.681 | <0.001 |
| 4 포아송(턴 수 그대로) | 187 | 0.374 | 0.292–0.479 | <0.001 |
| 5 회차 시각이 있는 기록만 | 14 | 못 돌림 | — | — |
| 6 S_integration 빈칸 뺌 | 115 (46/69) | 0.418 | 0.294–0.594 | <0.001 |
| 8 보조 결과: 분 | 187 | 0.551 | 0.399–0.761 | <0.001 |

- 주 분석 계수 −0.7855, 군집 표준오차 0.1679. HC3 표준오차로 바꿔도 구간 0.325–0.639.
- 주 표본의 기하평균 턴: 처음 81.0, 이어 보냄 27.8(중앙값 84.5 · 27).
- 단순 비교 0.34배가 보정 뒤 0.46배로 1 쪽으로 움직였다. 이어 보낸 일에 작은 일의 모양이 더 많이 섞여 있다는 뜻이다. 예를 들어 '기존 것 고치기'가 이어 보냄 27/65, 처음 25/122다. 보정한 뒤에도 효과는 남는다.

### 프로젝트를 하나씩 뺀 진단

| 뺀 프로젝트 | n | 배수 | 95% 구간 |
|---|---:|---:|---:|
| batman | 123 | 0.419 | 0.303–0.579 |
| exam_grader | 162 | 0.459 | 0.329–0.639 |
| gemmin | 173 | 0.493 | 0.341–0.713 |
| language_learning | 183 | 0.463 | 0.334–0.644 |
| movie_game | 167 | 0.333 | 0.258–0.428 |
| proviso | 127 | 0.458 | 0.297–0.706 |

어느 프로젝트를 빼도 방향이 뒤집히지 않는다(지난 설계 고정 분석과 다르다). movie_game을 빼면 효과가 더 커진다.

### 참고(판정에 쓰지 않음)

- **합치는 일**(S_integration = 예, Opus high): 처음 4건의 중앙값 101턴, 이어 보냄 4건의 중앙값 354.5턴. 이어 보내도 줄지 않는다는 쪼갠 조건과 방향은 같지만, 4건씩이라 판정하지 않는다.
- **같은 에이전트의 1회차 → 2회차**(에이전트 이름 칸이 있는 것 중 두 회차가 다 있는 3개, 모두 gemmin): p189 61 → p190 10, p183 148 → p185 53, p184 141 → p186 31(0.16·0.36·0.22배). 회차마다 일이 다르므로 효과의 크기로 읽지 않는다.
- **회차 시각이 있는 기록**(민감도 5의 단순 집계): 주 표본 40건(처음 25 · 이어 15), 중앙값 71 · 17턴. 보정 회귀는 못 돌렸다(아래 한계 2).

## 확인한 것

- `PYTHONPATH=. out/regression-venv/bin/python out/resumed_regression_2026-11-06/run.py` → 위 표 전부.
- 이 환경이 지난 분석을 재현하는지: `docs/worklog/2026-11-06-spec-fixed-regression.md` 부록 코드를 그대로 돌려 92 / 74 / 18, 0.958955, [0.509420, 1.805179], 0.893685로 일치.
- 주 분석 구간을 HC3 표준오차로 다시 계산해 결론이 같음을 확인.
- 이 문서 부록 코드를 같은 입력으로 돌려 주 분석 숫자와 일치함을 확인.

## 확인 못 한 것과 알려진 한계

1. **일의 크기**: 이어 보내는 회차는 "찾은 것 고치기", "남은 것 마저" 같은 후속 일이 많다. 작업 모양 스위치를 맞췄지만 일의 양 자체(쓸 파일 수, 고칠 곳 수)는 넣지 않았다. 그래서 0.46배 중 얼마가 가설의 이유('앞 회차에서 읽어 둬서 탐색 턴이 빠진다')이고 얼마가 '원래 작은 일'인지 가르지 못한다. 미리 정하지 않은 보정이라 이번에는 돌리지 않았다(F085).
2. **민감도 5를 못 돌렸다**: 회차 시각이 있는 기록 중 양쪽 집단이 다 있는 프로젝트는 14건뿐이라 변수 수보다 적다. 이 분석은 옛 기록에서 이어 보낸 회차를 잴 때 앞 회차 턴까지 같이 센 경우를 보려던 것이다. 그런 측정 오류가 있었다면 효과를 1 쪽으로 눌렀을 것이므로, 실제 효과는 이보다 클 수 있다.
3. **에이전트 안 비교가 거의 없다**: 에이전트 이름 칸이 2026-11-03부터라서, 같은 에이전트의 1·2회차를 다 가진 기록이 3쌍뿐이다. 에이전트 고정효과 분석은 못 했다.
4. **한쪽으로 쏠린 프로젝트**: exam_grader는 처음 1 · 이어 24, language_learning은 1 · 3이다. 이들의 프로젝트 효과는 거의 그 1건이 정한다. 빼고 돌려도 결과는 같았다.
5. **계산기 범위와의 비교**: 계산기 범위는 곱하기 조각 하나의 효과이고, 회귀 배수는 다른 조건을 맞춘 조건부 비라서 정확히 같은 양은 아니다. 크기 판정은 대략적인 비교로 읽는다.
6. 다중 검정 보정은 하지 않았다. 판정은 주 분석 하나로만 미리 정했다.

## 다음 작업자에게

- 판정: 방향 지지, 크기는 겹치지만 계산기가 조금 세게 깎을 가능성이 있다. knowledge.toml의 범위는 손으로 고치지 않는다(손으로 고친 범위는 audit 오류). 다시 맞출 때는 `fit final`로 하고, 그 전에 일의 크기를 함께 볼지 정한다.
- 한계 1을 풀려면 이어 보낸 회차와 1회차에 같은 단위의 일의 양(쓰는 파일 수 `files`, 2026-11-04부터 필수)을 넣은 분석을 **미리 정하고** 돌린다. `files`가 있는 기록이 아직 적으니(Opus high 결과 전 27건) 기록이 더 쌓인 뒤가 낫다.
- 같은 에이전트의 1·2회차 쌍이 쌓이면 에이전트 안 비교(고정효과)가 가장 깨끗한 시험이다.

## 부록: 주 분석 재현 코드

저장소 루트에서 pandas·NumPy·statsmodels가 있는 Python으로 `PYTHONPATH=.`를 주고 돌린다. 입력을 `87ab8dc`에 고정한다.

```python
import subprocess, tomllib
import numpy as np, pandas as pd
import statsmodels.api as sm, statsmodels.formula.api as smf
from domains.agent_usage import dispatches as dp

raw = subprocess.check_output(["git", "show", "87ab8dc:domains/agent_usage/dispatches.toml"]).decode("utf-8")
CATS = {"no_code": "S_no_code", "web": "S_web", "fixed_input": "S_fixed_input",
        "research": "S_research", "fix_existing": "S_fix_existing", "spec_fixed": "S_spec_fixed"}
cat = lambda v: {"예": "yes", "아니오": "no"}.get(v, "other")
rows = []
for d in tomllib.loads(raw)["dispatch"]:
    s, a = d.get("situation", {}), d.get("actual", {})
    if not dp.done(d) or not isinstance(a.get("turns"), (int, float)) or a["turns"] <= 0:
        continue
    if s.get("S_main_self") == "예" or s.get("S_resumed") not in ("예", "아니오"):
        continue
    if s.get("S_integration") == "예" or dp.setup(d) != ("Opus 5.5", "high"):
        continue
    rows.append(dict(project=d["project"], resumed=int(s["S_resumed"] == "예"), turns=a["turns"],
                     date=pd.Timestamp(d["date"]), cluster=f"{d['project']}:{d.get('batch')}",
                     **{k: cat(s.get(v)) for k, v in CATS.items()}))
df = pd.DataFrame(rows)
c = pd.crosstab(df.project, df.resumed)
df = df[df.project.isin(c.index[(c[0] > 0) & (c[1] > 0)])].copy()
df["day"] = (df.date - pd.Timestamp("2026-10-13")).dt.days.astype(float)
f = smf.ols("np.log(turns) ~ resumed + C(project) + C(no_code) + C(web) + C(fixed_input)"
            " + C(research) + C(fix_existing) + C(spec_fixed) + day", data=df).fit(
    cov_type="cluster", use_t=True,
    cov_kwds={"groups": pd.factorize(df.cluster)[0], "use_correction": True, "df_correction": True})
print(len(df), int(df.resumed.sum()), int((1 - df.resumed).sum()))
print(np.exp(f.params["resumed"]), np.exp(f.conf_int().loc["resumed"]).tolist(), f.pvalues["resumed"])
```

예상 출력: `187 65 122`, `0.4559…`, `[0.326…, 0.637…]`, p < 0.001.
