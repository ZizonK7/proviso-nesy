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
