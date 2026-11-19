"""CLI entry point.

  python -m ai_news_agent daily          # 4 AM: gather → shortlist (code) → one AI editor run → save
  python -m ai_news_agent daily --force  # rebuild today's edition
  python -m ai_news_agent check          # validate data/work/draft.json (used by the editor)
  python -m ai_news_agent app            # open your personal reading app (localhost)
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from datetime import date, timedelta

from . import config, reactions, store
from .collect import collect_new, normalize_link
from .editor import CANDIDATES, CONTEXT, HISTORY, PREFS, cmd_check, edit
from .prefs import preferences_note
from .shortlist import cluster, shortlist

log = logging.getLogger("ai_news_agent")
KEEP_SEEN_DAYS = 7


def _history(today: str) -> list[dict]:
    return [{k: s.get(k) for k in ("id", "date", "headline", "brief", "thread", "technology", "companies")}
            for s in store.recent_stories(today, config.HISTORY_DAYS)]


def _needs_reviews(today: str) -> list[dict]:
    """Stories from the last REACTION_DAYS days that haven't had their reviews collected."""
    return [s for s in store.recent_stories(today, config.REACTION_DAYS)
            if not s.get("reactions_checked")][:30]


def _source_health(state: dict, stats: dict[str, int], today: str) -> dict:
    for name, count in stats.items():
        h = state["sources"].setdefault(name, {"fails": 0, "picked": 0, "items": 0})
        if count < 0:
            h["fails"] += 1
        else:
            h["fails"], h["items"], h["last_ok"] = 0, h["items"] + count, today
    failing = sorted(n for n, h in state["sources"].items() if h["fails"] >= 2 and n in stats)
    return {"ok": sum(c >= 0 for c in stats.values()), "total": len(stats), "failing": failing}


def _token_warning() -> str:
    if not config.CLAUDE_TOKEN_CREATED:
        return ""
    try:
        age = (date.today() - date.fromisoformat(config.CLAUDE_TOKEN_CREATED)).days
    except ValueError:
        return ""
    left = 365 - age
    if left <= 0:
        return "Your Claude token has probably expired. Run `claude setup-token` and update the GitHub secret."
    if left <= 21:
        return f"Your Claude token expires in about {left} days. Run `claude setup-token` and update the GitHub secret."
    return ""


def cmd_daily(force: bool = False) -> dict:
    today = config.today_local()
    if store.load_digest(today) and not force:
        log.info("Edition for %s already exists", today)
        return store.load_digest(today)

    state = store.load_state()
    now = time.time()
    start = state["runs"].get(today) if force else None
    if start is not None and state.get("run_at", {}).get(today):
        # Rebuilding today: forget the links today's first run marked as covered.
        state["seen"] = {k: v for k, v in state["seen"].items() if v < state["run_at"][today]}
    if start is None:
        start = state["last_run"] - 3600 if state["last_run"] else now - config.LOOKBACK_HOURS * 3600
        start = max(start, now - 36 * 3600)

    # 1-2. Gather and shortlist (code only)
    articles, source_stats = collect_new(set(state["seen"]), (now - start) / 3600)
    candidates = shortlist(cluster(articles), config.SHORTLIST_SIZE)
    log.info("%d new articles → %d candidates", len(articles), len(candidates))

    # Reviews for the previous days' stories (discussion needs a day or so to build up)
    to_review = _needs_reviews(today)
    reaction_pool = reactions.gather(to_review) if to_review else {}

    # 3. Work files for the editor
    weekday = date.fromisoformat(today).weekday()
    week_start = (date.fromisoformat(today) - timedelta(days=6)).isoformat()
    history = _history(today)
    ctx = {"today": today, "recap": weekday == config.RECAP_WEEKDAY, "week_start": week_start,
           "history_ids": [h["id"] for h in history],
           "week_ids": [h["id"] for h in history if h["date"] >= week_start]}
    config.WORK_DIR.mkdir(parents=True, exist_ok=True)
    CANDIDATES.write_text(json.dumps(candidates, indent=1, ensure_ascii=False))
    HISTORY.write_text(json.dumps(history, indent=1, ensure_ascii=False))
    reactions.REACTIONS.write_text(json.dumps(reaction_pool, indent=1, ensure_ascii=False))
    PREFS.write_text(preferences_note())
    CONTEXT.write_text(json.dumps(ctx))
    ctx.update(candidates=candidates, reactions=reaction_pool)

    # 4. The one AI step
    result, editor = edit(ctx)

    # 5. Save: permanent ids, storyline links, reviews of earlier stories, weekly recap
    by_cand = {c["id"]: c for c in candidates}
    draft_to_id = {}
    for i, s in enumerate(result["stories"], 1):
        s["id"] = f"{today}-{i:02d}"
        draft_to_id[f"{today}-{s.pop('draft_index') + 1:02d}"] = s["id"]
        c = by_cand.get(s.get("candidate_id"))
        s["also_covered_by"] = sorted({x["source"] for x in c["coverage"][1:]} - {s["source"]})[:5] if c else []

    reviewed = []
    for day in {s["date"] for s in to_review}:
        old = store.load_digest(day)
        if not old:
            continue
        for s in old["stories"]:
            if s["id"] in reaction_pool:
                s["reactions_checked"] = True
                if s["id"] in result["past_reactions"]:
                    s["reactions"] = result["past_reactions"][s["id"]]
                    if s["reactions"]["reviews"]:
                        reviewed.append(s["id"])
        store.save_digest(old)

    weekly = result.get("weekly")
    if weekly:
        weekly["top"] = [draft_to_id.get(t, t) for t in weekly["top"]]
        weekly["from"] = week_start

    health = {
        "editor": editor, "editor_problem": ctx.get("claude_error", "") if editor != "claude-code" else "",
        "sources": _source_health(state, source_stats, today), "reviews": reactions.health(),
        "token_warning": _token_warning(),
    }
    digest = {
        "date": today, "generated_at": config.now_local().isoformat(timespec="seconds"),
        "articles_scanned": len(articles), "candidates": len(candidates),
        "stories": result["stories"], "opportunities": result["opportunities"],
        "reviewed_ids": sorted(reviewed), "weekly": weekly, "health": health,
    }
    store.save_digest(digest)

    # Remember covered links for a week; count which sources get picked.
    for s in result["stories"]:
        state["seen"][normalize_link(s["link"])] = now
        c = by_cand.get(s.get("candidate_id"))
        for x in (c["coverage"] if c else []):
            state["seen"][normalize_link(x["link"])] = now
        if s["source"] in state["sources"]:
            state["sources"][s["source"]]["picked"] += 1
    state["seen"] = {k: v for k, v in state["seen"].items() if v >= now - KEEP_SEEN_DAYS * 86400}
    state["runs"][today] = start
    state["runs"] = dict(sorted(state["runs"].items())[-7:])
    state["run_at"] = dict(sorted({**state.get("run_at", {}), today: now}.items())[-7:])
    state["last_run"] = now
    store.save_state(state)
    log.info("Saved %d stories, %d opportunities, %d reviewed stories for %s (editor: %s)",
             len(result["stories"]), len(result["opportunities"]), len(reviewed), today, editor)
    return digest


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    logging.getLogger("trafilatura").setLevel(logging.WARNING)
    parser = argparse.ArgumentParser(prog="ai_news_agent")
    sub = parser.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("daily")
    d.add_argument("--force", action="store_true", help="rebuild today's edition")
    sub.add_parser("check")
    a = sub.add_parser("app")
    a.add_argument("--no-sync", action="store_true", help="don't git pull / push")
    a.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()

    if args.cmd == "check":
        logging.disable(logging.CRITICAL)
        return cmd_check()
    if args.cmd == "daily":
        cmd_daily(args.force)
    else:
        from .app.server import run
        run(sync=not args.no_sync, open_browser=not args.no_browser)
    return 0


if __name__ == "__main__":
    sys.exit(main())
