"""Send the daily digest by email over SMTP (works with Gmail app passwords)."""
from __future__ import annotations

import logging
import os
import smtplib
import ssl
from email.message import EmailMessage
from html import escape

from . import config
from .site import _pretty_date, split_sections

log = logging.getLogger(__name__)


SERIF = "Georgia,'Times New Roman',serif"
SANS = "-apple-system,'Segoe UI',Roboto,Arial,sans-serif"


def _html(digest: dict) -> str:
    rows = []
    for section, stories in split_sections(digest["stories"]):
        rows.append(
            f'<tr><td style="padding:30px 0 4px;font:700 12px {SANS};letter-spacing:2px;text-transform:uppercase;'
            f'color:#b4441c;border-bottom:1px solid #e3d9c8">{escape(section)}</td></tr>')
        rows.extend(_story_row(n, s) for n, s in stories)
    return _wrap(digest, rows)


def _story_row(n: int, s: dict) -> str:
    tn = (' &nbsp;<span style="background:#fbecc8;color:#8a5a00;border-radius:3px;padding:1px 6px">TAMIL NADU</span>'
          if s.get("india") == "tamil_nadu" else "")
    kicker = " · ".join(escape(x) for x in (s["category"], s.get("technology")) if x)
    r = s.get("reactions") or {}
    talk = ""
    if r.get("pulse") or r.get("reviews"):
        gist = escape(r.get("pulse") or f"{len(r['reviews'])} comments from Reddit / Hacker News")
        more = (f' <a href="{escape(config.SITE_URL)}/#people-{n}" style="color:#b4441c">Read what they say →</a>'
                if config.SITE_URL else "")
        talk = (f'<div style="margin-top:10px;padding:10px 12px;background:#f7f2e8;border-radius:4px 12px 12px 12px;'
                f'font:italic 15px/1.5 {SERIF};color:#5a4f47">💬 People are saying: {gist}{more}</div>')
    return f"""
<tr><td style="padding:22px 0;border-bottom:1px solid #e3d9c8">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr>
<td valign="top" width="40" style="font:600 22px/1.2 {SERIF};color:#b8ab9d">{n:02d}</td>
<td valign="top">
<div style="font:700 11px {SANS};letter-spacing:1px;text-transform:uppercase;color:#b4441c">{kicker}{tn}</div>
<div style="font:700 21px/1.3 {SERIF};color:#2a2420;margin:6px 0 8px">{escape(s['headline'])}</div>
<div style="font:17px/1.6 {SERIF};color:#3b332d">{escape(s['summary'])}</div>
<div style="margin-top:10px;font:13px {SANS};color:#6b6058">{escape(s['source'])} &nbsp;·&nbsp;
<a href="{escape(s['link'])}" style="color:#b4441c;font-weight:700;text-decoration:none">Read the full story →</a></div>
{talk}
</td></tr></table>
</td></tr>"""


def _wrap(digest: dict, rows: list[str]) -> str:
    site = (f'<a href="{escape(config.SITE_URL)}" style="color:#b4441c">Open today\'s edition on the web</a> · '
            if config.SITE_URL else "")
    n = len(digest["stories"])
    return f"""<!doctype html><html><body style="margin:0;background:#f7f2e8">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr><td align="center" style="padding:24px 12px">
<table role="presentation" width="100%" style="max-width:640px;background:#fffdf8;border:1px solid #e3d9c8;padding:8px 26px 26px">
<tr><td style="text-align:center;padding:22px 0 12px;border-bottom:3px double #2a2420">
<div style="font:italic 16px {SERIF};color:#6b6058">Good morning. Here's what happened in AI while you slept.</div>
<div style="font:700 40px/1.1 {SERIF};color:#2a2420;margin:6px 0">The Morning Brief</div>
<div style="font:600 11px {SANS};letter-spacing:1.5px;text-transform:uppercase;color:#6b6058">
{_pretty_date(digest['date'])} &nbsp;·&nbsp; {n} stories</div></td></tr>
{''.join(rows) or f'<tr><td style="padding:24px 0;font:italic 17px {SERIF};color:#6b6058">A quiet day. Nothing worth your time.</td></tr>'}
<tr><td style="padding-top:22px;font:13px/1.6 {SANS};color:#8a7f75;text-align:center">
{site}Have a good day ☕</td></tr></table></td></tr></table></body></html>"""


def _text(digest: dict) -> str:
    parts = [f"THE MORNING BRIEF · {_pretty_date(digest['date'])}",
             "Good morning. Here's what happened in AI while you slept.\n"]
    for section, stories in split_sections(digest["stories"]):
        parts.append(f"== {section.upper()} ==\n")
        for n, s in stories:
            parts.append(f"{n:02d}. {s['headline']}\n{s['summary']}\nRead more: {s['link']}")
            pulse = (s.get("reactions") or {}).get("pulse")
            if pulse:
                parts.append(f"People are saying: {pulse}")
            parts.append("")
    if config.SITE_URL:
        parts.append(f"On the web (with 'What People Say'): {config.SITE_URL}")
    return "\n".join(parts)


def send_digest(digest: dict) -> None:
    user = os.environ["SMTP_USER"]
    password = os.environ["SMTP_PASSWORD"]
    to = os.getenv("EMAIL_TO") or user
    host = os.getenv("SMTP_HOST") or "smtp.gmail.com"
    port = int(os.getenv("SMTP_PORT") or 465)

    msg = EmailMessage()
    msg["Subject"] = f"☕ The Morning Brief · {_pretty_date(digest['date'])} · {len(digest['stories'])} AI stories"
    msg["From"] = f"The Morning Brief <{user}>"
    msg["To"] = to
    msg.set_content(_text(digest))
    msg.add_alternative(_html(digest), subtype="html")

    context = ssl.create_default_context()
    if port == 465:
        with smtplib.SMTP_SSL(host, port, context=context, timeout=60) as smtp:
            smtp.login(user, password)
            smtp.send_message(msg)
    else:
        with smtplib.SMTP(host, port, timeout=60) as smtp:
            smtp.starttls(context=context)
            smtp.login(user, password)
            smtp.send_message(msg)
    log.info("Sent digest for %s to %d recipient(s)", digest["date"], len(to.split(",")))
