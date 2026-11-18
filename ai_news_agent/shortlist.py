"""Free, code-only preparation (no AI): group duplicate articles, score, shortlist.

Turns a few hundred raw articles into ~70 distinct candidate stories, keeping enough
India / Tamil Nadu candidates for the editor's regional rules, with article text attached.
"""
from __future__ import annotations

import re
import time

from . import config
from .collect import Article, fetch_texts, india_relevance
from .sources import COMPANIES

STOP = set("a an the and or of to in on for with from by at as is are was be its it this that new how why what "
           "says said will can after over into amid more than about".split())
IMPORTANT = re.compile(r"\b(launch\w*|release[sd]?|unveil\w*|announc\w*|acquir\w*|raises?|funding|billion|"
                       r"regulat\w*|law|bill|ban|policy|model|open[- ]source|breakthrough|partnership|"
                       r"data cent\w*|chips?|gpus?|jobs|hiring|investment|mou|course|scheme|programme)\b", re.I)
LOW_VALUE = re.compile(r"\b(how to|tips|best .{0,30} to buy|deals?|discount|review|opinion|webinar|sponsored|"
                       r"podcast|quiz|horoscope|stocks? to|shares? (?:rise|fall|jump|surge))\b", re.I)
FIRST_HAND = {"OpenAI", "Google DeepMind", "Google AI Blog", "Hugging Face", "NVIDIA", "AWS Machine Learning"}
COMPANY_RE = [(c, re.compile(rf"\b{re.escape(c)}\b", re.I)) for c in COMPANIES]


def _tokens(title: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9]+", title.lower()) if w not in STOP and len(w) > 2}


def _similar(a: set[str], b: set[str]) -> bool:
    if not a or not b:
        return False
    shared = len(a & b)
    return shared / len(a | b) >= 0.5 or (shared >= 4 and shared / min(len(a), len(b)) >= 0.6)


def cluster(articles: list[Article]) -> list[dict]:
    """Group articles reporting the same event (by headline similarity)."""
    stories: list[dict] = []
    for a in articles:
        toks = _tokens(a.title)
        match = next((s for s in stories if _similar(toks, s["_tokens"])), None)
        if match:
            match["coverage"].append({"source": a.source, "title": a.title, "link": a.link})
            # prefer a direct publisher link over a Google News redirect
            if "news.google.com" in match["link"] and "news.google.com" not in a.link:
                match.update(link=a.link, source=a.source, title=a.title)
            if len(a.snippet) > len(match["snippet"]):
                match["snippet"] = a.snippet
            continue
        stories.append({
            "title": a.title, "link": a.link, "source": a.source, "snippet": a.snippet,
            "published": a.published, "_tokens": toks,
            "coverage": [{"source": a.source, "title": a.title, "link": a.link}],
        })
    for s in stories:
        text = " ".join([s["title"], s["snippet"], *(c["title"] for c in s["coverage"])])
        s["india"] = india_relevance(text)
        s["companies"] = [c for c, rx in COMPANY_RE if rx.search(text)][:3]
        s["score"] = _score(s, text)
        del s["_tokens"]
    return stories


def _score(s: dict, text: str) -> float:
    score = 4.0
    if IMPORTANT.search(text):
        score += 2
    if LOW_VALUE.search(s["title"]):
        score -= 3
    if s["source"] in FIRST_HAND:
        score += 1
    score += 0.8 * min(len({c["source"] for c in s["coverage"]}) - 1, 5)  # independent coverage
    if s["published"]:
        score -= min((time.time() - s["published"]) / 3600, 36) / 18  # slight freshness bonus
    return round(score, 2)


def shortlist(stories: list[dict], size: int = 70) -> list[dict]:
    """Best stories overall plus enough India / Tamil Nadu ones for the regional rules."""
    ranked = sorted(stories, key=lambda s: s["score"], reverse=True)
    per_company: dict[str, int] = {}
    picked: list[dict] = []

    def add(s: dict) -> None:
        if s in picked:
            return
        c = s["companies"][0] if s["companies"] else ""
        if c and per_company.get(c, 0) >= 4:  # looser cap here; the editor applies the real one
            return
        per_company[c] = per_company.get(c, 0) + 1
        picked.append(s)

    for s in [s for s in ranked if s["india"] == "tamil_nadu"][:10]:
        add(s)
    for s in [s for s in ranked if s["india"] == "india"][:18]:
        add(s)
    for s in ranked:
        if len(picked) >= size:
            break
        add(s)

    texts = fetch_texts([(_best_link(s), s["snippet"]) for s in picked])
    for i, (s, text) in enumerate(zip(picked, texts), 1):
        s["id"] = f"c{i}"
        s["text"] = " ".join(text.split()[: config.CANDIDATE_TEXT_WORDS])
    return picked


def _best_link(s: dict) -> str:
    if "news.google.com" in s["link"]:
        for c in s["coverage"]:
            if "news.google.com" not in c["link"]:
                return c["link"]
    return s["link"]
