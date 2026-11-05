# 2026-11-06 — 설계 사전 고정과 하위 에이전트 턴 수의 회귀 분석

작업자: 메인 Codex. 하위 에이전트 호출: 없음. 직접 작업 기록: `domains/agent_usage/direct.toml`의 `m002`.

## 질문과 현재 판정

> 설계 문서가 동작·데이터·검사까지 정해 두면, 서브 에이전트의 턴 수가 줄어드는가?

기존 주장 `C_turns_spec_fixed`를 다시 살펴봤다. 노출은 `S_spec_fixed`의 **예/아니오**, 결과는 `actual.turns`다. 이 상태는 지시서의 길이가 아니라, 설계 문서가 동작·데이터·검사까지 미리 정했는지를 뜻한다.

**현재 기록에서 턴 감소를 뚜렷하게 확인하지 못했다.** 주 분석의 예/아니오 턴 수 배수는 **0.959배**, 95% 신뢰구간은 **0.509–1.805배**, 양측 p값은 **0.894**다. 감소 효과가 없다는 확정도, 감소 효과가 있다는 확인도 아니다. 효과의 방향과 크기를 가려낼 비교 자료가 부족하다.

이번 작업은 **기존 기록의 탐색 회귀**다. 조건을 무작위로 배정한 새 개입 실험이나, 기존 가설을 보지 않고 수행한 독립 검증이 아니다. 기존 가설의 내려간 상태는 변경하지 않았다.

## 한 일

- 회귀 전에 표본·변수·주 분석식·민감도 분석을 정했다. 결과가 유의해지는 변수를 탐색해 고르지 않았다.
- 같은 모델·설정과 예/아니오가 모두 있는 프로젝트를 주 분석 대상으로 삼았다.
- 단순 비교, 작업 특성 보정, 작업량 보정, 다른 모델 포함, 포아송 회귀, 프로젝트별 제외 결과를 함께 살폈다.
- 입력 스냅숏·분석 계획·전체 계수·진단값·재실행 스크립트·그림은 `out/spec_fixed_regression_2026-11-06/`에 저장했다. 원본 입력과 기계 출력은 git 제외인 `out/`에만 둔다.
- 이 문서에는 요약·분석 방법·주 분석 재현 코드를 남긴다. 공개 저장소에 로컬 세션 경로나 대화 내용은 옮기지 않았다.

## 데이터와 표본

기준 커밋은 `b1f9b8f`(분석을 시작할 때의 main `d1c8856`과 작업 기록 내용은 동일)다. 당시 작업 기록은 366건이고, 로컬에 복원한 Codex 기록 3건(p242–p244)을 합친 스냅숏은 369건이었다. 로컬 3건은 턴 수의 단위가 달라 분석에서 모두 제외했다. **실제 회귀에 들어간 기록은 기준 커밋의 데이터와 동일함을 확인했다.**

로컬 입력 `dispatches.toml` 스냅숏 SHA-256: `a7b28021134fbb35d612c9995d343a35310a2c49bd6f2dacc878b0bc9e770464`.

| 단계 | 건수 | 예 | 아니오 |
|---|---:|---:|---:|
| 완료·양의 턴 실측·이진 상태, 기존 로그 단위 | 210 | 167 | 43 |
| 그중 Opus 5.5 high | 170 | 152 | 18 |
| 그중 양쪽 조건이 있는 프로젝트 — 주 분석 | **92** | **74** | **18** |

- 완료 여부는 `dispatches.done()`을 따랐다. 옛 기록에서 `actual.status`가 없는 경우도 이 함수의 완료 판정을 쓴다.
- `S_spec_fixed`가 일부·모름·미기록인 기록과, 턴 실측이 없거나 0 이하인 기록은 제외했다.
- 메인 자신의 작업과, Claude 로그의 블록 수와 다른 단위인 Codex native 응답 수를 제외했다.
- 모델·effort는 `dispatches.setup()`으로 읽었다. 명시 칸이 없는 옛 기본 설정 기록에는 저장소의 기존 추론 방식을 썼다.

Opus high의 프로젝트별 양쪽 조건 분포:

| 프로젝트 | 예 | 아니오 | 주 분석 포함 |
|---|---:|---:|---|
| batman | 25 | 4 | 예 |
| proviso | 35 | 11 | 예 |
| movie_game | 14 | 3 | 예 |
| 나머지 6개 프로젝트 | 78 | 0 | 아니오 |

한쪽 조건만 있는 프로젝트가 직접 비교를 대신하게 하지 않으려고 주 분석에서 뺐다. 이들을 포함한 회귀도 민감도 분석으로 보고했다.

## 회귀 방법

주 분석식:

```text
log(actual.turns) ~ fixed
                  + 프로젝트 범주
                  + 이어 보내기 범주(S_resumed)
                  + 코드 없는 작업 범주(S_no_code)
                  + 웹 작업 범주(S_web)
                  + 기록일의 선형 추세
```

`fixed=1`은 `S_spec_fixed=예`, `fixed=0`은 아니오다. 다른 상태의 일부·모름·미기록은 별도 범주로 유지했으며 아니오로 채우지 않았다. 모델·effort는 Opus high로 제한했다.

- 추정 방법: 로그 턴 수의 선형 회귀(OLS). `exp(fixed 계수)`를 예/아니오 배수로 보고한다. 이는 조건부 **기하평균**의 비이며, 산술평균이나 모든 작업의 공통 효과를 뜻하지 않는다.
- 불확실성: 같은 배치의 유사·반복 작업을 고려해 `project:batch` **35개 군집** 단위의 표준오차를 사용했다. 소표본 보정과 군집 수에 따른 t 기준으로 95% 구간과 양측 p값을 계산했다.
- 주 분석의 변수 열은 10개, 행렬의 독립 열 수도 10개다. `S_web`과 `S_resumed`의 누락 표시가 정확히 중복되어 웹 누락 열 하나를 제거했다. 기록을 빼거나 p값에 따라 변수를 고른 것이 아니며, 같은 회귀 공간의 중복을 제거한 것이다.
- HC3 방식으로 표준오차를 바꾸어도 주 분석의 구간은 0.496–1.855배, p=0.900으로 결론이 같았다.
- 실제 파일 수·수정 횟수·도구 호출·토큰·시간 같은 사후 결과, 결과와 연결된 `S_short`, 예측 턴 수, 뜻이 많이 겹치는 `S_specified`는 턴 수의 보정 변수로 넣지 않았다.

구현 기준: [statsmodels의 견고한 공분산](https://www.statsmodels.org/stable/generated/statsmodels.regression.linear_model.OLSResults.get_robustcov_results.html), [GLM·포아송](https://www.statsmodels.org/stable/glm.html).

## 결과

아래의 1배는 차이 없음, 1배 미만은 예 쪽 턴 수가 적다는 뜻이다. 구간과 p값은 모두 배치 군집 기준이다.

| 분석 | n | 예/아니오 배수 | 95% 신뢰구간 | p |
|---|---:|---:|---:|---:|
| 여러 모델 단순 비교, 같은 로그 단위 | 210 | 0.623 | 0.368–1.054 | 0.077 |
| Opus high 단순 비교 | 170 | 0.653 | 0.323–1.320 | 0.230 |
| 주 분석과 같은 3개 프로젝트의 단순 비교 | 92 | 0.659 | 0.332–1.306 | 0.224 |
| **주 분석: 프로젝트·작업 특성·날짜 보정** | **92** | **0.959** | **0.509–1.805** | **0.894** |
| 사전 작업량 수까지 추가 | 92 | 0.730 | 0.408–1.306 | 0.279 |
| 한쪽 조건만 있는 프로젝트도 포함·보정 | 170 | 0.953 | 0.509–1.784 | 0.879 |
| 다른 모델 포함·모델/effort도 보정 | 210 | 0.769 | 0.405–1.459 | 0.416 |
| 같은 주 표본의 포아송 턴 수 회귀 | 92 | 1.065 | 0.617–1.839 | 0.816 |
| 보조: 같은 조건의 실제 소요 시간 | 92 | 1.157 | 0.638–2.097 | 0.622 |

주 분석에서 `fixed`의 로그 계수는 **−0.041911**, 군집 표준오차는 **0.311267**다. 단순 비교의 0.659배가 보정 후 0.959배로 바뀌었다. 원래 차이에 작업 구성의 차이가 섞였을 가능성을 보여 주지만, 어느 변수가 원인이라고 이 회귀만으로 확정할 수는 없다.

포아송 회귀는 조건부 산술평균 턴 수를 로그 연결로 모델링한 민감도 분석이다. 시간 회귀는 턴 수 주장의 보조 결과이며, 턴 수 회귀를 대신하지 않는다. 어느 모델에서도 95% 구간이 1배의 양쪽에 걸쳐 있다. 표의 여러 p값은 탐색값이며 다중검정 보정을 하지 않았다.

### 작업량 보정의 범위

`size.outputs`, `size.edits`, `size.checks`에 `log1p`를 취해 추가했다. 누락은 각 칸의 주 표본 중앙값으로 채우고, 누락 여부를 별도 변수로 넣었다. **누락을 0으로 취급하지 않았다.**

옛 `size`는 작업 설명에서 사후에 보충한 값이 있고, 동일한 수가 항상 동일한 작업량을 뜻하지 않는다. `chunks`는 단위가 섞여 제외했다. 사전에 기록한 파일 수는 더 희소해서 주 보정 변수로 쓰지 않았다. 이 분석이 작업량 차이를 충분히 제거했다고 볼 수 없다.

### 프로젝트를 하나씩 뺀 진단

| 제외 프로젝트 | n | 턴 수 배수 | 95% 신뢰구간 |
|---|---:|---:|---:|
| batman | 63 | 0.825 | 0.518–1.315 |
| movie_game | 75 | 1.255 | 0.526–2.995 |
| proviso | 46 | 1.072 | 0.281–4.093 |

작은 표본과 비교군 구성을 바꾸면 추정 방향도 바뀐다. 이 진단을 보고 더 유리한 모델을 고르지는 않았다.

## 확인한 것

- `out/regression-venv/Scripts/python.exe out/spec_fixed_regression_2026-11-06/run_regression.py` → 위 회귀·민감도 분석과 보고서 생성 완료.
- OLS 계수를 NumPy 최소제곱으로 다시 계산해 일치 확인.
- 주 노출 계수를 다른 변수의 영향을 뺀 잔차끼리 계산해 일치 확인: −0.04191120770231459.
- 배치별 점수 합과 샌드위치 식으로 군집 공분산을 직접 다시 계산해 statsmodels와 일치 확인. 주 표준오차 0.31126720605237157.
- 주 표본 id 중복 없음, 설계 행렬의 독립성 확인.
- 기준 커밋 366건이 로컬 스냅숏의 앞부분과 동일하며, 추가 3건이 모두 분석에서 제외되는 Codex 기록임을 확인.
- 이 문서 부록의 코드를 기준 커밋 입력으로 실행해 주 표본 92건·배수·신뢰구간·p값이 원래 분석과 일치함을 확인.
- `python -m unittest tests.test_agent_usage_domain tests.test_feedback tests.test_eda tests.test_decide` → 관련 테스트 56개 통과. `python -m feedback check` → 문제 없음. 앞서 알려진 전체 테스트의 파일 수 비례 가설 오류와 Windows 환경 오류를 고친 작업은 아니다.
- 분석 환경: Python 3.12.10, NumPy 2.5.4, pandas 3.1.1, SciPy 1.18.1, statsmodels 0.15.0. 코어 의존성은 바꾸지 않았고 분석 패키지는 `out/`의 전용 가상환경에 설치했다.

## 확인 못 한 것과 알려진 한계

1. **비교군 부족**: 주 표본에서 아니오는 18건이며, 코드가 있는 작업으로 한정하면 예 11건·아니오 1건뿐이다. 코드 없는 작업은 예 38건·아니오 4건, 그 밖의 상태는 미기록·일부다. 모든 조건에서 충분히 비교되는 자료가 아니다.
2. **작업량·난이도**: 지시서를 다시 읽어 규모를 같은 단위로 재코딩하지 않았다. 원인 찾기, 새 글을 짓는 양, 검사 난이도 등의 차이가 남을 수 있다.
3. **시점과 역할**: 상태 값에는 옛 기록을 사후에 채운 것이 있다. 작업 유형·규모가 지시서 구체화의 결과인 경우, 이를 보정하면 구체화의 효과 일부까지 제거할 수 있다.
4. **독립성**: 배치 군집은 작업 사이의 의존성을 근사한 선택이다. 같은 에이전트가 여러 배치에 걸쳐 일하거나, 같은 지시서가 다른 배치에 반복되는 모든 의존성을 제거한 것은 아니다.
5. **인과 확인**: 원래 어려운 일을 더 자세히 지시했는지 등 작업 배정 이유는 충분히 기록돼 있지 않다. 현재 회귀로 ‘상세하게 지시한 효과’와 그런 배정 차이를 완전히 가를 수 없다.
6. **목표 범위**: 이 분석의 결과 변수는 작업자 턴 수다. 메인의 설계 작성 시간과 결과물 품질까지 합친 전체 효율은 시험하지 않았다.

## 다음 작업자에게

현재 판정은 **감소 효과 확인 못 함**으로 유지한다. 기록을 더 모으면 효과가 작다는 결론이 나올 수도 있다. 총건수만 늘리기보다, 같은 작업·모델·완료 기준에서 설계 고정 여부를 달리한 비교 자료가 이 질문을 가르는 데 도움이 된다.

개입 실험을 한다면 먼저 어떤 차이까지 구분할지와 반복 수·분석 기준을 정하고, 예/아니오 조건의 배정·실행 순서를 섞어 새 기록으로 확인한다. 다음 개입 실험의 구체적인 설계는 아직 정하지 않았다.

## 부록: 주 분석 재현 코드

저장소 루트에서 pandas·NumPy·statsmodels를 설치한 분석용 Python으로 실행한다. 입력을 `b1f9b8f`에 고정하므로 나중에 기록이 늘어도 같은 비교를 재현한다. 현재 작업 파일은 수정하지 않는다. 전체 분석 스크립트와 원본 출력은 앞서 적은 로컬 `out/`에 있다.

```python
import subprocess
import tomllib

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf

from domains.agent_usage import dispatches as dp

raw = subprocess.check_output([
    "git", "show", "b1f9b8f:domains/agent_usage/dispatches.toml"
]).decode("utf-8")
rows = []
for d in tomllib.loads(raw)["dispatch"]:
    s, a = d.get("situation", {}), d.get("actual", {})
    if not dp.done(d) or s.get("S_spec_fixed") not in ("예", "아니오"):
        continue
    if not isinstance(a.get("turns"), (int, float)) or a["turns"] <= 0:
        continue
    if dp.setup(d) != ("Opus 5.5", "high") or s.get("S_main_self") == "예":
        continue
    cat = lambda key: {"예": "yes", "아니오": "no"}.get(
        s.get(key), "unknown_or_partial"
    )
    rows.append(dict(
        id=d["id"], project=d["project"], fixed=int(s["S_spec_fixed"] == "예"),
        turns=a["turns"], resumed=cat("S_resumed"), no_code=cat("S_no_code"),
        web=cat("S_web"), date=pd.Timestamp(d["date"]),
        cluster=f"{d['project']}:{d['batch']}",
    ))
df = pd.DataFrame(rows)
counts = pd.crosstab(df.project, df.fixed)
projects = counts.index[(counts[0] > 0) & (counts[1] > 0)]
df = df[df.project.isin(projects)].copy()
df["day"] = (df.date - pd.Timestamp("2026-10-13")).dt.days.astype(float)
model = smf.ols(
    "np.log(turns) ~ fixed + C(project) + C(resumed) + C(no_code) + C(web) + day",
    data=df,
)
X = pd.DataFrame(model.exog, columns=model.exog_names, index=df.index)
# 이 스냅숏에서는 두 누락 표시가 정확히 같다.
assert np.array_equal(
    X["C(web)[T.unknown_or_partial]"],
    X["C(resumed)[T.unknown_or_partial]"],
)
X = X.drop(columns="C(web)[T.unknown_or_partial]")
assert np.linalg.matrix_rank(X) == X.shape[1]
fit = sm.OLS(model.endog, X).fit(
    cov_type="cluster",
    cov_kwds={"groups": df.cluster, "use_correction": True, "df_correction": True},
    use_t=True,
)
print("n / yes / no:", len(df), int(df.fixed.sum()), int((1-df.fixed).sum()))
print("ratio:", np.exp(fit.params["fixed"]))
print("95% CI:", np.exp(fit.conf_int().loc["fixed"]).to_list())
print("p:", fit.pvalues["fixed"])
```

예상 출력: `92 / 74 / 18`, `0.958955`, `[0.509420, 1.805179]`, `0.893685`.
