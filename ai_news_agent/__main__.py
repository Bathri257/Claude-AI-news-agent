"""CLI entry point.

  python -m ai_news_agent scan          # gather + triage new articles into the pool (every 4 hours)
  python -m ai_news_agent fetch         # final scan, pick the top 15-20, summarise, build site (4 AM)
  python -m ai_news_agent email         # email today's digest (8 AM)
  python -m ai_news_agent email --wait  # sleep until SEND_HOUR:SEND_MINUTE local time first
  python -m ai_news_agent site          # rebuild the website from saved digests
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from datetime import datetime

from . import config, pool as pool_mod
from .collect import collect_new
from .curate import curate
from .emailer import send_digest
from .site import build_site
from .summarize import summarize
from .triage import triage

log = logging.getLogger("ai_news_agent")


def _digest_path(date: str):
    return config.DATA_DIR / f"digest-{date}.json"


def cmd_scan(pool: dict | None = None) -> dict:
    pool = pool or pool_mod.load()
    articles = collect_new(set(pool["seen_links"]), config.LOOKBACK_HOURS)
    before = len(pool["stories"])
    method = triage(pool, articles)
    pool_mod.save(pool)
    log.info("Scan: %d new articles -> %d new stories (%s); %d candidates in today's window",
             len(articles), len(pool["stories"]) - before, method, len(pool_mod.window(pool)))
    return pool


def cmd_fetch(force: bool = False) -> dict:
    date = config.today_local()
    path = _digest_path(date)
    if path.exists() and not force:
        log.info("Digest for %s already exists", date)
        return json.loads(path.read_text())

    pool = pool_mod.load()
    if force and pool.get("window_start", {}).get(date) is not None:
        # Re-running today's digest: reopen today's window and stories.
        pool["last_digest_at"] = pool["window_start"][date]
        for s in pool["stories"]:
            if s.get("used_on") == date:
                s["status"] = "candidate"
    pool = cmd_scan(pool)  # one last catch-up before choosing
    candidates = pool_mod.window(pool)
    chosen, curate_method = curate(candidates)
    stories, summary_method = summarize(chosen)

    digest = {
        "date": date,
        "generated_at": datetime.now(config.TIMEZONE).isoformat(timespec="seconds"),
        "method": {"curation": curate_method, "summaries": summary_method},
        "candidates": len(candidates),
        "sources_seen": len({c["source"] for s in candidates for c in s["coverage"]}),
        "stories": stories,
    }
    path.write_text(json.dumps(digest, indent=2, ensure_ascii=False))

    chosen_ids = {s["id"] for s in chosen}
    for s in pool["stories"]:
        if s["id"] in chosen_ids:
            s["status"], s["used_on"] = "used", date
    pool.setdefault("window_start", {})[date] = pool["last_digest_at"]
    pool["window_start"] = dict(sorted(pool["window_start"].items())[-7:])
    pool["last_digest_at"] = time.time()
    pool_mod.save(pool)

    build_site()
    log.info("Saved %d stories for %s from %d candidates", len(stories), date, len(candidates))
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
    logging.getLogger("trafilatura").setLevel(logging.WARNING)
    parser = argparse.ArgumentParser(prog="ai_news_agent")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("scan")
    f = sub.add_parser("fetch")
    f.add_argument("--force", action="store_true", help="rebuild today's digest")
    e = sub.add_parser("email")
    e.add_argument("--wait", action="store_true", help="wait for the configured send time")
    sub.add_parser("site")
    args = parser.parse_args()

    if args.cmd == "scan":
        cmd_scan()
    elif args.cmd == "fetch":
        cmd_fetch(args.force)
    elif args.cmd == "email":
        cmd_email(args.wait)
    else:
        build_site()
    return 0


if __name__ == "__main__":
    sys.exit(main())
