"""Send the daily digest by email over SMTP (works with Gmail app passwords)."""
from __future__ import annotations

import logging
import os
import smtplib
import ssl
from email.message import EmailMessage
from html import escape

from . import config
from .site import _pretty_date

log = logging.getLogger(__name__)


def _html(digest: dict) -> str:
    rows = []
    for s in digest["stories"]:
        meta = " · ".join(escape(x) for x in (s.get("technology"), s.get("region"), s["source"]) if x)
        rows.append(f"""
<tr><td style="padding:18px 0;border-bottom:1px solid #e6e6e6">
<div style="font-size:12px;color:#4f46e5;font-weight:700;text-transform:uppercase;letter-spacing:.04em">{escape(s['category'])}</div>
<div style="font-size:12px;color:#777;margin:2px 0 6px">{meta}</div>
<div style="font-size:18px;font-weight:700;line-height:1.35;color:#111;margin-bottom:6px">{escape(s['headline'])}</div>
<div style="font-size:15px;line-height:1.6;color:#333">{escape(s['summary'])}</div>
<div style="margin-top:8px"><a href="{escape(s['link'])}" style="color:#4f46e5;font-weight:700;text-decoration:none">Read the full story →</a></div>
</td></tr>""")
    site = (
        f'<p style="margin:24px 0 0;font-size:13px;color:#777">Browse on the web: '
        f'<a href="{escape(config.SITE_URL)}" style="color:#4f46e5">{escape(config.SITE_URL)}</a></p>'
        if config.SITE_URL else ""
    )
    return f"""<!doctype html><html><body style="margin:0;background:#f4f4f2">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr><td align="center" style="padding:24px 12px">
<table role="presentation" width="100%" style="max-width:640px;background:#fff;border-radius:12px;padding:8px 24px 24px;font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif">
<tr><td style="padding:20px 0 4px"><div style="font-size:24px;font-weight:800;color:#111">AI Daily Brief</div>
<div style="font-size:14px;color:#777">{_pretty_date(digest['date'])} · {len(digest['stories'])} stories</div></td></tr>
{''.join(rows) or '<tr><td style="padding:20px 0;color:#777">No new stories today.</td></tr>'}
<tr><td>{site}</td></tr></table></td></tr></table></body></html>"""


def _text(digest: dict) -> str:
    parts = [f"AI Daily Brief — {_pretty_date(digest['date'])}\n"]
    for i, s in enumerate(digest["stories"], 1):
        parts.append(f"{i}. [{s['category']}] {s['headline']}\n{s['summary']}\nRead more: {s['link']}\n")
    if config.SITE_URL:
        parts.append(f"Website: {config.SITE_URL}")
    return "\n".join(parts)


def send_digest(digest: dict) -> None:
    user = os.environ["SMTP_USER"]
    password = os.environ["SMTP_PASSWORD"]
    to = os.getenv("EMAIL_TO") or user
    host = os.getenv("SMTP_HOST") or "smtp.gmail.com"
    port = int(os.getenv("SMTP_PORT") or 465)

    msg = EmailMessage()
    msg["Subject"] = f"AI Daily Brief · {_pretty_date(digest['date'])} · {len(digest['stories'])} stories"
    msg["From"] = f"AI Daily Brief <{user}>"
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
