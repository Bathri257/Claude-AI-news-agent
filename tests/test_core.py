"""Tests for the guarantees the brief relies on. Run: python -m pytest -q"""
from ai_news_agent import config, threads
from ai_news_agent.editor import check, repair
from ai_news_agent.reactions import verify_review

COMMENT = {"platform": "Reddit", "community": "r/LocalLLaMA", "score": 50, "link": "https://reddit.com/c/1",
           "text": "Ran the 4-bit quant on two 3090s last night. Coding quality is close to the big models."}
REACTIONS = {"2026-11-18-01": {"comments": [COMMENT]}}


def story(i, **kw):
    s = {"headline": f"Headline {i}", "tier": "must" if i <= config.MUST_KNOW else "quick",
         "brief": "A short one line essence of the story for quick scanning.", "summary": " ".join(["word"] * 80),
         "link": f"https://example.com/{i}", "source": "Src", "category": "Research", "technology": "x",
         "region": "US", "india": "none", "city": "", "companies": [f"Co{i}"], "thread": f"T{i}", "related": [],
         "candidate_id": f"c{i}"}
    s.update(kw)
    return s


def ctx(**kw):
    c = {"today": "2026-11-19", "recap": False, "history_ids": ["2026-11-18-01"], "week_ids": [],
         "candidates": [], "reactions": {}}
    c.update(kw)
    return c


def test_exact_quote_passes():
    r = {"link": COMMENT["link"], "quote": "Coding quality is close to the big models."}
    assert verify_review(r, "2026-11-18-01", REACTIONS) is None


def test_quote_with_ellipsis_passes():
    r = {"link": COMMENT["link"], "quote": "Ran the 4-bit quant … close to the big models"}
    assert verify_review(r, "2026-11-18-01", REACTIONS) is None


def test_invented_quote_fails():
    r = {"link": COMMENT["link"], "quote": "This model is amazing and changed my life."}
    assert verify_review(r, "2026-11-18-01", REACTIONS) is not None


def test_unknown_link_fails():
    r = {"link": "https://reddit.com/c/999", "quote": "Coding quality is close"}
    assert verify_review(r, "2026-11-18-01", REACTIONS) is not None


def test_valid_draft_has_no_errors():
    errors, _ = check({"stories": [story(i) for i in range(1, 16)], "opportunities": [], "past_reactions": {}}, ctx())
    assert errors == []


def test_rules_are_enforced():
    stories = [story(i, companies=["NVIDIA"]) for i in range(1, 16)]
    stories[3]["summary"] = "too short"
    stories[4]["related"] = ["2020-01-01-01"]
    errors, _ = check({"stories": stories, "opportunities": [], "past_reactions": {}}, ctx())
    text = " ".join(errors)
    assert "nvidia" in text and "summary has 2 words" in text and "not in history" in text


def test_missing_reviews_entry_is_an_error():
    draft = {"stories": [story(i) for i in range(1, 16)], "opportunities": [], "past_reactions": {}}
    errors, _ = check(draft, ctx(reactions=REACTIONS))
    assert any("past_reactions is missing" in e for e in errors)


def test_repair_caps_companies_and_fixes_tiers():
    stories = [story(i, companies=["NVIDIA"] if i < 6 else [f"Co{i}"], tier="quick") for i in range(1, 19)]
    stories[7]["related"] = ["2026-11-18-01", "bogus"]
    fixed = repair({"stories": stories, "past_reactions": {"2026-11-18-01": {
        "reviews": [{"link": COMMENT["link"], "quote": "made up"}], "sentiment": "positive", "pulse": "x"}}},
        ctx(reactions=REACTIONS))
    nvidia = [s for s in fixed["stories"] if s["companies"] == ["NVIDIA"]]
    assert len(nvidia) == config.MAX_PER_COMPANY
    assert [s["tier"] for s in fixed["stories"]][: config.MUST_KNOW] == ["must"] * config.MUST_KNOW
    assert any(s["related"] == ["2026-11-18-01"] for s in fixed["stories"])
    assert fixed["past_reactions"]["2026-11-18-01"]["reviews"] == []  # fabricated quote dropped


def test_storylines_chain_across_days():
    s = [{"id": "2026-11-17-01", "date": "2026-11-17", "headline": "a", "related": []},
         {"id": "2026-11-18-02", "date": "2026-11-18", "headline": "b", "related": ["2026-11-17-01"]},
         {"id": "2026-11-19-01", "date": "2026-11-19", "headline": "c", "related": ["2026-11-18-02"], "thread": "T"},
         {"id": "2026-11-19-02", "date": "2026-11-19", "headline": "d", "related": []}]
    chains = threads.build(s)
    assert [m["id"] for m in chains["2026-11-19-01"]] == ["2026-11-17-01", "2026-11-18-02", "2026-11-19-01"]
    assert threads.day_number(chains["2026-11-19-01"], s[2]) == 3
    assert len(chains["2026-11-19-02"]) == 1
    assert threads.storylines(s)[0]["name"] == "T"


def test_city_rules():
    stories = [story(i) for i in range(1, 16)]
    stories[5].update(city="Hyderabad", india="none")
    stories[6].update(city="Mumbai", india="india")
    errors, _ = check({"stories": stories, "opportunities": [], "past_reactions": {}}, ctx())
    assert any("Hyderabad" in e for e in errors) and any("city must be one of" in e for e in errors)
    fixed = repair({"stories": stories}, ctx())
    by_head = {s["headline"]: s for s in fixed["stories"]}
    assert by_head["Headline 6"]["india"] == "india" and by_head["Headline 7"]["city"] == ""


def test_city_detection():
    from ai_news_agent.collect import city_of, india_relevance
    assert city_of("Microsoft opens AI centre in Hyderabad") == "Hyderabad"
    assert city_of("Sarvam AI, the Bengaluru startup") == "Bengaluru"
    assert city_of("IIT Madras launches a course") == "Chennai"
    assert city_of("OpenAI launches a model") == ""
    assert india_relevance("Telangana AI policy") == "india"
