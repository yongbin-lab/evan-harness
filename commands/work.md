---
name: work
description: 승인된 계획을 기반으로 태스크를 실행합니다.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, WebSearch, WebFetch
---

# /work

`.harness/plan.md`의 계획을 기반으로 실제 작업을 수행합니다.

## Prerequisites

- `.harness/plan.md` must exist (run `/plan` first)
- `.harness/criteria.json` must exist
- User must have approved the plan

## Instructions

1. Read `.harness/plan.md` and `.harness/criteria.json`
2. Launch the **worker** agent
3. The worker will:
   - Execute each step in the plan sequentially
   - Track progress in `.harness/progress.md`
   - Self-check against criteria when done
4. When the worker declares done, notify the user
5. Suggest running `/review` to verify the output

## Usage

```
/work
```

## Output

- Actual deliverables (documents, code, analysis)
- `.harness/progress.md` — execution log with self-check results
