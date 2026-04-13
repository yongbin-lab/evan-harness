---
name: view
description: 파일 또는 디렉토리를 브라우저에서 뷰어로 띄운다 (단일 포트, 세션 독립, 루트 자동 승격)
allowed-tools:
  - Bash
  - Read
---

# /view

파일 또는 디렉토리를 브라우저의 로컬 뷰어에서 연다.

**핵심 설계**
- **단일 고정 포트 8080** — 매번 포트가 바뀌던 문제 해결 (이전 URL 좀비 없음)
- **루트 자동 승격** — 마커(`.harness`, `.git`, `CLAUDE.md`, `package.json`, `pyproject.toml`, `.claude`) 기반으로 타겟 상위 디렉토리를 루트로 자동 탐지. 같은 루트 내 다른 파일은 URL hash만 바꿔 즉시 접근 가능
- **Idempotent** — 이미 같은 루트로 8080에 떠있으면 재사용, 다른 루트면 교체
- **세션 독립** — `nohup` + `disown`으로 Claude 세션이 죽어도 뷰어는 유지
- **즉사 감지** — 시작 후 8회 폴링으로 bind 실패/즉사를 감지해 로그 tail 출력

## Instructions

1. 사용자가 경로를 제공하면 `TARGET`으로, 없으면 빈 문자열로 전달한다.
2. **반드시 아래 명령어를 그대로 실행한다** (`${CLAUDE_PLUGIN_ROOT}`는 Claude Code가 플러그인 런타임에 주입하는 절대경로 환경변수):

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/view-launcher.sh" "<경로 또는 빈 문자열>"
```

3. `run_in_background: false`로 실행한다 (런처 내부에서 이미 detach되므로 블로킹 없음, 보통 2초 이내 반환).
4. 출력에서 `URL: ...` 라인을 사용자에게 안내한다.
5. 포트를 바꿔야 하면 `VIEWER_PORT=9000 bash "${CLAUDE_PLUGIN_ROOT}/scripts/view-launcher.sh" <경로>` 형태로 실행한다.

## 설계상 해결된 문제들

| 과거 증상 | 원인 | 해결 방식 |
|---------|------|---------|
| 새 파일 열 때마다 fail | 매번 새 프로세스 bind 실패 → 즉사 | 같은 루트면 재사용, 다른 루트면 선점 kill |
| 이전 URL 좀비 | 포트가 매번 달라짐 (8080/8081/8082) | 단일 포트 8080 고정 |
| 뷰어가 세션 종료와 함께 죽음 | Claude 셸의 자식 프로세스 (SIGHUP) | `nohup` + `disown` detach |
| md vs 디렉토리 포트 혼동 | 두 스크립트 + 두 포트 분리 | viewer.py 하나만 사용 (디렉토리 루트 + 파일 해시) |
| 루트가 매번 달라 같은 파일도 URL 다름 | CWD 기반 | 마커 기반 자동 승격 |
| 에러 시 사용자는 connection refused만 봄 | 즉사 감지 없음 | 8회 재확인 후 실패 시 로그 tail 출력 |
| viewer.py가 존재 안 하는 경로에 즉사 | 조용히 exit | 런처가 사전 체크 후 에러 반환 |

## 런처 검증 결과

```
$ view-launcher.sh /Users/mlt359/Documents/growth_strategy/.harness/2026-04-13_k12-product-ideas/output.md
Started viewer on :8080 (root=/Users/mlt359/Documents/growth_strategy)
URL: http://localhost:8080/#.harness%2F2026-04-13_k12-product-ideas%2Foutput.md

$ view-launcher.sh .../plan.md   # 같은 루트
Reusing existing viewer on :8080 (root=/Users/mlt359/Documents/growth_strategy)
URL: http://localhost:8080/#.harness%2F2026-04-13_k12-product-ideas%2Fplan.md

$ view-launcher.sh /Users/mlt359/Documents/Epic/.../analysis.md   # 다른 루트
Replacing viewer on :8080 (was root='/Users/mlt359/Documents/growth_strategy')
Started viewer on :8080 (root=/Users/mlt359/Documents/Epic)
URL: http://localhost:8080/#kr-premium-free-trial%2Fanalysis-2026-04-13.md
```

## Usage

```
/view                        # 현재 디렉토리의 루트 자동 탐지
/view /path/to/file.md       # 파일 — 루트 탐지 후 파일은 hash로
/view /path/to/dir           # 디렉토리 — 그 디렉토리(또는 상위 마커)를 루트로
```

## 디버깅

- 로그: `tail -f /tmp/viewer-8080.log`
- 현재 루트 확인: `curl -s http://localhost:8080/api/root`
- 강제 재시작: `lsof -ti tcp:8080 | xargs kill -9` 후 `/view <경로>` 재실행
- 런처 스크립트: `${CLAUDE_PLUGIN_ROOT}/scripts/view-launcher.sh`
- viewer 본체: `${CLAUDE_PLUGIN_ROOT}/scripts/viewer.py`

## 의존성

- Python 3 (표준 라이브러리만 사용 — 외부 패키지 없음)
- `lsof` (macOS/Linux 기본 탑재)
- `curl` (기본 탑재)
- CDN 접근 (marked.js, highlight.js) — 첫 로드 시에만 필요. CDN 차단 환경에서는 마크다운이 plain text로 렌더링됨 (viewer.py의 try/catch fallback)

## 포팅 주의

플러그인이 클론된 경로와 무관하게 동작해야 하므로:
- `view-launcher.sh`와 `viewer.py`는 **플러그인 내부 `scripts/`에 위치**
- 커맨드 파일은 `${CLAUDE_PLUGIN_ROOT}`를 통해 이들을 참조
- 런처는 `${BASH_SOURCE[0]}` 기준으로 자기 디렉토리의 `viewer.py`를 찾음 (하드코딩 없음)
