#!/usr/bin/env bash
# view-launcher.sh — single-port, session-independent file/dir viewer launcher.
#
# Design goals:
#   1. Single stable port (default 8080) — previous URLs don't go stale.
#   2. Root auto-promotion via markers (.harness, .git, CLAUDE.md, ...).
#   3. Idempotent — reuse existing viewer if same root; otherwise replace.
#   4. Session-independent — setsid + nohup so Claude session death doesn't kill the viewer.
#   5. Fail loudly — detect immediate exit and tail the log.
#
# Usage: view-launcher.sh [target]
#   target: file or directory path (default: $PWD)

set -u

TARGET_IN="${1:-}"
PORT="${VIEWER_PORT:-8080}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VIEWER_PY="$SCRIPT_DIR/viewer.py"
LOG="/tmp/viewer-$PORT.log"

if [ ! -f "$VIEWER_PY" ]; then
  echo "Error: viewer.py not found at $VIEWER_PY" >&2
  exit 1
fi

# --- Resolve target, root (via markers), and relative path ---
RESOLVED=$(TARGET_IN="$TARGET_IN" python3 <<'PY'
import os, sys
raw = os.environ.get("TARGET_IN") or os.getcwd()
target = os.path.abspath(os.path.expanduser(raw))
if not os.path.exists(target):
    print(f"NOTFOUND\t{target}\t-\t-")
    sys.exit(0)

base = target if os.path.isdir(target) else os.path.dirname(target)
MARKERS = {".harness", ".git", "CLAUDE.md", "package.json", "pyproject.toml", ".claude"}
HOME = os.path.expanduser("~")

root = None
cur = base
while cur and cur != "/" and (cur == HOME or cur.startswith(HOME + "/")):
    try:
        entries = set(os.listdir(cur))
    except OSError:
        break
    if entries & MARKERS:
        root = cur
        break
    parent = os.path.dirname(cur)
    if parent == cur:
        break
    cur = parent
if root is None:
    root = base

rel = "-" if os.path.isdir(target) else os.path.relpath(target, root)
print(f"OK\t{target}\t{root}\t{rel}")
PY
)
STATUS=$(echo "$RESOLVED" | cut -f1)
TARGET=$(echo "$RESOLVED" | cut -f2)
ROOT=$(echo "$RESOLVED" | cut -f3)
REL=$(echo "$RESOLVED" | cut -f4)

if [ "$STATUS" = "NOTFOUND" ]; then
  echo "Error: '$TARGET' not found" >&2
  exit 1
fi

# --- Kill orphan viewers on non-canonical ports (prevents stale tab "fail" messages) ---
pkill -9 -f "viewer\.py.*--port 808[1-9]" 2>/dev/null || true
pkill -9 -f "md-viewer\.py" 2>/dev/null || true

# --- Check existing viewer on port ---
CURRENT_ROOT=$(curl -sf --max-time 1 "http://localhost:$PORT/api/root" 2>/dev/null \
  | python3 -c "import sys,json; print(json.load(sys.stdin).get('root',''))" 2>/dev/null || echo "")

if [ "$CURRENT_ROOT" = "$ROOT" ]; then
  echo "Reusing existing viewer on :$PORT (root=$ROOT)"
else
  EXISTING=$(lsof -ti tcp:$PORT 2>/dev/null || true)
  if [ -n "$EXISTING" ]; then
    echo "Replacing viewer on :$PORT (was root='$CURRENT_ROOT')"
    kill -9 $EXISTING 2>/dev/null || true
    sleep 0.3
  fi

  # Detach fully from this shell so the Claude session dying won't take it with us.
  # macOS doesn't ship setsid; nohup + backgrounding + disown handles SIGHUP.
  nohup python3 "$VIEWER_PY" "$ROOT" --port "$PORT" > "$LOG" 2>&1 < /dev/null &
  VIEWER_PID=$!
  disown "$VIEWER_PID" 2>/dev/null || true

  # Poll for startup (up to ~1.5s)
  for _ in 1 2 3 4 5 6 7 8; do
    sleep 0.2
    if curl -sf --max-time 1 "http://localhost:$PORT/api/root" >/dev/null 2>&1; then
      break
    fi
  done

  if ! curl -sf --max-time 1 "http://localhost:$PORT/api/root" >/dev/null 2>&1; then
    echo "ERROR: viewer failed to start on :$PORT. Last log lines:" >&2
    tail -30 "$LOG" >&2
    exit 1
  fi
  echo "Started viewer on :$PORT (root=$ROOT)"
fi

# --- Build and print URL ---
if [ "$REL" = "-" ]; then
  echo "URL: http://localhost:$PORT/"
else
  HASH=$(python3 -c "import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1], safe=''))" "$REL")
  echo "URL: http://localhost:$PORT/#$HASH"
fi
