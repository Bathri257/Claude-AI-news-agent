"""CLI entry point.

  python -m ai_news_agent fetch        # collect + summarise + rebuild website (4 AM job)
  python -m ai_news_agent email        # email today's digest (8 AM job)
  python -m ai_news_agent email --wait # sleep until SEND_HOUR:SEND_MINUTE local time first
  python -m ai_news_agent site         # rebuild the website from saved digests
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from datetime import datetime, timedelta

from . import config
from .collect import collect_candidates, fetch_full_text, normalize_link
from .emailer import send_digest
from .site import build_site
from .summarize import build_stories

log = logging.getLogger("ai_news_agent")
SEEN_FILE = config.DATA_DIR / "seen.json"


def _digest_path(date: str):
    return config.DATA_DIR / f"digest-{date}.json"


def _load_seen() -> dict[str, str]:
    try:
        return json.loads(SEEN_FILE.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def cmd_fetch(force: bool = False) -> dict:
    date = config.today_local()
    path = _digest_path(date)
    if path.exists() and not force:
        log.info("Digest for %s already exists", date)
        return json.loads(path.read_text())

    config.DATA_DIR.mkdir(exist_ok=True)
    seen = _load_seen()
    candidates = collect_candidates(set(seen))
    stories, method = build_stories(candidates, fetch_full_text)

    digest = {
        "date": date,
        "generated_at": datetime.now(config.TIMEZONE).isoformat(timespec="seconds"),
        "method": method,
        "candidates": len(candidates),
        "stories": stories,
    }
    path.write_text(json.dumps(digest, indent=2, ensure_ascii=False))

    # Remember what we've covered for a week so stories don't repeat.
    cutoff = (datetime.now(config.TIMEZONE) - timedelta(days=7)).strftime("%Y-%m-%d")
    seen = {k: v for k, v in seen.items() if v >= cutoff}
    for s in stories:
        seen[normalize_link(s["link"])] = date
    SEEN_FILE.write_text(json.dumps(seen, indent=1, sort_keys=True))

    build_site()
    log.info("Saved %d stories for %s (%s)", len(stories), date, method)
    return digest


def _wait_until_send_time() -> None:
    now = datetime.now(config.TIMEZONE)
    target = now.replace(hour=config.SEND_HOUR, minute=config.SEND_MINUTE, second=0, microsecond=0)
    delay = (target - now).total_seconds()
    if 0 < delay <= 3 * 3600:
        log.info("Waiting %.0f s until %s", delay, target.strftime("%H:%M %Z"))
        time.sleep(delay)


def cmd_email(wait: bool) -> None:
    path = _digest_path(config.today_local())
    # If the 4 AM job didn't run (or failed), build the digest now.
    digest = json.loads(path.read_text()) if path.exists() else cmd_fetch()
    if wait:
        _wait_until_send_time()
    send_digest(digest)


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    parser = argparse.ArgumentParser(prog="ai_news_agent")
    sub = parser.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("fetch")
    f.add_argument("--force", action="store_true", help="rebuild today's digest")
    e = sub.add_parser("email")
    e.add_argument("--wait", action="store_true", help="wait for the configured send time")
    sub.add_parser("site")
    args = parser.parse_args()

    if args.cmd == "fetch":
        cmd_fetch(args.force)
    elif args.cmd == "email":
        cmd_email(args.wait)
    else:
        build_site()
    return 0


if __name__ == "__main__":
    sys.exit(main())
