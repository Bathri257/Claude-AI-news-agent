"""4 AM editor step: pick the final 15-20 stories from the day's pool, with diversity rules.

1. Claude (or a score ranking without a key) proposes an ordered selection.
2. Code enforces the hard rules: at most MAX_PER_COMPANY stories per company, a target
   share of India / Tamil Nadu stories when worthwhile ones exist, and MIN..MAX stories.
"""
from __future__ import annotations

import logging

from . import config, llm
from .pool import score

log = logging.getLogger(__name__)

SCHEMA = {
    "type": "object",
    "properties": {"selected": {"type": "array", "items": {"type": "string"}}},
    "required": ["selected"],
    "additionalProperties": False,
}


def _system() -> str:
    india_target = round(config.MAX_STORIES * config.INDIA_SHARE)
    return f"""You are the editor of a daily AI briefing for a reader in Tamil Nadu, India, \
who wants to stay current on AI worldwide and know about opportunities close to home.

From the candidate stories gathered over the last day, choose {config.MIN_STORIES} to \
{config.MAX_STORIES} of the most relevant and useful ones, ordered most important first.

Rules:
- Diversity of companies: at most {config.MAX_PER_COMPANY} stories mainly about the same \
company. Cover the big labs (OpenAI, Google, Anthropic, Meta, Microsoft, NVIDIA, Chinese labs…) \
but also smaller firms and startups doing notable things (e.g. Sarvam AI, Mistral, new startups).
- Diversity of technology: mix models, agents, research, chips and infrastructure, robotics, \
generative media, policy, business, safety, jobs and skills. No more than 5 from one category.
- Regional mix: about {india_target} stories should concern India, and when there are \
worthwhile Tamil Nadu items (Chennai, Coimbatore, IIT Madras, state policy, investments, \
jobs, training programmes) include at least {config.MIN_TAMIL_NADU} of them. Include other \
regions too (US, Europe, China, rest of Asia). Do not include weak items just to fill a quota.
- Prefer stories with broad coverage (high cov), first-hand announcements, concrete facts \
and things that create opportunities for the reader (jobs, programmes, tools, funding).
- Never pick two stories about the same event.
Return only the ids."""


def _line(s: dict) -> str:
    tags = [s["category"], ", ".join(s["companies"]) or "-", s["region"] or "-"]
    if s["india"] != "none":
        tags.append("TAMIL NADU" if s["india"] == "tamil_nadu" else "INDIA")
    return (f"[{s['id']}] imp={s['importance']} cov={len(s['coverage'])} | {' | '.join(tags)} | "
            f"{s['title']}" + (f" — {s['snippet'][:160]}" if s["snippet"] else ""))


def _primary(s: dict) -> str:
    return s["companies"][0].lower() if s["companies"] else ""


def enforce(ordered: list[dict], pool_ranked: list[dict]) -> list[dict]:
    """Apply the hard diversity rules to an ordered proposal."""
    per_company: dict[str, int] = {}
    chosen: list[dict] = []

    def fits(s: dict) -> bool:
        c = _primary(s)
        return not c or per_company.get(c, 0) < config.MAX_PER_COMPANY

    def take(s: dict) -> None:
        chosen.append(s)
        c = _primary(s)
        if c:
            per_company[c] = per_company.get(c, 0) + 1

    for s in ordered:
        if len(chosen) < config.MAX_STORIES and s not in chosen and fits(s):
            take(s)

    def top_up(predicate, needed: int, min_importance: int) -> None:
        extra = [s for s in pool_ranked if s not in chosen and predicate(s)
                 and s["importance"] >= min_importance and fits(s)]
        for s in extra[:needed]:
            if len(chosen) >= config.MAX_STORIES:
                # replace the lowest-ranked global story to make room
                for i in range(len(chosen) - 1, -1, -1):
                    if chosen[i]["india"] == "none":
                        chosen.pop(i)
                        break
                else:
                    return
            take(s)

    tn = sum(s["india"] == "tamil_nadu" for s in chosen)
    top_up(lambda s: s["india"] == "tamil_nadu", config.MIN_TAMIL_NADU - tn, 4)
    india = sum(s["india"] != "none" for s in chosen)
    top_up(lambda s: s["india"] != "none", round(config.MAX_STORIES * config.INDIA_SHARE) - india, 5)
    if len(chosen) < config.MIN_STORIES:
        top_up(lambda s: True, config.MIN_STORIES - len(chosen), 1)
    return chosen


def curate(candidates: list[dict]) -> tuple[list[dict], str]:
    ranked = sorted(candidates, key=score, reverse=True)
    shortlist = ranked[:80]
    method = "score"
    proposal = shortlist
    if llm.available() and len(shortlist) > config.MIN_STORIES:
        try:
            data = llm.ask_json(config.MODEL, _system(),
                                "Candidate stories:\n" + "\n".join(_line(s) for s in shortlist),
                                SCHEMA, effort="medium")
            by_id = {s["id"]: s for s in shortlist}
            proposal = [by_id[i] for i in data["selected"] if i in by_id]
            method = "claude"
        except Exception as exc:
            log.error("Claude curation failed (%s); ranking by score", exc)
    chosen = enforce(proposal, ranked)
    log.info("Curated %d stories (%s): %d India, %d Tamil Nadu", len(chosen), method,
             sum(s["india"] != "none" for s in chosen), sum(s["india"] == "tamil_nadu" for s in chosen))
    return chosen, method
