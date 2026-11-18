"""Settings, all overridable with environment variables (GitHub repo Variables)."""
import os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
DOCS_DIR = ROOT / "docs"

TIMEZONE = ZoneInfo(os.getenv("DIGEST_TIMEZONE") or "Asia/Kolkata")
MODEL = os.getenv("CLAUDE_MODEL") or "claude-opus-5-5"
MAX_STORIES = int(os.getenv("MAX_STORIES") or 12)
LOOKBACK_HOURS = int(os.getenv("LOOKBACK_HOURS") or 30)
SITE_URL = (os.getenv("SITE_URL") or "").rstrip("/")

# Email delivery time (local time in TIMEZONE).
SEND_HOUR = int(os.getenv("SEND_HOUR") or 8)
SEND_MINUTE = int(os.getenv("SEND_MINUTE") or 0)

MIN_WORDS, MAX_WORDS = 60, 100

USER_AGENT = "Mozilla/5.0 (compatible; PersonalAINewsDigest/1.0; RSS reader)"


def today_local() -> str:
    return datetime.now(TIMEZONE).strftime("%Y-%m-%d")
