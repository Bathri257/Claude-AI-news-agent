"""Collect recent AI articles from RSS feeds and fetch article text."""
from __future__ import annotations

import calendar
import html
import logging
import re
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from urllib.parse import urlparse, urlunparse

import feedparser
import trafilatura

from . import config
from .sources import FEEDS

log = logging.getLogger(__name__)

# Used to drop general-tech items (e.g. BBC Technology) that aren't about AI.
AI_KEYWORDS = re.compile(
    r"\b(ai|a\.i\.|artificial intelligence|machine learning|deep learning|llms?|"
    r"gpt|chatgpt|claude|gemini|llama|copilot|neural|generative|genai|chatbots?|"
    r"openai|anthropic|deepmind|nvidia|agents?|agentic|robot\w*|transformer|"
    r"diffusion|multimodal|inference|foundation model|computer vision|automation)\b",
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
    id: int = field(default=-1)


def _clean(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text or "")
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def normalize_link(link: str) -> str:
    p = urlparse(link)
    return urlunparse((p.scheme, p.netloc.lower(), p.path.rstrip("/"), "", "", ""))


def _parse_feed(source: str, url: str, cutoff: float) -> list[Article]:
    try:
        feed = feedparser.parse(url, agent=config.USER_AGENT)
    except Exception as exc:  # feedparser rarely raises, but be safe
        log.warning("Feed failed %s: %s", source, exc)
        return []
    if feed.bozo and not feed.entries:
        log.warning("Feed unreadable %s: %s", source, feed.get("bozo_exception"))
        return []

    out = []
    for e in feed.entries[:40]:
        ts_struct = e.get("published_parsed") or e.get("updated_parsed")
        ts = calendar.timegm(ts_struct) if ts_struct else 0.0
        if ts and ts < cutoff:
            continue
        title = _clean(e.get("title", ""))
        link = e.get("link", "")
        if not title or not link:
            continue
        snippet = _clean(e.get("summary", ""))[:600]
        out.append(Article(source, title, link, ts, snippet))
    log.info("%-26s %3d recent items", source, len(out))
    return out


def collect_candidates(seen_links: set[str]) -> list[Article]:
    cutoff = time.time() - config.LOOKBACK_HOURS * 3600
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = pool.map(lambda f: _parse_feed(f[0], f[1], cutoff), FEEDS)

    articles, links, titles = [], set(), set()
    for batch in results:
        for a in batch:
            key = normalize_link(a.link)
            tkey = re.sub(r"\W+", "", a.title.lower())[:80]
            if key in seen_links or key in links or tkey in titles:
                continue
            if not AI_KEYWORDS.search(f"{a.title} {a.snippet}"):
                continue
            links.add(key)
            titles.add(tkey)
            articles.append(a)

    articles.sort(key=lambda a: a.published, reverse=True)
    articles = articles[:200]
    for i, a in enumerate(articles):
        a.id = i
    log.info("Collected %d unique candidate articles", len(articles))
    return articles


def _fetch_text(article: Article) -> None:
    # Google News links are redirects; feed snippet is the best we have there.
    if "news.google.com" in article.link:
        article.text = article.snippet
        return
    try:
        downloaded = trafilatura.fetch_url(article.link)
        text = trafilatura.extract(downloaded, include_comments=False) if downloaded else None
    except Exception as exc:
        log.info("Could not fetch %s: %s", article.link, exc)
        text = None
    article.text = (text or article.snippet or "").strip()


def fetch_full_text(articles: list[Article]) -> None:
    with ThreadPoolExecutor(max_workers=6) as pool:
        list(pool.map(_fetch_text, articles))
