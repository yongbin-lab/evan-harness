---
name: fix
description: 사용자 피드백을 반영하여 결과물을 즉시 수정합니다.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, WebSearch, WebFetch, Agent
---

# /fix

결과물이 마음에 안 들 때, 피드백을 반영하여 **결과물을 즉시 수정**합니다.

## 언제 쓰나

- `/run` 또는 `/work` 후 결과물을 봤는데 수정이 필요할 때
- "이 부분 좀 더 구체적으로", "톤이 너무 딱딱해", "이 섹션 빠졌어" 같은 피드백이 있을 때

## Instructions

1. Read the latest `.harness/{task-slug}/plan.md` and `.harness/{task-slug}/criteria.json` for context
2. Read the user's feedback carefully
3. Launch the **worker** agent with the following additional context:
   - Original plan (unchanged)
   - User's specific feedback as the primary directive
   - Previous review results if available (`.harness/{task-slug}/review.md`)
4. Worker modifies the **actual deliverables** (documents, code, etc.) — NOT the harness files
5. Worker updates `.harness/{task-slug}/progress.md` with a fix log entry
6. After fix, launch the **reviewer** agent to re-verify against criteria

## Important

- This command fixes the **output**, not the harness itself
- The plan and criteria stay the same — only the deliverables change
- If the same feedback keeps recurring across different tasks, suggest `/tune` instead

## Usage

```
/fix 성공 메트릭 섹션이 너무 추상적이야. 구체적인 수치 목표를 넣어줘.
/fix 코드에서 에러 핸들링이 빠져있어
/fix 톤이 너무 딱딱해. 좀 더 conversational하게.
```
