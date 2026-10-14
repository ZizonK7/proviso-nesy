# SELA: 환각 억제 및 추론 토큰 절감을 위한 자기 진화형 신경-기호 논리 아키텍처

**(SELA: Self-Evolving Neuro-Symbolic Logic Architecture for Mitigating Hallucinations and Compressing Reasoning Tokens via Dynamic Teacher-Student Escalation)**

---

## 초록 (Abstract)

대규모 언어 모델(LLM)은 복잡한 추론 과제에서 뛰어난 성능을 보이지만, 확률적 토큰 생성 메커니즘의 한계로 인한 논리적 환각(Logical Hallucination)과 매 추론마다 방대한 생각의 사슬(Chain-of-Thought, CoT)을 처음부터 재생성해야 하는 **토큰 비효율성**이라는 두 가지 근본적 한계를 안고 있다. 반면, Lean과 같은 정형 증명기(Formal Theorem Prover)는 문법적·논리적 무결성을 보장하지만, 예외와 불확실성이 존재하는 실세계(Real-world)의 비연역적(Non-deductive) 문제를 다루기에는 지나치게 경직되어 있다.

본 논문은 이러한 간극을 해소하기 위해 실세계 프로젝트의 성공 및 실패 경험을 축적·검증·재사용하는 자기 진화형 신경-기호 논리 아키텍처(SELA)를 제안한다. SELA는 (1) 툴민 논증 모델(Toulmin Argumentation Model)을 기반으로 성공 논리와 실패 예외 조건(Rebuttal)을 그래프 형태로 저장하는 **경험적 논리집(ELKB)**, (2) 평소에는 로컬 소형 언어 모델(sLLM)이 논리집을 활용하여 비용 없이 추론하되, 자연어 해석 실패나 논리적 공백 발생 시에만 상용 대형 LLM을 소환하는 **불확실성 기반 동적 에스컬레이션(Dynamic Escalation)**, (3) 소환된 상용 LLM이 로컬 AI를 도구(Tool)로 호출하여 새로운 논리를 추론·기록하면, 이를 바탕으로 로컬 sLLM이 즉시 캐싱(Stage 1) – 야간 QLoRA 미세조정(Stage 2) – 성공/실패 기반 선호도 최적화(Stage 3)를 거쳐 스스로 진화하는 3단계 학습 파이프라인으로 구성된다. 본 아키텍처는 상용 LLM 호출 비용을 일회성 소모가 아닌 로컬 모델의 영구적 추론 자산으로 전환함으로써, 장기적으로 상용 API 의존도를 0에 수렴시키면서 대형 모델 수준의 논리적 정합성을 달성하는 새로운 패러다임을 제시한다.

---

## 1. 서론 (Introduction)

### 1.1 연구 배경 및 문제 정의

현대 LLM은 다음 토큰 예측(Next-Token Prediction)이라는 자기회귀적(Autoregressive) 목적 함수 위에서 작동한다. 최근 추론 특화 모델들은 문제 해결 정확도를 높이기 위해 수천에서 수만 개의 중간 추론 토큰을 생성하는 방식을 채택하고 있으나, 이는 두 가지 구조적 문제를 야기한다.

1. **추론의 휘발성과 토큰 낭비:** 이전에 성공적으로 해결했던 프로젝트와 동일한 논리 구조를 가진 과제가 주어져도, LLM은 과거의 논리 뼈대를 재사용하지 못하고 매번 백지상태에서 추론 토큰을 소모한다.
2. **논리적 환각(Logical Hallucination):** 외부 지식을 검색하는 RAG(Retrieval-Augmented Generation)는 ‘사실적 환각’은 줄일 수 있으나, 주어진 전제로부터 잘못된 결론을 도출하는 ‘논리적 비약’이나 ‘추론 규칙 위반’은 통제하지 못한다.

### 1.2 정형 논리(Lean)의 차용과 실세계 적용의 한계

수학적 정리를 코드로 작성하고 문법적·논리적 오류를 기계적으로 검출하는 정형 증명기 **Lean**의 패러다임을 LLM에 이식하려는 시도가 존재한다. 그러나 수학적 세계와 달리 실세계의 의사결정 및 프로젝트는 항상 100% 연역적(Deductive)으로 떨어지지 않는다. 실세계의 논리는 *“대체로 성립하지만 특정 경계 조건에서는 깨지는 경험적·귀납적 규칙”*에 가깝다. 따라서 실세계 AI에 필요한 것은 불변의 수학 공리집이 아니라, 성공한 프로젝트에서는 추론 템플릿을 얻고 실패한 프로젝트에서는 반례(Counter-example)와 예외 조건을 학습해 나가는 ‘경험적 판례집(Experiential Case Law)’이다.

### 1.3 연구의 핵심 기여 (Main Contributions)

본 논문은 로컬 환경의 소형 언어 모델($\mathcal{M}_{\text{local}}$)과 외부 상용 대형 모델($\mathcal{M}_{\text{cloud}}$), 그리고 기호적 논리 검증 엔진($\mathcal{E}_{\text{sym}}$)을 결합한 **SELA 프레임워크**를 제안하며, 주요 기여는 다음과 같다.

* **경험적 논리집(ELKB)의 정형화:** 연역적 논리 기호에 실세계의 ‘예외 조건(Rebuttal)’과 ‘경험적 신뢰도(Confidence)’를 결합한 데이터 구조 및 문법 제약 디코딩(Grammar-Constrained Decoding) 메커니즘을 정의한다.
* **역방향 도구 호출을 동반한 동적 에스컬레이션:** 로컬 sLLM이 자연어 명령의 의도 파악(Parsing)이나 논리 매칭에 실패할 때만 상용 LLM을 호출하고, 소환된 상용 LLM이 로컬 논리 엔진을 도구(Function Tool)로 조작하여 빈 논리를 채워 넣는 비대칭 협업 구조를 설계한다.
* **3단계 자기 진화형 지식 증류 파이프라인:** 상용 LLM이 남긴 추론 흔적을 바탕으로 로컬 AI가 (1) 의미론적 파싱 캐시 확장, (2) 수면 단계(Sleep-phase) QLoRA 미세조정, (3) 프로젝트 성패에 기반한 신뢰도 갱신 및 직접 선호도 최적화(DPO)를 수행하여 자립도를 높이는 구체적 학습 수식을 정립한다.

---

## 2. 제안 방법론: SELA 시스템 아키텍처 (System Architecture)

SELA는 크게 세 가지 구성 요소로 이루어진다: 자연어를 논리 쿼리로 번역하는 **로컬 신경망 통역기($\mathcal{M}_{\text{local}}$)**, 논리 규칙의 저장 및 문법 검증을 담당하는 **기호 논리 엔진($\mathcal{E}_{\text{sym}}$)**, 그리고 난제 해결 및 논리 생성을 담당하는 외부 상용 교사 모델($\mathcal{M}_{\text{cloud}}$)이다.

```
[사용자 자연어 입력 (x)]
         │
         ▼
┌───────────────────────────────────────────────────────────┐
│ 로컬 AI 에이전트 (Local Environment)                        │
│                                                           │
│  1. 로컬 신경망 통역기 (M_local: sLLM)                      │
│     ├─ 의미론적 파싱 캐시 조회 (Stage 1 학습 자산)            │
│     └─ 자연어 x ➔ 정형 논리 쿼리 q 변환 시도                 │
│                    │                                      │
│        [불확실성 게이트 (Gate Check)]                       │
│         ├─ (통과) ──► 2. 기호 논리 엔진 (E_sym)             │
│         │               ├─ 경험적 논리집 (ELKB) 그래프 탐색  │
│         │               └─ Lean 스타일 전제-결론 정합성 검증  │
│         │                        │                        │
│         │             [논리 제약 디코딩 (Guided Generation)] │
│         │                        ▼                        │
│         │                 [최종 응답 출력]                  │
│         │                                                 │
│         └─ (실패: 말귀 해석 불가 or 논리 부재)               │
└─────────────────┼─────────────────────────────────────────┘
                  │ (SOS 에스컬레이션 호출)
                  ▼
┌───────────────────────────────────────────────────────────┐
│ 외부 상용 대형 LLM (M_cloud: Teacher & Logic Compiler)     │
│  ├─ Tool 1: search_local_logic() 으로 로컬 ELKB 상태 진단   │
│  ├─ 자체 고차원 추론(CoT)을 통해 누락된 논리 사슬 생성       │
│  └─ Tool 2: commit_new_logic() 으로 로컬 DB에 새 논리 및    │
│             '자연어-논리 번역 쌍' 기록 (➔ Stage 2, 3 학습용) │
└───────────────────────────────────────────────────────────┘

```

### 2.1 경험적 논리집(ELKB)의 정형적 정의

Lean이 절대적 참인 정리(Theorem)를 저장한다면, SELA의 경험적 논리집 $\mathcal{K} = {L_1, L_2, \dots, L_m}$은 실세계의 비연역적 특성을 반영하기 위해 철학자 스티븐 툴민(Stephen Toulmin)의 논증 모델을 변형한 **5-튜플(Tuple) 구조**로 각 논리 단위 $L_i$를 정의한다.

$$L_i = \langle P_i, W_i, C_i, \mathcal{R}_i, \omega_i \rangle$$

* **$P_i$ (Premise / Data):** 논리가 발동하기 위한 입력 전제 조건 및 컨텍스트 타입 명세.
* **$W_i$ (Warrant / Inference Rule):** 전제 $P_i$로부터 결론을 도출하는 추론 연산 규칙 또는 도구 호출 시퀀스.
* **$C_i$ (Claim / Conclusion):** 추론 규칙 $W_i$가 적용되었을 때 보장되는 출력 상태 또는 결론 명제.
* **$\mathcal{R}_i = \{r_{i,1}, r_{i,2}, \dots\}$ (Rebuttals / Exception Conditions):** **실패한 프로젝트들로부터 추출된 반례 집합**이다. 만약 현재 과제 맥락에서 $r_{i,k} \in \mathcal{R}_i$가 참(True)으로 판별되면, 전제 $P_i$가 충족되더라도 해당 논리 $L_i$의 적용은 기각(Invalidate)된다.
* **$\omega_i \in [0, 1]$ (Experiential Confidence):** 실세계 프로젝트의 누적 성공/실패 횟수에 따라 동적으로 갱신되는 경험적 신뢰도 가중치이다.

### 2.2 논리 구조 기반의 다음 토큰 예측 제어 (Logic-Guided Next-Token Prediction)

로컬 모델 $\mathcal{M}*{\text{local}}$이 답변을 생성할 때, 선택된 논리 사슬 $\mathcal{T} = (L*{(1)} \rightarrow L_{(2)} \rightarrow \dots \rightarrow L_{(k)})$의 구조를 벗어나지 않도록 토큰 생성 확률 분포에 기호적 마스크(Symbolic Mask)를 씌운다. 현재 단계의 논리 규칙 $W_{(t)}$와 문법 검증기 $\mathcal{V}$가 허용하는 유효 토큰 집합을 $\Sigma_{\text{valid}}(y_{\lt j}, W_{(t)})$라 할 때, $j$번째 토큰 $y_j$의 예측 확률은 다음과 같이 제약된다.

$$P_{\text{guided}}(y_j \mid y_{\lt j}, x, \mathcal{T}) = \frac{P_{\theta}(y_j \mid y_{\lt j}, x, \mathcal{T}) \cdot \mathbb{I}\big(y_j \in \Sigma_{\text{valid}}(y_{\lt j}, W_{(t)})\big)}{\sum_{v \in V} P_{\theta}(v \mid y_{\lt j}, x, \mathcal{T}) \cdot \mathbb{I}\big(v \in \Sigma_{\text{valid}}(y_{\lt j}, W_{(t)})\big)}$$

여기서 $\mathbb{I}(\cdot)$는 지시 함수(Indicator Function)로, 논리 구조를 위배하는 토큰의 생성 확률을 물리적으로 $0$으로 차단하여 논리적 환각을 원천 봉쇄한다. 또한 긴 생각의 사슬(CoT)을 생성하는 대신, 검증된 논리 경로 $\mathcal{T}$의 변수 슬롯(Slot)만 채우도록 유도하여 생성 토큰 수를 대폭 압축한다.

---

## 3. 불확실성 게이트와 상용 LLM의 도구 소환 프로토콜

### 3.1 로컬 AI의 자가 진단: 3중 불확실성 게이트 (Tri-Gate Escalation Mechanism)

파라미터 크기가 작은 로컬 모델($\mathcal{M}_{\text{local}}$, 예: 3B~8B)이 사용자의 의도를 잘못 해석한 채 잘못된 논리를 적용하는 참사를 막기 위해, SELA는 3단계의 에스컬레이션 게이트를 통과해야만 로컬 단독 실행을 허가한다.

1. **의미 해석 게이트 ($\mathcal{G}_{\text{parse}}$ — "말귀를 알아들었는가?"):**
사용자 입력 $x$를 정형 논리 쿼리 $q$로 변환할 때, 토큰 생성의 평균 조건부 엔트로피(Entropy) $H(q \mid x)$가 임계치 $\tau_{\text{ent}}$를 초과하거나 필수 인자(Required Slot)가 누락되면 실패로 판정한다.

$$H(q \mid x) = -\frac{1}{\vert{}q\vert{}} \sum_{t=1}^{\vert{}q\vert{}} \sum_{v \in V} P_{\theta}(q_t = v \mid q_{\lt t}, x) \log P_{\theta}(q_t = v \mid q_{\lt t}, x) \gt \tau_{\text{ent}}$$


2. **논리 존재 게이트 ($\mathcal{G}_{\text{retrieve}}$ — "적용할 논리가 있는가?"):**
변환된 쿼리 $q$로 경험적 논리집 $\mathcal{K}$를 검색했을 때, 전제 조건 $P_i$가 일치하고 예외 조건 $\mathcal{R}_i$에 저촉되지 않으면서 신뢰도 $\omega_i \ge \tau_{\text{conf}}$를 만족하는 논리 블록이 존재하지 않으면 실패로 판정한다.
3. **정합성 검증 게이트 ($\mathcal{G}_{\text{verify}}$ — "논리 연결에 모순이 없는가?"):**
Lean의 타입 체커(Type Checker)와 유사하게, 복합 과제를 위해 여러 논리 블록 $L_a \rightarrow L_b$를 연결할 때 선행 논리의 결론 $C_a$가 후행 논리의 전제 $P_b$를 함의($C_a \vdash P_b$)하지 못하면 문법 오류(Logic Type Error)를 발생시킨다.

위 세 게이트 중 하나라도 실패($\mathcal{G}_{\text{parse}} \land \mathcal{G}_{\text{retrieve}} \land \mathcal{G}_{\text{verify}} = \text{False}$)하면, 로컬 AI는 즉시 추론을 중단하고 상용 LLM($\mathcal{M}_{\text{cloud}}$)을 소환한다.

### 3.2 상용 LLM의 역방향 도구 호출 (Reverse Tool-Calling)

소환된 상용 LLM은 단순히 텍스트 답변만 내놓는 것이 아니라, **로컬 AI의 기호 논리 엔진($\mathcal{E}_{\text{sym}}$)을 자신의 도구(Function Tool)로 삼아 조작**한다. 상용 LLM에게 제공되는 핵심 도구 인터페이스는 다음과 같다.

| 도구 함수명 (Tool API) | 입력 파라미터 | 작동 역할 및 목적 |
| --- | --- | --- |
| `inspect_parse_failure` | `raw_input`, `local_attempt` | 로컬 sLLM이 왜 사용자의 말귀($x$)를 해석하지 못했는지 오류 로그를 조회함 |
| `query_logic_graph` | `premise_type`, `goal_type` | 로컬 논리집($\mathcal{K}$)에 현재 존재하는 논리 블록과 비어 있는 추론 간극(Gap)을 탐색함 |
| `verify_candidate_chain` | `logic_chain_spec` | 상용 LLM이 새로 고안한 논리 구조가 로컬 문법 검증기($\mathcal{V}$)를 통과하는지 사전 테스트함 |
| `commit_logic_and_ alignment` | `natural_utterance`, `formal_query`, `new_logic_block` | 검증이 완료된 **새로운 논리 블록($L_{\text{new}}$)**과 **‘자연어 표현 ↔ 정형 쿼리’ 번역 쌍**을 로컬 DB에 영구 기록함 |

---

## 4. 로컬 AI의 3단계 자기 진화형 학습 구조 (Self-Evolving Learning Pipeline)

상용 LLM이 `commit_logic_and_alignment` 도구를 호출하여 로컬 시스템에 기록을 남기면, 로컬 AI는 다음 **3단계의 시간차 학습 메커니즘**을 통해 이 지식을 자신의 것으로 흡수한다.

### 4.1 [Stage 1] 무지연 즉시 학습: 의미론적 파싱 캐시 및 논리집 확장 (In-Context Memory Update)

신경망 가중치를 업데이트하기 전에도 로컬 AI는 즉각적인 성능 향상을 얻는다. 상용 LLM이 기록하고 간 데이터는 두 개의 저장소에 즉시 인덱싱된다.

1. **논리집($\mathcal{K}$) 확장:** 새로 추론된 논리 블록 $L_{\text{new}}$가 그래프에 추가되어, 이후 동일한 구조의 문제는 로컬 엔진 단독으로 해결 가능해진다.
2. **말귀 번역 캐시($\mathcal{D}_{\text{cache}}$) 등록:** 로컬 sLLM이 해석에 실패했던 자연어 입력 $x$와 상용 LLM이 교정한 정형 쿼리 $q^*$의 쌍 $(x, q^*)$가 벡터 데이터베이스에 저장된다. 이후 유사한 구어체나 도메인 은어가 입력되면, 로컬 sLLM은 $\mathcal{D}_{\text{cache}}$에서 가장 유사한 상위 $k$개의 번역 사례를 동적 퓨샷(Dynamic Few-shot) 프롬프트로 참조하여 즉시 말귀를 알아듣는다.

### 4.2 [Stage 2] 주기적 신경망 학습: 수면 단계(Sleep-Phase) QLoRA 지식 증류

Stage 1의 번역 캐시와 도구 호출 기록이 일정 임계치(예: $N_{\text{batch}} = 200$건) 이상 쌓이면, 로컬 시스템의 유휴 시간(야간 등)에 로컬 sLLM($\mathcal{M}_{\text{local}}$)의 신경망 가중치 자체를 미세조정(Fine-tuning)한다.

이 과정의 핵심은 로컬 sLLM에게 세상의 모든 지식을 외우게 하는 것이 아니라, 오직 “사용자의 모호한 자연어를 정형 논리 쿼리로 번역(Parsing)하고 로컬 논리집 도구를 호출하는 법”만 집중적으로 증류(Distillation)한다는 점이다. 학습 데이터셋 $\mathcal{D}_{\text{SFT}} = {(x_i, q^*_i, \mathcal{T}^*_i)}$에 대한 로컬 모델 파라미터 $\theta$와 저랭크 어댑터(LoRA) 가중치 $\Delta \theta$의 목적 함수는 다음과 같다.

$$\mathcal{L}_{\text{SFT}}(\Delta \theta) = -\mathbb{E}_{(x, q^*, \mathcal{T}^*) \sim \mathcal{D}_{\text{SFT}}} \left[ \sum_{t=1}^{\vert{}z^*\vert{}} \log P_{\theta + \Delta \theta} \big( z^*_t \mid z^*_{\lt t}, x \big) \right]$$

여기서 $z^* = [q^*; \mathcal{T}^*]$는 상용 LLM이 시범을 보인 ‘정확한 의도 번역 및 논리 블록 선택 시퀀스’이다. 이 학습이 반복될수록 로컬 sLLM은 외부 캐시 힌트 없이도 사용자의 개인화된 화법과 복잡한 도메인 요구사항을 즉각 논리 기호로 변환할 수 있게 된다.

### 4.3 [Stage 3] 경험적 귀납 학습: 성공/실패 복기 기반의 베이지안 갱신 및 DPO

실세계 프로젝트가 종료된 후 얻어지는 **성공($S=1$) 또는 실패($S=0$) 피드백**은 본 아키텍처를 단순한 연역 시스템에서 ‘경험적 진화 시스템’으로 탈바꿈시키는 핵심 동력이다.

#### (1) 논리 신뢰도($\omega_i$)의 베이지안 업데이트 및 예외 조건($\mathcal{R}_i$) 패치

각 논리 블록 $L_i$의 성공 확률을 베타 분포 $\text{Beta}(\alpha_i, \beta_i)$로 모델링한다(초기값 $\alpha_i=1, \beta_i=1$). 프로젝트에 사용된 논리 $L_i$가 성공하면 $\alpha_i \leftarrow \alpha_i + 1$, 실패하면 $\beta_i \leftarrow \beta_i + 1$로 갱신하며, 경험적 신뢰도 $\omega_i$는 사후 기대값으로 정의된다.

$$\omega_i = \frac{\alpha_i}{\alpha_i + \beta_i}$$

특히 **실패($S=0$)가 발생한 경우**, 시스템은 상용 LLM($\mathcal{M}_{\text{cloud}}$)을 ‘사후 부검관(Post-mortem Analyzer)’으로 소환한다. 상용 LLM은 성공했던 과거 프로젝트와 이번 실패 프로젝트의 컨텍스트 차이를 대조(Contrastive Analysis)하여 실패를 유발한 결정적 환경 변수를 추출하고, 이를 기존 논리 $L_i$의 반박/예외 조건 집합에 패치($\mathcal{R}_i \leftarrow \mathcal{R}_i \cup \{r_{\text{new}}\}$)한다.

#### (2) 직접 선호도 최적화(DPO)를 통한 실전적 논리 선택 학습

동일한 전제 $P$에 대해 문법적으로는 모두 유효하지만 프로젝트 성공으로 이어진 논리 경로 $\mathcal{T}_w$(Winner)와 실패로 이어진 논리 경로 $\mathcal{T}_l$(Loser)이 누적되면, 로컬 sLLM이 현실 세계에서 성공 확률이 높은 논리를 우선적으로 선택하도록 DPO(Direct Preference Optimization) 손실 함수를 적용하여 미세조정한다.

$$\mathcal{L}_{\text{DPO}}(\theta_{\text{local}}; \theta_{\text{ref}}) = -\mathbb{E}_{(x, \mathcal{T}_w, \mathcal{T}_l)} \left[ \log \sigma \left( \beta \log \frac{P_{\theta_{\text{local}}}(\mathcal{T}_w \mid x)}{P_{\theta_{\text{ref}}}(\mathcal{T}_w \mid x)} - \beta \log \frac{P_{\theta_{\text{local}}}(\mathcal{T}_l \mid x)}{P_{\theta_{\text{ref}}}(\mathcal{T}_l \mid x)} \right) \right]$$

이를 통해 로컬 AI는 단순한 문법 검사기를 넘어, **“이론적으로는 맞지만 현실에서는 자주 실패하는 논리”를 스스로 회피하는 실전적 직관**을 획득한다.

---

## 5. 이론적 효율성 분석: 토큰 소모량의 점근적 수렴

과제 수행 횟수를 $t = 1, 2, \dots, N$이라 하자. 순수 상용 LLM을 사용할 때 매 과제당 소모되는 평균 추론(CoT) 토큰 비용을 $C_{\text{cloud}}$라 하면, 누적 비용은 $\text{Cost}_{\text{pure}}(N) = N \cdot C_{\text{cloud}}$로 선형 발산($\mathcal{O}(N)$)한다.

반면 SELA 아키텍처에서 $t$번째 과제가 로컬 AI의 3중 게이트를 통과하지 못해 상용 LLM을 소환할 확률(Escalation Probability)을 $p_e(t)$라 하자. 매 에스컬레이션마다 새로운 논리가 $\mathcal{K}$에 등록되고 Stage 2 학습을 통해 로컬 모델의 파싱 커버리지가 넓어지므로, 도메인 내 유효 논리 패턴의 총 개수가 유한($M$)하다면 $p_e(t)$는 지수적으로 감소한다($p_e(t) \approx p_0 e^{-\lambda t}$). 따라서 SELA의 기대 누적 상용 토큰 비용은 다음과 같이 상수 한계로 수렴한다.

$$\mathbb{E}[\text{Cost}_{\text{SELA}}(N)] = \sum_{t=1}^{N} p_e(t) \cdot C_{\text{compile}} \approx C_{\text{compile}} \sum_{t=1}^{N} p_0 e^{-\lambda t} \xrightarrow{N \to \infty} \frac{p_0 C_{\text{compile}}}{1 - e^{-\lambda}} = \mathcal{O}(1)$$

여기서 $C_{\text{compile}}$은 상용 LLM이 로컬 도구를 호출해 논리를 작성하는 1회 비용이다. 즉, 초기에는 논리집 구축을 위한 투자 비용이 발생하지만, **작업이 누적될수록 한계 토큰 비용(Marginal Token Cost)은 $0$으로 수렴**한다.

---

## 6. 실험 설계 및 검증 프로토타입 제안 (Evaluation Protocol)

본 논문의 아키텍처를 실제 로컬 환경에서 구현하고 성능을 입증하기 위한 표준 실험 설계는 다음과 같다.

1. **시스템 구성 (Implementation Stack):**
* **로컬 통역기 ($\mathcal{M}_{\text{local}}$):** `Qwen-2.5-7B-Instruct` 또는 `Llama-3.1-8B-Instruct` (로컬 단일 GPU 구동, Unsloth 기반 야간 QLoRA 학습 파이프라인 연결).
* **기호 논리 엔진 ($\mathcal{E}_{\text{sym}}$):** JSON Schema 기반의 툴민 그래프 저장소(NetworkX / Neo4j) + Python 기반 전제-결론 타입 체커 + `Outlines` 라이브러리를 활용한 문법 제약 디코더.
* **상용 교사 모델 ($\mathcal{M}_{\text{cloud}}$):** 고성능 추론 모델 API (Function Calling 활성화).


2. **검증용 타겟 도메인:**
* **도메인 A (연역·규칙 중심):** 소프트웨어 레거시 코드 리팩토링 및 버그 수정 프로젝트.
* **도메인 B (비연역·경험 중심):** 비즈니스 기획안 리스크 검토 또는 재무/계약서 독소 조항 분석.


3. **핵심 평가 지표 (Metrics):**
* **논리적 환각 발생률 (Logical Fallacy Rate):** 전제에서 결론으로 이어지는 과정 중 전건 부정, 후건 긍정, 예외 조건 무시 등 논리 규칙 위반 비율(%).
* **상용 API 에스컬레이션 감소율 (Escalation Decay Curve):** 에피소드 진행(1회~500회)에 따른 상용 LLM 소환 빈도 변화.
* **과제당 유효 토큰 압축률 (Token Compression Ratio):** 동일 정확도 달성 시 순수 상용 추론 모델(CoT) 대비 소모된 총 토큰 수 비율.



---

## 7. 한계점 및 향후 과제 (Limitations & Future Work)

본 아키텍처가 실세계에서 완벽히 작동하기 위해 해결해야 할 두 가지 후속 연구 과제가 존재한다.

* **초기 오염된 논리의 전파 (Garbage-in, Logic-out):** 만약 상용 LLM($\mathcal{M}_{\text{cloud}}$)마저 초기 추론에 실패하여 잘못된 인과관계를 로컬 논리집($\mathcal{K}$)에 등록할 경우, 로컬 AI가 그 오류를 그대로 학습할 위험이 있다. 이를 방지하기 위해 새로 등록된 논리는 일정 횟수($k$회) 이상 실전 성공을 거두기 전까지는 ‘임시 논리(Probationary Logic)’ 상태로 격리하는 샌드박스 메커니즘이 필요하다.
* **논리집 비대화에 따른 규칙 간 충돌 (Rule Contradiction):** 경험이 장기 축적됨에 따라 동일한 전제 $P$에 대해 서로 상반된 결론 $C_1, C_2$를 지시하는 두 논리가 공존할 수 있다. 이를 해결하기 위해 주기적으로 상용 LLM이 전체 논리 그래프를 순회하며 중복 논리를 병합하고 상충 논리의 우선순위를 재정립하는 **‘메타 논리 가비지 컬렉션(Meta-Logic Garbage Collection)’** 프로세스가 요구된다.

---

## 8. 결론 (Conclusion)

본 논문에서 제안한 **SELA**는 대형 언어 모델의 고질적인 문제인 환각과 토큰 비효율성을 해결하기 위해, 정형 검증기(Lean)의 엄밀함과 실세계 경험 법칙의 유연함을 결합한 신경-기호 아키텍처이다. 특히 로컬 소형 LLM을 기본 실행기로 두되, 해석 불가능한 난제 앞에서만 상용 대형 LLM을 소환하여 로컬 시스템을 도구로 조작·기록하게 하고, 이를 3단계(캐시 확장 – 야간 QLoRA – 성공/실패 DPO)에 걸쳐 로컬 AI가 흡수하도록 설계함으로써 **“상용 AI를 사용할수록 내 로컬 AI가 진화하여 궁극적으로 독립하는”** 지속 가능하고 경제적인 AI 발전 모델을 제시한다.
