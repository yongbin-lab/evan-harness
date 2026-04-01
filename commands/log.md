---
name: log
description: autopilot 실행 결과를 유즈케이스 로그에 기록합니다.
allowed-tools: Read, Write, Edit, Glob
---

# /log

autopilot 또는 run 실행 후 결과를 `usecases.md`에 한 줄씩 누적 기록합니다.

## Instructions

1. Find the latest completed task in `.harness/` (most recent {task-slug}/ folder)
2. Read its `plan.md` and `review.md` for context
3. Append one entry to `usecases.md` (project root) in this format:

```markdown
| {날짜} | {태스크 한 줄 요약} | {PM/Coding/Hybrid} | {PASS/FAIL} | {소요 체인 수} | {한 줄 인사이트} |
```

4. If `usecases.md` doesn't exist, create it with the header:

```markdown
# Harness Use Cases

하네스를 실제로 쓴 기록. 글 쓸 때 사례로 활용.

| 날짜 | 태스크 | 유형 | 결과 | 체인 | 인사이트 |
|------|--------|------|------|------|----------|
```

## Auto-Logging

`/autopilot`과 `/run` 완료 시 자동으로 `/log`를 실행하도록 권장.
autopilot.md와 run.md의 마지막 단계에 "log this run" 지시 포함.

## Usage

```
/log
/log 직접 메모: Planner가 PRD 구조를 잡는 게 제일 유용했음
```
