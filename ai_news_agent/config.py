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
# Model for the frequent scan/triage calls. Set to "claude-haiku-5-5" to cut cost.
TRIAGE_MODEL = os.getenv("TRIAGE_MODEL") or MODEL

# Final digest size and diversity rules.
MAX_STORIES = int(os.getenv("MAX_STORIES") or 20)
MIN_STORIES = int(os.getenv("MIN_STORIES") or 15)
MAX_PER_COMPANY = int(os.getenv("MAX_PER_COMPANY") or 2)
INDIA_SHARE = float(os.getenv("INDIA_SHARE") or 0.3)  # target share of India / Tamil Nadu stories
MIN_TAMIL_NADU = int(os.getenv("MIN_TAMIL_NADU") or 2)  # if worthwhile ones exist

# How far back the first scan looks (later scans only add what is new).
LOOKBACK_HOURS = int(os.getenv("LOOKBACK_HOURS") or 30)
SITE_URL = (os.getenv("SITE_URL") or "").rstrip("/")

# Email delivery time (local time in TIMEZONE).
SEND_HOUR = int(os.getenv("SEND_HOUR") or 8)
SEND_MINUTE = int(os.getenv("SEND_MINUTE") or 0)

MIN_WORDS, MAX_WORDS = 60, 100

USER_AGENT = "Mozilla/5.0 (compatible; PersonalAINewsDigest/1.0; RSS reader)"


def today_local() -> str:
    return datetime.now(TIMEZONE).strftime("%Y-%m-%d")
