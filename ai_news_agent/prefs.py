"""Turn your 👍 / 👎 / "more like this" clicks into a short note for the editor (no AI)."""
from __future__ import annotations

from collections import Counter

from . import store

WEIGHT = {"more": 2, "up": 1, "down": -1}


def preferences_note(days: int = 60) -> str:
    feedback = store.load_feedback()
    if not feedback:
        return "No feedback yet. Use your judgement."
    stories = {s["id"]: s for s in store.all_stories()[-days * 20:]}
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
    lines = ["# What the reader liked and skipped recently (from their 👍 / 👎)"]
    if likes:
        lines.append("More interested in: " + ", ".join(likes))
    if dislikes:
        lines.append("Less interested in: " + ", ".join(dislikes))
    if liked:
        lines.append("\nRecently liked:\n" + "\n".join(f"- {h}" for h in liked[:10]))
    if skipped:
        lines.append("\nRecently disliked:\n" + "\n".join(f"- {h}" for h in skipped[:8]))
    return "\n".join(lines)
