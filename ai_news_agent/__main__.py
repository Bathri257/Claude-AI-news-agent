"""CLI entry point.

  python -m ai_news_agent daily          # 4 AM: gather → shortlist (code) → one AI editor run → website
  python -m ai_news_agent daily --force  # rebuild today's digest
  python -m ai_news_agent check          # validate data/work/draft.json (used by the editor)
  python -m ai_news_agent email          # email today's digest
  python -m ai_news_agent email --wait   # wait until SEND_HOUR:SEND_MINUTE local time first
  python -m ai_news_agent site           # rebuild the website from saved digests
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from datetime import datetime

from . import config
from .collect import collect_new, normalize_link
from .editor import cmd_check, edit
from .reactions import cmd_reactions
from .emailer import send_digest
from .shortlist import cluster, shortlist
from .site import build_site

log = logging.getLogger("ai_news_agent")
STATE = config.DATA_DIR / "state.json"
KEEP_SEEN_DAYS = 7


def _digest_path(date: str):
    return config.DATA_DIR / f"digest-{date}.json"


def _load_state() -> dict:
    try:
        state = json.loads(STATE.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        state = {}
    state.setdefault("seen", {})        # links already sent -> unix time
    state.setdefault("runs", {})        # date -> unix time the window started
    state.setdefault("last_run", 0)
    return state


def _recent_headlines(today: str) -> str:
    lines = []
    for p in sorted(config.DATA_DIR.glob("digest-*.json"), reverse=True):
        if p.stem[7:] >= today:
            continue
        lines += [f"- {s['headline']}" for s in json.loads(p.read_text())["stories"]]
        if len(lines) > 60:
            break
    return "\n".join(lines)


def cmd_daily(force: bool = False) -> dict:
    date = config.today_local()
    path = _digest_path(date)
    if path.exists() and not force:
        log.info("Digest for %s already exists", date)
        return json.loads(path.read_text())

    state = _load_state()
    now = time.time()
    start = state["runs"].get(date) if force else None
    if start is None:
        start = state["last_run"] - 3600 if state["last_run"] else now - config.LOOKBACK_HOURS * 3600
        start = max(start, now - 36 * 3600)
    lookback = (now - start) / 3600

    articles = collect_new(set(state["seen"]), lookback)
    stories = cluster(articles)
    candidates = shortlist(stories, config.SHORTLIST_SIZE)
    log.info("%d articles → %d distinct stories → %d candidates", len(articles), len(stories), len(candidates))

    final, method = edit(candidates, _recent_headlines(date))
    by_id = {c["id"]: c for c in candidates}
    for s in final:
        c = by_id.get(s.get("candidate_id"))
        s["also_covered_by"] = sorted({x["source"] for x in c["coverage"][1:]} - {s["source"]})[:5] if c else []
        s["words"] = len(s["summary"].split())

    digest = {
        "date": date,
        "generated_at": datetime.now(config.TIMEZONE).isoformat(timespec="seconds"),
        "editor": method,
        "articles_scanned": len(articles),
        "candidates": len(candidates),
        "stories": final,
    }
    path.write_text(json.dumps(digest, indent=2, ensure_ascii=False))

    # Remember what was sent (including other outlets' links to the same story) for a week.
    for s in final:
        state["seen"][normalize_link(s["link"])] = now
        c = by_id.get(s.get("candidate_id"))
        for x in (c["coverage"] if c else []):
            state["seen"][normalize_link(x["link"])] = now
    state["seen"] = {k: v for k, v in state["seen"].items() if v >= now - KEEP_SEEN_DAYS * 86400}
    state["runs"][date] = start
    state["runs"] = dict(sorted(state["runs"].items())[-7:])
    state["last_run"] = now
    STATE.write_text(json.dumps(state, indent=1, sort_keys=True))

    build_site()
    log.info("Saved %d stories for %s (editor: %s)", len(final), date, method)
    return digest


def _wait_until_send_time() -> None:
    now = datetime.now(config.TIMEZONE)
    target = now.replace(hour=config.SEND_HOUR, minute=config.SEND_MINUTE, second=0, microsecond=0)
    delay = (target - now).total_seconds()
    if 0 < delay <= 3600:
        log.info("Waiting %.0f s until %s", delay, target.strftime("%H:%M %Z"))
        time.sleep(delay)


def cmd_email(wait: bool) -> None:
    path = _digest_path(config.today_local())
    # If the 4 AM run didn't happen (or failed), build the digest now.
    digest = json.loads(path.read_text()) if path.exists() else cmd_daily()
    if wait:
        _wait_until_send_time()
    send_digest(digest)


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    logging.getLogger("trafilatura").setLevel(logging.WARNING)
    parser = argparse.ArgumentParser(prog="ai_news_agent")
    sub = parser.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("daily")
    d.add_argument("--force", action="store_true", help="rebuild today's digest")
    sub.add_parser("check")
    sub.add_parser("reactions")
    e = sub.add_parser("email")
    e.add_argument("--wait", action="store_true", help="wait for the configured send time")
    sub.add_parser("site")
    args = parser.parse_args()

    if args.cmd == "check":
        logging.disable(logging.CRITICAL)
        return cmd_check()
    if args.cmd == "reactions":
        logging.disable(logging.INFO)
        return cmd_reactions()
    if args.cmd == "daily":
        cmd_daily(args.force)
    elif args.cmd == "email":
        cmd_email(args.wait)
    else:
        build_site()
    return 0


if __name__ == "__main__":
    sys.exit(main())
