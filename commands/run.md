---
name: run
description: Plan → Work → Review 전체 파이프라인을 원클릭으로 실행합니다.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, WebSearch, WebFetch, AskUserQuestion, Agent
---

# /run

태스크를 받아서 Plan → (사용자 승인) → Work → Review 전체 사이클을 실행합니다.

## Instructions

### Phase 0: Load Memory
0. If `.harness/memory.md` exists, read it first — this contains learnings from previous sessions

### Phase 1: Plan
1. Create `.harness/` directory if it doesn't exist
2. Launch the **planner** agent with the user's task
3. Planner writes `.harness/plan.md` + `.harness/criteria.json`
4. Present the plan summary to the user
5. **STOP: Ask for user approval**
   - If approved → proceed to Phase 2
   - If rejected → revise plan based on feedback

### Phase 2: Work
6. Launch the **worker** agent
7. Worker executes the plan, tracking progress in `.harness/progress.md`
8. Worker self-checks against criteria

### Phase 3: Review
9. Launch the **reviewer** agent (separate context — independent verification)
10. Reviewer checks each criterion in `.harness/criteria.json`
11. Reviewer writes `.harness/review.md`

### Phase 4: Resolution
12. If **PASS** → proceed to Phase 5
13. If **FAIL** →
    - Show specific failures with actionable feedback
    - Re-launch Worker with the Reviewer's feedback (retry 1)
    - Re-launch Reviewer to verify fixes
    - If still FAIL after 2 retries → escalate to user with full context

### Phase 5: Log
14. Append this run to `/Users/mlt359/Documents/private/evan-harness/usecases.md`
    - Read the file first, then append one row:
      ```
      | {날짜} | {태스크 한 줄 요약} | {PM/Coding/Hybrid/Trading} | {PASS/FAIL} (점수, Fix 횟수 포함) | {체인 수} | {한 줄 인사이트} |
      ```
    - 날짜: task-slug의 날짜 prefix
    - 결과: review.md verdict 그대로
    - 인사이트: review.md 핵심 발견 한 줄
    - Do NOT skip this step

### Phase 6: Save Memory
15. If anything was learned that would help future sessions, append to `.harness/memory.md`
    - Project context, conventions discovered, user preferences observed
    - Do NOT save if nothing new was learned

## Usage

```
/run <task description>
```

## Examples

```
/run Epic 12 PRD 작성
/run 블로그 포스트 초안: "PM이 AI를 쓰는 법"
/run Next.js 랜딩 페이지 MVP 구현
/run 3월 포트폴리오 리밸런싱 분석
```

## Output

Full pipeline produces:
- `.harness/plan.md` — execution plan
- `.harness/criteria.json` — success criteria
- `.harness/progress.md` — execution log
- `.harness/review.md` — independent review verdict
- Actual deliverables (documents, code, etc.)
