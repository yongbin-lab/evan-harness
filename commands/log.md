---
name: log
description: autopilot 실행 결과를 유즈케이스 로그에 기록합니다.
allowed-tools: Read, Write, Edit, Glob
---

# /log

autopilot 또는 run 실행 후 결과를 **하네스 플러그인 내 고정 경로**에 누적 기록합니다.

**고정 경로**: `~/.claude/plugins/cache/local-plugins/evan-harness/0.1.0/usecases.md`
**소스 경로**: `/Users/mlt359/Documents/private/evan-harness/usecases.md`

어떤 프로젝트에서 실행하든 한 곳에 모입니다.

## Instructions

1. Find the latest completed task in `.harness/` (most recent {task-slug}/ folder)
2. Read its `plan.md` and `review.md` for context
3. Append one entry to `/Users/mlt359/Documents/private/evan-harness/usecases.md` in this format:

```markdown
| {날짜} | {태스크 한 줄 요약} | {PM/Coding/Hybrid} | {PASS/FAIL} | {소요 체인 수} | {한 줄 인사이트} |
```

4. If `/Users/mlt359/Documents/private/evan-harness/usecases.md` doesn't exist, create it with the header:

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
