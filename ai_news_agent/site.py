"""Render the static website (GitHub Pages serves the docs/ folder)."""
from __future__ import annotations

import json
from datetime import datetime
from html import escape

from . import config
from .sources import CATEGORIES

CSS = """
:root{--bg:#f7f7f5;--card:#fff;--ink:#1c1d21;--muted:#62656e;--line:#e4e4e0;
--accent:#4f46e5;--accent-soft:#eef0ff;--chip:#f0f0ec}
@media (prefers-color-scheme:dark){:root{--bg:#111215;--card:#1a1b1f;--ink:#ececef;
--muted:#9a9ca5;--line:#2a2b31;--accent:#8b8cff;--accent-soft:#25264a;--chip:#24252b}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,Roboto,sans-serif}
.wrap{max-width:780px;margin:0 auto;padding:32px 16px 64px}
header h1{margin:0;font-size:28px;letter-spacing:-.02em}
header p{margin:4px 0 0;color:var(--muted)}
nav{margin:18px 0 6px;display:flex;flex-wrap:wrap;gap:8px}
nav button{border:1px solid var(--line);background:var(--chip);color:var(--ink);
border-radius:999px;padding:5px 12px;font-size:13px;cursor:pointer}
nav button.on{background:var(--accent);border-color:var(--accent);color:#fff}
.story{background:var(--card);border:1px solid var(--line);border-radius:14px;
padding:18px 20px;margin:14px 0}
.meta{display:flex;flex-wrap:wrap;gap:6px 10px;font-size:12.5px;color:var(--muted);margin-bottom:6px}
.cat{background:var(--accent-soft);color:var(--accent);font-weight:600;border-radius:6px;padding:1px 8px}
.story h2{font-size:19px;line-height:1.35;margin:4px 0 8px;letter-spacing:-.01em}
.story p{margin:0 0 10px}
.story a.more{color:var(--accent);font-weight:600;text-decoration:none}
.story a.more:hover{text-decoration:underline}
.archive a{color:var(--accent)}
.archive li{margin:6px 0}
footer{margin-top:40px;color:var(--muted);font-size:13px}
.empty{color:var(--muted);padding:40px 0}
"""

FILTER_JS = """
document.querySelectorAll('nav button').forEach(b=>b.onclick=()=>{
document.querySelectorAll('nav button').forEach(x=>x.classList.toggle('on',x===b));
const c=b.dataset.cat;document.querySelectorAll('.story').forEach(s=>
s.style.display=(c==='All'||s.dataset.cat===c)?'':'none')});
"""


def _pretty_date(date: str) -> str:
    return datetime.strptime(date, "%Y-%m-%d").strftime("%A, %d %B %Y")


def _page(title: str, body: str, prefix: str) -> str:
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(title)}</title><style>{CSS}</style></head>
<body><div class="wrap">{body}
<footer>Updated automatically every morning ·
<a href="{prefix}archive.html">Archive</a> · <a href="{prefix}index.html">Latest</a></footer>
</div><script>{FILTER_JS}</script></body></html>"""


def _story_html(s: dict) -> str:
    meta = [f'<span class="cat">{escape(s["category"])}</span>']
    for key in ("technology", "region", "source"):
        if s.get(key):
            meta.append(f"<span>{escape(s[key])}</span>")
    return f"""<article class="story" data-cat="{escape(s['category'])}">
<div class="meta">{' · '.join(meta)}</div>
<h2>{escape(s['headline'])}</h2>
<p>{escape(s['summary'])}</p>
<a class="more" href="{escape(s['link'])}" target="_blank" rel="noopener">Read the full story →</a>
</article>"""


def _digest_body(digest: dict) -> str:
    stories = digest["stories"]
    cats = [c for c in CATEGORIES if any(s["category"] == c for s in stories)]
    chips = "".join(
        f'<button data-cat="{escape(c)}"{" class=on" if c == "All" else ""}>{escape(c)}</button>'
        for c in ["All", *cats]
    )
    items = "\n".join(_story_html(s) for s in stories) or '<p class="empty">No stories today.</p>'
    return f"""<header><h1>AI Daily Brief</h1>
<p>{_pretty_date(digest['date'])} · {len(stories)} stories from around the world</p></header>
<nav>{chips}</nav>{items}"""


def build_site() -> None:
    config.DOCS_DIR.mkdir(exist_ok=True)
    (config.DOCS_DIR / "days").mkdir(exist_ok=True)
    (config.DOCS_DIR / ".nojekyll").touch()

    digests = sorted(config.DATA_DIR.glob("digest-*.json"), reverse=True)
    for i, path in enumerate(digests):
        digest = json.loads(path.read_text())
        page = _page(f"AI Daily Brief – {digest['date']}", _digest_body(digest), "../")
        (config.DOCS_DIR / "days" / f"{digest['date']}.html").write_text(page)
        if i == 0:
            latest = _page("AI Daily Brief", _digest_body(digest), "")
            (config.DOCS_DIR / "index.html").write_text(latest)

    if not digests:
        (config.DOCS_DIR / "index.html").write_text(
            _page("AI Daily Brief", '<header><h1>AI Daily Brief</h1></header>'
                  '<p class="empty">The first digest will appear after the next 4 AM run.</p>', "")
        )

    rows = "".join(
        f'<li><a href="days/{p.stem[7:]}.html">{_pretty_date(p.stem[7:])}</a></li>' for p in digests
    )
    (config.DOCS_DIR / "archive.html").write_text(
        _page("AI Daily Brief – Archive",
              f'<header><h1>Archive</h1><p>Every past briefing</p></header><ul class="archive">{rows}</ul>', "")
    )
