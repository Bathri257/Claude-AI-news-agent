"""Reading and writing the agent's files in data/.

data/digests/YYYY-MM-DD.json   one edition per day (stories, opportunities, recap, health)
data/state.json                links already covered, run times, source health
data/feedback.json             your 👍 / 👎 / "more like this" from the app
"""
from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

from . import config


def _read(path: Path, default):
    try:
        return json.loads(path.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def _write(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=1, ensure_ascii=False))
    tmp.replace(path)


# ---- digests

def digest_path(day: str) -> Path:
    return config.DIGESTS_DIR / f"{day}.json"


def load_digest(day: str) -> dict | None:
    return _read(digest_path(day), None)


def save_digest(digest: dict) -> None:
    _write(digest_path(digest["date"]), digest)


def digest_dates() -> list[str]:
    return sorted(p.stem for p in config.DIGESTS_DIR.glob("*.json"))


def days_before(day: str, n: int) -> list[str]:
    d = date.fromisoformat(day)
    return [(d - timedelta(days=i)).isoformat() for i in range(1, n + 1)]


def recent_stories(today: str, days: int) -> list[dict]:
    """Stories published in the `days` days before `today`, newest first, with their date."""
    out = []
    for day in days_before(today, days):
        digest = load_digest(day)
        for s in (digest or {}).get("stories", []):
            out.append({**s, "date": day})
    return out


def all_stories() -> list[dict]:
    out = []
    for day in digest_dates():
        for s in load_digest(day)["stories"]:
            out.append({**s, "date": day})
    return out


# ---- state and feedback

def load_state() -> dict:
    state = _read(config.STATE_FILE, {})
    state.setdefault("seen", {})       # covered links -> unix time
    state.setdefault("runs", {})       # date -> unix time the collection window started
    state.setdefault("last_run", 0)
    state.setdefault("sources", {})    # source name -> health and usefulness stats
    return state


def save_state(state: dict) -> None:
    _write(config.STATE_FILE, state)


def load_feedback() -> dict:
    return _read(config.FEEDBACK_FILE, {})


def save_feedback(feedback: dict) -> None:
    _write(config.FEEDBACK_FILE, feedback)


def load_interests() -> dict:
    data = _read(config.INTERESTS_FILE, {})
    for key in ("follow", "mute", "storylines"):
        data.setdefault(key, [])
    data.setdefault("cities", list(config.FOCUS_CITIES))
    return data


def save_interests(data: dict) -> None:
    _write(config.INTERESTS_FILE, data)
