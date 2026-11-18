# AI Daily Brief: your personal AI news agent

An automatic agent that follows AI news worldwide all day and emails you the **15–20 most useful updates every morning at 8 AM**. The selection mixes companies and regions and gives real space to **India and Tamil Nadu**.

## How it works

```
Every 4 hours  scan-news.yml    gather new articles → sort into new / duplicate / skip → story pool
4:00 AM        fetch-news.yml   final scan → editor picks the top 15–20 (diversity rules) → 60–100 word summaries → website
8:00 AM        send-email.yml   emails the digest (builds it on the spot if the 4 AM run failed)
```

1. **All-day catch-up, not a 4 AM snapshot.** Every 4 hours (8 AM, 12, 4 PM, 8 PM, midnight and 4 AM IST) the agent collects what's new since the last scan and compares it with the stories it already has:
   - **duplicate:** the same event from another outlet. It's merged into the existing story, and more coverage counts as a sign the story matters.
   - **skip:** opinion pieces, listicles, deals, reviews, non-AI news.
   - **new:** scored 1–10 for importance and tagged with category, companies, region and India / Tamil Nadu relevance.
2. **4 AM: editor's choice.** From everything gathered since yesterday's digest, it picks 15–20 stories and then applies hard rules in code:
   - **at most 2 stories per company**, so the brief is never all NVIDIA;
   - a mix of big labs (OpenAI, Google, Anthropic, Meta…) and **smaller firms and startups** (Sarvam AI, Mistral, new startups);
   - about **30% India**, with **at least 2 Tamil Nadu items** when worthwhile ones exist (Chennai, Coimbatore, IIT Madras, state policy, investments, jobs, courses);
   - a spread of technologies: models, agents, chips, robotics, policy, funding, jobs and skills…
3. **Summaries:** each story gets a 60–100 word summary (what happened, key facts, why it matters, and any opportunity for you) plus a **"Read the full story →" link**. The code checks every word count and has Claude rewrite any summary outside the range.
4. **Email at 8 AM** in two sections: *Around the world* and *India & Tamil Nadu*. The **website** (GitHub Pages) has the same content, with category and India filters and an archive.

## News sources: all free, no API keys

| Source | What it adds | Key needed? |
|---|---|---|
| **RSS feeds** (~25 global): TechCrunch, The Verge, MIT Tech Review, BBC, Rest of World, Sifted, SCMP, OpenAI, DeepMind, Hugging Face, NVIDIA… | global tech press and first-hand lab announcements | No |
| **India RSS:** Economic Times Tech, The Hindu, BusinessLine, Indian Express, Inc42, YourStory, Entrackr, MediaNama, Analytics India Mag | Indian AI industry, startups, policy | No |
| **Tamil Nadu:** The Hindu Tamil Nadu, Times of India Chennai, Google News searches (Chennai, Coimbatore, IIT Madras, TN AI jobs & policy, Tamil-language AI news) | local developments and opportunities | No |
| **Google News RSS search** | labs without RSS (e.g. Anthropic), AI startups, Indian AI firms (Sarvam AI, Krutrim, IndiaAI…) | No |
| **GDELT** (gdeltproject.org) | worldwide news in ~65 languages, filterable by country | No |
| **Hacker News** (Algolia API) | launches from small AI companies that get developer attention | No |

Sources are listed in `ai_news_agent/sources.py`. Add or remove lines as you like. If one source is down, it's skipped and the rest still run.

The **only key** is the Anthropic API key, which Claude uses to triage, choose and summarise. It isn't free (see cost below). **Without it the agent still works:** duplicates are matched by title similarity, stories are ranked by keyword scores with the same diversity rules, and the summaries are short extracts from each article. The quality is noticeably lower, but you still get a daily email.

## One-time setup (about 10 minutes)

1. **Merge to `main`.** Scheduled workflows only run on the default branch.
2. **Gmail app password:** Google Account → Security → turn on 2-Step Verification → "App passwords" → create one (16 characters).
3. **(Recommended) Anthropic API key:** https://console.anthropic.com → API Keys.
4. **Repository secrets** (Settings → Secrets and variables → Actions → *Secrets*):

   | Secret | Value |
   |---|---|
   | `SMTP_USER` | the Gmail address that sends the email |
   | `SMTP_PASSWORD` | the 16-character app password |
   | `EMAIL_TO` | where to deliver it (comma-separate several) |
   | `ANTHROPIC_API_KEY` | optional, see above |

5. **Website:** Settings → Pages → Deploy from a branch → `main` / `/docs`. Then add the *variable* `SITE_URL` = `https://<username>.github.io/<repo>/`. (Pages on a private repo needs a paid GitHub plan.)
6. **Test:** Actions → "Scan AI news" → Run workflow. Then "Fetch AI news (4 AM)" → Run. Then "Email AI news (8 AM)" → Run.

## Cost (Anthropic API, estimate)

About 6 short triage calls a day plus one curation call and one summary call. That comes to roughly **$0.50–1.00 per day** with the default model (Claude Opus 5.5). To cut it, set the variable `TRIAGE_MODEL` = `claude-haiku-5-5`, which makes the frequent scan calls very cheap while keeping Opus for the final choice and summaries. The real cost depends on how much news there is, so check the Anthropic console after the first few days.

## Settings (repository *variables*, all optional)

| Variable | Default | Meaning |
|---|---|---|
| `MAX_STORIES` / `MIN_STORIES` | `20` / `15` | digest size |
| `MAX_PER_COMPANY` | `2` | most stories about one company |
| `INDIA_SHARE` | `0.3` | target share of India stories |
| `MIN_TAMIL_NADU` | `2` | Tamil Nadu stories to include when worthwhile ones exist |
| `TRIAGE_MODEL` | `claude-opus-5-5` | model for the 4-hourly scans |
| `CLAUDE_MODEL` | `claude-opus-5-5` | model for the final choice and summaries |
| `DIGEST_TIMEZONE` | `Asia/Kolkata` | your time zone |
| `SITE_URL` | – | website link shown in the email |
| `SMTP_HOST` / `SMTP_PORT` | `smtp.gmail.com` / `465` | other mail providers |

**Time zone:** the schedules are in IST. If you change `DIGEST_TIMEZONE`, also change the `cron:` lines in `.github/workflows/`. Cron uses UTC.

## Run locally

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=...            # optional
python -m ai_news_agent scan            # run a few times during the day
python -m ai_news_agent fetch --force   # build today's digest + website (open docs/index.html)
SMTP_USER=you@gmail.com SMTP_PASSWORD=app-password python -m ai_news_agent email
```

State lives in `data/`: `pool.json` (stories gathered since the last digest) and one `digest-DATE.json` per day.
