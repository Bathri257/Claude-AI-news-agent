"""Scan step (runs every few hours): sort new articles into new / duplicate / skip.

With Claude: each batch of new articles is compared with the stories already in the pool,
so repeat coverage of the same event is merged and low-value items are dropped.
Without an API key: title-similarity matching and keyword scoring do the same job, less well.
"""
from __future__ import annotations

import logging
import re
import time

from . import config, llm
from .collect import Article, india_relevance, normalize_link
from .pool import window
from .sources import CATEGORIES, COMPANIES

log = logging.getLogger(__name__)
BATCH = 100

SCHEMA = {
    "type": "object",
    "properties": {
        "items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "action": {"type": "string", "enum": ["new", "duplicate", "skip"]},
                    "duplicate_of": {"type": "string"},
                    "importance": {"type": "integer"},
                    "category": {"type": "string", "enum": CATEGORIES},
                    "companies": {"type": "array", "items": {"type": "string"}},
                    "region": {"type": "string"},
                    "india": {"type": "string", "enum": ["none", "india", "tamil_nadu"]},
                },
                "required": ["id", "action", "duplicate_of", "importance", "category",
                             "companies", "region", "india"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["items"],
    "additionalProperties": False,
}

SYSTEM = """You triage incoming articles for a daily AI news briefing read by someone in \
Tamil Nadu, India, who wants to follow AI worldwide plus Indian and Tamil Nadu developments.

You get the stories already collected today (ids starting with "s") and a batch of new \
articles (ids starting with "n"). For EVERY new article return one item:
- action "duplicate": it reports the same event as an existing story or an earlier new \
article in this batch; put that id in duplicate_of. Same event = same announcement, \
launch, deal or ruling, even if worded differently or from another outlet.
- action "skip": not really about AI, or low value: opinion/listicle/how-to/product deal/\
review/webinar/sponsored post, minor rewrite of old news, stock-price chatter.
- action "new": a distinct, worthwhile AI development.
For "new" and "duplicate" items also give:
- importance 1-10: 9-10 major industry-shaping news (frontier model launch, landmark \
regulation, very large deal); 6-8 notable launches, research, funding, policy; 3-5 minor \
but useful; 1-2 marginal. For Indian/Tamil Nadu items judge importance for a reader there \
(e.g. a state AI policy, a new AI centre or jobs in Chennai can be 6-8).
- category, companies (main organisations involved, short canonical names, e.g. \
"Google", "Sarvam AI"), region (e.g. "US", "China", "EU", "India", "Global").
- india: "tamil_nadu" if it concerns Tamil Nadu (Chennai, Coimbatore, Madurai, IIT Madras, \
Zoho, Freshworks, state government, etc.), "india" if it concerns India more broadly, else "none".
For "skip" items fill the other fields with your best guess; duplicate_of is "" unless duplicate."""


def _apply(pool: dict, art: Article, item: dict, by_id: dict, batch_ids: dict, now: float, method: str) -> None:
    pool["seen_links"][normalize_link(art.link)] = now
    action = item["action"]
    if action == "duplicate":
        target = by_id.get(item["duplicate_of"]) or batch_ids.get(item["duplicate_of"])
        if target is not None:
            target["coverage"].append({"source": art.source, "link": art.link, "title": art.title})
            target["importance"] = max(target["importance"], int(item["importance"]))
            # Prefer a direct publisher link over a Google News redirect.
            if "news.google.com" in target["link"] and "news.google.com" not in art.link:
                target["link"], target["source"] = art.link, art.source
            return
        action = "new"
    if action == "skip":
        return
    story = {
        "id": f"s{pool['next_id']}",
        "title": art.title, "link": art.link, "source": art.source, "snippet": art.snippet,
        "published": art.published, "first_seen": now, "status": "candidate",
        "importance": max(1, min(10, int(item["importance"]))),
        "category": item["category"], "companies": item["companies"][:4],
        "region": item["region"], "india": item["india"],
        "coverage": [{"source": art.source, "link": art.link, "title": art.title}],
        "triage": method,
    }
    pool["next_id"] += 1
    pool["stories"].append(story)
    by_id[story["id"]] = story
    batch_ids[item.get("id", story["id"])] = story


def _claude_triage(pool: dict, articles: list[Article]) -> None:
    now = time.time()
    for start in range(0, len(articles), BATCH):
        batch = articles[start:start + BATCH]
        existing = window(pool)
        by_id = {s["id"]: s for s in existing}
        known = "\n".join(f"[{s['id']}] {s['title']}" for s in existing) or "(none yet)"
        new = "\n".join(
            f"[n{i}] {a.source} | {a.title}" + (f" — {a.snippet[:220]}" if a.snippet else "")
            for i, a in enumerate(batch)
        )
        data = llm.ask_json(
            config.TRIAGE_MODEL, SYSTEM,
            f"<existing_stories>\n{known}\n</existing_stories>\n\n<new_articles>\n{new}\n</new_articles>",
            SCHEMA, effort="low",
        )
        results = {it["id"]: it for it in data["items"]}
        batch_ids: dict = {}
        for i, a in enumerate(batch):
            item = results.get(f"n{i}")
            if item is None:  # model left it out: keep it as a low-importance candidate
                item = _heuristic_item(a)
            _apply(pool, a, item, by_id, batch_ids, now, "claude")


# ---------------- keyless fallback ----------------

STOP = set("a an the and or of to in on for with from by at as is are was be its it this that new how why what "
           "says said will can after over into amid".split())
IMPORTANT = re.compile(r"\b(launch|launches|released?|unveil\w*|announc\w*|acquir\w*|raises?|funding|"
                       r"billion|regulat\w*|law|bill|ban|policy|model|open[- ]source|breakthrough|"
                       r"partnership|data cent\w*|chip|gpu|jobs|hiring|investment|mou)\b", re.I)
LOW_VALUE = re.compile(r"\b(how to|tips|best .* to buy|deal|discount|review|opinion|webinar|sponsored|"
                       r"podcast|quiz|horoscope|stock|shares? (?:rise|fall|jump))\b", re.I)
COMPANY_RE = [(c, re.compile(rf"\b{re.escape(c)}\b", re.I)) for c in COMPANIES]


def _tokens(title: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9]+", title.lower()) if w not in STOP and len(w) > 2}


def _heuristic_item(a: Article) -> dict:
    text = f"{a.title} {a.snippet}"
    importance = 4 + (2 if IMPORTANT.search(text) else 0) - (3 if LOW_VALUE.search(text) else 0)
    india = india_relevance(text)
    return {
        "action": "new" if importance >= 2 else "skip", "duplicate_of": "",
        "importance": importance + (1 if india != "none" else 0),
        "category": "Industry & Products",
        "companies": [c for c, rx in COMPANY_RE if rx.search(text)][:3],
        "region": "India" if india != "none" else "", "india": india,
    }


def _heuristic_triage(pool: dict, articles: list[Article]) -> None:
    now = time.time()
    existing = window(pool)
    by_id = {s["id"]: s for s in existing}
    token_index = [(s["id"], _tokens(s["title"])) for s in existing]
    for a in articles:
        item = _heuristic_item(a)
        toks = _tokens(a.title)
        for sid, other in token_index:
            if toks and other and len(toks & other) / len(toks | other) >= 0.5:
                item["action"], item["duplicate_of"] = "duplicate", sid
                break
        before = pool["next_id"]
        _apply(pool, a, item, by_id, {}, now, "heuristic")
        if pool["next_id"] != before:
            token_index.append((f"s{before}", toks))


def triage(pool: dict, articles: list[Article]) -> str:
    if not articles:
        return "none"
    if llm.available():
        try:
            _claude_triage(pool, articles)
            return "claude"
        except Exception as exc:
            log.error("Claude triage failed (%s); using heuristics", exc)
            # articles already processed are in seen_links; handle the rest heuristically
            articles = [a for a in articles if normalize_link(a.link) not in pool["seen_links"]]
    _heuristic_triage(pool, articles)
    return "heuristic"
