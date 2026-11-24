# From script to daily Short: the AI-video pipeline

One episode = one `episode.json`. Everything else (prompt sheet, generations, edit, upload) is derived from it.

```
your one-liner ─▶ Claude: script + shot list ─▶ episode.json ─▶ build_prompts.py ─▶ PROMPTS.md / prompts.jsonl
                                                                                         │
             ┌───────────────────────────────────────────────────────────────────────────┘
             ▼
   references (once per series) ─▶ start frames (cheap, iterate) ─▶ ✅ you approve ─▶ image-to-video clips
                                                                                         │
             ┌───────────────────────────────────────────────────────────────────────────┘
             ▼
   assemble: clips + captions + voice + music + end card (Remotion, this repo) ─▶ ✅ you approve ─▶ YouTube (scheduled)
```

The two ✅ gates are deliberate. Images cost far less than video, so you only animate frames you like. And a
human final check keeps the channel clear of YouTube's "mass-produced / repetitive content" problems.

## Folder layout

```
ai-video/
  build_prompts.py          expands an episode.json into a prompt sheet
  ep001/
    episode.json            the source of truth (story, anchors, shots, captions, sound)
    PROMPTS.md              copy-paste sheet for manual generation
    prompts.jsonl           one prompt per line, for automated generation
    refs/                   REF_HERO.png, REF_KID.png, REF_BIKE.png, REF_LOCATION.png
    frames/                 S01.png ... approved start frames
    clips/                  S01.mp4 ... generated clips
    audio/                  kid-line.wav, music.mp3, ambience.mp3
```

## The trial: one episode, by hand

1. Generate the 4 references and save the best of each in `refs/`.
2. Generate start frames for the 8 key shots (S03, S05, S07, S10, S11, S12, S14, S17) and save them in `frames/`.
3. Animate those 8 into 5-second clips and save them in `clips/`.
4. Judge them together. Does the man look like the same man in S03, S12 and S17? Does the kid hold up in S11? If yes,
   generate the other 10 shots. If not, fix the references first. Everything downstream inherits them.
5. Record or synthesize the kid's line and pick the music.
6. Assemble and review.

## Which tool, and what it costs

- **Higgsfield through Claude (the automatable route).** Official MCP server: `https://mcp.higgsfield.ai/mcp`.
  - In the Claude app or claude.ai, add it as a custom connector at claude.ai/customize/connectors, then start a
    new session.
  - In Claude Code on your laptop: `claude mcp add --transport http higgsfield https://mcp.higgsfield.ai/mcp`.
    A connector added on your laptop does not carry over to cloud sessions.
  - **There are no free credits here.** Generations through the MCP are billed against your Higgsfield credits at
    standard rates. The free plan currently has no daily allowance, and its consistent-character feature
    (Soul ID) needs a paid plan.
  - Avoid the unofficial "unlimited" Higgsfield MCP projects on GitHub. They drive your browser login in ways the
    service may not allow, which puts your account at risk.
- **Free daily credits (manual, good for the trial).**
  - Kling's free tier is widely reported at about 66 credits a day: roughly 5–6 standard 5-second clips,
    watermarked, personal use.
  - Google Flow (Veo) reportedly gives a small daily allowance.
  - Free tiers are usually watermarked and/or non-commercial. That's fine for testing, but **check the terms
    before publishing on a monetized channel**.
- **Rule of thumb for budgeting:** cost per episode ≈ (number of clips you keep × average retries) × credits per
  clip. 18 shots × ~2 attempts ≈ 36 clip generations per video. On free daily allowances that is about a week per
  video. Daily publishing needs a paid plan.

## Automating it later (once the trial looks right)

1. **Story intake.** A theme bank plus your one-liners. Claude writes the script and `episode.json` in this exact
   format. The anchors (characters, style, place) are reused across episodes for a recurring cast.
2. **Generation.** A Claude Code session with the Higgsfield connector reads `prompts.jsonl` and generates the
   frames. It stops at the frame gate for your approval, then generates the clips into `clips/`.
3. **Assembly.** A Remotion composition in this repo reads `episode.json` and `clips/`, then lays in captions, the
   voice line, music, ambience and the end card, and renders a 9:16 MP4.
4. **Publishing.** Upload through the YouTube Data API as a scheduled video. For realistic-looking AI scenes,
   tick YouTube's "altered or synthetic content" disclosure.
5. **Schedule.** A daily scheduled task runs steps 1–3 overnight. You review in the morning and publish.

## Production tips for AI video

- **One action per shot.** Models handle "he brushes his trousers and looks up" well, and a crash or a two-person
  lift badly. That's why the fall is shown as its cause (S04) and its aftermath (S05), never the crash itself.
- **Keep the anchor text identical.** Never paraphrase a character between shots. Change the anchor once in
  `episode.json` and rebuild.
- **Hands and faces:** use close-ups with the reference images attached, and expect retries on S10.
- **No text in generations.** Models garble letters. All captions are added in the edit.
- **Generate a little long, cut tight.** Use 5-second clips and keep the best 3–4 seconds of each.
