# evan-harness

Lean 3-agent harness: Plan → Work → Review. PM 업무 + 코딩 프로젝트 자동화.

## 이 프로젝트가 뭔지

Claude Code 플러그인. `/plan`, `/work`, `/review`, `/run`, `/autopilot`, `/fix`, `/tune`, `/log` 커맨드 제공.
3개 에이전트(Planner, Worker, Reviewer)가 파일 기반으로 협업하며, 핵심은 **만드는 놈과 검증하는 놈의 분리**.

## 핵심 파일

- `agents/planner.md` — 계획 에이전트 (Write 없음, 읽기 전용)
- `agents/worker.md` — 실행 에이전트 (전체 권한)
- `agents/reviewer.md` — 검증 에이전트 (Write 없음, 회의적 톤)
- `commands/` — 슬래시 커맨드 정의
- `skills/harness-workflow/` — 워크플로우 가이드 + 패턴 레퍼런스
- `usecases.md` — 실행 기록 (자동 누적)

## 세션 간 기억

이 하네스를 사용하는 프로젝트에서는 `.harness/memory.md`에 세션 간 유지할 정보를 기록한다.

**기록해야 할 것:**
- 이전 태스크에서 배운 프로젝트 컨텍스트 (기술 스택, 컨벤션, 주의사항)
- /tune으로 변경한 하네스 설정과 그 이유
- 반복 FAIL 패턴과 해결 방법
- 사용자의 선호도 (톤, 구조, 깊이)

**기록하지 말 것:**
- 코드 자체 (git에 있음)
- 일회성 태스크 디테일 (task-slug 폴더에 있음)

**매 세션 시작 시:** `.harness/memory.md`가 있으면 반드시 읽어라.
**매 세션 종료 시:** 다음 세션에 유용할 정보가 있으면 `.harness/memory.md`에 추가하라.

## 도구 제한 원칙

| 에이전트 | 쓸 수 있는 도구 | 못 쓰는 도구 | 이유 |
|---------|---------------|-------------|------|
| Planner | Read, Glob, Grep, WebSearch | Write, Edit, Bash | 계획만 |
| Worker | 전체 | — | 실행 |
| Reviewer | Read, Glob, Grep, Bash | Write, Edit | 검증만 |

## 상태 파일 구조

```
.harness/
├── memory.md                    # 세션 간 기억 (영속)
├── chain.json                   # autopilot 체인 상태
├── {task-slug}/
│   ├── plan.md
│   ├── criteria.json
│   ├── progress.md
│   └── review.md
└── context.md                   # (deprecated → memory.md 사용)
```
