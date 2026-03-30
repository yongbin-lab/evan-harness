# evan-harness

**"하나 시키면 알아서 돌아가는" AI 작업 자동화 하네스.**

Claude Code 위에서 동작하는 3-agent 하네스 플러그인. PM 업무(PRD, 분석, 리서치)와 코딩 프로젝트 모두에 사용할 수 있다.

```
/autopilot "링크드인 포스트 작성: PM이 AI를 쓰는 법"
  → Planner가 계획 수립
  → Worker가 실행
  → Reviewer가 독립 검증
  → FAIL이면 자동 수정
  → PASS면 후속 태스크 자동 시작
  → 끝까지 자동
```

---

## 왜 만들었나

Claude Code에 "블로그 포스트 써줘"라고 시키면 한 번에 결과물이 나온다. 근데 품질이 들쭉날쭉하다.

문제의 핵심은 **자기가 만든 걸 자기가 평가하면 항상 관대해진다**는 것. Anthropic이 이걸 "self-evaluation bias"라고 부른다. 해결책은 간단하다 — **만드는 놈과 검증하는 놈을 분리**하면 된다.

이게 이 하네스의 핵심 아이디어다.

---

## 어떻게 리서치했나

### 출발점: Anthropic 공식 블로그

- [Harness Design for Long-Running Apps](https://www.anthropic.com/engineering/harness-design-long-running-apps) — GAN 영감의 Generator-Evaluator 분리 패턴
- [Effective Harnesses for Long-Running Agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) — 파일 기반 상태 관리, feature_list.json 패턴
- [Building a C Compiler](https://www.anthropic.com/engineering/building-c-compiler) — 16개 에이전트 병렬 작업, $20,000, 2주

### GitHub 레포 딥다이브 (상위 5개)

| 레포 | Stars | 핵심 인사이트 |
|------|-------|-------------|
| [garrytan/gstack](https://github.com/garrytan/gstack) | 55K | CEO/디자이너/QA 등 **역할 기반** 에이전트 분리. SKILL.md로 정의. |
| [langchain-ai/deepagents](https://github.com/langchain-ai/deepagents) | 18K | **미들웨어 아키텍처**. TodoList로 계획, 서브에이전트로 위임, 파일시스템으로 통신. |
| [parcadei/Continuous-Claude-v3](https://github.com/parcadei/Continuous-Claude-v3) | 3.6K | "컨텍스트=RAM, 파일시스템=디스크". **Ledger+Handoff**로 세션 간 연속성. 30개 Hook. |
| [Danau5tin/multi-agent-coding-system](https://github.com/Danau5tin/multi-agent-coding-system) | 1.4K | Orchestrator/Explorer/Coder 3-agent. **Context Store**(영속 지식) + Task Manager(여정 추적). Stanford 벤치마크 13위. |
| [Chachamaru127/claude-code-harness](https://github.com/Chachamaru127/claude-code-harness) | 350 | Plan→Work→Review 사이클. TypeScript 가드레일 엔진(R01-R13). **Sprint Contract** 패턴. |

### 추가 참고 레포

- [gsd-build/get-shit-done](https://github.com/gsd-build/get-shit-done) (44K) — 메타 프롬프팅 + spec-driven 개발
- [shareAI-lab/learn-claude-code](https://github.com/shareAI-lab/learn-claude-code) (42K) — Agent harness 밑바닥 구현
- [hesreallyhim/awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code) (34K) — 에코시스템 큐레이션
- [ruvnet/ruflo](https://github.com/ruvnet/ruflo) (28K) — 엔터프라이즈급 에이전트 스웜
- [OthmanAdi/planning-with-files](https://github.com/OthmanAdi/planning-with-files) (18K) — Manus 스타일 파일 기반 planning
- [disler/claude-code-hooks-mastery](https://github.com/disler/claude-code-hooks-mastery) (3.4K) — Hooks 심층 가이드

---

## 리서치에서 뽑아낸 설계 원칙

| # | 원칙 | 출처 |
|---|------|------|
| 1 | **Generator ≠ Evaluator** — 만드는 놈과 검증하는 놈을 분리 | Anthropic 블로그 |
| 2 | **파일시스템 = 디스크, 컨텍스트 = RAM** — 중요한 건 파일로 써라 | vv-claude-harness |
| 3 | **JSON은 계약, Markdown은 컨텍스트** — 구조적 검증엔 JSON, 풍부한 정보엔 Markdown | Anthropic 블로그 |
| 4 | **Mechanical Enforcement > 말로 지시** — Hook으로 물리적 강제가 확실 | vv-harness v3.1 |
| 5 | **하네스의 모든 컴포넌트는 가설** — 모델이 좋아지면 불필요해지는 부분이 있다 | Anthropic 블로그 |

---

## 아키텍처

### 3-Agent 코어

```
사용자: "링크드인 포스트 써줘"
         │
         ▼
┌─────────────────────────┐
│  PLANNER (읽기 전용)     │
│  태스크 분석 → 계획 수립  │
│  → plan.md              │
│  → criteria.json        │
└────────┬────────────────┘
         ▼
┌─────────────────────────┐
│  WORKER (실행)           │
│  계획대로 작업 수행       │
│  → 결과물 (문서/코드)    │
│  → progress.md          │
└────────┬────────────────┘
         ▼
┌─────────────────────────┐
│  REVIEWER (독립 검증)    │
│  criteria.json 기준 판정  │
│  → review.md            │
│  → PASS: 완료           │
│  → FAIL: Worker 재실행   │
└─────────────────────────┘
```

**왜 3개인가?**
- Planner: 계획이 없으면 실행이 산으로 간다. 계획에서 "성공이 뭔지"를 먼저 정의해야 검증이 가능하다.
- Worker: 실행만 하는 놈. 범위를 벗어나거나 "개선"하지 않는다.
- Reviewer: 회의적(skeptical)으로 튜닝된 검증자. Worker의 자기평가를 신뢰하지 않는다.

### 커맨드 체계

```
기본 (단계별)          자동화              유지보수
─────────────        ──────              ────────
/plan  계획 수립      /run   전체 실행     /fix   결과물 수정
/work  실행          /autopilot 완전 자율  /tune  하네스 수정
/review 검증
```

| 커맨드 | 사용자 개입 | 용도 |
|--------|-----------|------|
| `/plan` | 승인 필요 | 계획만 보고 싶을 때 |
| `/work` | 없음 | 승인된 계획 실행 |
| `/review` | 없음 | 결과물 독립 검증 |
| `/run` | Plan 후 승인 | 전체 사이클 (안전하게) |
| `/autopilot` | 없음 | 전체 사이클 + 후속 체이닝 (딸깍 제로) |
| `/fix` | 피드백 입력 | 결과물 즉시 수정 |
| `/tune` | 피드백 입력 | 하네스 자체 수정 (반복 문제용) |

### 상태 파일 구조

태스크별로 폴더가 생긴다:

```
.harness/
├── 2026-03-29_linkedin-post/
│   ├── plan.md           # 계획 (Markdown — 사람이 읽기 편함)
│   ├── criteria.json     # 성공 기준 (JSON — 구조적 계약)
│   ├── progress.md       # 실행 로그
│   └── review.md         # 검증 결과
├── 2026-03-30_prd-epic12/
│   └── ...
└── context.md            # 세션 간 핸드오프
```

**criteria.json 예시:**
```json
{
  "task": "링크드인 포스트 작성",
  "type": "PM",
  "criteria": [
    {
      "id": "C1",
      "description": "훅(첫 문장)이 스크롤을 멈추게 하는가",
      "type": "quality",
      "status": "pending"
    },
    {
      "id": "C2",
      "description": "본문에 구체적 사례/숫자가 2개 이상 포함",
      "type": "completeness",
      "status": "pending"
    }
  ]
}
```

---

## 디렉토리 구조

```
evan-harness/
├── .claude-plugin/
│   └── plugin.json              # 플러그인 인식용 (이름, 버전만)
├── plugin.json                  # 전체 매니페스트 (커맨드, 에이전트, 스킬 등록)
├── agents/
│   ├── planner.md               # 계획 에이전트 (YAML frontmatter + 시스템 프롬프트)
│   ├── worker.md                # 실행 에이전트
│   └── reviewer.md              # 검증 에이전트 (회의적 톤)
├── commands/
│   ├── plan.md                  # /plan
│   ├── work.md                  # /work
│   ├── review.md                # /review
│   ├── run.md                   # /run
│   ├── fix.md                   # /fix — 결과물 수정
│   ├── tune.md                  # /tune — 하네스 수정
│   └── autopilot.md             # /autopilot — 완전 자율
├── skills/
│   └── harness-workflow/
│       ├── SKILL.md             # 워크플로우 가이드
│       └── references/
│           ├── pm-patterns.md   # PM 업무 패턴
│           ├── coding-patterns.md # 코딩 패턴
│           └── tuning-guide.md  # 튜닝 가이드
├── templates/
│   ├── plan.md.tmpl
│   ├── criteria.json.tmpl
│   └── review.md.tmpl
└── hooks/                       # (Phase 2에서 추가 예정)
```

---

## 자기만의 하네스 만들기

### Step 1: 용도 정하기

하네스가 뭘 자동화할 건지 정한다.

```
나의 경우: PM 업무(PRD, 분석, 리서치) + 사이드 프로젝트 코딩
당신의 경우: _________
```

### Step 2: 에이전트 역할 분리하기

핵심은 **만드는 놈과 검증하는 놈을 분리**하는 것. 최소 구성:

```
agents/
├── planner.md    # 뭘 할지 정하는 놈 (실행 안 함)
├── worker.md     # 실제 하는 놈
└── reviewer.md   # 잘 했는지 보는 놈 (만든 놈과 다른 놈이어야 함)
```

에이전트 파일 형식 (Claude Code 플러그인):
```yaml
---
name: my-agent
description: "이 에이전트가 뭘 하는지"
whenToUse:
  - "언제 이 에이전트를 쓰나"
tools:
  - Read
  - Write
---

여기에 시스템 프롬프트를 쓴다.
이 에이전트의 역할, 제약사항, 출력 형식 등.
```

### Step 3: Reviewer를 회의적으로 만들기

이게 하네스의 품질을 결정한다. Reviewer 프롬프트에 반드시 넣어야 할 것:

```markdown
## Critical Mindset

**You are intentionally skeptical.** Worker의 자기평가를 신뢰하지 마라.
- "괜찮아 보인다"는 절대 안 됨 — 증거를 대라
- 모든 criterion을 직접 검증해라
- 기준 미달이면 관대하게 넘기지 마라
```

### Step 4: 계약 구조 만들기 (criteria.json)

Planner가 정의하고 Reviewer가 검증하는 **계약**이 있어야 한다. JSON이 좋은 이유:
- 구조가 강제됨 (Markdown은 에이전트가 마음대로 바꿀 수 있음)
- PASS/FAIL이 명확함
- 자동화하기 쉬움

### Step 5: 커맨드 만들기

최소 구성:
```
commands/
├── run.md        # 전체 파이프라인
└── fix.md        # 결과물 수정
```

여유가 되면:
```
commands/
├── plan.md       # 계획만
├── work.md       # 실행만
├── review.md     # 검증만
├── run.md        # 전체 (승인 게이트 있음)
├── autopilot.md  # 전체 (승인 없이 자동)
├── fix.md        # 결과물 수정
└── tune.md       # 하네스 수정
```

### Step 6: Claude Code 플러그인으로 설치

```
.claude-plugin/plugin.json  — 이름, 버전만
plugin.json                 — 커맨드/에이전트/스킬 등록
```

### Step 7: 쓰면서 튜닝

**이게 제일 중요하다.**

하네스는 처음부터 완벽할 수 없다. 써보면서:
1. 결과물이 마음에 안 들면 → `/fix`로 즉시 수정
2. 같은 문제가 3번 반복되면 → `/tune`으로 에이전트 프롬프트 수정
3. 새로운 태스크 유형이 생기면 → `references/`에 패턴 추가

Anthropic이 말한 것처럼: **"하네스의 모든 컴포넌트는 모델이 혼자 못하는 것에 대한 가설이다."** 모델이 좋아지면 불필요해지는 부분이 생기고, 새로운 가능성이 열린다. 정기적으로 재평가하라.

---

## 비용 참고 (Anthropic 블로그 기준)

| 방식 | 비용 | 시간 | 품질 |
|------|------|------|------|
| 하네스 없이 | ~$9 | 20분 | 낮음 |
| 하네스 (Opus 4.6) | ~$125 | 3.8시간 | 높음 |
| 하네스 (Opus 4.5) | ~$200 | 6시간 | 높음 |

하네스는 비용이 더 들지만, 결과물을 다시 고치는 시간까지 포함하면 오히려 효율적이다.

---

## 로드맵

- [x] Phase 1: 3-agent 코어 + 커맨드 (plan, work, review, run, fix, tune, autopilot)
- [ ] Phase 2: Hooks (pre-review-gate, post-work-progress)
- [ ] Phase 3: 세션 간 컨텍스트 핸드오프 (context.md 자동화)
- [ ] Phase 4: 병렬 워커 (독립 태스크 자동 감지 + worktree 격리)

---

## 참고 자료

### Anthropic 공식
- [Harness Design for Long-Running Apps](https://www.anthropic.com/engineering/harness-design-long-running-apps)
- [Effective Harnesses for Long-Running Agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
- [Building a C Compiler](https://www.anthropic.com/engineering/building-c-compiler)

### 주요 레퍼런스 레포
- [garrytan/gstack](https://github.com/garrytan/gstack) (55K) — 역할 기반 에이전트
- [langchain-ai/deepagents](https://github.com/langchain-ai/deepagents) (18K) — 미들웨어 아키텍처
- [parcadei/Continuous-Claude-v3](https://github.com/parcadei/Continuous-Claude-v3) (3.6K) — 컨텍스트 관리
- [Danau5tin/multi-agent-coding-system](https://github.com/Danau5tin/multi-agent-coding-system) (1.4K) — Context Store
- [Chachamaru127/claude-code-harness](https://github.com/Chachamaru127/claude-code-harness) (350) — Plan→Work→Review

### 커뮤니티
- [hesreallyhim/awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code) (34K) — 에코시스템 인덱스
- [shanraisshan/claude-code-best-practice](https://github.com/shanraisshan/claude-code-best-practice) (24K) — 베스트 프랙티스
- [disler/claude-code-hooks-mastery](https://github.com/disler/claude-code-hooks-mastery) (3.4K) — Hooks 가이드
