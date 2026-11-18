"""Write the 60-100 word summary for each chosen story.

Claude writes summaries from the article text. Any summary outside the word range is
sent back once for a rewrite. Without an API key, a short extract of the article is used.
"""
from __future__ import annotations

import logging
import re
from datetime import datetime, timezone

from . import config, llm
from .collect import fetch_texts, india_relevance
from .sources import CATEGORIES

log = logging.getLogger(__name__)

SCHEMA = {
    "type": "object",
    "properties": {
        "stories": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "headline": {"type": "string"},
                    "category": {"type": "string", "enum": CATEGORIES},
                    "technology": {"type": "string"},
                    "region": {"type": "string"},
                    "summary": {"type": "string"},
                },
                "required": ["id", "headline", "category", "technology", "region", "summary"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["stories"],
    "additionalProperties": False,
}

SYSTEM = f"""You write a daily AI news briefing for a reader in Tamil Nadu, India. \
For each article provided, write:
- headline: a clear, factual headline (max 14 words), no clickbait.
- category: one of the allowed categories.
- technology: the specific technology or product involved (e.g. "Gemini 3", \
"humanoid robots", "AI accelerators", "EU AI Act", "Indic language models").
- region: where it is happening (e.g. "US", "China", "EU", "India", "Tamil Nadu", "Global").
- summary: between {config.MIN_WORDS} and {config.MAX_WORDS} words (aim for about 80), \
in English even if the article is in another language. Explain what happened, the key \
specifics (names, numbers, dates), and why it matters. If it creates an opportunity for \
the reader (jobs, programmes, tools they can use, funding), say so. One plain paragraph, \
no bullet points, no links.

Use only facts stated in the provided text. Several reports of the same event may be given; \
combine them. If the text is thin, stay accurate and do not invent details."""


def word_count(text: str) -> int:
    return len(re.findall(r"\S+", text))


def _fmt_date(ts: float) -> str:
    return datetime.fromtimestamp(ts, timezone.utc).strftime("%Y-%m-%d %H:%M UTC") if ts else ""


def _article_block(s: dict) -> str:
    other = "; ".join(c["title"] for c in s["coverage"][1:4])
    return (f'<article id="{s["id"]}" source="{s["source"]}" published="{_fmt_date(s["published"])}">\n'
            f"<title>{s['title']}</title>\n"
            + (f"<other_headlines>{other}</other_headlines>\n" if other else "")
            + f"<text>{' '.join(s['text'].split()[:1200])}</text>\n</article>")


def _claude(stories: list[dict]) -> list[dict]:
    prompt = "Write one entry per article below. Keep the article ids.\n\n" + "\n\n".join(
        _article_block(s) for s in stories)
    out = {e["id"]: e for e in llm.ask_json(config.MODEL, SYSTEM, prompt, SCHEMA, "medium")["stories"]}

    bad = [i for i, e in out.items() if not config.MIN_WORDS <= word_count(e["summary"]) <= config.MAX_WORDS]
    if bad:
        log.info("Rewriting %d summaries outside %d-%d words", len(bad), config.MIN_WORDS, config.MAX_WORDS)
        by_id = {s["id"]: s for s in stories}
        prompt = (f"These summaries are outside the required {config.MIN_WORDS}-{config.MAX_WORDS} word range. "
                  "Rewrite each to about 80 words using the article.\n\n" + "\n\n".join(
                      f'<previous_summary id="{i}" words="{word_count(out[i]["summary"])}">'
                      f'{out[i]["summary"]}</previous_summary>\n{_article_block(by_id[i])}'
                      for i in bad if i in by_id))
        try:
            for e in llm.ask_json(config.MODEL, SYSTEM, prompt, SCHEMA, "low")["stories"]:
                if e["id"] in out:
                    out[e["id"]] = e
        except Exception as exc:
            log.warning("Rewrite failed: %s", exc)
    return [out[s["id"]] for s in stories if s["id"] in out]


def _extractive(stories: list[dict]) -> list[dict]:
    result = []
    for s in stories:
        words: list[str] = []
        for sentence in re.split(r"(?<=[.!?])\s+", s["text"] or s["snippet"]):
            if len(words) >= config.MIN_WORDS + 15:
                break
            words.extend(sentence.split())
        summary = " ".join(words[: config.MAX_WORDS])
        if summary and not summary.endswith((".", "!", "?")):
            summary += "…"
        result.append({"id": s["id"], "headline": s["title"], "category": s["category"],
                       "technology": "", "region": s["region"], "summary": summary or s["title"]})
    return result


def summarize(stories: list[dict]) -> tuple[list[dict], str]:
    texts = fetch_texts([(s["link"], s["snippet"]) for s in stories])
    for s, t in zip(stories, texts):
        s["text"] = t

    method = "extractive"
    entries = None
    if llm.available():
        try:
            entries = _claude(stories)
            method = "claude"
        except Exception as exc:
            log.error("Claude summaries failed (%s); using extracts", exc)
    if entries is None:
        entries = _extractive(stories)

    by_id = {s["id"]: s for s in stories}
    final = []
    for e in entries:
        s = by_id[e["id"]]
        india = s["india"]
        if india == "none":
            india = india_relevance(f"{e['headline']} {e['region']}")
        elif india == "india" and india_relevance(f"{e['region']} {e['summary']}") == "tamil_nadu":
            india = "tamil_nadu"
        final.append({
            "headline": e["headline"].strip(),
            "category": e["category"],
            "technology": e["technology"].strip(),
            "region": e["region"].strip(),
            "india": india,
            "companies": s["companies"],
            "summary": " ".join(e["summary"].split()),
            "words": word_count(e["summary"]),
            "source": s["source"],
            "link": s["link"],
            "also_covered_by": sorted({c["source"] for c in s["coverage"][1:]})[:5],
            "published": _fmt_date(s["published"]),
        })
    return final, method
