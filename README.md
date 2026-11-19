# The Morning Brief: your private AI news app

A calm, personal answer to AI information overload. It covers what matters in AI around the world, plus India, with a close eye on **Bengaluru, Chennai and Hyderabad**, where new opportunities are most likely to appear. Every night at **4 AM IST** an agent reads ~50 sources so you don't have to. When you open the app, a short brief is waiting, and it ends with **"You're caught up."**

- **Your brief:** the 5 Must-know stories plus up to 4 **picked for you** from what you follow, usually 2–4 minutes of reading. Everything else is folded under "Everything else today", grouped by world and by city. Stories you've read fade.
- **Your focus:** follow topics, companies or technologies (e.g. *AI Agents*, *Sarvam AI*), mute what you don't care about (e.g. *Robotics*), follow a storyline, and choose your cities. Use **⚙ Tune** on any story, or the *Your focus* screen. The app ranks by it immediately, and the next morning's editor is told about it.
- **India tab:** a 7-day or 30-day **city pulse** for Bengaluru, Chennai, Hyderabad and the rest of India. It shows how many AI stories each city had, whether it's getting busier or quieter, which kinds of news (agents, policy, data centres, jobs…), and the storylines running there. Below it, every India story for the chosen city.
- **Must know:** the 5 most important stories, each with a headline, a 60–100 word essence and a link to the full article.
- **Quick hits:** the other 10–15 stories as one-liners. Tap one to see the full essence.
- **For you · opportunities:** jobs, free courses, schemes, grants and tools you could act on, Tamil Nadu and India first.
- **Storylines:** when a story continues ("NVIDIA launches a GPU" → "clouds order it" → "benchmarks disappoint"), each update shows *the story so far*: earlier days' reports with their links and what people said at each step.
- **What people said:** genuine comments from Reddit and Hacker News on the previous day's stories, collected a day late so people have had time to actually try things. Every quote is copied word for word, and code checks it against the original comment, so nothing can be invented.
- **This week:** a Sunday recap of the week's big themes and the stories that mattered.
- **Search** across every edition, an **archive**, **👍 / 👎 / ✨ More like this** buttons that teach the editor your taste, and a **status light** that tells you when something needs attention (for example, your Claude token is about to expire).

**Cost: ₹0 extra.** It runs on free GitHub Actions and free news sources. The one AI step uses the **Claude Pro subscription you already have**.

## How it works

```
4:00 AM IST · GitHub Actions (daily-digest.yml)
  1. Gather    (code, free)   ~45 free sources: RSS, Google News, GDELT, Hacker News
  2. Shortlist (code, free)   merge duplicate reports, drop junk, score → ~70 candidates
  3. Reviews   (code, free)   real Reddit / Hacker News comments on the last 2 days' stories
  4. Edit      ONE Claude Code session on your Pro plan:
                 picks 15–20 stories by your rules · writes headlines, essences and one-liners
                 links each story to earlier ones (storylines) · picks opportunities
                 chooses genuine reviews · writes the Sunday recap
                 runs `python -m ai_news_agent check` until every rule passes
  5. Save      code re-checks everything → data/digests/<date>.json → pushed to your repo

Whenever you like · on your laptop
  python -m ai_news_agent app   → pulls the latest editions, opens the app in your browser
```

**Your rules, checked by code and not just requested:** at most 2 stories per company; big labs *and* small firms; a spread of technologies; about 30% India, including the day's best story from each of your cities (Bengaluru, Chennai, Hyderabad) when there is one worth reading; at least 2 global stories in Must know; no repeats unless something new happened. What you follow is preferred and what you mute is left out, within those rules.

**If something fails, you still get an edition:** Claude Code (Pro) → Gemini free tier (optional) → plain article extracts. The app's status light tells you which one ran.

## Setup (about 15 minutes, once)

### 1. GitHub (the overnight part)
1. Keep the repository **private**. One run a day uses about 10 minutes, well inside GitHub's 2,000 free minutes a month.
2. Merge this branch into `main`. Scheduled runs only start from `main`.
3. Install Claude Code on your computer (`npm install -g @anthropic-ai/claude-code`) and run `claude setup-token`. Log in with your Pro account and copy the token it prints.
4. Repository → Settings → Secrets and variables → Actions:

   | Kind | Name | Value |
   |---|---|---|
   | Secret | `CLAUDE_CODE_OAUTH_TOKEN` | the token from step 3 |
   | Variable | `CLAUDE_TOKEN_CREATED` | today's date, e.g. `2026-11-20` (for the expiry reminder) |
   | Secret *(recommended)* | `REDDIT_CLIENT_ID` / `REDDIT_CLIENT_SECRET` | from a free Reddit app: reddit.com/prefs/apps → "create another app" → type **script**, redirect `http://localhost` |
   | Secret *(optional)* | `GEMINI_API_KEY` | free backup key from aistudio.google.com |

5. Actions → "Daily AI brief" → **Run workflow** to make your first edition now.

### 2. Your laptop (the reading part)
```bash
git clone <your repo URL> morning-brief
cd morning-brief
python3 -m ai_news_agent app        # opens http://127.0.0.1:8765
```
Or double-click **`start-app.sh`** (Mac/Linux) or **`start-app.bat`** (Windows). The app needs only Python 3.10+ with nothing to install, because it uses Python's standard library. It's reachable only from your own computer. Your 👍/👎 are pushed back to GitHub automatically so tomorrow's editor sees them.

## Where the user reviews come from
| Platform | Works? | Notes |
|---|---|---|
| Hacker News | ✅ free, no key | developers trying new tools, often hands-on |
| Reddit | ✅ free | reliable with the free app key above; without it Reddit often blocks cloud servers |
| Discord | ❌ | conversations sit in login-only servers, and reading them automatically breaks Discord's rules |
| X / Twitter | ❌ | its API is paid |

## Changing things

- **Tone, priorities, what counts as an opportunity:** edit `ai_news_agent/prompts/editor.md`. It's plain English.
- **News sources:** `ai_news_agent/sources.py`.
- **Numbers** (GitHub repository *variables*, all optional):

| Variable | Default | Meaning |
|---|---|---|
| `MAX_STORIES` / `MIN_STORIES` | `20` / `15` | edition size |
| `MUST_KNOW` | `5` | full-size stories at the top |
| `MAX_PER_COMPANY` | `2` | most stories about one company |
| `INDIA_SHARE` | `0.3` | target share of India stories |
| `MIN_TAMIL_NADU` | `2` | Tamil Nadu stories when worthwhile ones exist |
| `MAX_WEB_SEARCHES` | `5` | extra searches the editor may do for missed stories |
| `CLAUDE_CODE_MODEL` | plan default | e.g. `opus` or `sonnet` |
| `DIGEST_TIMEZONE` | `Asia/Kolkata` | also change the `cron:` line, which is in UTC |

## Files

```
ai_news_agent/
  sources.py      free news sources            collect.py    fetch feeds, GDELT, HN
  shortlist.py    merge duplicates, score      reactions.py  Reddit / HN comments + quote check
  editor.py       the AI step, rules, repair   prompts/editor.md  the editor's instructions
  threads.py      storylines                   prefs.py      your 👍/👎 → a note for the editor
  store.py        reading/writing data/        app/          the local app (server + page)
data/digests/     one edition per day          data/feedback.json  your votes
data/interests.json  what you follow / mute, your storylines and cities (set in the app)
tests/            checks for the safety rules (python -m pytest)
```

## Run things by hand
```bash
pip install -r requirements.txt
USE_LOCAL_CLAUDE=1 python -m ai_news_agent daily --force   # build today's edition with your local Claude login
python -m ai_news_agent app --no-sync                     # open the app without git pull/push
python -m pytest -q                                       # run the tests
```
