"""Render the static website (GitHub Pages serves the docs/ folder).

Two tabs per day:
  The News         - each story: headline, 60-100 word essence, link to the full article
  What People Say  - for the same story numbers: real user comments from Reddit / Hacker News
"""
from __future__ import annotations

import json
from datetime import datetime
from html import escape

from . import config
from .sources import CATEGORIES

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600;9..144,700'
         '&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&family=Inter:wght@500;600&display=swap" rel="stylesheet">')

CSS = """
:root{--paper:#f7f2e8;--card:#fffdf8;--ink:#2a2420;--soft:#6b6058;--faint:#a3978c;--rule:#e3d9c8;
--accent:#b4441c;--accent-soft:#f6e3d6;--tn:#8a5a00;--tn-soft:#fbecc8;
--pos:#2f6b3f;--pos-soft:#e1efe2;--mix:#8a6400;--mix-soft:#f6ebcc;--neg:#9b2f2f;--neg-soft:#f6dede;
--serif:"Source Serif 4",Georgia,"Times New Roman",serif;--display:"Fraunces",Georgia,serif;
--ui:Inter,-apple-system,"Segoe UI",Roboto,sans-serif}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--paper:#1c1916;--card:#24201c;--ink:#ece3d5;--soft:#b3a796;
--faint:#7d7266;--rule:#3a332c;--accent:#e98a5c;--accent-soft:#3d2a1f;--tn:#f0c46a;--tn-soft:#3b3020;
--pos:#8fcf9c;--pos-soft:#1f3326;--mix:#e8c46b;--mix-soft:#3a3120;--neg:#ee9a9a;--neg-soft:#3d2424}}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--paper);color:var(--ink);font:18px/1.65 var(--serif);
-webkit-font-smoothing:antialiased}
a{color:inherit}
.wrap{max-width:720px;margin:0 auto;padding:28px 16px 80px}
.mast{text-align:center;border-bottom:3px double var(--ink);padding-bottom:14px}
.mast .hello{font:italic 17px/1.4 var(--serif);color:var(--soft);margin:0 0 6px}
.mast h1{font:700 clamp(38px,9vw,60px)/1 var(--display);letter-spacing:-.02em;margin:0}
.mast .line{display:flex;justify-content:space-between;flex-wrap:wrap;gap:4px 12px;margin-top:12px;
padding-top:8px;border-top:1px solid var(--ink);font:500 12px/1.4 var(--ui);letter-spacing:.06em;
text-transform:uppercase;color:var(--soft)}
.tabs{display:flex;gap:28px;justify-content:center;margin:18px 0 6px;border-bottom:1px solid var(--rule)}
.tabs a{font:600 15px var(--ui);text-decoration:none;color:var(--soft);padding:10px 2px 12px;
border-bottom:3px solid transparent;margin-bottom:-1px}
.tabs a.on{color:var(--ink);border-color:var(--accent)}
.tabs .n{font-weight:500;color:var(--faint);margin-left:4px}
.filters{font:500 13px/2 var(--ui);color:var(--soft);text-align:center;margin:10px 0 4px}
.filters button{background:none;border:0;font:inherit;color:inherit;cursor:pointer;padding:2px 6px;
border-radius:4px}
.filters button.on{background:var(--ink);color:var(--paper)}
.section{display:flex;align-items:center;gap:12px;margin:40px 0 6px;font:700 13px var(--ui);
letter-spacing:.14em;text-transform:uppercase;color:var(--accent)}
.section:after{content:"";flex:1;border-top:1px solid var(--rule)}
.section small{font-weight:500;letter-spacing:.02em;text-transform:none;color:var(--faint)}
.story{display:grid;grid-template-columns:44px 1fr;gap:0 14px;padding:22px 0;border-bottom:1px solid var(--rule)}
.num{font:600 26px/1 var(--display);color:var(--faint);padding-top:4px}
.kicker{font:600 11.5px/1.4 var(--ui);letter-spacing:.1em;text-transform:uppercase;color:var(--accent)}
.kicker .tn{color:var(--tn);background:var(--tn-soft);border-radius:3px;padding:1px 6px;margin-left:6px}
.story h2{font:600 23px/1.25 var(--display);letter-spacing:-.01em;margin:6px 0 8px}
.story.lead h2{font-size:31px}
.story.lead .summary:first-letter{float:left;font:700 54px/.85 var(--display);padding:6px 8px 0 0;color:var(--accent)}
.summary{margin:0}
.byline{display:flex;flex-wrap:wrap;gap:6px 16px;align-items:center;margin-top:10px;font:500 13px/1.5 var(--ui);color:var(--soft)}
.byline .more{color:var(--accent);font-weight:600;text-decoration:none}
.byline .more:hover,.byline .talk:hover{text-decoration:underline}
.byline .talk{text-decoration:none}
.chip{display:inline-block;font:600 11.5px/1 var(--ui);border-radius:99px;padding:5px 9px}
.chip.positive{color:var(--pos);background:var(--pos-soft)}
.chip.mixed{color:var(--mix);background:var(--mix-soft)}
.chip.negative{color:var(--neg);background:var(--neg-soft)}
.chip.none{color:var(--soft);background:var(--rule)}
.people{padding:24px 0;border-bottom:1px solid var(--rule);display:grid;grid-template-columns:44px 1fr;gap:0 14px}
.people h3{font:600 20px/1.3 var(--display);margin:2px 0 8px}
.people h3 a{text-decoration:none}
.pulse{font-style:italic;color:var(--soft);margin:8px 0 14px}
.quote{position:relative;background:var(--card);border:1px solid var(--rule);border-radius:4px 16px 16px 16px;
padding:14px 16px 12px;margin:12px 0;box-shadow:0 1px 0 var(--rule)}
.quote p{margin:0;font-size:17px}
.quote p:before{content:"“";font:700 30px/0 var(--display);color:var(--accent);vertical-align:-10px;margin-right:2px}
.quote .gist{font:500 13.5px/1.5 var(--ui);color:var(--soft);margin-top:8px}
.quote .who{display:flex;justify-content:space-between;flex-wrap:wrap;gap:4px 12px;margin-top:8px;
font:500 12px/1.4 var(--ui);color:var(--faint)}
.quote .who a{color:var(--accent);text-decoration:none}
.quiet{margin-top:34px;padding:16px 18px;border:1px dashed var(--rule);border-radius:10px;font-size:16px;color:var(--soft)}
.quiet a{color:var(--ink)}
.note{font:500 13px/1.6 var(--ui);color:var(--faint);text-align:center;margin:30px 0 0}
footer{margin-top:44px;padding-top:16px;border-top:3px double var(--ink);font:500 13px/1.7 var(--ui);color:var(--soft);text-align:center}
footer a{color:var(--accent)}
[hidden]{display:none!important}
.archive{list-style:none;padding:0;margin:20px 0}
.archive li{padding:14px 0;border-bottom:1px solid var(--rule)}
.archive a{text-decoration:none}
.archive .d{font:600 12px var(--ui);letter-spacing:.08em;text-transform:uppercase;color:var(--accent)}
.archive .h{display:block;font:600 19px/1.35 var(--display);margin-top:3px}
.empty{text-align:center;color:var(--soft);padding:48px 0;font-style:italic}
@media (max-width:520px){body{font-size:17px}.story,.people{grid-template-columns:30px 1fr;gap:0 10px}
.num{font-size:20px}.story h2{font-size:21px}.story.lead h2{font-size:25px}.tabs{gap:18px}}
"""

JS = """
(function(){
 var tabs=document.querySelectorAll('.tabs a'),panes=document.querySelectorAll('[data-pane]');
 function show(h){var name=(h||'').indexOf('#people')===0?'people':'news';
  tabs.forEach(function(t){t.classList.toggle('on',t.dataset.tab===name)});
  panes.forEach(function(p){p.hidden=p.dataset.pane!==name});
  var el=h&&h.length>1&&document.getElementById(h.slice(1)); if(el&&h!=='#people'&&h!=='#news')el.scrollIntoView();}
 window.addEventListener('hashchange',function(){show(location.hash)}); show(location.hash);
 document.querySelectorAll('.filters button').forEach(function(b){b.onclick=function(){
  document.querySelectorAll('.filters button').forEach(function(x){x.classList.toggle('on',x===b)});
  var c=b.dataset.cat;document.querySelectorAll('.story').forEach(function(s){
   s.hidden=!(c==='All'||s.dataset.cat===c||(c==='India'&&s.dataset.india!=='none'))});
  document.querySelectorAll('[data-pane=news] .section').forEach(function(h){h.hidden=c!=='All'})}});
})();
"""

SENTIMENT = {"positive": "Mostly positive", "mixed": "Mixed feelings", "negative": "Skeptical",
             "none": "Quiet so far"}


def _pretty_date(date: str) -> str:
    return datetime.strptime(date, "%Y-%m-%d").strftime("%A, %d %B %Y")


def split_sections(stories: list[dict]) -> list[tuple[str, list[tuple[int, dict]]]]:
    """Group stories into world / India sections, numbered 1..N in reading order."""
    world = [s for s in stories if s.get("india", "none") == "none"]
    india = [s for s in stories if s.get("india", "none") != "none"]
    out, n = [], 0
    for title, group in (("Around the world", world), ("Closer to home · India & Tamil Nadu", india)):
        if group:
            out.append((title, [(n + i, s) for i, s in enumerate(group, 1)]))
            n += len(group)
    return out


def numbered(stories: list[dict]) -> list[tuple[int, dict]]:
    return [item for _, group in split_sections(stories) for item in group]


def _page(title: str, body: str, prefix: str) -> str:
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(title)}</title>{FONTS}<style>{CSS}</style></head>
<body><div class="wrap">{body}
<footer>Gathered while you slept by your own little news agent ·
<a href="{prefix}index.html">Today</a> · <a href="{prefix}archive.html">Past mornings</a></footer>
</div><script>{JS}</script></body></html>"""


def _reviews_of(s: dict) -> list[dict]:
    return (s.get("reactions") or {}).get("reviews", [])


def _story_html(n: int, s: dict, lead: bool) -> str:
    tn = '<span class="tn">Tamil Nadu</span>' if s.get("india") == "tamil_nadu" else ""
    kicker = " · ".join(escape(x) for x in (s["category"], s.get("technology")) if x)
    by = [escape(s["source"])]
    if s.get("also_covered_by"):
        k = len(s["also_covered_by"])
        by.append(f"also in {k} other outlet{'s' if k > 1 else ''}")
    reviews = _reviews_of(s)
    talk = (f'<a class="talk" href="#people-{n}">💬 What people say ({len(reviews)})</a>' if reviews else "")
    return f"""<article class="story{' lead' if lead else ''}" id="story-{n}" data-cat="{escape(s['category'])}" data-india="{escape(s.get('india', 'none'))}">
<div class="num">{n:02d}</div><div>
<div class="kicker">{kicker}{tn}</div>
<h2>{escape(s['headline'])}</h2>
<p class="summary">{escape(s['summary'])}</p>
<div class="byline"><span>{' · '.join(by)}</span>
<a class="more" href="{escape(s['link'])}" target="_blank" rel="noopener">Read the full story →</a>{talk}</div>
</div></article>"""


def _people_html(n: int, s: dict) -> str:
    r = s.get("reactions") or {}
    reviews = _reviews_of(s)
    sentiment = r.get("sentiment") if r.get("sentiment") in SENTIMENT else "none"
    chip = "" if r.get("auto") else f'<span class="chip {sentiment}">{SENTIMENT[sentiment]}</span>'
    pulse = f'<p class="pulse">{escape(r["pulse"])}</p>' if r.get("pulse") else ""
    quotes = []
    for q in reviews:
        votes = f" · ▲ {q['score']}" if q.get("platform") == "Reddit" and q.get("score") else ""
        gist = f'<div class="gist">In short: {escape(q["takeaway"])}</div>' if q.get("takeaway") else ""
        quotes.append(f"""<div class="quote"><p>{escape(q['quote'])}</p>{gist}
<div class="who"><span>{escape(' · '.join(dict.fromkeys(x for x in (q.get('platform'), q.get('community')) if x)))}{votes}</span>
<a href="{escape(q['link'])}" target="_blank" rel="noopener">See the conversation ↗</a></div></div>""")
    return f"""<section class="people" id="people-{n}"><div class="num">{n:02d}</div><div>
<h3><a href="#story-{n}">{escape(s['headline'])}</a></h3>{chip}{pulse}{''.join(quotes)}
</div></section>"""


def _digest_body(digest: dict, edition: int) -> str:
    stories = digest["stories"]
    total_words = sum(len(s["summary"].split()) + 14 for s in stories)
    minutes = max(1, round(total_words / 220))
    with_talk = [(n, s) for n, s in numbered(stories) if _reviews_of(s)]
    quiet = [(n, s) for n, s in numbered(stories) if not _reviews_of(s)]

    cats = [c for c in CATEGORIES if any(s["category"] == c for s in stories)]
    if any(s.get("india", "none") != "none" for s in stories):
        cats.insert(0, "India")
    filters = "".join(f'<button data-cat="{escape(c)}"{" class=on" if c == "All" else ""}>{escape(c)}</button>'
                      for c in ["All", *cats])

    news = []
    for title, group in split_sections(stories):
        news.append(f'<h3 class="section">{escape(title)} <small>{len(group)}</small></h3>')
        news += [_story_html(n, s, lead=(n == 1)) for n, s in group]

    people = [_people_html(n, s) for n, s in with_talk]
    if quiet:
        links = ", ".join(f'<a href="#story-{n}">{n:02d}</a>' for n, _ in quiet)
        people.append(f'<div class="quiet"><b>Quiet so far:</b> {links}. No genuine discussion turned up '
                      "yet. Policy and regional news often takes a few days to get people talking.</div>")
    if not with_talk:
        people.insert(0, '<p class="empty">Nobody seems to be talking about today\'s stories yet.</p>')
    auto = any((s.get("reactions") or {}).get("auto") for s in stories)

    return f"""<header class="mast">
<p class="hello">Good morning. Here's what happened in AI while you slept.</p>
<h1>The Morning Brief</h1>
<div class="line"><span>{_pretty_date(digest['date'])}</span><span>No. {edition}</span>
<span>{len(stories)} stories · {minutes} min read</span></div></header>
<nav class="tabs"><a href="#news" data-tab="news" class="on">The News<span class="n">{len(stories)}</span></a>
<a href="#people" data-tab="people">What People Say<span class="n">{len(with_talk)}</span></a></nav>
<div data-pane="news"><div class="filters">{filters}</div>{''.join(news) or '<p class="empty">A quiet day.</p>'}</div>
<div data-pane="people" hidden>{''.join(people)}
<p class="note">Every quote is a real comment from Reddit or Hacker News, copied word for word and linked.
{'Some were auto-picked by votes because the editor was unavailable.' if auto else ''}</p></div>"""


def build_site() -> None:
    config.DOCS_DIR.mkdir(exist_ok=True)
    (config.DOCS_DIR / "days").mkdir(exist_ok=True)
    (config.DOCS_DIR / ".nojekyll").touch()

    digests = sorted(config.DATA_DIR.glob("digest-*.json"))
    rows = []
    for edition, path in enumerate(digests, 1):
        digest = json.loads(path.read_text())
        body = _digest_body(digest, edition)
        (config.DOCS_DIR / "days" / f"{digest['date']}.html").write_text(
            _page(f"The Morning Brief · {digest['date']}", body, "../"))
        if edition == len(digests):
            (config.DOCS_DIR / "index.html").write_text(_page("The Morning Brief", body, ""))
        lead = digest["stories"][0]["headline"] if digest["stories"] else ""
        rows.append(f'<li><a href="days/{digest["date"]}.html"><span class="d">{_pretty_date(digest["date"])} · '
                    f'No. {edition}</span><span class="h">{escape(lead)}</span></a></li>')

    if not digests:
        (config.DOCS_DIR / "index.html").write_text(_page("The Morning Brief", (
            '<header class="mast"><p class="hello">Hello there.</p><h1>The Morning Brief</h1></header>'
            '<p class="empty">The first edition lands after the next 4 AM run.</p>'), ""))

    (config.DOCS_DIR / "archive.html").write_text(_page("The Morning Brief · Past mornings", (
        '<header class="mast"><h1>Past mornings</h1></header>'
        f'<ul class="archive">{"".join(reversed(rows))}</ul>'), ""))
