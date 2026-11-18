# AI Daily Brief: your personal AI news agent

Every morning at **8 AM IST** you get an email with the **15–20 most useful AI developments from around the world**. Each one has a headline, its essence in **60–100 words**, and a **"Read the full story →" link** if you want to go deeper. There's a dedicated **India & Tamil Nadu** section. The same brief is published on a small website with filters and an archive.

**Cost: ₹0 extra.** It runs on free GitHub Actions and free news sources, and the one AI step uses the **Claude Pro subscription you already have**.

## How it works: one run a day

```
4:00 AM IST  daily-digest.yml
  1. Gather  (code, free)   ~45 free sources, everything published since yesterday's run
  2. Shortlist (code, free) merge duplicate reports of the same event, drop junk, score,
                            keep ~70 candidates (with enough India / Tamil Nadu ones) + article text
  3. Edit (ONE Claude Code session on your Pro plan)
       - reads the shortlist (and may do up to 5 web searches for big stories the feeds missed)
       - picks 15–20 stories by your rules, writes headline + 60–100 word essence + link
       - runs `python -m ai_news_agent check` and fixes anything that breaks the rules
  4. Code re-checks everything, saves the digest, rebuilds the website

8:00 AM IST  send-email.yml  → emails the brief (builds it on the spot if the 4 AM run failed)
```

**Your rules (checked by code, not just requested):**
- **At most 2 stories per company.** Big labs (OpenAI, Google, Anthropic, Meta, NVIDIA…) are covered alongside **smaller firms and startups** (Sarvam AI, Mistral…).
- A mix of technologies: models, agents, chips, robotics, research, policy, funding, jobs & skills.
- About **30% India** (at most that plus 2), with **at least 2 Tamil Nadu items** when worthwhile ones exist (Chennai, Coimbatore, IIT Madras, state policy, investments, jobs, free courses).
- No repeats of stories sent in the last few days, and no opinion pieces, listicles or shopping deals.

**If something goes wrong, you still get an email:** Claude Code (Pro) → Gemini free tier (optional backup) → plain extracts from each article (no AI).

## Free news sources (no API keys)

About 40 RSS feeds and Google News searches, plus GDELT (worldwide news database) and Hacker News:
- **Global:** TechCrunch, The Verge, MIT Tech Review, Ars Technica, Wired, BBC, Rest of World, Sifted, SCMP, the labs' own blogs.
- **India:** Economic Times Tech, The Hindu, BusinessLine, Indian Express, Inc42, YourStory, Entrackr, MediaNama, Analytics India Magazine.
- **Tamil Nadu:** The Hindu Tamil Nadu, Times of India Chennai, and searches for Chennai, Coimbatore, Madurai, IIT Madras and AI news in Tamil.

Edit `ai_news_agent/sources.py` to add or remove sources.

## One-time setup (about 10 minutes)

1. **Make the repository public and merge to `main`.**
   - Public repos get unlimited free Actions minutes and free GitHub Pages.
   - Your secrets stay hidden either way.
   - Scheduled jobs only run from `main`.
2. **Claude Pro token:** on your computer, install Claude Code (`npm install -g @anthropic-ai/claude-code`) and run:
   ```
   claude setup-token
   ```
   Log in with your Pro account. It prints a long-lived token (valid about a year).
3. **Gmail app password:** Google Account → Security → 2-Step Verification on → "App passwords" → create one.
4. **Repository secrets** (Settings → Secrets and variables → Actions → *Secrets*):

   | Secret | Value |
   |---|---|
   | `CLAUDE_CODE_OAUTH_TOKEN` | the token from step 2 |
   | `SMTP_USER` | the Gmail address that sends the email |
   | `SMTP_PASSWORD` | the Gmail app password |
   | `EMAIL_TO` | where to deliver (comma-separate several) |
   | `GEMINI_API_KEY` | *optional* free backup key from aistudio.google.com |

5. **Website:** Settings → Pages → Deploy from a branch → `main` / `/docs`. Add the *variable* `SITE_URL` = `https://<username>.github.io/<repo>/`.
6. **Test:** Actions → "Daily AI digest" → Run workflow. When it finishes, Actions → "Email AI digest" → Run workflow.

### About your Pro usage
The daily run is one Claude Code session at 4 AM, while you're asleep. It uses part of your Pro usage window, which resets every few hours, so it shouldn't affect your daytime chats. If your limit is ever used up at 4 AM, the agent falls back automatically to Gemini or the plain extracts. Renew the token with `claude setup-token` when it expires.

## Settings (repository *variables*, all optional)

| Variable | Default | Meaning |
|---|---|---|
| `MAX_STORIES` / `MIN_STORIES` | `20` / `15` | digest size |
| `MAX_PER_COMPANY` | `2` | most stories about one company |
| `INDIA_SHARE` | `0.3` | target share of India stories |
| `MIN_TAMIL_NADU` | `2` | Tamil Nadu stories to include when worthwhile |
| `MAX_WEB_SEARCHES` | `5` | extra searches Claude may do to catch missed stories (0 = none) |
| `CLAUDE_CODE_MODEL` | plan default | e.g. `opus` or `sonnet` |
| `GEMINI_MODEL` | `gemini-2.5-flash` | backup model name |
| `DIGEST_TIMEZONE` | `Asia/Kolkata` | change the `cron:` lines too (they are UTC) |
| `SITE_URL` | – | website link in the email |

## Run locally

```bash
pip install -r requirements.txt
USE_LOCAL_CLAUDE=1 python -m ai_news_agent daily --force   # uses your local Claude Code login
open docs/index.html
SMTP_USER=you@gmail.com SMTP_PASSWORD=app-password python -m ai_news_agent email
```
