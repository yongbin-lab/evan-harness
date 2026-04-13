#!/usr/bin/env python3
"""
Local Directory Viewer
Browse any local directory in the browser with syntax highlighting,
markdown rendering, and a clean file tree sidebar.

Usage:
    python3 viewer.py /path/to/dir [--port 8080]
"""

from __future__ import annotations

import argparse
import http.server
import json
import mimetypes
import os
import socket
import sys
import urllib.parse
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Globals set at startup
# ---------------------------------------------------------------------------
ROOT_DIR: str = ""
PORT: int = 8080

# Directories / files to hide from the tree
HIDDEN = {".git", ".DS_Store", "__pycache__", ".mypy_cache", ".pytest_cache",
           "node_modules", ".venv", "venv", ".env"}

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".ico", ".bmp"}

# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def get_local_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def safe_path(relative: str) -> Optional[str]:
    """Resolve *relative* under ROOT_DIR and return the real path.
    Returns None if the result escapes ROOT_DIR (path traversal)."""
    joined = os.path.join(ROOT_DIR, relative)
    real = os.path.realpath(joined)
    if not real.startswith(os.path.realpath(ROOT_DIR)):
        return None
    return real


def build_tree(directory: str) -> list[dict]:
    """Recursively build a JSON-serialisable directory tree."""
    items: list[dict] = []
    try:
        entries = sorted(os.listdir(directory), key=lambda x: (not os.path.isdir(os.path.join(directory, x)), x.lower()))
    except PermissionError:
        return items

    for name in entries:
        if name in HIDDEN:
            continue
        full = os.path.join(directory, name)
        rel = os.path.relpath(full, ROOT_DIR)
        if os.path.isdir(full):
            children = build_tree(full)
            items.append({"name": name, "path": rel, "type": "dir", "children": children})
        else:
            items.append({"name": name, "path": rel, "type": "file"})
    return items


def is_binary(filepath: str) -> bool:
    """Quick heuristic: read first 8 KB and look for null bytes."""
    try:
        with open(filepath, "rb") as f:
            chunk = f.read(8192)
        return b"\x00" in chunk
    except Exception:
        return True

# ---------------------------------------------------------------------------
# HTML template (inline)
# ---------------------------------------------------------------------------

HTML_PAGE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Directory Viewer</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css"/>
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/marked/12.0.1/marked.min.js"></script>
<style>
:root {
  --bg: #0d1117;
  --sidebar-bg: #161b22;
  --content-bg: #0d1117;
  --text: #c9d1d9;
  --text-muted: #8b949e;
  --border: #30363d;
  --accent: #58a6ff;
  --hover: #1c2128;
  --active: #1f2937;
  --search-bg: #21262d;
  --font: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
  --mono: "SF Mono", "Cascadia Code", "Fira Code", Consolas, monospace;
}
* { margin:0; padding:0; box-sizing:border-box; }
html, body { height:100%; font-family:var(--font); background:var(--bg); color:var(--text); }
body { display:flex; overflow:hidden; }

/* Sidebar */
#sidebar {
  width: 280px; min-width: 220px; max-width: 400px;
  background: var(--sidebar-bg); border-right: 1px solid var(--border);
  display: flex; flex-direction: column; height: 100vh;
  flex-shrink: 0;
}
#sidebar-header {
  padding: 12px; border-bottom: 1px solid var(--border);
}
#sidebar-header h2 {
  font-size: 13px; font-weight: 600; color: var(--text-muted);
  text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;
}
#search {
  width: 100%; padding: 6px 10px; font-size: 13px;
  background: var(--search-bg); border: 1px solid var(--border);
  border-radius: 6px; color: var(--text); outline: none;
  font-family: var(--font);
}
#search:focus { border-color: var(--accent); }
#search::placeholder { color: var(--text-muted); }
#tree-container {
  flex: 1; overflow-y: auto; padding: 4px 0;
}
#tree-container::-webkit-scrollbar { width: 6px; }
#tree-container::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }

.tree-item {
  display: flex; align-items: center; padding: 3px 8px 3px 0;
  cursor: pointer; font-size: 13px; line-height: 1.6;
  white-space: nowrap; user-select: none; border-radius: 4px;
  color: var(--text);
}
.tree-item:hover { background: var(--hover); }
.tree-item.active { background: var(--active); color: var(--accent); }
.tree-item .icon { width: 16px; text-align: center; margin-right: 4px; flex-shrink:0; font-size: 12px; }
.tree-item .name { overflow: hidden; text-overflow: ellipsis; }

.tree-children { display: none; }
.tree-children.open { display: block; }

/* Content */
#content {
  flex: 1; overflow-y: auto; padding: 32px 48px;
  background: var(--content-bg); height: 100vh;
}
#content::-webkit-scrollbar { width: 8px; }
#content::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }

#welcome {
  display: flex; align-items: center; justify-content: center;
  height: 100%; color: var(--text-muted); font-size: 15px;
}
#file-header {
  margin-bottom: 16px; padding-bottom: 12px; border-bottom: 1px solid var(--border);
}
#file-header h1 { font-size: 18px; font-weight: 600; }
#file-header .path { font-size: 12px; color: var(--text-muted); font-family: var(--mono); margin-top: 4px; }

/* Markdown */
.md-body { line-height: 1.7; font-size: 15px; }
.md-body h1, .md-body h2, .md-body h3, .md-body h4 { margin: 1.2em 0 0.6em; font-weight: 600; }
.md-body h1 { font-size: 1.8em; border-bottom: 1px solid var(--border); padding-bottom: 8px; }
.md-body h2 { font-size: 1.4em; border-bottom: 1px solid var(--border); padding-bottom: 6px; }
.md-body h3 { font-size: 1.15em; }
.md-body p { margin: 0.8em 0; }
.md-body a { color: var(--accent); text-decoration: none; }
.md-body a:hover { text-decoration: underline; }
.md-body ul, .md-body ol { margin: 0.6em 0; padding-left: 2em; }
.md-body li { margin: 0.3em 0; }
.md-body code { font-family: var(--mono); background: var(--search-bg); padding: 2px 6px; border-radius: 4px; font-size: 0.9em; }
.md-body pre { background: var(--sidebar-bg); border: 1px solid var(--border); border-radius: 8px; padding: 16px; overflow-x: auto; margin: 1em 0; }
.md-body pre code { background: none; padding: 0; }
.md-body blockquote { border-left: 3px solid var(--accent); padding-left: 16px; color: var(--text-muted); margin: 1em 0; }
.md-body table { border-collapse: collapse; width: 100%; margin: 1em 0; }
.md-body th, .md-body td { border: 1px solid var(--border); padding: 8px 12px; text-align: left; }
.md-body th { background: var(--sidebar-bg); font-weight: 600; }
.md-body img { max-width: 100%; border-radius: 8px; }

/* CSV table */
.csv-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.csv-table th, .csv-table td { border: 1px solid var(--border); padding: 6px 10px; text-align: left; }
.csv-table th { background: var(--sidebar-bg); font-weight: 600; position: sticky; top: 0; }
.csv-table tr:hover { background: var(--hover); }

/* Code block */
.code-view { font-family: var(--mono); font-size: 13px; line-height: 1.6; }
.code-view pre { margin: 0; }
.code-view code { display: block; padding: 16px; overflow-x: auto; border-radius: 8px; border: 1px solid var(--border); }

/* Image */
.image-view { text-align: center; }
.image-view img { max-width: 100%; max-height: 80vh; border-radius: 8px; box-shadow: 0 4px 16px rgba(0,0,0,0.4); }

/* Plain text */
.plain-view { font-family: var(--mono); font-size: 13px; line-height: 1.6; white-space: pre-wrap; word-break: break-all; background: var(--sidebar-bg); padding: 16px; border-radius: 8px; border: 1px solid var(--border); }

/* JSON */
.json-view pre { margin: 0; }
.json-view code { display: block; padding: 16px; overflow-x: auto; border-radius: 8px; border: 1px solid var(--border); font-family: var(--mono); font-size: 13px; line-height: 1.6; }

/* Resize handle */
#resize-handle {
  width: 4px; cursor: col-resize; background: transparent;
  flex-shrink: 0; transition: background 0.15s;
}
#resize-handle:hover, #resize-handle.active { background: var(--accent); }

/* Sidebar toggle */
#sidebar.collapsed { width: 0 !important; min-width: 0; overflow: hidden; border-right: none; }
#sidebar.collapsed + #resize-handle { display: none; }
#toggle-sidebar {
  position: fixed; top: 8px; left: 8px; z-index: 100;
  width: 32px; height: 32px; border: 1px solid var(--border);
  background: var(--sidebar-bg); color: var(--text-muted); border-radius: 6px;
  cursor: pointer; font-size: 16px; display: flex; align-items: center; justify-content: center;
  transition: background 0.15s, left 0.15s;
}
#toggle-sidebar:hover { background: var(--hover); color: var(--text); }
body:not(.sidebar-collapsed) #toggle-sidebar { left: 248px; }
body.sidebar-collapsed #toggle-sidebar { left: 8px; }
</style>
</head>
<body>
<button id="toggle-sidebar" title="Toggle sidebar">&#9776;</button>
<div id="sidebar">
  <div id="sidebar-header">
    <h2>Files</h2>
    <input type="text" id="search" placeholder="Search files..." autocomplete="off"/>
  </div>
  <div id="tree-container"></div>
</div>
<div id="resize-handle"></div>
<div id="content">
  <div id="welcome">Select a file from the sidebar to view its contents.</div>
</div>

<script>
// ---- State ----
let treeData = [];
let activeEl = null;

// ---- Tree ----
async function loadTree() {
  try {
    const res = await fetchRetry('/api/tree');
    if (!res.ok) throw new Error('tree HTTP ' + res.status);
    treeData = await res.json();
    renderTree(treeData);
  } catch (e) {
    console.error('loadTree failed:', e);
    document.getElementById('tree-container').innerHTML =
      '<div style="padding:12px;color:#f85149;font-size:12px">Failed to load tree: ' + escHtml(e.message || String(e)) + '</div>';
  }
  // Restore from hash (attempted even if tree failed — file API may still work)
  if (location.hash) {
    try {
      const p = decodeURIComponent(location.hash.slice(1));
      openFile(p);
    } catch (e) {
      console.error('hash decode failed:', e);
    }
  }
}
window.addEventListener('error', e => console.error('[viewer] window error:', e.message, e.error));
window.addEventListener('unhandledrejection', e => console.error('[viewer] unhandled rejection:', e.reason));

function renderTree(data, container, depth) {
  container = container || document.getElementById('tree-container');
  depth = depth || 0;
  container.innerHTML = '';
  data.forEach(item => buildNode(item, container, depth));
}

function buildNode(item, parent, depth) {
  const div = document.createElement('div');
  if (item.type === 'dir') {
    const row = document.createElement('div');
    row.className = 'tree-item';
    row.style.paddingLeft = (12 + depth * 16) + 'px';
    row.innerHTML = '<span class="icon">&#9654;</span><span class="name">' + escHtml(item.name) + '</span>';
    div.appendChild(row);

    const children = document.createElement('div');
    children.className = 'tree-children';
    item.children.forEach(c => buildNode(c, children, depth + 1));
    div.appendChild(children);

    row.addEventListener('click', () => {
      const open = children.classList.toggle('open');
      row.querySelector('.icon').innerHTML = open ? '&#9660;' : '&#9654;';
    });
  } else {
    const row = document.createElement('div');
    row.className = 'tree-item';
    row.style.paddingLeft = (12 + depth * 16) + 'px';
    row.dataset.path = item.path;
    const ext = item.name.includes('.') ? item.name.split('.').pop().toLowerCase() : '';
    row.innerHTML = '<span class="icon">' + fileIcon(ext) + '</span><span class="name">' + escHtml(item.name) + '</span>';
    row.addEventListener('click', () => openFile(item.path));
    div.appendChild(row);
  }
  parent.appendChild(div);
}

function fileIcon(ext) {
  const icons = {md:'📝',csv:'📊',json:'{}',py:'🐍',js:'JS',ts:'TS',html:'🌐',css:'🎨',svg:'🖼',png:'🖼',jpg:'🖼',jpeg:'🖼',gif:'🖼',txt:'📄',sh:'⚙',yaml:'⚙',yml:'⚙',toml:'⚙'};
  return icons[ext] || '📄';
}

function escHtml(s) {
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

// ---- Highlight helper (per-block try/catch) ----
function highlightAll(root) {
  if (typeof hljs === 'undefined') return;
  root.querySelectorAll('pre code').forEach(b => {
    try { hljs.highlightElement(b); }
    catch (e) { console.warn('hljs failed on block:', e); }
  });
}

// ---- Fetch with retry ----
async function fetchRetry(url, retries) {
  retries = retries || 3;
  for (let i = 0; i < retries; i++) {
    try {
      const res = await fetch(url);
      return res;
    } catch (e) {
      if (i === retries - 1) throw e;
      await new Promise(r => setTimeout(r, 300 * (i + 1)));
    }
  }
}

// ---- File opening ----
async function openFile(relPath) {
  location.hash = encodeURIComponent(relPath);
  // Highlight active
  if (activeEl) activeEl.classList.remove('active');
  const el = document.querySelector('.tree-item[data-path="' + CSS.escape(relPath) + '"]');
  if (el) { el.classList.add('active'); activeEl = el; expandParents(el); }

  const content = document.getElementById('content');
  const ext = relPath.includes('.') ? relPath.split('.').pop().toLowerCase() : '';
  const name = relPath.split('/').pop();
  const imageExts = ['png','jpg','jpeg','gif','svg','webp','ico','bmp'];

  // Header
  let header = '<div id="file-header"><h1>' + escHtml(name) + '</h1><div class="path">' + escHtml(relPath) + '</div></div>';

  if (imageExts.includes(ext)) {
    content.innerHTML = header + '<div class="image-view"><img src="/api/file?path=' + encodeURIComponent(relPath) + '"/></div>';
    return;
  }

  try {
    const res = await fetchRetry('/api/file?path=' + encodeURIComponent(relPath));
    if (!res.ok) {
      const msg = await res.text();
      if (res.status === 415) {
        content.innerHTML = header + '<p style="color:var(--text-muted)">Binary file — preview not supported.</p>';
      } else {
        content.innerHTML = header + '<p style="color:#f85149">Error ' + res.status + ': ' + escHtml(msg) + '</p>';
      }
      return;
    }
    const text = await res.text();

    if (ext === 'md') {
      let html;
      if (typeof marked !== 'undefined') {
        try {
          html = '<div class="md-body">' + marked.parse(text) + '</div>';
        } catch (mdErr) {
          console.error('marked.parse failed:', mdErr);
          html = '<div class="md-body"><p style="color:#f85149">Markdown render error: ' + escHtml(mdErr.message) + ' — showing raw text below.</p><pre class="plain-view">' + escHtml(text) + '</pre></div>';
        }
      } else {
        html = '<div class="plain-view">' + escHtml(text) + '</div>';
      }
      content.innerHTML = header + html;
      highlightAll(content);
    } else if (ext === 'csv') {
      content.innerHTML = header + csvToTable(text);
    } else if (ext === 'json') {
      let formatted;
      try { formatted = JSON.stringify(JSON.parse(text), null, 2); } catch { formatted = text; }
      content.innerHTML = header + '<div class="json-view"><pre><code class="language-json">' + escHtml(formatted) + '</code></pre></div>';
      highlightAll(content);
    } else if (['py','js','ts','tsx','jsx','java','c','cpp','h','go','rs','rb','php','swift','kt','scala','sh','bash','zsh','sql','r','lua','pl','ex','exs','hs','clj','yaml','yml','toml','ini','xml','html','css','scss','less','vue','svelte','dockerfile','makefile','cmake'].includes(ext)) {
      const lang = ext === 'yml' ? 'yaml' : ext;
      content.innerHTML = header + '<div class="code-view"><pre><code class="language-' + lang + '">' + escHtml(text) + '</code></pre></div>';
      highlightAll(content);
    } else {
      content.innerHTML = header + '<div class="plain-view">' + escHtml(text) + '</div>';
    }
  } catch (e) {
    console.error('openFile failed:', e);
    content.innerHTML = header + '<p style="color:#f85149">Failed to load file: ' + escHtml(e.message || String(e)) + '</p><p style="color:var(--text-muted);font-size:12px">See browser console for details.</p>';
  }
  content.scrollTop = 0;
}

function expandParents(el) {
  let p = el.parentElement;
  while (p && p.id !== 'tree-container') {
    if (p.classList.contains('tree-children')) {
      p.classList.add('open');
      const arrow = p.previousElementSibling;
      if (arrow && arrow.querySelector('.icon')) arrow.querySelector('.icon').innerHTML = '&#9660;';
    }
    p = p.parentElement;
  }
}

function csvToTable(text) {
  const lines = text.trim().split('\n');
  if (!lines.length) return '<p>Empty CSV</p>';
  const parse = line => {
    const cols = []; let cur = '', inQ = false;
    for (let i = 0; i < line.length; i++) {
      const ch = line[i];
      if (ch === '"') { inQ = !inQ; }
      else if (ch === ',' && !inQ) { cols.push(cur.trim()); cur = ''; }
      else { cur += ch; }
    }
    cols.push(cur.trim());
    return cols;
  };
  const headers = parse(lines[0]);
  let html = '<div style="overflow-x:auto"><table class="csv-table"><thead><tr>';
  headers.forEach(h => html += '<th>' + escHtml(h) + '</th>');
  html += '</tr></thead><tbody>';
  for (let i = 1; i < lines.length; i++) {
    if (!lines[i].trim()) continue;
    const cols = parse(lines[i]);
    html += '<tr>';
    cols.forEach(c => html += '<td>' + escHtml(c) + '</td>');
    html += '</tr>';
  }
  html += '</tbody></table></div>';
  return html;
}

// ---- Search ----
document.getElementById('search').addEventListener('input', function() {
  const q = this.value.toLowerCase().trim();
  if (!q) { renderTree(treeData); return; }
  const filtered = filterTree(treeData, q);
  renderTree(filtered);
  // Auto-expand all when filtering
  document.querySelectorAll('.tree-children').forEach(c => {
    c.classList.add('open');
    const arrow = c.previousElementSibling;
    if (arrow && arrow.querySelector('.icon')) arrow.querySelector('.icon').innerHTML = '&#9660;';
  });
});

function filterTree(nodes, q) {
  const result = [];
  for (const node of nodes) {
    if (node.type === 'file') {
      if (node.name.toLowerCase().includes(q)) result.push(node);
    } else {
      const kids = filterTree(node.children, q);
      if (kids.length > 0 || node.name.toLowerCase().includes(q)) {
        result.push({...node, children: kids});
      }
    }
  }
  return result;
}

// ---- Resize handle ----
const handle = document.getElementById('resize-handle');
const sidebar = document.getElementById('sidebar');
let dragging = false;
handle.addEventListener('mousedown', e => { dragging = true; handle.classList.add('active'); e.preventDefault(); });
document.addEventListener('mousemove', e => { if (dragging) sidebar.style.width = Math.max(180, Math.min(600, e.clientX)) + 'px'; });
document.addEventListener('mouseup', () => { dragging = false; handle.classList.remove('active'); });

// ---- Hash change ----
window.addEventListener('hashchange', () => {
  if (location.hash) openFile(decodeURIComponent(location.hash.slice(1)));
});

// ---- Sidebar toggle ----
document.getElementById('toggle-sidebar').addEventListener('click', () => {
  document.getElementById('sidebar').classList.toggle('collapsed');
  document.body.classList.toggle('sidebar-collapsed');
});

// ---- Init ----
loadTree();
</script>
</body>
</html>"""

# ---------------------------------------------------------------------------
# Request handler
# ---------------------------------------------------------------------------

class ViewerHandler(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def do_HEAD(self):
        """Safari sends HEAD requests — handle them like GET but without body."""
        self._handle_request(head_only=True)

    def do_GET(self):
        self._handle_request()

    def _handle_request(self, head_only: bool = False):
        try:
            parsed = urllib.parse.urlparse(self.path)
            path = parsed.path
            query = urllib.parse.parse_qs(parsed.query)

            if path == "/":
                self._serve_html(head_only)
            elif path == "/api/root":
                data = json.dumps({"root": ROOT_DIR}, ensure_ascii=False).encode("utf-8")
                self._send(200, "application/json; charset=utf-8", data, head_only)
            elif path == "/api/tree":
                self._serve_tree(head_only)
            elif path == "/api/file":
                rel = query.get("path", [""])[0]
                self._serve_file(rel, head_only)
            else:
                self._error(404, "Not found")
        except Exception as e:
            try:
                self._error(500, f"Internal server error: {e}")
            except Exception:
                pass

    # --- Responses ---

    def _send(self, code: int, content_type: str, data: bytes, head_only: bool = False):
        """Send a response with standard headers (CORS, Connection)."""
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Connection", "keep-alive")
        self.end_headers()
        if not head_only:
            self.wfile.write(data)

    def _serve_html(self, head_only: bool = False):
        data = HTML_PAGE.encode("utf-8")
        self._send(200, "text/html; charset=utf-8", data, head_only)

    def _serve_tree(self, head_only: bool = False):
        tree = build_tree(ROOT_DIR)
        data = json.dumps(tree, ensure_ascii=False).encode("utf-8")
        self._send(200, "application/json; charset=utf-8", data, head_only)

    def _serve_file(self, rel_path: str, head_only: bool = False):
        if not rel_path:
            self._error(400, "Missing path parameter")
            return

        real = safe_path(rel_path)
        if real is None:
            self._error(403, "Access denied")
            return
        if not os.path.isfile(real):
            self._error(404, "File not found")
            return

        ext = os.path.splitext(real)[1].lower()

        # Image files — serve binary
        if ext in IMAGE_EXTS:
            mime = mimetypes.guess_type(real)[0] or "application/octet-stream"
            try:
                with open(real, "rb") as f:
                    data = f.read()
                self._send(200, mime, data, head_only)
            except Exception:
                self._error(500, "Cannot read file")
            return

        # Binary check
        if is_binary(real):
            self._error(415, "Unsupported binary file format")
            return

        # Text files
        try:
            with open(real, "r", encoding="utf-8", errors="replace") as f:
                text = f.read()
            data = text.encode("utf-8")
            self._send(200, "text/plain; charset=utf-8", data, head_only)
        except Exception:
            self._error(500, "Cannot read file")

    def _error(self, code: int, msg: str):
        self._send(code, "text/plain; charset=utf-8", msg.encode("utf-8"))

    def log_message(self, format, *args):
        # Quieter logging — only errors
        if len(args) >= 2 and "200" in str(args[1]):
            return
        super().log_message(format, *args)


# ---------------------------------------------------------------------------
# CLI & Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Local Directory Viewer — browse files in your browser.",
        usage="python3 viewer.py [directory] [--port PORT]",
    )
    parser.add_argument("directory", nargs="?", help="Path to directory to serve")
    parser.add_argument("--port", type=int, default=8080, help="Port number (default: 8080)")

    args = parser.parse_args()

    target = os.path.abspath(args.directory if args.directory else os.getcwd())
    if not os.path.isdir(target):
        print(f"Error: '{args.directory}' is not a valid directory.")
        sys.exit(1)

    global ROOT_DIR, PORT
    ROOT_DIR = target
    PORT = args.port

    ip = get_local_ip()

    server = http.server.ThreadingHTTPServer(("0.0.0.0", PORT), ViewerHandler)

    print(f"""
  Directory Viewer
  ────────────────────────────────
  Serving  {ROOT_DIR}

  Local    http://localhost:{PORT}
  Network  http://{ip}:{PORT}
  ────────────────────────────────
  Press Ctrl+C to stop
""", flush=True)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        server.server_close()


if __name__ == "__main__":
    main()
