---
name: autopilot
description: 태스크를 받으면 완전 자율 실행. 승인 없이 Plan→Work→Review→Fix 루프를 돌고, 완료 후 후속 태스크까지 자동 체이닝.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, WebSearch, WebFetch, Agent
---

# /autopilot

사용자가 딸깍도 안 해도 결과물이 완성되는 완전 자율 모드.

## How it differs from /run

| | /run | /autopilot |
|--|------|-----------|
| Plan 후 승인 | 사용자 승인 필요 | 자동 진행 |
| Review FAIL 시 | 사용자에게 보고 | 자동 수정 + 재검증 (최대 3회) |
| 완료 후 | 끝 | 후속 태스크 자동 제안 + 실행 |
| 적합한 경우 | 중요한/민감한 작업 | 반복적이거나 잘 정의된 작업 |

## Instructions

### Phase 0: Load Memory
0. If `.harness/memory.md` exists, read it first — this contains learnings from previous sessions

### Phase 1: Autonomous Plan
1. Create `.harness/{task-slug}/` directory
2. Launch **planner** agent — plan.md + criteria.json 생성
3. **DO NOT ask for approval** — proceed immediately to Phase 2
4. Write a brief plan summary to the console for the user's reference (not a gate, just FYI)

### Phase 2: Autonomous Work
5. Launch **worker** agent — execute the plan
6. Worker tracks progress in `.harness/{task-slug}/progress.md`

### Phase 3: Autonomous Review
7. Launch **reviewer** agent in a **separate context** (independent verification)
8. Reviewer writes `.harness/{task-slug}/review.md`

### Phase 4: Auto-Fix Loop (if FAIL)
9. If FAIL:
   - Read reviewer's specific feedback from review.md
   - Re-launch **worker** with the feedback as primary directive
   - Re-launch **reviewer** to verify fixes
   - Repeat up to **3 times**
   - If still FAIL after 3 retries → stop and report to user with full context
10. If PASS → proceed to Phase 5

### Phase 5: Chain — What's Next?
11. After PASS, analyze the completed deliverable and determine if there's a logical next step:
    - Does this output naturally lead to another task?
    - Would the user benefit from a follow-up?
12. If yes:
    - Write the follow-up task description
    - Log it in `.harness/{task-slug}/progress.md` under "## Chain"
    - **Automatically start a new autopilot cycle** for the follow-up task
13. If no obvious follow-up:
    - Report completion with a summary of all deliverables
    - Proceed to Phase 6

### Phase 6: Log
14. Append this run to `/Users/mlt359/Documents/private/evan-harness/usecases.md`
    - Read the file first, then append one row per completed task in this format:
      ```
      | {날짜} | {태스크 한 줄 요약} | {PM/Coding/Hybrid/Trading} | {PASS/FAIL} (점수, Fix 횟수 포함) | {체인 수} | {한 줄 인사이트} |
      ```
    - 날짜: task-slug의 날짜 prefix (e.g. 2026-04-16)
    - 유형: PM, Coding, Hybrid, Trading 중 판단
    - 결과: review.md의 verdict 그대로. Fix 있으면 "PASS (10/10, Fix 1회)" 식으로
    - 체인: chain.json의 tasks 배열 길이 - 1 (첫 태스크는 0)
    - 인사이트: review.md의 핵심 발견 또는 deliverable 요약 한 줄
    - 체인 태스크가 여러 개면 **각각 별도 행**으로 기록
    - This happens automatically — do NOT skip

### Phase 7: Save Memory
15. If anything was learned that would help future sessions, append to `.harness/memory.md`
    - Project context, conventions discovered, user preferences observed, tuning decisions
    - Do NOT save if nothing new was learned

### Chain Examples

```
"링크드인 포스트 작성"
  → [Task 1] 포스트 초안 작성 → PASS
  → [Task 2] 제목 & 훅 3가지 변형 생성 → PASS
  → [Task 3] 발행 체크리스트 + CTA 최적화 → PASS → 끝

"Epic PRD 작성"
  → [Task 1] PRD 본문 작성 → PASS
  → [Task 2] 기술 스펙 요약 (개발팀용) → PASS
  → [Task 3] 스테이크홀더 커뮤니케이션 초안 → PASS → 끝

"블로그 MVP 구현"
  → [Task 1] 프로젝트 셋업 + 기본 구조 → PASS
  → [Task 2] 핵심 페이지 구현 → PASS
  → [Task 3] 스타일링 + 반응형 → PASS → 끝
```

### Chain State: `.harness/chain.json`

Autopilot은 체인 전체 상태를 `.harness/chain.json`에 기록한다. 이 파일이 태스크 간의 연결고리 역할을 한다.

```json
{
  "original_task": "링크드인 포스트 작성",
  "started_at": "2026-03-29T10:00:00Z",
  "max_depth": 5,
  "tasks": [
    {
      "index": 1,
      "slug": "2026-03-29_linkedin-post-draft",
      "status": "passed",
      "output_files": ["output.md"],
      "review_verdict": "PASS"
    },
    {
      "index": 2,
      "slug": "2026-03-29_linkedin-hook-variants",
      "status": "in_progress",
      "depends_on": "2026-03-29_linkedin-post-draft",
      "output_files": []
    }
  ]
}
```

**각 체인 태스크 시작 시:**
1. Read `.harness/chain.json` — 이전 태스크 결과물 경로 확인
2. Read 이전 태스크의 실제 결과물 — 다음 태스크의 입력으로 사용
3. chain.json 업데이트 — 새 태스크 추가

### Chain Rules
- 각 체인 태스크는 **자체 .harness/{task-slug}/ 폴더**에 상태 저장
- `.harness/chain.json`이 전체 체인의 인덱스 역할
- 최대 체인 깊이: **5 태스크** (무한 루프 방지)
- 각 체인 시작 시 이전 태스크의 결과물을 **직접 읽어서** 컨텍스트로 활용
- 체인이 의미 없으면 (이미 충분히 완성) 강제로 만들지 말 것

## Safety

- `/autopilot`은 파괴적 명령(rm -rf, force push, DB 삭제 등)을 실행하지 않음
- 외부 서비스에 POST/발행하는 작업은 자동 실행하지 않고 "발행 준비 완료" 상태로 멈춤
- 3회 연속 Review FAIL이면 반드시 멈추고 사용자에게 보고

## Usage

```
/autopilot 링크드인 포스트: "PM이 AI 하네스를 쓰는 법"
/autopilot Epic 12 PRD 작성
/autopilot 3월 포트폴리오 리밸런싱 분석
/autopilot Next.js 블로그 MVP 구현
```
