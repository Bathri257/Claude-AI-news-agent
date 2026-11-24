#!/usr/bin/env python3
"""Expand an episode.json into a copy-paste prompt sheet (PROMPTS.md) and a flat prompts.jsonl.

Every prompt is built from the same anchor text ({HERO}, {KID}, {STYLE}, ...), so characters are described
identically in every shot. That consistency is what keeps AI video tools from drifting between clips.

Usage:  python3 build_prompts.py ep001/episode.json [--live-action]
"""
import json
import re
import sys
from pathlib import Path


def expand(text: str, anchors: dict) -> str:
    for _ in range(3):  # anchors may reference other anchors
        text = re.sub(r"\{([A-Z_]+)\}", lambda m: anchors.get(m.group(1), m.group(0)), text)
    return re.sub(r"\s+", " ", text).strip()


def main() -> None:
    src = Path(sys.argv[1])
    ep = json.loads(src.read_text(encoding="utf-8"))
    anchors = dict(ep["anchors"])
    if "--live-action" in sys.argv:
        anchors["STYLE"] = anchors["STYLE_LIVE_ACTION"]
    neg = anchors["NEGATIVE"]
    out = src.parent
    total = sum(s["duration_s"] for s in ep["shots"])
    key = [s["id"] for s in ep["shots"] if s.get("key")]

    md = [f"# {ep['title']} ({ep['id']}): AI video prompt sheet", ""]
    md += [f"**Logline:** {ep['logline']}", "", f"**Takeaway:** {ep['takeaway']}", ""]
    md += [f"{len(ep['shots'])} shots, {total} s of raw footage, edited down to about {ep['target_length_s']} s. Aspect ratio {ep['aspect_ratio']}.", ""]
    md += ["## How to use this sheet", ""]
    md += [
        "1. **Make the references once (Step 1).** Generate each reference image, regenerate until you love it, and save the best one. "
        "Reuse these files for every shot. They are your cast and set.",
        "2. **Make a start frame for each shot (Step 2a).** Use a text-to-image model and attach the listed reference images "
        "(\"reference\" / \"character\" / \"elements\" input). Iterate here: images are far cheaper than video.",
        "3. **Animate only approved frames (Step 2b).** Use image-to-video with the start frame plus the motion prompt, and generate 5 s clips (10 s only where noted). "
        "Paste the negative prompt where the tool has one.",
        "4. **Leave text, voice and music out of the generation.** Captions, the kid's line and the music are added in the edit, so they stay sharp and consistent.",
        "5. **Name clips by shot id** (`S01.mp4`, `S02.mp4`, ...) in `clips/`, so the assembly step can find them.",
        "",
        f"**Trial run (proof of concept):** generate only the key shots first: {', '.join(key)}. "
        "If those eight look right together, generate the rest.",
        "",
        "**Negative prompt (all shots):**",
        "```",
        neg,
        "```",
        "",
        "## Step 1: reference images (generate once, reuse for every shot)",
        "",
    ]
    jsonl = []
    for r in ep["references"]:
        p = expand(r["prompt"], anchors)
        ar = r.get("aspect_ratio", "16:9")
        md += [f"### {r['id']} · aspect {ar}", "```", p, "```", ""]
        jsonl.append({"id": r["id"], "kind": "reference", "image_prompt": p, "negative": neg, "aspect_ratio": ar})

    md += ["## Step 2: shots", ""]
    t = 0
    for s in ep["shots"]:
        sp = expand(s["start_frame"], anchors)
        mp = expand(s["motion"], anchors)
        tag = " ★ key shot" if s.get("key") else ""
        md += [f"### {s['id']} · {s['duration_s']} s · {s['camera']}{tag}", "", f"*{s['purpose']}*  ", f"Timeline {t}–{t + s['duration_s']} s · attach: {', '.join(s['refs']) or 'nothing'}", ""]
        md += ["**2a · Start frame (text-to-image, 9:16):**", "```", sp, "```"]
        md += ["**2b · Motion (image-to-video):**", "```", mp, "```"]
        if s.get("caption"):
            sub = f"  ({s['caption_sub']})" if s.get("caption_sub") else ""
            md += [f"**Caption in edit:** {s['caption']}{sub}  "]
        if s.get("voice"):
            md += [f"**Voice in edit:** {s['voice']}  "]
        md += [f"**Sound:** {s['sfx']}", ""]
        jsonl.append({"id": s["id"], "kind": "shot", "duration_s": s["duration_s"], "key": bool(s.get("key")), "refs": s["refs"],
                      "image_prompt": sp, "video_prompt": mp, "negative": neg, "aspect_ratio": "9:16", "caption": s.get("caption", ""),
                      "caption_sub": s.get("caption_sub", ""), "caption_style": s.get("caption_style", "plain")})
        t += s["duration_s"]

    md += ["## Sound plan", ""] + [f"- **{k.capitalize()}:** {v}" for k, v in ep["audio"].items()] + [""]
    (out / "PROMPTS.md").write_text("\n".join(md), encoding="utf-8")
    (out / "prompts.jsonl").write_text("\n".join(json.dumps(j, ensure_ascii=False) for j in jsonl) + "\n", encoding="utf-8")
    print(f"wrote {out / 'PROMPTS.md'} and {out / 'prompts.jsonl'} ({len(jsonl)} prompts)")


if __name__ == "__main__":
    main()
