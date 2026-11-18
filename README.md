# AI Daily Brief: your personal AI news agent

An automatic agent that keeps you up to date on AI news from around the world.

- **4:00 AM, while you sleep:** it pulls the last day's articles from about 24 global AI news sources (US, EU, Asia and India press, plus the labs themselves: OpenAI, Google DeepMind, Hugging Face, NVIDIA and others). It removes duplicates and non-AI news, and Claude picks the ~12 most important stories.
- For each story, Claude writes a **60–100 word summary** (what happened, the key facts, why it matters), tags it by **technology category** (Models & LLMs, AI Agents, Robotics, Chips, Policy, …) and region, and adds a **"Read the full story →" link**. The code checks every summary's word count, and Claude rewrites any summary outside 60–100 words.
- **8:00 AM:** the digest is emailed to you.
- **Website:** a simple, readable page (GitHub Pages) with today's brief, category filters and an archive of every past day.

It runs entirely on **GitHub Actions** (free). Nothing has to stay on overnight.

```
4:00 AM  fetch-news.yml  →  RSS feeds → Claude selects + summarises → data/digest-DATE.json → docs/ website
8:00 AM  send-email.yml  →  emails today's digest (builds it on the spot if the 4 AM run failed)
```

## One-time setup (about 10 minutes)

### 1. Merge to `main`
Scheduled workflows only run on the repository's default branch.

### 2. Get two credentials
- **Anthropic API key:** https://console.anthropic.com → API Keys. Expect roughly $0.20–0.40 per day.
- **Gmail app password:** Google Account → Security → turn on 2-Step Verification → search "App passwords" → create one. You get a 16-character password. (Your normal Gmail password won't work.)

### 3. Add repository secrets
GitHub repo → **Settings → Secrets and variables → Actions → New repository secret**:

| Secret | Value |
|---|---|
| `ANTHROPIC_API_KEY` | your Anthropic key |
| `SMTP_USER` | your Gmail address (the account that sends the email) |
| `SMTP_PASSWORD` | the 16-character Gmail app password |
| `EMAIL_TO` | where to deliver the email (can be the same address; comma-separate several) |

### 4. Turn on the website
**Settings → Pages → Build and deployment → Deploy from a branch → `main` / `/docs` → Save.**
Your site will be at `https://<your-username>.github.io/<repo-name>/`.
Then add a repository **variable** (Variables tab) `SITE_URL` with that address so the email links to it.

> GitHub Pages on a **private** repository needs a paid GitHub plan. On a free plan, make the repo public or just use the emails. The digest is also saved as JSON in `data/`.

### 5. Test it now
**Actions → "Fetch AI news (4 AM)" → Run workflow**, then **Actions → "Email AI news (8 AM)" → Run workflow** (leave "wait" unchecked). You should get the email within a minute or two.

## Time zone

The schedule is set for **India Standard Time (Asia/Kolkata)**: 4:00 AM fetch, 8:00 AM email.
To use another time zone:
1. Set the repository variable `DIGEST_TIMEZONE`, for example `America/New_York` or `Europe/London`.
2. Edit the two `cron:` lines in `.github/workflows/`. Cron uses **UTC**: the fetch time is 4 AM local converted to UTC, and the email job should start about 55 minutes before 8 AM local.

GitHub sometimes starts scheduled jobs late. That's why the email job starts around 7:05, prepares everything, then waits so the email goes out at exactly 8:00.

## Optional settings (repository variables)

| Variable | Default | Meaning |
|---|---|---|
| `DIGEST_TIMEZONE` | `Asia/Kolkata` | your local time zone |
| `MAX_STORIES` | `12` | stories per day |
| `SITE_URL` | – | website link shown in the email |
| `SMTP_HOST` / `SMTP_PORT` | `smtp.gmail.com` / `465` | for Outlook use `smtp.office365.com` / `587` |

Edit news sources in `ai_news_agent/sources.py`, and the summary style in the prompts in `ai_news_agent/summarize.py`.

## Run locally

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=...            # optional: without it, summaries are simple extracts
python -m ai_news_agent fetch --force   # build today's digest + website (open docs/index.html)
SMTP_USER=you@gmail.com SMTP_PASSWORD=app-password python -m ai_news_agent email
```

## How it behaves when something fails
- A news source is down → skipped; the others still run.
- Claude API unavailable or no key → falls back to short extracts from the article so you still get an email.
- If Claude's safety filter declines a request, the API automatically retries on a fallback model (server-side fallbacks).
- The 4 AM run failed → the 8 AM job builds the digest itself before sending.
- Stories already covered in the last 7 days aren't repeated.
