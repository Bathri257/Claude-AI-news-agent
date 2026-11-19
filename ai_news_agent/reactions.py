"""Find what real users say about each chosen story on open platforms.

Sources (all free):
  - Hacker News (Algolia API, no key): developer discussion, often hands-on.
  - Reddit: with REDDIT_CLIENT_ID / REDDIT_CLIENT_SECRET (a free personal "script" app)
    it uses the official API; without them it tries Reddit's public JSON, which Reddit
    sometimes blocks for cloud servers.
Discord, X/Twitter etc. are not used: Discord is closed (login-only servers) and X's API is paid.

Reviews are gathered a day late on purpose: discussion of a story usually peaks 12-48 hours
after the news, so each morning we look at the previous days' stories, not today's.

Only real comments are collected here. The editor may quote them, and `check` verifies
that every quoted review exists word-for-word in reactions.json, so reviews can't be invented.
"""
from __future__ import annotations

import base64
import html
import json
import logging
import os
import re
import threading
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

from . import config

log = logging.getLogger(__name__)

REACTIONS = config.WORK_DIR / "reactions.json"
UA = "python:ai-daily-brief:v1.0 (personal news digest)"
PER_STORY = 12          # comments kept per story for the editor to choose from
MIN_WORDS, MAX_WORDS = 12, 220
BOTS = {"automoderator", "[deleted]", "[removed]"}
_reddit_token: str | None = None
_reddit_lock = threading.Lock()
STATS = {"hn_ok": 0, "hn_fail": 0, "reddit_ok": 0, "reddit_fail": 0, "reddit_mode": "public"}


def _get(url: str, headers: dict | None = None, data: bytes | None = None) -> dict:
    req = urllib.request.Request(url, data=data, headers={"User-Agent": UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def _clean(text: str) -> str:
    text = re.sub(r"<p>", "\n", text or "")
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)  # markdown links -> text
    text = re.sub(r"https?://\S+", "", text)
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def _keep(text: str, author: str = "") -> bool:
    n = len(text.split())
    return MIN_WORDS <= n <= MAX_WORDS and author.lower() not in BOTS and not text.startswith(">")


# ---------------------------------------------------------------- Hacker News

def _hn(story: dict, since: int) -> list[dict]:
    hits = []
    base = "https://hn.algolia.com/api/v1/search?"
    host_path = re.sub(r"^https?://(www\.)?", "", story["link"]).split("?")[0]
    queries = [
        {"query": host_path, "restrictSearchableAttributes": "url", "tags": "story"},
        {"query": story["search_terms"], "tags": "story", "numericFilters": f"created_at_i>{since},num_comments>5"},
    ]
    for q in queries:
        try:
            hits += _get(base + urllib.parse.urlencode(q)).get("hits", [])
            STATS["hn_ok"] += 1
        except Exception as exc:
            STATS["hn_fail"] += 1
            log.info("HN search failed: %s", exc)
    threads = {h["objectID"]: h for h in hits if (h.get("num_comments") or 0) > 0}
    best = sorted(threads.values(), key=lambda h: h.get("points") or 0, reverse=True)[:2]

    comments = []
    for t in best:
        try:
            item = _get(f"https://hn.algolia.com/api/v1/items/{t['objectID']}")
        except Exception as exc:
            log.info("HN item failed: %s", exc)
            continue
        for c in item.get("children", [])[:40]:
            text = _clean(c.get("text") or "")
            if _keep(text, c.get("author") or ""):
                comments.append({
                    "platform": "Hacker News", "community": "Hacker News",
                    "thread": t.get("title", ""), "text": text,
                    "score": len(c.get("children", [])),  # replies as a proxy (HN hides comment points)
                    "link": f"https://news.ycombinator.com/item?id={c['id']}",
                })
    return comments


# ---------------------------------------------------------------- Reddit

def _reddit_auth() -> dict | None:
    global _reddit_token
    cid, secret = os.getenv("REDDIT_CLIENT_ID"), os.getenv("REDDIT_CLIENT_SECRET")
    if not (cid and secret):
        return None
    with _reddit_lock:
        if _reddit_token is None:
            basic = base64.b64encode(f"{cid}:{secret}".encode()).decode()
            data = _get("https://www.reddit.com/api/v1/access_token",
                        headers={"Authorization": f"Basic {basic}"},
                        data=b"grant_type=client_credentials")
            _reddit_token = data["access_token"]
    return {"Authorization": f"Bearer {_reddit_token}"}


def _reddit(story: dict) -> list[dict]:
    try:
        auth = _reddit_auth()
    except Exception as exc:
        log.warning("Reddit login failed: %s", exc)
        auth = None
    STATS["reddit_mode"] = "api" if auth else "public"
    host = "https://oauth.reddit.com" if auth else "https://www.reddit.com"
    suffix = "" if auth else ".json"

    posts = []
    url_q = "url:" + re.sub(r"^https?://(www\.)?", "", story["link"]).split("?")[0]
    for q in (url_q, story["search_terms"]):
        params = urllib.parse.urlencode({"q": q, "sort": "relevance", "t": "week", "limit": 6, "raw_json": 1})
        try:
            data = _get(f"{host}/search{suffix}?{params}", headers=auth)
            posts += [c["data"] for c in data["data"]["children"]]
            STATS["reddit_ok"] += 1
        except Exception as exc:
            STATS["reddit_fail"] += 1
            log.info("Reddit search failed (%s): %s", "api" if auth else "public", exc)
            break
        time.sleep(1.0)
    seen, threads = set(), []
    for p in sorted(posts, key=lambda p: p.get("num_comments", 0), reverse=True):
        if p["id"] not in seen and p.get("num_comments", 0) >= 5:
            seen.add(p["id"])
            threads.append(p)
    comments = []
    for p in threads[:2]:
        try:
            data = _get(f"{host}/comments/{p['id']}{suffix}?sort=top&limit=40&depth=1&raw_json=1", headers=auth)
        except Exception as exc:
            log.info("Reddit comments failed: %s", exc)
            continue
        time.sleep(1.0)
        for c in data[1]["data"]["children"]:
            d = c.get("data", {})
            text = _clean(d.get("body") or "")
            if c.get("kind") == "t1" and _keep(text, d.get("author") or "") and (d.get("score") or 0) >= 3:
                comments.append({
                    "platform": "Reddit", "community": f"r/{p.get('subreddit', '')}",
                    "thread": p.get("title", ""), "text": text, "score": d.get("score", 0),
                    "link": f"https://www.reddit.com{d.get('permalink', '')}",
                })
    return comments


# ---------------------------------------------------------------- public

def _terms(story: dict) -> str:
    terms = (story.get("search_terms") or "").strip()
    if terms:
        return terms
    words = [w for w in re.findall(r"[A-Za-z0-9.\-]+", story.get("headline", "")) if len(w) > 2]
    return " ".join(words[:5])


def gather(stories: list[dict]) -> dict:
    """Collect candidate user comments for each story, keyed by story id."""
    since = int(time.time() - 10 * 86400)
    fixture = json.loads(open(os.environ["REACTIONS_FIXTURE"]).read()) if os.getenv("REACTIONS_FIXTURE") else None

    def one(s: dict) -> dict:
        s = {**s, "search_terms": _terms(s)}
        if fixture is not None:  # offline testing: {keyword: [comments]}
            text = f"{s.get('headline', '')} {s['search_terms']}".lower()
            comments = [c for k, cs in fixture.items() if k.lower() in text for c in cs]
        else:
            comments = _hn(s, since) + _reddit(s)
        comments.sort(key=lambda c: c["score"], reverse=True)
        return {"headline": s.get("headline", ""), "date": s.get("date", ""),
                "search_terms": s["search_terms"], "comments": comments[:PER_STORY]}

    # Two at a time keeps Reddit under its rate limit (~100 requests/minute).
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(one, stories))
    out = {s["id"]: r for s, r in zip(stories, results)}
    log.info("Reactions: %d comments for %d stories (HN ok/fail %d/%d, Reddit %s ok/fail %d/%d)",
             sum(len(v["comments"]) for v in out.values()), len(out), STATS["hn_ok"], STATS["hn_fail"],
             STATS["reddit_mode"], STATS["reddit_ok"], STATS["reddit_fail"])
    return out


def health() -> dict:
    def status(ok: int, fail: int) -> str:
        return "unused" if ok + fail == 0 else ("ok" if ok else "failing")
    return {"hacker_news": status(STATS["hn_ok"], STATS["hn_fail"]),
            "reddit": status(STATS["reddit_ok"], STATS["reddit_fail"]),
            "reddit_mode": STATS["reddit_mode"]}


# ---------------------------------------------------------------- verification

def _norm(text: str) -> str:
    text = text.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    return re.sub(r"\s+", " ", text).strip().lower()


def verify_review(review: dict, story_id: str, reactions: dict) -> str | None:
    """Return an error message if the review doesn't match a collected comment word-for-word."""
    pool = reactions.get(story_id, {}).get("comments", [])
    match = next((c for c in pool if c["link"] == review.get("link")), None)
    if match is None:
        return "its link is not one of the collected comments for this story"
    quote = _norm(str(review.get("quote", "")).strip(' "…'))
    if not quote or any(part and part not in _norm(match["text"]) for part in quote.split("…")):
        return "its quote is not an exact excerpt of that comment"
    if len(quote.split()) > 45:
        return "its quote is longer than 45 words"
    return None


def auto_pick(reactions: dict) -> dict:
    """Fallback when no AI editor ran: the top-voted comments as-is, keyed by story id."""
    out = {}
    for sid, entry in reactions.items():
        picks = entry.get("comments", [])[:2]
        reviews = []
        for c in picks:
            words = c["text"].split()
            quote = " ".join(words[:40]) + ("…" if len(words) > 40 else "")
            reviews.append({"platform": c["platform"], "community": c["community"], "quote": quote,
                            "takeaway": "", "link": c["link"], "score": c["score"]})
        out[sid] = {"pulse": "", "sentiment": "none", "reviews": reviews, "auto": True}
    return out
