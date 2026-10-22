# 2026-10-22 — 조사: 연구 근거 — 왕초보의 어휘·문자 습득에 무엇이 통하나

에이전트: 조사 작업자 (Haiku 5.5, high). 하위 에이전트 호출: 없음.
커밋·push: 안 함.

## 한 일
- 보고서 작성: `out/research/2026-10-22-language-learning/research_evidence.md` (318줄). 후보 12개 (간격, 인출, 학습법 리뷰, 방향, 섞기, 기억술, 손 쓰기, 따라 말하기, 예문 대 목록, 묶음 크기, 피드백·자기 판단, 앱 사례), 탈락 후보, 각도 요약, 조사 범위 돌아보기 절을 포함.
- 이 작업 보고서 작성.
- 저장소의 다른 파일은 건드리지 않았다.

## 확인한 것 (어떻게)
- WebSearch 25회 (standard 모드). 검색 결과에 실린 제목, DOI, 학술지 서지, 초록 요약을 근거로 썼다.
- WebFetch 열기 시도 9회.
  - 열림: en.wikipedia.org/wiki/Spaced_repetition, en.wikipedia.org/wiki/Testing_effect (원문 확인 가능한 것은 이 두 쪽뿐).
  - 404: en.wikipedia.org/wiki/Keyword_method, en.wikipedia.org/wiki/Interleaved_practice (문서 이름이 다를 수 있음, 재시도 안 함).
  - 호스트 이름 해석 실패 (ENOTFOUND): evullab.org, courseware.epfl.ch, brucehayes.org, kansai-u.repo.nii.ac.jp, psychologicalscience.org. 각 한 번씩 시도.
- curl 연결 확인 (HTTPS 프록시 경유, 호스트마다 1회):
  - 403 (CONNECT 거부, 프록시 상태 조회에서 정책 차단으로 기록): doi.org, pubmed.ncbi.nlm.nih.gov, ncbi.nlm.nih.gov, europepmc.org, scholar.google.com, semanticscholar.org (www와 api 모두), journals.sagepub.com, link.springer.com, tandfonline.com, onlinelibrary.wiley.com, cambridge.org, eric.ed.gov, researchgate.net, dx.doi.org.
  - 열림: en.wikipedia.org (301 응답).
  - 프록시 상태 조회 결과에 한국 포털과 일부 블로그 도메인이 403으로 기록되어 있었다. 우회하지 않았다.
- 프록시 README (`/root/.ccr/README.md`)의 지침대로 403 정책 차단은 재시도하거나 우회하지 않고 보고만 했다.

## 확인 못 한 것
- 원문 논문 대부분: Cepeda 2006, Rowland 2014, Karpicke & Roediger 2008, Karpicke & Bauernschmidt 2011, Nakata 2015 (SSLA), Kim & Webb 2022, Latimier 2021, Brunmair & Richter 2019, Webb 2005·2007, Kroll & Stewart 1994, Lee 2021, Butler 2008, Kulik & Kulik 1988, Dunlosky 2013, Thomson & Derwing 2015, Atkinson & Raugh 1975. 모두 검색 요약 또는 2차 인용으로만 확인.
- 효과 크기: 대부분 검색 요약 기준 (Cepeda 편수, Rowland g=0.50, Brunmair g=0.42, Latimier g=0.74). Kim & Webb 2022의 효과 크기는 찾지 못함.
- DOI: Karpicke & Roediger 2008, Nakata 2015, Kroll & Stewart 1994, Nelson & Dunlosky 1991의 DOI는 확인 못 함. 위키 인용 목록의 DOI는 "위키 인용 목록 기준"으로 표시.
- 어휘·왕초보 전용 메타분석: 외국어 키워드 기법, 확장 간격 대 고정 간격 (어휘), 섞기 (어휘), 세션당 단어 수에 대한 메타분석은 찾지 못함.
- 국내 연구 (한국어 화자 대상, KCI 학술지), 가나 쓰기 연구는 검색하지 않음.
- Lee 2021 ERIC 주소가 같은 논문인지, 일본 대학 한자 연구 (nufs 저장소) 제목은 확인 못 함.

## 알려진 문제
- 보고서의 "근거 강도"와 "확신도"는 대부분 검색 요약 기반이다. 인용하기 전에 원문으로 재확인해야 한다. 보고서 0절에 명시.
- Brunmair & Richter 2019 주소는 수용본 (accepted manuscript)이다. 최종본과 다를 수 있다.
- 블로그·벤더 자료가 일부 근거처럼 섞일 수 있으므로 "개인 후기" 또는 "기사"로 분류하고, 근거 강도 계산에는 넣지 않았다.
- Kulik & Kulik 1988의 연구 형식 (메타분석 여부)은 검색 요약에서 확인하지 못해 "확인 못 함"으로 표시.
- 보고서의 "현재 앱 스케줄 (1일→1일→4일)" 관련 해석은 추정으로 표시했다.

## 다음 작업자에게
- 원문 접근이 되는 환경이면 다음 순서로 확인: (1) Cepeda 2006과 Rowland 2014의 효과 크기 표, (2) Nakata 2015 SSLA 원문 (확장 간격 대 고정 간격, 어휘), (3) Kim & Webb 2022 효과 크기, (4) Brunmair & Richter 2019 최종본 (어휘·그림 조건 분리), (5) Webb 2005·2007 원문 (수용 대 생산, 반복 횟수), (6) Atkinson & Raugh 1975 원문.
- 찾지 못한 것: 외국어 키워드 기법 메타분석, 세션당 새 단어 수 실험, 가나 쓰기 실험. 검색어를 바꿔 보고 (Pigott, Mastropieri 등 키워드 연구 저자명, "number of words per session" 등) 다시 조사할 가치가 있다.
- 우리 앱 설계 적용: 후보 1 (간격), 후보 2 (떠올려 보기), 후보 11 (정답 즉시 표시 후 재판단)이 근거가 가장 두텁다. 후보 6 (키워드·연상), 후보 7 (손 쓰기), 후보 8 (따라 말하기)는 근거가 약해 설계 결정의 1차 근거로 쓰지 않는 것이 좋다.
- 한국어 화자 대상 국내 연구와 일본어 학습자 대상 연구 (JLPT 준비 등)는 아직 확인하지 않았다.

## 이어서: 원문 확인
같은 날 사용자가 환경의 허용 도메인을 넓혀서, 메인 지시로 보고서의 출처를 원문으로 확인하고 제자리에서 고쳤다. 모델·effort 동일(Haiku 5.5, high). 하위 에이전트 없음. 커밋·push 안 함.

### 어떻게
- WebFetch 도구는 프록시를 타지 않아 모두 ENOTFOUND로 실패했다. 대신 Bash의 curl(HTTPS_PROXY 경유)로 내려받고 `pdftotext -layout`과 간단한 HTML 태그 제거로 읽었다.
- 초록 경로: PubMed E-utilities(esearch/efetch), ERIC API(api.ies.ed.gov, 초록 포함), Crossref API(일부 초록 포함), Semantic Scholar API(DOI 조회만 됨, 검색은 429).
- 각 주소는 최대 2회 시도. 403은 프록시 README 지침대로 재시도·우회하지 않고 "사이트 거부"로 적었다.

### 원문 확인 수: 26편 (전문 9, 공식 초록 17)
- 전문: Cepeda 2006, Rowland 2014, Karpicke & Roediger 2008, Dunlosky 2013, Nakata 2018, Lee 2021, Fitzpatrick 2008, Serfaty & Serrano 2024, Kim 외 2026.
- 초록: Latimier 2021, Karpicke & Bauernschmidt 2011, Nakata 2015, Brunmair & Richter 2019, Webb 2005, Webb 2007, Webb 2008, Atkinson & Raugh 1975, Butler 2008, Kulik & Kulik 1988, Nelson & Dunlosky 1991, Thomson & Derwing 2015, Nakata 2013 학위논문 요약, Yang 2021, Adesope 2017, Smith 2024, Astarilla 2019.
- 보고서 안 표시: "[원문 확인]" 71곳, "[원문에 없음]" 5곳.

### 바뀐 수치·판정 (15건)
1. 후보 5 섞어 배우기: 단어 자료에서는 몰아 배우기가 유리(g=−0.39, Brunmair & Richter 2019 초록). 적용 판정 "일부"→"아니오(단어 목록)". 각도 요약 상위 3에서 제외. 가장 큰 변화.
2. 후보 1 확장 대 고정: "엇갈림"→"차이 없음"(Latimier g=0.034 유의하지 않음; Cepeda 62.0% 대 58.6%, p=.61; Karpicke 2011 차이 없음; Nakata 2015 이득은 수용 시험만, 저자 스스로 실질적 의미 없음). 근거 강도 중→강, 확신도 중간→높음.
3. 후보 1: 1차 때 탈락시킨 Karpicke 2011 "200%"가 초록에 있어 후보로 복귀.
4. 후보 1: Cepeda 수치 추가(47.3% 대 36.7%, 271건·14,811명; 최적 간격은 보유 기간에 비례), Cepeda 2008의 10–20% 규칙(Dunlosky 본문 인용). Nakata 2015 "226명"은 [원문에 없음], 128명 확정.
5. 후보 1: Serfaty & Serrano 2024 추가(앱·초보·96명, 1주 간격 > 1일 간격, 승산비 1.6).
6. 후보 2: g=0.50 [0.42, 0.58], 피드백 0.73 대 0.39, 보유 기간 1일 이상 0.69, 초기 인출 50% 이하·무피드백 g=0.03 조건 추가. Karpicke 2008 80% 대 36%·33%, 예측 약 50% 확정. Yang 2021(g=0.499, 222편) 추가.
7. 후보 3: 표 4 등급 확정. 키워드 기억술 "낮음" 등급과 그 이유 확정.
8. 후보 4: Webb 2005의 "수용>생산, 저빈도에서 격차 큼" 주장은 [원문에 없음]. 실제 결과는 읽기 과제 대 쓰기 과제(시간 같으면 읽기, 시간 충분하면 쓰기 우세). 근거를 Nakata 2013 Study 2·Serfaty 2024·Fitzpatrick 2008로 재구성.
9. 후보 6: Atkinson & Raugh 72% 대 46% 확정(ERIC 저자 초록). Dunlosky "낮음" 등급 반영. 확신도 낮음→중간(단기)/낮음(장기).
10. 후보 7: Lee 2021은 종이 대 태블릿(둘 다 손 쓰기) 비교. "보기만 한 쪽보다"는 [원문에 없음]. η²=.15–.20, 지연 시험 24시간 추가.
11. 후보 9: Webb 2007은 반복 횟수(1·3·7·10회) 연구이지 목록 대 문맥 비교가 아님 [원문에 없음]. Webb 2008 문맥 질 결과 추가. 근거 강도 약→중.
12. 후보 10: Fitzpatrick 수치 추가(하루 15개·20일, 283→191→135→149, 후반 단어 1/3 유지). 근거 강도 약→중.
13. 후보 11: Kulik 1988이 53편 메타분석임을 확정, Nelson 1991 초록 확정, Rowland 지연 피드백 g=1.38(k=6), Nakata 2013 지연 피드백 무차이 추가. 근거 강도 중→강.
14. 후보 12: Kim 외 2026 SSLA 48(3) 확정(n=58/65/60, 16주, 세 집단 비슷), Astarilla 무작위 30/30 확정, Smith 2024 무대조군 확정.
15. 각도 요약 상위 3: 후보 2·1·11로 변경.

### 새 후보 수: 1
- 후보 13 "한 항목을 몇 번 다시 만나야 하나" — Webb 2007(10회), Nakata 2013(인출 5회, 4주 유지), Latimier 2021(횟수 많을수록 확장 유리), Fitzpatrick 2008.

### 못 연 곳
- 사이트 거부(403): onlinelibrary.wiley.com(Kim & Webb 2022 효과 크기), journals.sagepub.com, academic.oup.com(Webb 2007·Thomson & Derwing 전문), sciencedirect.com(Kroll & Stewart 1994), psycnet.apa.org, tandfonline.com, researchgate.net.
- 연결 끊김 2회: cogpsy.educ.kyoto-u.ac.jp(교토대 한자 연상 연구).
- 속도 제한 429: Semantic Scholar 검색 API. DNS 실패: eric.ed.gov 본사이트(API는 됨), ifp.nyu.edu. 502: Nakata 개인 사이트.
- 그래서 여전히 "검색 요약만"인 출처: Kim & Webb 2022, Kroll & Stewart 1994, 교토대 연구, 중국·일본 손 쓰기 연구 2편, 쉐도잉 연구 3편, Waisman 기사, Weaver & Kelemen 1997, 소규모 EFL 목록 연구.

### 확인한 것 (명령)
- `curl -sS -m 20 -o /dev/null -w "%{http_code}" -L <주소>`로 호스트 32곳 확인 → 위 열림/거부 목록.
- `pdftotext -layout <pdf> <txt>` 뒤 `grep -n`으로 수치 줄 확인(Rowland 표의 g 값, Cepeda 표 1·8, Dunlosky 표 4, Lee 표 1).
- 보고서 검사: `wc -l` 341줄, `grep -c "^## 후보"` 13, `grep -c "\[원문 확인\]"` 71, 개인정보 문자열(@, 이메일) 없음.

### 알려진 문제
- Brunmair & Richter 2019는 출판 초록만 확인했다(전문 PDF 주소는 503). 단어 자료 g=−0.39의 세부 조건(어떤 단어 과제인지)은 전문에서 확인해야 한다.
- Nakata 2015 세부(수용 시험 이득의 효과 크기 값)는 저자의 2018 리뷰 서술로 확인했고 2015 원문 표는 보지 못했다.
- Kim 외 2026은 2026년 7월호로, 메인이 "최신 연구"로 다룰 때 출판 시점을 밝힐 것.

### 다음 작업자에게
- 설계 근거로 바로 쓸 수 있는 것: 후보 1(간격, 10–20% 규칙), 후보 2(떠올리기+즉시 정답), 후보 11(피드백), 후보 13(완료 기준 횟수). 후보 5는 "단어 카드는 섞지 않는다"로 방향이 바뀌었으니 1차 보고서를 읽은 사람은 주의.
- Wiley가 열리는 환경이면 Kim & Webb 2022 효과 크기를 먼저 받아 후보 1에 넣는다.
