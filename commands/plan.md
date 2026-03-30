---
name: plan
description: 태스크를 분석하고 실행 계획 + 성공 기준을 수립합니다.
allowed-tools: Read, Glob, Grep, Write, WebSearch, WebFetch, AskUserQuestion
---

# /plan

사용자의 태스크를 분석하여 실행 계획과 성공 기준을 수립합니다.

## Instructions

1. Create `.harness/` directory if it doesn't exist
2. Launch the **planner** agent with the user's task
3. The planner will:
   - Analyze the task and detect type (PM / Coding / Hybrid)
   - Explore relevant context (files, codebase, external resources)
   - Write `.harness/plan.md` with the execution plan
   - Write `.harness/criteria.json` with measurable acceptance criteria
4. Present the plan summary to the user
5. **STOP and wait for user approval** before any execution begins

## Usage

```
/plan <task description>
```

## Examples

```
/plan Epic 12 PRD 작성 — 유저 저니, 기능 요구사항, 성공 메트릭 포함
/plan 퍼스널 브랜딩 블로그 사이트 MVP 구현
/plan 포트폴리오 수익률 분석 리포트 작성
```

## Output

- `.harness/plan.md` — 실행 계획
- `.harness/criteria.json` — 성공 기준 (Reviewer가 이걸로 검증)
