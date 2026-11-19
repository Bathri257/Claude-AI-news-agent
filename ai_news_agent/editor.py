"""The single AI step of the day.

One Claude Code session (on your Claude Pro/Max login) reads the shortlist, recent history,
collected user comments and your preferences, then writes data/work/draft.json:
today's stories (tiers, briefs, storyline links), opportunities, reviews of earlier stories and,
on recap day, the weekly recap. It runs `python -m ai_news_agent check` until the draft passes.

Fallbacks keep the brief coming: Gemini free tier (one request), then plain extracts (no AI).
Whatever the editor produces is validated and repaired by code before it is saved.
"""
from __future__ import annotations

import json
import logging
import os
import re
import shutil
import subprocess
import urllib.request
from string import Template

from . import config
from .reactions import REACTIONS, auto_pick, verify_review
from .sources import CATEGORIES

log = logging.getLogger(__name__)

WORK = config.WORK_DIR
CANDIDATES = WORK / "candidates.json"
HISTORY = WORK / "history.json"
PREFS = WORK / "preferences.md"
CONTEXT = WORK / "context.json"
DRAFT = WORK / "draft.json"
PROMPT_FILE = config.ROOT / "ai_news_agent" / "prompts" / "editor.md"

STORY_FIELDS = {
    "headline": "clear factual headline, at most 14 words",
    "tier": '"must" for the top stories, "quick" for the rest',
    "brief": f"{config.BRIEF_MIN}-{config.BRIEF_MAX} word one-line essence",
    "summary": f"{config.MIN_WORDS}-{config.MAX_WORDS} words (aim for ~80), one plain-English paragraph",
    "link": "URL of the best source to read the full story",
    "source": "publication name",
    "category": "one of: " + ", ".join(CATEGORIES),
    "technology": 'specific technology/product, e.g. "Gemini 3", "humanoid robots", "EU AI Act"',
    "region": 'e.g. "US", "China", "EU", "India", "Tamil Nadu", "Global"',
    "india": '"tamil_nadu", "india" or "none"',
    "companies": "main organisations involved, short names, most important first",
    "thread": "storyline name, reused from history.json when this continues an earlier story",
    "related": "ids of earlier stories in history.json that this continues, or []",
    "candidate_id": 'id from candidates.json, or "web" if you found it yourself',
}


def _schema(recap: bool) -> str:
    story = ",\n".join(f'      "{k}": <{v}>' for k, v in STORY_FIELDS.items())
    weekly = (',\n  "weekly": {"trend": <60-120 words>, "top": [<5-10 story ids>]}' if recap else "")
    return ("{\n  \"stories\": [\n    {\n" + story + "\n    }\n  ],\n"
            '  "opportunities": [\n    {"title": <short>, "detail": <max 40 words: what, who can apply, how>,\n'
            '     "where": <place or "Online">, "deadline": <date or "">, "link": <URL>}\n  ],\n'
            '  "past_reactions": {\n    "<story id from reactions.json>": {\n'
            '      "pulse": <max 35 words on what users say, or "">,\n'
            '      "sentiment": <"positive", "mixed", "negative" or "none">,\n'
            '      "reviews": [ {"platform": <"Reddit" or "Hacker News">, "community": <e.g. "r/LocalLLaMA">,\n'
            '                    "quote": <exact excerpt, max 40 words>, "takeaway": <max 20 words>,\n'
            '                    "link": <comment link exactly as in reactions.json>, "score": <its score>} ]\n'
            "    }\n  }" + weekly + "\n}")


def prompt(ctx: dict) -> str:
    india_target = round(config.MAX_STORIES * config.INDIA_SHARE)
    weekly = ""
    if ctx["recap"]:
        weekly = (f"\nWEEKLY RECAP (today is recap day)\nAlso write \"weekly\": \"trend\" is 60-120 words on this "
                  f"week's biggest themes and what they mean for the reader; \"top\" lists the 5-10 most "
                  f"important story ids of the week, from history.json entries dated {ctx['week_start']} or "
                  f"later and today's ids.\n")
    return Template(PROMPT_FILE.read_text()).safe_substitute(
        min_stories=config.MIN_STORIES, max_stories=config.MAX_STORIES, must_know=config.MUST_KNOW,
        max_per_company=config.MAX_PER_COMPANY, india_target=india_target, india_max=india_target + 2,
        min_tamil_nadu=config.MIN_TAMIL_NADU, min_words=config.MIN_WORDS, max_words=config.MAX_WORDS,
        brief_min=config.BRIEF_MIN, brief_max=config.BRIEF_MAX, history_days=config.HISTORY_DAYS,
        today=ctx["today"], max_opportunities=config.MAX_OPPORTUNITIES, weekly_task=weekly,
        work=WORK.relative_to(config.ROOT), shortlist_size=config.SHORTLIST_SIZE,
        max_web_searches=config.MAX_WEB_SEARCHES, schema=_schema(ctx["recap"]),
    )


# ---------------------------------------------------------------- validation

def _words(text) -> int:
    return len(str(text).split())


def check(draft: dict, ctx: dict) -> tuple[list[str], list[str]]:
    """Return (errors, warnings) for a draft."""
    errors, warnings = [], []
    stories = draft.get("stories")
    if not isinstance(stories, list):
        return ["draft.json needs a \"stories\" list."], []
    n = len(stories)
    if not config.MIN_STORIES <= n <= config.MAX_STORIES:
        errors.append(f"There are {n} stories; need {config.MIN_STORIES}-{config.MAX_STORIES}.")
    history_ids = set(ctx["history_ids"])
    links, per_company = set(), {}
    for i, s in enumerate(stories, 1):
        label = f"Story {i} ({str(s.get('headline', '?'))[:50]!r})"
        missing = [k for k in STORY_FIELDS if k not in s]
        if missing:
            errors.append(f"{label}: missing fields {missing}.")
            continue
        w = _words(s["summary"])
        if not config.MIN_WORDS <= w <= config.MAX_WORDS:
            errors.append(f"{label}: summary has {w} words; must be {config.MIN_WORDS}-{config.MAX_WORDS}.")
        w = _words(s["brief"])
        if not config.BRIEF_MIN <= w <= config.BRIEF_MAX:
            errors.append(f"{label}: brief has {w} words; must be {config.BRIEF_MIN}-{config.BRIEF_MAX}.")
        if s["tier"] not in ("must", "quick"):
            errors.append(f"{label}: tier must be \"must\" or \"quick\".")
        if not str(s["link"]).startswith("http"):
            errors.append(f"{label}: link is not a URL.")
        if s["link"] in links:
            errors.append(f"{label}: duplicate link (same story twice?).")
        links.add(s["link"])
        if s["category"] not in CATEGORIES:
            errors.append(f"{label}: category must be one of {CATEGORIES}.")
        if s["india"] not in ("none", "india", "tamil_nadu"):
            errors.append(f"{label}: india must be none, india or tamil_nadu.")
        bad = [r for r in s["related"] if r not in history_ids] if isinstance(s["related"], list) else ["?"]
        if bad:
            errors.append(f"{label}: related ids {bad} are not in history.json.")
        if s["companies"]:
            c = str(s["companies"][0]).lower()
            per_company[c] = per_company.get(c, 0) + 1
    for c, k in per_company.items():
        if k > config.MAX_PER_COMPANY:
            errors.append(f"{k} stories are mainly about {c!r}; at most {config.MAX_PER_COMPANY} allowed.")

    tiers = [s.get("tier") for s in stories]
    must = min(config.MUST_KNOW, n)
    if tiers[:must] != ["must"] * must or "must" in tiers[must:]:
        errors.append(f"The first {must} stories must have tier \"must\" and all others \"quick\".")

    india = sum(s.get("india") in ("india", "tamil_nadu") for s in stories)
    tn = sum(s.get("india") == "tamil_nadu" for s in stories)
    target = round(n * config.INDIA_SHARE)
    have_india = sum(c["india"] != "none" for c in ctx["candidates"])
    have_tn = sum(c["india"] == "tamil_nadu" for c in ctx["candidates"])
    if india < target - 1 and have_india > india:
        warnings.append(f"Only {india} India stories (target about {target}); {have_india} India candidates exist.")
    if india > target + 2:
        errors.append(f"{india} India stories; at most {target + 2}.")
    if tn < config.MIN_TAMIL_NADU and have_tn > tn:
        warnings.append(f"Only {tn} Tamil Nadu stories (target {config.MIN_TAMIL_NADU}); {have_tn} candidates exist.")

    opps = draft.get("opportunities", [])
    if not isinstance(opps, list) or len(opps) > config.MAX_OPPORTUNITIES:
        errors.append(f"opportunities must be a list of at most {config.MAX_OPPORTUNITIES}.")
    else:
        for o in opps:
            if not o.get("title") or not str(o.get("link", "")).startswith("http"):
                errors.append(f"Opportunity {o.get('title', '?')!r} needs a title and a link.")
            elif _words(o.get("detail", "")) > 45:
                errors.append(f"Opportunity {o['title']!r}: detail is over 40 words.")

    reactions = ctx.get("reactions") or {}
    past = draft.get("past_reactions", {})
    missing = [sid for sid in reactions if sid not in past]
    if missing:
        errors.append(f"past_reactions is missing entries for {missing} (use empty reviews if nothing is genuine).")
    for sid, r in past.items():
        if sid not in reactions:
            errors.append(f"past_reactions[{sid!r}]: not an id from reactions.json.")
            continue
        if r.get("sentiment") not in ("positive", "mixed", "negative", "none"):
            errors.append(f"past_reactions[{sid!r}]: sentiment must be positive, mixed, negative or none.")
        reviews = r.get("reviews", [])
        if len(reviews) > 3:
            errors.append(f"past_reactions[{sid!r}]: at most 3 reviews.")
        for rv in reviews:
            problem = verify_review(rv, sid, reactions)
            if problem:
                errors.append(f"past_reactions[{sid!r}]: review {rv.get('link', '?')} is invalid: {problem}.")

    if ctx["recap"]:
        weekly = draft.get("weekly") or {}
        allowed = set(ctx["week_ids"]) | {f"{ctx['today']}-{i:02d}" for i in range(1, n + 1)}
        if not 40 <= _words(weekly.get("trend", "")) <= 130:
            errors.append("weekly.trend must be 60-120 words.")
        top = weekly.get("top", [])
        if not 3 <= len(top) <= 10 or any(t not in allowed for t in top):
            errors.append("weekly.top must list 5-10 ids from this week's history or today's ids.")
    return errors, warnings


def _trim(text: str, limit: int) -> str:
    words = text.split()
    if len(words) <= limit:
        return text
    cut = " ".join(words[:limit])
    end = max(cut.rfind(". "), cut.rfind("! "), cut.rfind("? "))
    if end != -1 and _words(cut[: end + 1]) >= min(config.MIN_WORDS, limit // 2):
        return cut[: end + 1]
    return cut.rstrip(",;:") + "…"


def _first_sentence(text: str) -> str:
    first = re.split(r"(?<=[.!?])\s+", text.strip())[0]
    return _trim(first, config.BRIEF_MAX)


def repair(draft: dict, ctx: dict) -> dict:
    """Last-line enforcement in code, whatever the editor returned."""
    history_ids = set(ctx["history_ids"])
    stories, links, per_company = [], set(), {}
    for idx, s in enumerate(draft.get("stories", [])):
        if not isinstance(s, dict) or not all(k in s for k in ("headline", "summary", "link")):
            continue
        if not str(s["link"]).startswith("http") or s["link"] in links:
            continue
        out = {k: s.get(k) for k in STORY_FIELDS}
        out["draft_index"] = idx
        out["headline"] = str(s["headline"]).strip()
        out["summary"] = _trim(" ".join(str(s["summary"]).split()), config.MAX_WORDS)
        brief = " ".join(str(s.get("brief") or "").split())
        out["brief"] = brief if config.BRIEF_MIN <= _words(brief) <= config.BRIEF_MAX else _first_sentence(out["summary"])
        out["category"] = s.get("category") if s.get("category") in CATEGORIES else "Industry & Products"
        out["india"] = s.get("india") if s.get("india") in ("none", "india", "tamil_nadu") else "none"
        out["companies"] = [str(c) for c in (s.get("companies") or [])][:4]
        out["related"] = [r for r in (s.get("related") or []) if r in history_ids]
        out["thread"] = str(s.get("thread") or out["headline"])[:60]
        for k in ("source", "technology", "region", "candidate_id"):
            out[k] = str(s.get(k) or "")
        out["tier"] = "must" if s.get("tier") == "must" else "quick"
        c = out["companies"][0].lower() if out["companies"] else ""
        if c and per_company.get(c, 0) >= config.MAX_PER_COMPANY:
            continue
        per_company[c] = per_company.get(c, 0) + 1
        links.add(s["link"])
        stories.append(out)

    short = [s for s in stories if _words(s["summary"]) < config.MIN_WORDS]
    while short and len(stories) > config.MIN_STORIES:
        stories.remove(short.pop())
    stories = stories[: config.MAX_STORIES]
    # Exactly MUST_KNOW "must" stories, placed first (editor's picks first, topped up in order).
    musts = [s for s in stories if s["tier"] == "must"][: config.MUST_KNOW]
    for s in stories:
        if len(musts) >= min(config.MUST_KNOW, len(stories)):
            break
        if s not in musts:
            musts.append(s)
    rest = [s for s in stories if s not in musts]
    for s in musts:
        s["tier"] = "must"
    for s in rest:
        s["tier"] = "quick"

    opportunities = [
        {k: str(o.get(k) or "") for k in ("title", "detail", "where", "deadline", "link")}
        for o in (draft.get("opportunities") or []) if isinstance(o, dict)
        and o.get("title") and str(o.get("link", "")).startswith("http")
    ][: config.MAX_OPPORTUNITIES]

    reactions = ctx.get("reactions") or {}
    past = {}
    for sid, r in (draft.get("past_reactions") or {}).items():
        if sid not in reactions or not isinstance(r, dict):
            continue
        reviews = [rv for rv in (r.get("reviews") or [])[:3] if verify_review(rv, sid, reactions) is None]
        sentiment = r.get("sentiment") if r.get("sentiment") in ("positive", "mixed", "negative") else "none"
        past[sid] = {"pulse": str(r.get("pulse") or "") if reviews else "",
                     "sentiment": sentiment if reviews else "none", "reviews": reviews,
                     **({"auto": True} if r.get("auto") else {})}

    result = {"stories": musts + rest, "opportunities": opportunities, "past_reactions": past}
    if ctx["recap"] and isinstance(draft.get("weekly"), dict):
        result["weekly"] = {"trend": str(draft["weekly"].get("trend") or ""),
                            "top": [str(t) for t in draft["weekly"].get("top", [])][:10]}
    return result


def cmd_check() -> int:
    """Used by Claude Code during its session: prints OK or the problems to fix."""
    try:
        draft = json.loads(DRAFT.read_text())
    except Exception as exc:
        print(f"ERROR: could not read {DRAFT.relative_to(config.ROOT)} as JSON: {exc}")
        return 1
    errors, warnings = check(draft, load_ctx())
    for e in errors:
        print("ERROR:", e)
    for w in warnings:
        print("WARNING:", w)
    if not errors:
        print(f"OK: {len(draft['stories'])} stories pass all hard rules.")
    return 1 if errors else 0


def load_ctx() -> dict:
    ctx = json.loads(CONTEXT.read_text())
    ctx["candidates"] = json.loads(CANDIDATES.read_text())
    ctx["reactions"] = json.loads(REACTIONS.read_text()) if REACTIONS.exists() else {}
    return ctx


# ---------------------------------------------------------------- editors

def _claude_code(ctx: dict) -> dict | None:
    # In GitHub Actions the token comes from secrets; locally set USE_LOCAL_CLAUDE=1 to use your login.
    if not (os.getenv("CLAUDE_CODE_OAUTH_TOKEN") or os.getenv("USE_LOCAL_CLAUDE")):
        ctx["claude_error"] = "No CLAUDE_CODE_OAUTH_TOKEN secret is set."
        log.info("Claude Code: no CLAUDE_CODE_OAUTH_TOKEN set, skipping")
        return None
    exe = shutil.which("claude")
    if not exe:
        ctx["claude_error"] = "Claude Code CLI is not installed."
        log.warning("Claude Code CLI not installed, skipping")
        return None
    cmd = [exe, "-p", prompt(ctx), "--permission-mode", "dontAsk", "--output-format", "json",
           "--allowedTools", "Read", "Write(./data/work/**)", "Edit(./data/work/**)",
           "WebSearch", "WebFetch", "Bash(python -m ai_news_agent check)"]
    if config.CLAUDE_CODE_MODEL:
        cmd += ["--model", config.CLAUDE_CODE_MODEL]
    DRAFT.unlink(missing_ok=True)
    log.info("Running Claude Code editor session…")
    try:
        result = subprocess.run(cmd, cwd=config.ROOT, capture_output=True, text=True,
                                timeout=config.CLAUDE_TIMEOUT_MIN * 60)
    except subprocess.TimeoutExpired:
        ctx["claude_error"] = f"Timed out after {config.CLAUDE_TIMEOUT_MIN} minutes."
        log.error("Claude Code timed out after %d minutes", config.CLAUDE_TIMEOUT_MIN)
    else:
        try:
            info = json.loads(result.stdout)
            log.info("Claude Code finished: %s (turns=%s, error=%s)",
                     str(info.get("result", ""))[:200], info.get("num_turns"), info.get("is_error"))
            if info.get("is_error"):
                ctx["claude_error"] = str(info.get("result", ""))[:300]
        except json.JSONDecodeError:
            ctx["claude_error"] = (result.stderr or result.stdout)[-300:]
            log.warning("Claude Code exit %s: %s", result.returncode, ctx["claude_error"])
    try:
        return json.loads(DRAFT.read_text())
    except Exception as exc:
        ctx.setdefault("claude_error", "The session ended without writing a draft.")
        log.error("Claude Code produced no usable draft: %s", exc)
        return None


def _gemini(ctx: dict) -> dict | None:
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        return None
    files = "\n\n".join(f"=== {p.name} ===\n{p.read_text()}" for p in (CANDIDATES, HISTORY, PREFS))
    text = (prompt(ctx) + "\n\nNOTE: you have no tools. The files are included below; leave past_reactions "
            "empty, skip web searches and the check step, and return only the JSON.\n\n" + files)
    body = json.dumps({"contents": [{"parts": [{"text": text}]}],
                       "generationConfig": {"responseMimeType": "application/json", "temperature": 0.3}})
    req = urllib.request.Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/{config.GEMINI_MODEL}:generateContent",
        data=body.encode(), headers={"Content-Type": "application/json", "x-goog-api-key": key})
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            data = json.loads(r.read())
        draft = json.loads(data["candidates"][0]["content"]["parts"][0]["text"])
        draft["past_reactions"] = auto_pick(ctx.get("reactions") or {})
        return draft
    except Exception as exc:
        log.error("Gemini backup failed: %s", exc)
        return None


def _extractive(ctx: dict) -> dict:
    ranked = sorted(ctx["candidates"], key=lambda c: c["score"], reverse=True)
    tn = [c for c in ranked if c["india"] == "tamil_nadu"][: config.MIN_TAMIL_NADU]
    india_n = max(0, round(config.MAX_STORIES * config.INDIA_SHARE) - len(tn))
    india = [c for c in ranked if c["india"] == "india"][:india_n]
    world = [c for c in ranked if c["india"] == "none"]
    ordered = world[: config.MUST_KNOW] + tn + india + world[config.MUST_KNOW:]
    stories = []
    for c in ordered:
        words: list[str] = []
        for sentence in re.split(r"(?<=[.!?])\s+", c["text"] or c["snippet"]):
            if len(words) >= config.MIN_WORDS + 15:
                break
            words.extend(sentence.split())
        stories.append({"headline": c["title"], "tier": "quick", "brief": "", "summary": " ".join(words) or c["title"],
                        "link": c["link"], "source": c["source"], "category": "Industry & Products",
                        "technology": "", "region": "India" if c["india"] != "none" else "",
                        "india": c["india"], "companies": c["companies"], "thread": c["title"],
                        "related": [], "candidate_id": c["id"]})
    return {"stories": stories, "opportunities": [], "past_reactions": auto_pick(ctx.get("reactions") or {})}


def edit(ctx: dict) -> tuple[dict, str]:
    """Run the best available editor (the work files must already be written)."""
    for name, run in (("claude-code", _claude_code), ("gemini", _gemini)):
        draft = run(ctx)
        if draft:
            errors, warnings = check(draft, ctx)
            for msg in errors + warnings:
                log.info("%s draft: %s", name, msg)
            fixed = repair(draft, ctx)
            if len(fixed["stories"]) >= min(config.MIN_STORIES, len(ctx["candidates"])) // 2:
                return fixed, name
            log.warning("%s draft unusable after repair (%d stories)", name, len(fixed["stories"]))
    log.warning("No AI editor available; using extracts")
    return repair(_extractive(ctx), ctx), "extractive"
