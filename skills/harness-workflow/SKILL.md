---
name: harness-workflow
description: Plan → Work → Review 3-agent harness workflow guide
triggers:
  - /plan
  - /work
  - /review
  - /run
  - harness
  - 하네스
---

# Harness Workflow

## Overview

This harness implements a 3-agent cycle inspired by the GAN-inspired Generator-Evaluator pattern from Anthropic's research:

```
/plan → /work → /review → (PASS: done | FAIL: retry /work)
```

Or use `/run` for the full pipeline with one command.

## Core Principle

**Generator ≠ Evaluator**: The Worker (generator) and Reviewer (evaluator) are structurally separated. The Worker cannot review its own output — this prevents self-evaluation bias.

## Commands

| Command | Agent | Purpose |
|---------|-------|---------|
| `/plan` | Planner | Analyze task, create plan + criteria |
| `/work` | Worker | Execute plan, track progress |
| `/review` | Reviewer | Independent verification against criteria |
| `/run` | All three | Full pipeline with user approval gate |

## State Files

State is stored in `.harness/{task-slug}/` (add `.harness/` to .gitignore):

```
.harness/
├── 2026-03-29_blog-post-draft/
│   ├── plan.md          # Planner output
│   ├── criteria.json    # Success contract
│   ├── progress.md      # Worker execution log
│   └── review.md        # Reviewer verdict
├── 2026-03-30_portfolio-analysis/
│   └── ...
└── context.md           # Session handoff (shared)
```

**Why JSON for criteria?** JSON is harder to accidentally corrupt and enforces structured contracts. Markdown is better for rich, human-readable context.

## Tips

- Start with `/plan` to see if the harness understands your intent
- Review the criteria.json carefully — this is the contract the Reviewer enforces
- If the Reviewer keeps failing the same criterion, the criterion might be too strict — adjust it
- For quick tasks, you can skip the harness and work directly

## Output이 마음에 안 들 때

자세한 튜닝 가이드: `references/tuning-guide.md`

**빠른 요약:**

| 문제 | 고칠 곳 |
|------|---------|
| 계획 방향이 틀림 | `agents/planner.md` 또는 criteria.json 직접 편집 |
| 실행 품질이 낮음 | plan.md Steps 더 구체화 → `agents/worker.md` 수정 |
| Reviewer가 너무 관대 | `agents/reviewer.md` Critical Mindset 강화 |
| Reviewer가 너무 엄격 | criteria.json에서 기준 완화/삭제 |
| 같은 문제 반복 | `references/`에 패턴 추가 |

**추천**: 빠른 수정으로 당장 해결 → 3번 반복되면 근본 수정
