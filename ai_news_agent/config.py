"""Settings, all overridable with environment variables (GitHub repository Variables)."""
import os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
WORK_DIR = DATA_DIR / "work"  # scratch files for the editor run (not committed)
DOCS_DIR = ROOT / "docs"

TIMEZONE = ZoneInfo(os.getenv("DIGEST_TIMEZONE") or "Asia/Kolkata")

# Editor (the single AI step each day)
CLAUDE_CODE_MODEL = os.getenv("CLAUDE_CODE_MODEL") or ""  # empty = your plan's default model
CLAUDE_TIMEOUT_MIN = int(os.getenv("CLAUDE_TIMEOUT_MIN") or 25)
MAX_WEB_SEARCHES = int(os.getenv("MAX_WEB_SEARCHES") or 5)  # gap-filling searches by Claude
GEMINI_MODEL = os.getenv("GEMINI_MODEL") or "gemini-2.5-flash"  # free backup if GEMINI_API_KEY is set

# Digest size and diversity rules
MAX_STORIES = int(os.getenv("MAX_STORIES") or 20)
MIN_STORIES = int(os.getenv("MIN_STORIES") or 15)
MAX_PER_COMPANY = int(os.getenv("MAX_PER_COMPANY") or 2)
INDIA_SHARE = float(os.getenv("INDIA_SHARE") or 0.3)
MIN_TAMIL_NADU = int(os.getenv("MIN_TAMIL_NADU") or 2)
MIN_WORDS, MAX_WORDS = 60, 100

# Collection
LOOKBACK_HOURS = int(os.getenv("LOOKBACK_HOURS") or 28)  # used on the first run only
SHORTLIST_SIZE = int(os.getenv("SHORTLIST_SIZE") or 70)
CANDIDATE_TEXT_WORDS = int(os.getenv("CANDIDATE_TEXT_WORDS") or 350)

SITE_URL = (os.getenv("SITE_URL") or "").rstrip("/")
SEND_HOUR = int(os.getenv("SEND_HOUR") or 8)
SEND_MINUTE = int(os.getenv("SEND_MINUTE") or 0)

USER_AGENT = "Mozilla/5.0 (compatible; PersonalAINewsDigest/1.0; RSS reader)"


def today_local() -> str:
    return datetime.now(TIMEZONE).strftime("%Y-%m-%d")
