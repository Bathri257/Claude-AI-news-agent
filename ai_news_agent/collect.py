"""Collect articles from free, keyless sources (RSS, GDELT, Hacker News) and fetch article text."""
from __future__ import annotations

import calendar
import html
import json
import logging
import re
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime, timezone

import feedparser
import trafilatura

from . import config
from .sources import SOURCES

log = logging.getLogger(__name__)

AI_KEYWORDS = re.compile(
    r"\b(ai|a\.i\.|artificial intelligence|machine learning|deep learning|llms?|gpt|chatgpt|"
    r"claude|gemini|llama|copilot|neural|generative|genai|chatbots?|openai|anthropic|deepmind|"
    r"nvidia|ai agents?|agentic|robotics?|humanoid|transformer models?|diffusion model|multimodal|"
    r"foundation models?|computer vision|data cent(?:re|er)s?|semiconductors?|gpus?)\b",
    re.IGNORECASE,
)

INDIA = re.compile(
    r"\b(india|indian|bharat|bengaluru|bangalore|mumbai|delhi|hyderabad|pune|noida|gurugram|"
    r"meity|indiaai|sarvam|krutrim|bharatgpt|corover|infosys|tcs|wipro|hcltech|tech mahindra|"
    r"reliance|jio|nasscom|iit|iisc)\b",
    re.IGNORECASE,
)
TAMIL_NADU = re.compile(
    r"(tamil nadu|chennai|coimbatore|madurai|tiruchirappalli|trichy|salem|tirunelveli|vellore|"
    r"hosur|iit madras|iit-madras|zoho|freshworks|startuptn|tnega|guidance tamil nadu|தமிழ்)",
    re.IGNORECASE,
)


@dataclass
class Article:
    source: str
    title: str
    link: str
    published: float  # unix timestamp, 0 if unknown
    snippet: str
    text: str = ""


def clean(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text or "")
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def normalize_link(link: str) -> str:
    p = urllib.parse.urlparse(link)
    return urllib.parse.urlunparse((p.scheme, p.netloc.lower().removeprefix("www."), p.path.rstrip("/"), "", "", ""))


def india_relevance(text: str) -> str:
    if TAMIL_NADU.search(text):
        return "tamil_nadu"
    if INDIA.search(text):
        return "india"
    return "none"


def _get_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": config.USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def _rss(src: dict, cutoff: float) -> list[Article]:
    feed = feedparser.parse(src["url"], agent=config.USER_AGENT)
    if feed.bozo and not feed.entries:
        raise RuntimeError(feed.get("bozo_exception"))
    out = []
    for e in feed.entries[:50]:
        ts_struct = e.get("published_parsed") or e.get("updated_parsed")
        ts = calendar.timegm(ts_struct) if ts_struct else 0.0
        if ts and ts < cutoff:
            continue
        title, link = clean(e.get("title", "")), e.get("link", "")
        if title and link:
            out.append(Article(src["name"], title, link, ts, clean(e.get("summary", ""))[:600]))
    return out


def _gdelt(src: dict, cutoff: float) -> list[Article]:
    hours = max(1, int((time.time() - cutoff) / 3600))
    params = urllib.parse.urlencode({
        "query": src["url"], "mode": "artlist", "format": "json",
        "maxrecords": 75, "timespan": f"{hours}h", "sort": "datedesc",
    })
    try:
        data = _get_json(f"https://api.gdeltproject.org/api/v2/doc/doc?{params}")
    except json.JSONDecodeError as exc:  # GDELT answers query errors in plain text
        raise RuntimeError("GDELT rejected the query") from exc
    out = []
    for a in data.get("articles", []):
        try:
            ts = datetime.strptime(a.get("seendate", ""), "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc).timestamp()
        except ValueError:
            ts = 0.0
        if a.get("title") and a.get("url"):
            out.append(Article(a.get("domain") or "GDELT", clean(a["title"]), a["url"], ts, ""))
    return out


def _hn(src: dict, cutoff: float) -> list[Article]:
    params = urllib.parse.urlencode({
        "query": src["url"], "tags": "story", "hitsPerPage": 60,
        "numericFilters": f"created_at_i>{int(cutoff)},points>=40",
    })
    data = _get_json(f"https://hn.algolia.com/api/v1/search?{params}")
    out = []
    for h in data.get("hits", []):
        if h.get("url") and h.get("title"):
            out.append(Article("Hacker News", clean(h["title"]), h["url"], float(h.get("created_at_i", 0)),
                               f"{h.get('points', 0)} points on Hacker News"))
    return out


FETCHERS = {"rss": _rss, "gdelt": _gdelt, "hn": _hn}


def _fetch_source(src: dict, cutoff: float) -> list[Article] | None:
    """Articles from one source, or None if the source failed."""
    try:
        items = FETCHERS[src["kind"]](src, cutoff)
    except Exception as exc:
        log.warning("Source failed: %s (%s)", src["name"], exc)
        return None
    if not src.get("ai_only", True):
        items = [a for a in items if AI_KEYWORDS.search(f"{a.title} {a.snippet}")]
    log.info("%-34s %3d items", src["name"], len(items))
    return items


def collect_new(seen_links: set[str], lookback_hours: float) -> tuple[list[Article], dict[str, int]]:
    """Return (articles not seen before, newest first; per-source item counts, -1 = failed)."""
    cutoff = time.time() - lookback_hours * 3600
    others = [s for s in SOURCES if s["kind"] != "gdelt"]
    gdelt = [s for s in SOURCES if s["kind"] == "gdelt"]

    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(lambda s: _fetch_source(s, cutoff), others))
    for i, s in enumerate(gdelt):  # GDELT allows ~1 request per 5 seconds
        if i:
            time.sleep(6)
        results.append(_fetch_source(s, cutoff))
    stats = {s["name"]: (-1 if r is None else len(r)) for s, r in zip(others + gdelt, results)}
    batches = [r or [] for r in results]

    articles, links, titles = [], set(), set()
    for batch in batches:
        for a in batch:
            key = normalize_link(a.link)
            tkey = re.sub(r"\W+", "", a.title.lower())[:80]
            if key in seen_links or key in links or tkey in titles:
                continue
            links.add(key)
            titles.add(tkey)
            articles.append(a)
    articles.sort(key=lambda a: a.published, reverse=True)
    log.info("Collected %d new articles", len(articles))
    return articles, stats


def fetch_text(link: str, fallback: str = "") -> str:
    if "news.google.com" in link:  # redirect links; the snippet is all we have
        return fallback
    try:
        downloaded = trafilatura.fetch_url(link)
        text = trafilatura.extract(downloaded, include_comments=False) if downloaded else None
    except Exception as exc:
        log.info("Could not fetch %s: %s", link, exc)
        text = None
    return (text or fallback or "").strip()


def fetch_texts(links_and_fallbacks: list[tuple[str, str]]) -> list[str]:
    with ThreadPoolExecutor(max_workers=6) as pool:
        return list(pool.map(lambda lf: fetch_text(*lf), links_and_fallbacks))
