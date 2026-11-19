"""Turn your 👍 / 👎 / "more like this" clicks into a short note for the editor (no AI)."""
from __future__ import annotations

from collections import Counter

from . import store

WEIGHT = {"more": 2, "up": 1, "down": -1}


def _interests_lines(stories: dict) -> list[str]:
    it = store.load_interests()
    lines = []
    if it["follow"]:
        lines.append("FOLLOWS (topics, companies, technologies): " + ", ".join(it["follow"]))
    if it["mute"]:
        lines.append("MUTES (leave out unless truly major): " + ", ".join(it["mute"]))
    names = [stories[i].get("thread") or stories[i]["headline"] for i in it["storylines"] if i in stories]
    if names:
        lines.append("FOLLOWS these storylines (always include genuine new developments): " + "; ".join(names))
    lines.append("Focus cities: " + ", ".join(it["cities"] or ["none"]))
    return lines


def preferences_note(days: int = 60) -> str:
    feedback = store.load_feedback()
    stories = {s["id"]: s for s in store.all_stories()[-days * 20:]}
    head = ["# The reader's focus (set in the app)", *_interests_lines(stories)]
    if not feedback:
        return "\n".join(head + ["", "No 👍 / 👎 feedback yet."])
    score: Counter = Counter()
    liked, skipped = [], []
    for sid, fb in sorted(feedback.items(), key=lambda kv: kv[1].get("at", ""), reverse=True):
        s = stories.get(sid)
        if not s or fb.get("vote") not in WEIGHT:
            continue
        w = WEIGHT[fb["vote"]]
        for key in [s.get("category"), s.get("thread"), *(s.get("companies") or [])[:2],
                    "India / Tamil Nadu" if s.get("india") != "none" else None]:
            if key:
                score[key] += w
        (liked if w > 0 else skipped).append(s["headline"])
    likes = [k for k, v in score.most_common() if v > 0][:8]
    dislikes = [k for k, v in sorted(score.items(), key=lambda kv: kv[1]) if v < 0][:6]
    lines = head + ["", "# What the reader liked and skipped recently (from their 👍 / 👎)"]
    if likes:
        lines.append("More interested in: " + ", ".join(likes))
    if dislikes:
        lines.append("Less interested in: " + ", ".join(dislikes))
    if liked:
        lines.append("\nRecently liked:\n" + "\n".join(f"- {h}" for h in liked[:10]))
    if skipped:
        lines.append("\nRecently disliked:\n" + "\n".join(f"- {h}" for h in skipped[:8]))
    return "\n".join(lines)
