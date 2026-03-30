# 튜닝 가이드: Output이 마음에 안 들 때

## 디시전 트리

```
Output이 마음에 안 든다
    │
    ├─ 계획 자체가 별로다 (방향이 틀림)
    │   → agents/planner.md 수정
    │   → 또는 /plan 후 criteria.json을 직접 편집
    │
    ├─ 계획은 맞는데 실행 품질이 낮다
    │   → agents/worker.md 수정
    │   → 또는 plan.md의 Steps를 더 구체적으로 편집
    │
    ├─ Reviewer가 너무 관대하다 (통과시키면 안 되는 걸 통과)
    │   → agents/reviewer.md의 Critical Mindset 강화
    │   → criteria.json의 기준을 더 구체적으로
    │
    ├─ Reviewer가 너무 엄격하다 (사소한 것에 FAIL)
    │   → agents/reviewer.md의 Decision Rules 완화
    │   → criteria.json에서 해당 기준 삭제/수정
    │
    └─ 특정 유형의 태스크에서 반복적으로 문제
        → skills/harness-workflow/references/ 에 패턴 추가
        → 해당 패턴을 에이전트가 참조하도록 연결
```

## 구체적 튜닝 포인트

### 1. 계획 품질이 낮을 때 → `agents/planner.md`

| 증상 | 원인 | 수정 위치 |
|------|------|----------|
| 계획이 너무 추상적 | Planner가 WHAT만 쓰고 구체성 부족 | `## Constraints` 섹션에 "각 Step은 30분 이내에 완료 가능한 크기로 분해" 추가 |
| 계획이 너무 상세 (과도한 명세) | HOW까지 지정하고 있음 | `## Constraints`의 "specify WHAT and WHY, not HOW" 강화 |
| 태스크 유형 감지 실패 | PM인데 코딩 모드로 동작 | `## Task Detection` 섹션에 키워드/패턴 추가 |
| Criteria가 모호 | "잘 작성되었는가" 같은 주관적 기준 | `## Constraints`에 "모든 criterion은 제3자가 10초 안에 PASS/FAIL 판단 가능해야 함" 추가 |

### 2. 실행 품질이 낮을 때 → `agents/worker.md` 또는 `plan.md`

| 증상 | 원인 | 수정 위치 |
|------|------|----------|
| 결과물이 얕다 | Worker가 최소한만 하고 넘어감 | `agents/worker.md`에 "각 섹션은 최소 3문장 이상" 같은 품질 기준 추가 |
| 범위를 벗어남 | 계획에 없는 것을 추가 | `agents/worker.md`의 Constraints 강화 (이미 있음) |
| 기존 패턴을 무시 | 컨벤션 파악 없이 구현 | `agents/worker.md`에 "구현 전 기존 코드를 최소 3개 파일 읽어서 패턴 파악" 추가 |
| 특정 부분만 반복적으로 약함 | 해당 영역에 대한 가이드 부재 | `references/pm-patterns.md` 또는 `references/coding-patterns.md`에 패턴 추가 |

**핵심**: Worker의 품질이 낮으면, Worker를 고치기 전에 **plan.md가 충분히 구체적인지** 먼저 확인. 계획이 모호하면 실행도 모호해짐.

### 3. 리뷰 기준이 안 맞을 때 → `agents/reviewer.md` 또는 `criteria.json`

| 증상 | 원인 | 수정 위치 |
|------|------|----------|
| 다 PASS인데 결과물이 별로 | Reviewer가 관대함 | `agents/reviewer.md`의 `## Critical Mindset`에 구체적 체크 항목 추가 |
| 사소한 이유로 FAIL | 기준이 과도함 | `criteria.json`에서 해당 criterion 삭제 또는 description 완화 |
| 핵심을 놓치고 지엽적인 것만 체크 | Reviewer의 우선순위 문제 | `agents/reviewer.md`에 "가장 중요한 criterion부터 검증" 지시 추가 |

### 4. 반복적 문제 → `references/` 패턴 추가

같은 유형의 태스크에서 같은 문제가 반복되면, 에이전트 프롬프트를 고치는 것보다 **레퍼런스에 패턴을 추가**하는 게 효과적.

```
예시: "PRD를 쓸 때마다 성공 메트릭이 빠진다"

→ references/pm-patterns.md의 "Epic/PRD 작성" 섹션에 추가:
  "성공 메트릭은 필수. 최소 3개, 각각 측정 방법과 목표 수치 포함."

→ agents/planner.md에서 pm-patterns.md를 참조하도록 연결
```

## 빠른 수정 vs 근본 수정

| 빠른 수정 (즉시 효과) | 근본 수정 (지속적 효과) |
|----------------------|----------------------|
| criteria.json 직접 편집 | agents/planner.md 수정 |
| plan.md Steps 직접 편집 | agents/worker.md 수정 |
| /review 전 결과물 직접 수정 | agents/reviewer.md 수정 |
| | references/ 패턴 추가 |

**추천 순서**: 빠른 수정으로 당장 해결 → 같은 문제가 3번 반복되면 근본 수정
