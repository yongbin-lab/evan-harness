---
name: tune
description: 반복되는 문제를 해결하기 위해 하네스 자체를 수정합니다.
allowed-tools: Read, Write, Edit, Glob, Grep, AskUserQuestion
---

# /tune

같은 문제가 반복될 때, **하네스 자체**(에이전트 프롬프트, 패턴, 기준)를 수정합니다.

## 언제 쓰나

- `/fix`로 같은 종류의 피드백을 3번 이상 줬을 때
- "매번 성공 메트릭이 빠져", "항상 톤이 딱딱해" 같은 반복 패턴이 보일 때
- Reviewer가 매번 너무 관대하거나 너무 엄격할 때

## Instructions

1. Ask the user: "어떤 문제가 반복되고 있나요?"
2. Diagnose which harness component needs tuning:

### Diagnosis Decision Tree

```
반복되는 문제
 │
 ├─ 계획 단계에서 반복적으로 빠지는 것이 있다
 │   → agents/planner.md 수정
 │   → 또는 references/pm-patterns.md, coding-patterns.md에 패턴 추가
 │
 ├─ 실행 결과물의 품질/스타일이 매번 안 맞는다
 │   → agents/worker.md 수정
 │   → Task-Specific Behavior 섹션에 구체적 지시 추가
 │
 ├─ Reviewer가 통과시키면 안 되는 걸 통과시킨다
 │   → agents/reviewer.md의 Critical Mindset 또는 Verification Methods 강화
 │
 ├─ Reviewer가 사소한 것에 FAIL을 준다
 │   → agents/reviewer.md의 Decision Rules 완화
 │
 └─ 특정 유형의 태스크에서만 문제
     → skills/harness-workflow/references/ 에 새 패턴 파일 추가
```

3. Show the user the specific file and section that will be modified
4. Ask for approval before making changes
5. Edit the harness file with **minimal, targeted changes**
6. Explain what was changed and why

## Important

- This command modifies the **harness** (agents, patterns, skills), not the deliverables
- Always show the before/after diff to the user
- One tune at a time — don't change multiple agents in one go
- After tuning, suggest running `/run` on a new task to verify the improvement

## Usage

```
/tune 매번 PRD에 성공 메트릭이 빠져. Planner가 기본으로 포함하게 해줘.
/tune Reviewer가 너무 관대해. 코드 리뷰할 때 테스트 커버리지를 꼭 체크하게 해줘.
/tune Worker가 문서 쓸 때 항상 톤이 딱딱해. 더 conversational하게 기본값을 바꿔줘.
```

## 수정 가능한 파일

| 파일 | 영향 범위 |
|------|----------|
| `agents/planner.md` | 계획의 구조, 깊이, 기본 포함 항목 |
| `agents/worker.md` | 실행 스타일, 품질 기준, 태스크별 행동 |
| `agents/reviewer.md` | 검증 엄격도, 체크 항목, PASS/FAIL 기준 |
| `references/pm-patterns.md` | PM 태스크 유형별 기본 패턴 |
| `references/coding-patterns.md` | 코딩 태스크 유형별 기본 패턴 |
| `templates/*.tmpl` | 산출물 기본 형식 |
