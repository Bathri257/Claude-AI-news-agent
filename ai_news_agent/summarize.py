"""Use Claude to pick the most important stories and write 60-100 word summaries.

Falls back to a simple extractive summary if no API key is configured or the
API call fails, so the daily email still goes out.
"""
from __future__ import annotations

import json
import logging
import os
import re
from datetime import datetime, timezone

import anthropic

from . import config
from .collect import Article
from .sources import CATEGORIES

log = logging.getLogger(__name__)

FALLBACK_BETA = "server-side-fallback-2026-07-01"

SELECT_SCHEMA = {
    "type": "object",
    "properties": {
        "selected": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "reason": {"type": "string"},
                },
                "required": ["id", "reason"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["selected"],
    "additionalProperties": False,
}

SUMMARY_SCHEMA = {
    "type": "object",
    "properties": {
        "stories": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
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

SELECT_SYSTEM = """You are the editor of a daily AI news briefing for one busy reader \
who wants to stay current on what is happening in AI around the world.

From the candidate articles, choose the {n} most significant, distinct stories. Prefer:
- genuinely new developments: model and product launches, research results, major \
funding or acquisitions, chips and infrastructure, regulation and policy, safety;
- first-hand sources (the company or lab's own announcement) or high-quality reporting;
- a mix of technologies and a global spread (US, Europe, Asia, India, elsewhere).
Avoid: duplicates of the same story (pick the best single source), opinion pieces, \
listicles, how-to tutorials, minor sponsored or promotional posts, and non-AI tech news.
Return fewer than {n} if there aren't that many worthwhile stories."""

SUMMARY_SYSTEM = f"""You write a daily AI news briefing. For each article provided, write:
- headline: a clear, factual headline (max 14 words), no clickbait.
- category: one of the allowed categories.
- technology: the specific technology or product involved (e.g. "Gemini 3", \
"humanoid robots", "AI accelerators", "EU AI Act").
- region: where it is happening (e.g. "US", "China", "EU", "India", "Global").
- summary: between {config.MIN_WORDS} and {config.MAX_WORDS} words (aim for about 80). \
Explain what happened, the key specifics (names, numbers, dates), and why it matters \
for someone following AI. Plain prose, one paragraph, no bullet points, no links.

Use only facts stated in the provided article text. If the text is thin, write a \
shorter but still accurate summary within the word range and do not invent details."""


def word_count(text: str) -> int:
    return len(re.findall(r"\S+", text))


def _client() -> anthropic.Anthropic | None:
    if not (os.getenv("ANTHROPIC_API_KEY") or os.getenv("ANTHROPIC_AUTH_TOKEN")):
        return None
    return anthropic.Anthropic(max_retries=4)


def _ask_json(client: anthropic.Anthropic, system: str, prompt: str, schema: dict, effort: str) -> dict:
    response = client.beta.messages.create(
        model=config.MODEL,
        max_tokens=16000,
        system=system,
        messages=[{"role": "user", "content": prompt}],
        output_config={"effort": effort, "format": {"type": "json_schema", "schema": schema}},
        betas=[FALLBACK_BETA],
        fallbacks="default",  # retry on a fallback model if a safety classifier declines
    )
    if response.stop_reason == "refusal":
        raise RuntimeError(f"Request declined: {response.stop_details}")
    if response.stop_reason == "max_tokens":
        raise RuntimeError("Response hit max_tokens")
    text = next(b.text for b in response.content if b.type == "text")
    return json.loads(text)


def _fmt_date(ts: float) -> str:
    if not ts:
        return "unknown date"
    return datetime.fromtimestamp(ts, timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def _select(client: anthropic.Anthropic, candidates: list[Article]) -> list[Article]:
    if len(candidates) <= config.MAX_STORIES // 2:
        return candidates
    lines = [
        f"[{a.id}] {a.source} | {_fmt_date(a.published)} | {a.title}\n    {a.snippet[:300]}"
        for a in candidates
    ]
    data = _ask_json(
        client,
        SELECT_SYSTEM.format(n=config.MAX_STORIES),
        "Candidate articles:\n\n" + "\n".join(lines),
        SELECT_SCHEMA,
        effort="low",
    )
    by_id = {a.id: a for a in candidates}
    chosen = [by_id[s["id"]] for s in data["selected"] if s["id"] in by_id]
    # de-duplicate ids while keeping order
    seen, result = set(), []
    for a in chosen:
        if a.id not in seen:
            seen.add(a.id)
            result.append(a)
    return result[: config.MAX_STORIES]


def _summarize(client: anthropic.Anthropic, articles: list[Article]) -> list[dict]:
    blocks = []
    for a in articles:
        body = " ".join(a.text.split()[:1200]) or a.snippet
        blocks.append(
            f'<article id="{a.id}" source="{a.source}" published="{_fmt_date(a.published)}">\n'
            f"<title>{a.title}</title>\n<text>{body}</text>\n</article>"
        )
    prompt = (
        "Write one entry per article below. Keep the article ids.\n\n" + "\n\n".join(blocks)
    )
    data = _ask_json(client, SUMMARY_SYSTEM, prompt, SUMMARY_SCHEMA, effort="medium")
    stories = data["stories"]

    # Enforce the 60-100 word rule: ask Claude to rewrite any entry that misses it.
    bad = [s for s in stories if not config.MIN_WORDS <= word_count(s["summary"]) <= config.MAX_WORDS]
    if bad:
        log.info("Rewriting %d summaries outside %d-%d words", len(bad), config.MIN_WORDS, config.MAX_WORDS)
        by_id = {a.id: a for a in articles}
        retry_prompt = (
            f"These summaries are outside the required {config.MIN_WORDS}-{config.MAX_WORDS} word "
            "range. Rewrite each to about 80 words using the article text.\n\n"
            + "\n\n".join(
                f'<entry id="{s["id"]}" words="{word_count(s["summary"])}">\n'
                f'<summary>{s["summary"]}</summary>\n'
                f'<text>{" ".join(by_id[s["id"]].text.split()[:1200]) if s["id"] in by_id else ""}</text>\n</entry>'
                for s in bad
            )
        )
        try:
            fixed = {s["id"]: s for s in _ask_json(client, SUMMARY_SYSTEM, retry_prompt, SUMMARY_SCHEMA, "low")["stories"]}
            stories = [fixed.get(s["id"], s) if s in bad else s for s in stories]
        except Exception as exc:
            log.warning("Rewrite failed: %s", exc)
    return stories


def _extractive(articles: list[Article]) -> list[dict]:
    """No-LLM fallback: first sentences of the article, trimmed to the word range."""
    stories = []
    for a in articles:
        sentences = re.split(r"(?<=[.!?])\s+", a.text or a.snippet)
        words: list[str] = []
        for s in sentences:
            if len(words) >= config.MIN_WORDS + 15:
                break
            words.extend(s.split())
        words = words[: config.MAX_WORDS]
        summary = " ".join(words)
        if words and not summary.endswith((".", "!", "?")):
            summary += "…"
        stories.append({
            "id": a.id, "headline": a.title, "category": "Industry & Products",
            "technology": "", "region": "", "summary": summary or a.title,
        })
    return stories


def build_stories(candidates: list[Article], fetch_text) -> tuple[list[dict], str]:
    """Return (stories, method). `fetch_text` loads article bodies for the chosen items."""
    client = _client()
    if client is None:
        log.warning("ANTHROPIC_API_KEY not set - using extractive fallback summaries")
        chosen = candidates[: config.MAX_STORIES]
        fetch_text(chosen)
        return _attach(_extractive(chosen), chosen), "extractive"

    try:
        chosen = _select(client, candidates)
        fetch_text(chosen)
        return _attach(_summarize(client, chosen), chosen), "claude"
    except (anthropic.APIError, RuntimeError, json.JSONDecodeError, StopIteration) as exc:
        log.error("Claude summarisation failed (%s); using extractive fallback", exc)
        chosen = candidates[: config.MAX_STORIES]
        fetch_text([a for a in chosen if not a.text])
        return _attach(_extractive(chosen), chosen), "extractive"


def _attach(stories: list[dict], articles: list[Article]) -> list[dict]:
    by_id = {a.id: a for a in articles}
    out = []
    for s in stories:
        a = by_id.get(s["id"])
        if not a:
            continue
        out.append({
            "headline": s["headline"].strip(),
            "category": s["category"],
            "technology": s.get("technology", "").strip(),
            "region": s.get("region", "").strip(),
            "summary": " ".join(s["summary"].split()),
            "words": word_count(s["summary"]),
            "source": a.source,
            "link": a.link,
            "published": _fmt_date(a.published) if a.published else "",
        })
    return out
