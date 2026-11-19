"""Your private reading app: a tiny local web server (standard library only).

    python -m ai_news_agent app

- Listens on 127.0.0.1 only, so nothing outside your computer can reach it.
- On start it runs `git pull` to fetch the editions GitHub Actions made overnight.
- Your 👍 / 👎 / "more like this" are saved to data/feedback.json and pushed back to GitHub
  (a few seconds later, batched) so tomorrow's editor can use them.
"""
from __future__ import annotations

import json
import logging
import re
import subprocess
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from .. import config, store, threads

log = logging.getLogger(__name__)
HERE = Path(__file__).resolve().parent
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
ID_RE = re.compile(r"^\d{4}-\d{2}-\d{2}-\d{2}$")
VOTES = {"up", "down", "more"}


# ---------------------------------------------------------------- git sync

class Sync:
    def __init__(self, enabled: bool):
        self.enabled = enabled and (config.ROOT / ".git").exists()
        self.status = "off" if not self.enabled else "not synced yet"
        self.last = 0.0
        self._lock = threading.Lock()
        self._timer: threading.Timer | None = None

    def _git(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(["git", *args], cwd=config.ROOT, capture_output=True, text=True, timeout=60)

    def pull(self) -> str:
        if not self.enabled:
            return self.status
        with self._lock:
            r = self._git("pull", "--rebase", "--autostash")
            self.status = "synced" if r.returncode == 0 else f"pull failed: {(r.stderr or r.stdout).strip()[:160]}"
            self.last = time.time()
        return self.status

    def push_feedback_soon(self) -> None:
        if not self.enabled:
            return
        if self._timer:
            self._timer.cancel()
        self._timer = threading.Timer(8, self._push)
        self._timer.daemon = True
        self._timer.start()

    def _push(self) -> None:
        with self._lock:
            self._git("add", str(config.FEEDBACK_FILE.relative_to(config.ROOT)))
            if self._git("diff", "--cached", "--quiet").returncode == 0:
                return
            self._git("commit", "-m", "Reader feedback")
            self._git("pull", "--rebase", "--autostash")
            r = self._git("push")
            self.status = "synced" if r.returncode == 0 else f"push failed: {(r.stderr or r.stdout).strip()[:160]}"
            self.last = time.time()


SYNC = Sync(False)


# ---------------------------------------------------------------- data views

def _light(s: dict) -> dict:
    keep = ("id", "date", "headline", "brief", "summary", "link", "source", "thread", "category",
            "technology", "india", "tier", "reactions")
    return {k: s.get(k) for k in keep}


def _with_chains(stories: list[dict], chains: dict) -> list[dict]:
    out = []
    for s in stories:
        chain = chains.get(s["id"], [s])
        item = dict(s)
        item["storyline"] = {
            "day": threads.day_number(chain, s),
            "days": len({m["date"] for m in chain}),
            "items": [_light(m) for m in chain if m["id"] != s["id"]],
        }
        out.append(item)
    return out


def api_index() -> dict:
    stories = store.all_stories()
    days = []
    for d in reversed(store.digest_dates()):
        dg = store.load_digest(d)
        days.append({"date": d, "count": len(dg["stories"]), "weekly": bool(dg.get("weekly")),
                     "lead": dg["stories"][0]["headline"] if dg["stories"] else ""})
    return {
        "days": days,
        "search": [{k: s.get(k) for k in ("id", "date", "headline", "brief", "thread", "category",
                                          "technology", "india")} for s in stories],
        "storylines": threads.storylines(stories)[:60],
        "feedback": {k: v.get("vote") for k, v in store.load_feedback().items()},
        "sync": {"status": SYNC.status, "last": SYNC.last},
    }


def api_day(day: str) -> dict | None:
    digest = store.load_digest(day)
    if not digest:
        return None
    all_s = store.all_stories()
    chains = threads.build(all_s)
    by_id = {s["id"]: s for s in all_s}
    today_stories = [{**s, "date": day} for s in digest["stories"]]
    out = dict(digest)
    out["stories"] = _with_chains(today_stories, chains)
    out["reviewed"] = _with_chains([by_id[i] for i in digest.get("reviewed_ids", []) if i in by_id], chains)
    if digest.get("weekly"):
        out["weekly"] = {**digest["weekly"], "stories": [_light(by_id[i]) for i in digest["weekly"]["top"] if i in by_id]}
    return out


def api_storyline(sid: str) -> dict | None:
    all_s = store.all_stories()
    chain = threads.build(all_s).get(sid)
    if not chain:
        return None
    return {"name": chain[-1].get("thread") or chain[-1]["headline"], "items": [_light(s) for s in chain]}


def save_vote(sid: str, vote: str | None) -> None:
    feedback = store.load_feedback()
    if vote:
        feedback[sid] = {"vote": vote, "at": config.now_local().isoformat(timespec="seconds")}
    else:
        feedback.pop(sid, None)
    store.save_feedback(feedback)
    SYNC.push_feedback_soon()


# ---------------------------------------------------------------- HTTP

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):  # keep the terminal quiet
        pass

    def _send(self, code: int, body: bytes, ctype: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _json(self, data, code: int = 200) -> None:
        self._send(code, json.dumps(data, ensure_ascii=False).encode(), "application/json; charset=utf-8")

    def do_GET(self):
        path = self.path.split("?")[0]
        if path in ("/", "/index.html"):
            return self._send(200, (HERE / "index.html").read_bytes(), "text/html; charset=utf-8")
        if path == "/api/index":
            return self._json(api_index())
        m = re.match(r"^/api/day/(.+)$", path)
        if m and DATE_RE.match(m.group(1)):
            data = api_day(m.group(1))
            return self._json(data) if data else self._json({"error": "no edition"}, 404)
        m = re.match(r"^/api/storyline/(.+)$", path)
        if m and ID_RE.match(m.group(1)):
            data = api_storyline(m.group(1))
            return self._json(data) if data else self._json({"error": "not found"}, 404)
        self._json({"error": "not found"}, 404)

    def do_POST(self):
        # Only accept requests from the app's own page.
        origin = self.headers.get("Origin", "")
        if origin and not re.match(rf"^http://(127\.0\.0\.1|localhost):{config.APP_PORT}$", origin):
            return self._json({"error": "forbidden"}, 403)
        length = min(int(self.headers.get("Content-Length") or 0), 10_000)
        try:
            body = json.loads(self.rfile.read(length) or b"{}")
        except json.JSONDecodeError:
            return self._json({"error": "bad json"}, 400)
        if self.path == "/api/feedback":
            sid, vote = body.get("id", ""), body.get("vote")
            if not ID_RE.match(str(sid)) or (vote is not None and vote not in VOTES):
                return self._json({"error": "bad feedback"}, 400)
            save_vote(sid, vote)
            return self._json({"ok": True})
        if self.path == "/api/sync":
            return self._json({"status": SYNC.pull()})
        self._json({"error": "not found"}, 404)


def run(sync: bool = True, open_browser: bool = True) -> None:
    global SYNC
    SYNC = Sync(sync)
    if SYNC.enabled:
        print("Fetching the latest editions…", SYNC.pull())
    server = ThreadingHTTPServer(("127.0.0.1", config.APP_PORT), Handler)
    url = f"http://127.0.0.1:{config.APP_PORT}/"
    print(f"The Morning Brief is open at {url}  (Ctrl+C to close)")
    if open_browser:
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        if SYNC._timer:
            SYNC._timer.cancel()
            SYNC._push()
        server.server_close()
