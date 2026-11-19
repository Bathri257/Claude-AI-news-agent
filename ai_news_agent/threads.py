"""Storylines: chain today's story to earlier stories about the same thing.

The editor marks each new story's `related` earlier story ids. Here those links are
joined into connected groups, so a story published on day 3 shows days 1 and 2 as well.
"""
from __future__ import annotations

from collections import defaultdict


def build(stories: list[dict]) -> dict[str, list[dict]]:
    """Map every story id to its full storyline (oldest first)."""
    by_id = {s["id"]: s for s in stories}
    parent = {sid: sid for sid in by_id}

    def find(x: str) -> str:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for s in stories:
        for other in s.get("related", []):
            if other in by_id:
                parent[find(other)] = find(s["id"])

    groups: dict[str, list[dict]] = defaultdict(list)
    for sid, s in by_id.items():
        groups[find(sid)].append(s)
    chains = {}
    for members in groups.values():
        members.sort(key=lambda s: (s["date"], s["id"]))
        for s in members:
            chains[s["id"]] = members
    return chains


def storylines(stories: list[dict], min_len: int = 2) -> list[dict]:
    """Storylines with at least `min_len` stories, most recently active first."""
    seen, out = set(), []
    for members in build(stories).values():
        key = members[0]["id"]
        if key in seen or len(members) < min_len:
            continue
        seen.add(key)
        latest = members[-1]
        out.append({
            "name": latest.get("thread") or latest["headline"],
            "first": members[0]["date"], "last": latest["date"],
            "days": len({m["date"] for m in members}),
            "ids": [m["id"] for m in members],
            "latest_headline": latest["headline"],
        })
    out.sort(key=lambda t: (t["last"], t["days"]), reverse=True)
    return out


def day_number(chain: list[dict], story: dict) -> int:
    """1 for a new storyline, 2 for its second day of coverage, and so on."""
    dates = sorted({m["date"] for m in chain})
    return dates.index(story["date"]) + 1
