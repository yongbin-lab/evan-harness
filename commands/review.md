---
name: review
description: Worker의 결과물을 독립적으로 검증합니다.
allowed-tools: Read, Glob, Grep, Bash, Write
---

# /review

Worker의 결과물을 `.harness/criteria.json` 기준으로 독립 검증합니다.

## Prerequisites

- `.harness/criteria.json` must exist
- `.harness/progress.md` must exist (Worker must have completed)

## Instructions

1. Read `.harness/criteria.json`, `.harness/plan.md`, and `.harness/progress.md`
2. Launch the **reviewer** agent
3. The reviewer will:
   - Independently verify each criterion (do NOT trust Worker's self-check)
   - For PM deliverables: check completeness, logic, measurability
   - For code: run tests, check functionality, review code quality
   - Write `.harness/review.md` with PASS/FAIL verdict per criterion
4. Present the review results to the user

## Verdict Handling

- **PASS**: All criteria met → task complete
- **FAIL**: Specific feedback provided → user can run `/work` again for the Worker to fix issues (max 2 retries)

## Usage

```
/review
```

## Output

- `.harness/review.md` — verdict with evidence for each criterion
