"""Settings, all overridable with environment variables (GitHub repository Variables)."""
import os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
DIGESTS_DIR = DATA_DIR / "digests"   # one JSON file per day
WORK_DIR = DATA_DIR / "work"         # scratch files for the editor run (not committed)
STATE_FILE = DATA_DIR / "state.json"
FEEDBACK_FILE = DATA_DIR / "feedback.json"

TIMEZONE = ZoneInfo(os.getenv("DIGEST_TIMEZONE") or "Asia/Kolkata")

# Editor (the single AI step each day)
CLAUDE_CODE_MODEL = os.getenv("CLAUDE_CODE_MODEL") or ""  # empty = your plan's default model
CLAUDE_TIMEOUT_MIN = int(os.getenv("CLAUDE_TIMEOUT_MIN") or 30)
CLAUDE_TOKEN_CREATED = os.getenv("CLAUDE_TOKEN_CREATED") or ""  # YYYY-MM-DD, for expiry reminders
MAX_WEB_SEARCHES = int(os.getenv("MAX_WEB_SEARCHES") or 5)
GEMINI_MODEL = os.getenv("GEMINI_MODEL") or "gemini-2.5-flash"  # free backup if GEMINI_API_KEY is set

# Digest shape and rules
MAX_STORIES = int(os.getenv("MAX_STORIES") or 20)
MIN_STORIES = int(os.getenv("MIN_STORIES") or 15)
MUST_KNOW = int(os.getenv("MUST_KNOW") or 5)             # full cards; the rest are quick hits
MAX_OPPORTUNITIES = int(os.getenv("MAX_OPPORTUNITIES") or 5)
MAX_PER_COMPANY = int(os.getenv("MAX_PER_COMPANY") or 2)
INDIA_SHARE = float(os.getenv("INDIA_SHARE") or 0.3)
MIN_TAMIL_NADU = int(os.getenv("MIN_TAMIL_NADU") or 2)
MIN_WORDS, MAX_WORDS = 60, 100
BRIEF_MIN, BRIEF_MAX = 8, 30
RECAP_WEEKDAY = int(os.getenv("RECAP_WEEKDAY") or 6)     # 6 = Sunday

# Memory
HISTORY_DAYS = int(os.getenv("HISTORY_DAYS") or 14)      # earlier stories the editor can link to
REACTION_DAYS = 2                                         # review stories from the last N days

# Collection
LOOKBACK_HOURS = int(os.getenv("LOOKBACK_HOURS") or 28)  # first run only
SHORTLIST_SIZE = int(os.getenv("SHORTLIST_SIZE") or 70)
CANDIDATE_TEXT_WORDS = int(os.getenv("CANDIDATE_TEXT_WORDS") or 350)

# Local app
APP_PORT = int(os.getenv("APP_PORT") or 8765)

USER_AGENT = "Mozilla/5.0 (compatible; PersonalAINewsDigest/1.0; RSS reader)"


def now_local() -> datetime:
    return datetime.now(TIMEZONE)


def today_local() -> str:
    return now_local().strftime("%Y-%m-%d")
