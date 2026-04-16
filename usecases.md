# Harness Use Cases

하네스를 실제로 쓴 기록. 글 쓸 때 사례로 활용.

| 날짜 | 태스크 | 유형 | 결과 | 체인 | 인사이트 |
|------|--------|------|------|------|----------|
| 2026-04-03 | evan-harness 구조 리뷰 | PM | PASS (7/7 기준 충족) | 0 | 도구 제한 불일치·경로 패턴 혼재·미참조 자원 등 12건 발견. 요약 숫자 오류 등 경미한 concern 3건 |
| 2026-04-05 | /insta 커맨드 생성 — 세션→인스타 콘텐츠 변환 | Coding | PASS | 0 | 커맨드 프롬프트에 few-shot 예시 포함하면 출력 일관성 확보 가능 |
| 2026-04-06 | 디렉토리 파일 뷰어 | Coding | PASS (9/9) | 0 | 단일 Python 파일 602줄. marked.js+highlight.js CDN으로 마크다운/코드 렌더링. Reviewer가 실제 서버 실행+curl 테스트까지 수행 |
| 2026-04-06 | MD 파일 뷰어 | Coding | PASS (9/9, 재검증 1회) | 0 | viewer.py 스타일 재활용. TOC+라이브리로드+진행률바. 미사용 import 1건으로 FAIL→수정→PASS |
| 2026-04-06 | /view 커맨드 통합 | Coding | PASS (6/6) | 0 | 기존 디렉토리 전용 /view를 파일+디렉토리 통합으로 확장. view.md + plugin.json 2파일만 수정 |
| 2026-04-13 | 퍼스널 브랜딩 리서치 + 시작 플랜 | PM | PASS (10/10) | 0 | 기존 플레이북의 원칙 위에 실행 레이어(플랫폼/니치/3개월 캘린더/첫 포스트 5개) 스택. 니치 5개 4축 비교 → "AI-native PM × 지침서 AX" 확정. 디스콰이엇 2025-12 종료 발견이 LinkedIn KR primary 선택의 결정적 근거 |
| 2026-04-14 | card-news 스킬 생성 — 주제 기반 인터랙티브 카드뉴스 (10개 공식) | Coding | PASS | 0 | 추천 매트릭스(목적×소재→공식)를 표로 정리하면 AI가 일관되게 추천 |
| 2026-04-14 | 300만원 주식 배치 계획 (NAVER 매도 대금) | Trading | PASS (10/10, Fix 1회) | 0 | 전쟁주 제외 + 한국 비반도체/비자동차 제외 제약 하 STZ/NVO/CEG/IAU 4종목 분산. 4월 말 실적시즌 필터로 V/MA/LLY/BRK.B 희생, LLY→NVO 대체. 1회 Fix는 reviewer가 잡은 수치 오류 4건(반도체 비중 50.9%→62.5%, IAU 가격 3중표기, 합계 484원, 한국 비중 43%→50.6%). 종목 선정 자체는 1차에 통과 |
| 2026-04-14 | 5종목 심층 분석 (MSFT/ORCL/STZ/LULU/CEG) | Trading | PASS (10/10) | 0 | 각 종목 11섹션 구조로 통일. ORCL AVOID(falling knife)/LULU HOLD(PFAS+EPS)/STZ·CEG BUY 유지, MSFT BUY 신규 추가(실적 후 5/1 진입 룰). 이전 300man-allocation-plan의 STZ/CEG 결론 재검증 일치. NVO/IAU는 본 범위 밖이라 별도 유지. "MS"→Microsoft 해석 서두 명시. Reviewer concern: STZ 수량 검산, Fwd P/E 출처 2건만 명시 |
| 2026-04-15 | persona-review 플러그인 구축 | Coding | PASS (10/10) | 0 | 산출물 타입 감지→3~5 페르소나 동적 생성(casting-director)→Task 병렬 리뷰(persona-reviewer)→공통/상충/P0·P1·P2 통합(synthesizer) 파이프라인. 3 command(review/panel/apply)+3 agent+1 skill(refs 2개). apply는 승인 게이트+Before/After diff. local-marketplace 등록. Reviewer concern: plugin.json의 commands/agents 배열이 디렉토리 디스커버리와 중복될 수 있음, /panel 재사용 플로우 Step 1 미구현 |
| 2026-04-16 | 5종목 매수 각도 분석 (STZ/CEG/PLTR/ORCL/UNH) | Trading | PASS (10/10) | 0 | STZ BUY(즉시 4주)/CEG BUY(분할 2주)/PLTR AVOID(전쟁주+Fwd PE 102)/ORCL AVOID(falling knife)/UNH HOLD(Medicare +2.48% 확정→9주 유지, 4/21 실적 후 재판단). UNH "5주 매도→9주 유지" 변경이 sell-conditions "+2%→유지" 조건과 정확 매칭. 300만원 중 190만원 즉시(STZ+CEG), 잔여 113만원 대기 |
| 2026-04-16 | moodboard 디자인 컨셉 플러그인 구축 | Coding | PASS (10/10) | 0 | /moodboard로 제품 설명 입력→trend-researcher(WebSearch/WebFetch 실시간 리서치)→concept-designer(3가지 축 차별화 무드보드 생성) 파이프라인. 2 command(moodboard/save)+2 agent+1 skill(refs 2개: output-template+design-vocabulary 7축). /moodboard-save로 선택 컨셉 저장. persona-review 패턴 재사용(에이전트 본문 반환→orchestrator 파일 저장). marketplace "design" 카테고리로 등록 |
| 2026-04-16 | private 레포 README.md 생성 | PM | PASS (7/7, Fix 1회) | 0 | 레포 구조 파악→디렉토리 트리+역할 테이블+도구 스택 한글 README 생성. 1차 FAIL: gitignore 대상 유틸리티 스크립트(viewer.py 등) 누락→추가 후 PASS. 개인정보 필터링 기준(C5) 별도 설정이 유효 |
| 2026-03-30 | 기능 사용 데이터 기반 Retention 아이디어 도출 | PM | FAIL→PASS (재검증) | 0 | #9 "오늘의 한 문제"가 기존 backlog와 중복→수정 후 재검증 PASS. agent_question D1 +2.6pp, 방문만 유저 44.6K 레버 발견 |
| 2026-03-31 | 콴다 앱 종합 성장 분석 v1 | PM | PASS | 0 | stickiness 3.6%(기존 ~15% 추정 대폭 수정), Chat D1 +6.4pp Aha Moment 후보 등 7개 신규 발견. BQ 실데이터 기반 8개 UX 문제점 식별 |
| 2026-03-31 | 콴다 앱 종합 성장 분석 v2 | PM | PASS | 0 | v1 대비 올바른 테이블(event_total_visit_user) 사용. DAU 77,835/MAU 554,442/Stickiness 14.0% 정정. agent_question D1 23.7%(+7.0pp) Aha Moment 정의 |
| 2026-03-31 | 콴다 앱 Growth 아이디어 10선 | PM | PASS | 0 | Retention 4/CAC 3.5/CVR 2.5 균형. 10개 모두 경쟁사 레퍼런스+BQ 데이터 근거. 기존 20개 백로그 비중복 확인 |
| 2026-03-31 | agent_question Epic 5개 작성 | PM | PASS | 0 | 구성 효과(composition effect) 논리로 D1/Retention 개선 추산. 할인 계수 30~50% 적용. 12주 실행 로드맵+시너지 맵 포함 |
| 2026-03-31 | 시험지 스캔 저CAC 유입 제품 Brief | PM | PASS | 0 | 5개 Acquisition 채널 설계(학부모/학생 바이럴, 무료 진단, SEO/ASO, B2B2C). Blended CAC $0.8-1.5. 한국 시장 특수성(시험 캘린더 8회, 카톡 오픈율 80-95%) 반영 |
| 2026-03-31 | 시험지 스캔 Brief v2 — 3관점 비판적 리뷰+재작성 | PM | PASS | 0 | PM/CPO/CMO 3관점 13개 이슈 식별. v1 652줄→v2 200줄(69% 압축). CAC 불일치($0.8-1.5 vs $0.13) 해소. K-factor 0.3→0.10-0.15 하향 |
| 2026-03-31 | 시험지 스캔 Paid 마케팅 테스트 Brief (v3) | PM | PASS | 0 | MVP 5개 Must-have만. Meta+Google UAC 2채널, 예산 1,500만원/2주. Go/Watch/Kill 기준(CPI $4/$4-6/$6+) 명시. 149줄 실행 중심 |
| 2026-03-31 | 콴다 앱 종합 성장 분석 (plan만) | PM | 미검증 | 0 | plan.md만 존재. 유저 데이터 종합+UX 문제점/wow point 식별+신규 성장 아이템 도출 계획 |
| 2026-03-31 | 복귀 유저 강제 웰컴 온보딩 Epic 초안 | PM | PASS | 0 | 방문만 유저 63,522명 중 복귀 32,076명(64.4%) 타겟. D7 47.9%→55%+ 목표. 4단계 솔루션(Welcome-back→카메라→미션→푸시). [TODO] 15개+ 정직 표기 |
| 2026-03-31 | 신규 유저 14일 내 CVR 2배 시뮬레이션 | Hybrid | PASS | 0 | BQ 데이터 추출+Python 시뮬레이션. 105행 전 행 계산 검증 0건 오류. KR cross-validation +-5% 이내. 비KR 리전 locale 매핑 불일치 원인 식별 |
| 2026-04-01 | 2Q 2026 에픽 임팩트 랭킹 | PM | PASS | 0 | 23개 에픽+3개 인프라 S/A/B/C Tier 분류. 4축 평가(2Q기여/데이터근거/효율성/시급성). selection bias 할인 30-50% 적용. 1Q A/B 실험 검증과 명시 구분 |
| 2026-04-01 | 에픽 임팩트 랭킹 템플릿 카드 작성 | PM | PASS | 0 | 26개 아이템 각 4줄(배경/가설/솔루션/임팩트). 정량 데이터 원본 일치. 모든 가설 "만약~한다면~할 것이다" 형식 통일 |
| 2026-04-01 | PM 피드백 리포트 | PM | 미검증 | 0 | Discovery Backlog 아이디어+Library DB Metric Review 교차 분석. plan.md+output.md 존재, review 미실시 |
| 2026-04-01 | SG 홈 개선 아이디어 5개 최종 정리 (plan만) | PM | 미검증 | 0 | plan.md만 존재. 경쟁사 앱 레퍼런스+콴다 BQ 실측+1Q A/B 실험 근거로 최종 정리 계획 |
| 2026-04-01 | SG 홈 화면 데이터 기반 UX 개선안 도출 | Hybrid | PASS | 0 | BQ에서 12개 컴포넌트 사용률 추출(91,373명). 7개 개선안 P0/P1/P2 정렬. 캐릭터 40% 면적/인터랙션 0% 기회비용 데이터 논증 |
| 2026-04-01 | 연구독 타임딜 D365 Premium LTV 기여도 산출 | PM | PASS | 0 | 업셀+윈백 2채널 분리 계산. Baseline 29.9원/목표 48.7원. Premium D365 갭(338) 대비 8.8-14.4% 커버. 전 수치 검산 일치 |
| 2026-04-02 | KR 단기 이탈 유저 복귀율 개선 아이디어 | PM | 미검증 | 0 | gap 1-2 이탈 풀 498K 대상. "앱을 열면 쓸만하지만 열 이유가 없어졌다" 진단. pre-open 단계 초점 아이디어 도출 |
| 2026-04-02 | WR 기여도 추정 비판적 리뷰 | PM | 미검증 | 0 | 리텐션 상승 아이템 WR 기여도 산술 정합성 검증. Timer/SG min 불일치(1.05 vs 1.1), Live Tutor min 불일치(0.3 vs 0) 발견 |
| 2026-04-02 | SG 홈 화면 개선 (빈 폴더) | PM | 미검증 | 0 | 폴더만 존재, 산출물 없음. sg-home-ux-improvement로 대체된 것으로 추정 |
| 2026-04-03 | QANDA KR CRM Framework 구축 | PM | 미검증 | 0 | CRM 5단계(신규/활성/이탈위험/이탈/복귀) 정의. 단계별 KPI+터치포인트 설계 |
| 2026-04-03 | 콴다 KR 복귀 유저 증대 아이디어 10선 | PM | 미검증 | 0 | 기존 PM 재점검 5개+신규 메커니즘 5개. gap 1 복귀율 21.8%(YoY -4.7%p) 기반 |
| 2026-04-03 | KR 단기 이탈 유저 복귀 아이디어 PM 재점검 | PM | 미검증 | 0 | 기존 11개 아이디어 교차 대조. Push 알림 4개 과다/F2 독립 불필요/D1+D3 통합 등 구조적 문제 식별 |
| 2026-04-03 | Notion SG/Timer/Social 리서치 정리 | PM | PASS | 0 | 9개 Notion 문서에서 데이터 추출. SG 기능 리텐션 18.67%, SG+쿼리0=39%, 4일 허들 등 이전 분석 빈칸 보충. Confirmed 아이템과 자체 분석 관계 정리 |
| 2026-04-03 | SG 홈 개선 아이디어 5개 최종 정리 | PM | PASS | 0 | 5개 모두 이중 근거(BQ 실측+경쟁사 레퍼런스). selection bias 할인 30-50% 명시. "진짜 될까?" 자기 검증 포함. 15개+ 수치 원본 대조 전수 일치 |
| 2026-04-03 | SG 홈 화면 개선안 PM 재점검 | PM | PASS | 0 | 7개→5개 재구조화. 신규/기존 유저별 D1/D[3,6]/W1 분리 추산. "SG 홈 개선만으로 M.Ret +3pp는 어렵다" 정직 평가. 9개 소스 교차 검증 |
| 2026-04-06 | Discovery Backlog CPO/PM 피드백 | PM | 미검증 | 0 | 기본 5개+추가 10개+프렌즈 분석+경쟁사 리서치+SG 이탈+Streak 리텐션 종합. 20년차 CPO+10년차 PM 관점 피드백 |
| 2026-04-13 | K-12 매출 Growth 제품 아이디어 모음집 | PM | PASS | 0 | 단기 S1-S25 25장+장기 L1-L5 5개. 9필드 완비. Pain A 24%(타이트). 한국 K-12 맥락 중심(내신/수행평가/학종/학원/맘카페) |
| 2026-04-13 | K-12 아이디어 모음집 v2 수정 | PM | PASS | 0 | 드랍 17장 제거→잔존 8장+신규 6장=14장 라인업. F8/F9 필터 추가. 모든 카드 실재 사례 검증, 환각 경쟁사명 0건 |
| 2026-04-13 | Notion 카드 토글 업데이트 페이로드 | Coding | 미검증 | 0 | Notion 테이블 toggle 업데이트용 payload.md 생성. 자동화 스크립트 페이로드 |
| 2026-04-13 | Notion Output 섹션 채우기 페이로드 | PM | 미검증 | 0 | "빠르게 시도해볼 수 있는 아이템들" Notion 페이지 업데이트용 payload 작성 |
| 2026-04-14 | 교육 AI OS 정의 3문답 피드백 | PM | PASS | 0 | Q1-Q3 각 Evan 요지/피드백/Assistant 견해 블록. OS=default 진입점+lock-in+메타레이어 프레임. Context ontology pulled vs pushed 구분. 결제자별 분해(학생=효율, 학부모=안심) |
| 2026-04-14 | 교육 AI OS "생각 정리" 노션 서브페이지 작성 | PM | 미검증 | 0 | 피드백 반영 후 3문답 통합 답변. spine 구조(학습 메타데이터 흡수) OS 정의. plan.md+notion_draft.md 존재 |
| 2026-04-15 | Education AI OS GTM/수익화 포지션 판단 | PM | 미검증 | 0 | "24시간 개인 선생님 케어" 포지션의 수익화 가능성 조건부 판단. 학원 대체재 전환 필요성 분석. plan.md+output.md 존재 |
| 2026-04-16 | Education AI OS 시장 소구 포인트 분석 v1 | PM | 미검증 | 0 | product-brief/prd/background/GTM 기반 소구 포인트 도출 |
| 2026-04-16 | Education AI OS 시장 소구 포인트 분석 v2 | PM | 미검증 | 0 | 학생/학부모 각 8개+ 포인트 확장. 페르소나 세분화, 학부모 결제 갈증 유형 분류. 타겟별 5축 스코어링 |
| 2026-04-16 | Education AI OS 소구 포인트 카피 v3 | PM | 미검증 | 0 | 13개 앱 카피 리서치 기반. 프로 6원칙+토스 8원칙 적용 실전 카피 재작성 |
