"""The rolling story pool: everything gathered by the scans since the last digest.

Each story is one real-world event; extra articles about the same event are merged into
its `coverage` list (more coverage = a stronger signal that it matters).
"""
from __future__ import annotations

import json
import time

from . import config

POOL_FILE = config.DATA_DIR / "pool.json"
KEEP_DAYS = 7


def load() -> dict:
    try:
        pool = json.loads(POOL_FILE.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        pool = {}
    pool.setdefault("stories", [])
    pool.setdefault("seen_links", {})  # normalized link -> unix time first seen
    pool.setdefault("last_digest_at", 0)
    pool.setdefault("next_id", 1)
    return pool


def save(pool: dict) -> None:
    cutoff = time.time() - KEEP_DAYS * 86400
    pool["stories"] = [s for s in pool["stories"] if s["first_seen"] >= cutoff]
    pool["seen_links"] = {k: v for k, v in pool["seen_links"].items() if v >= cutoff}
    config.DATA_DIR.mkdir(exist_ok=True)
    POOL_FILE.write_text(json.dumps(pool, indent=1, ensure_ascii=False))


def window(pool: dict) -> list[dict]:
    """Candidate stories gathered since the previous digest (max 36 hours back)."""
    since = max(pool["last_digest_at"], time.time() - 36 * 3600)
    return [s for s in pool["stories"] if s["status"] == "candidate" and s["first_seen"] >= since]


def score(story: dict) -> float:
    """Importance plus a bonus for being covered by several independent outlets."""
    return story["importance"] + 0.6 * min(len(story["coverage"]) - 1, 5)
