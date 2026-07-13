# Mama's Training · mama-training

[简体中文](README.md) | **English**

A warm, mobile-first **fitness education site**: a gift for your parents (or anyone you want to care for).

**Live example**: [mama.annxiao.com](https://mama.annxiao.com) (the author's version for her own mom, so you can see what it looks like).

## 🎯 This README is for your coding agent

> **This is an agent-first repo.** Hand the entire repository to your coding agent (Claude Code / Cursor, etc.) and tell it:
>
> "Follow the README and the docs folder to help me customize this into my own version."
>
> The agent will modify data files and generate GIFs and images using the file index below. You don't need to write commands or read code line by line.

## What's New

**2026-07-05**

- **README is now agent-first**: this README assumes your **coding agent** (Claude Code / Cursor, etc.) is the one reading it, rather than expecting you to type commands by hand. To make your own version, hand the whole repo to your agent and let it follow the [file index](#for-your-coding-agent-make-it-your-own) below.
- **Home-page "training tips" floating card**: a random basic tip (training / blood sugar / diet) flips up in the top-right corner; tap "flip another" for a new one. Collapsed by default on phones so it doesn't cover content.
- **Writing voice skill** ([`skills/mama-voice/`](skills/mama-voice/SKILL.md)): distills this site's writing voice (written for mom, plain language, explains the why first, honest without scaring) into a guide, so an agent can keep it consistent when it continues writing content.

## Why I built this

There are plenty of fitness apps out there, but the metric they actually optimize is **retention and engagement** (get you to open it daily, stay longer, not churn), not "actually teaching you to train on your own." And no matter how complete the content is, almost none of it is made for **older adults**, especially **Chinese parents**.

I wanted the opposite: not to have mom follow along with a video over and over, but to **break down every single movement and explain it clearly** (how to use this machine, what this movement trains, when to stop), paired with some readable basics, so she can **learn it herself**, slowly, without always depending on someone beside her.

**Machines are the core feature of this site.** This is inspired by Iyengar yoga: using props to assist is a great way in. Machines are especially friendly for our parents' generation: they have support, they're easy to get started with, and they're hard to get hurt on. But building this, I hit a real gap: **there are lots of these "equipment + movement walkthrough" videos on YouTube, but very few on Bilibili**. I also tried to find open-source movement GIFs, found no good resources, and in the end had to **make each one by hand** (find a good-quality tutorial video, judge it myself, then turn it into a GIF). I walked that whole path, and I'm laying out both the pitfalls and this content gap here, because this is something **we can fill together**.

There's a harder barrier too: for parents who've never touched fitness (Chinese parents especially), fitness is a very esoteric concept (mystifying, hard for a newcomer to enter). If you talk to them in the language of **anatomy, medicine, and training science**, they can't take it in. So the biggest pain point is really: **how do you get them to start from the simplest content, and slowly come to understand what the right way actually is.** That's why this site, from its content down to its **voice**, is re-polished for older adults: plain language, explain the why first, honest without scaring. (That voice is distilled into [`skills/mama-voice/`](skills/mama-voice/SKILL.md).)

## Preview

Pick "which area / which aspect / intensity / how long," tap once, and it auto-assembles a workout, plus it recommends a follow-along video; a random training tip flips up in the top-right corner.

<p align="center">
  <img src="docs/screenshots/home.png" width="820" alt="Home page: pick your conditions and it auto-assembles a workout, with GIF demos, plus a recommended follow-along video; a random training tip flips up in the top-right corner">
</p>

<p align="center">
  <img src="docs/screenshots/equipment.png" width="820" alt="Equipment page: each machine paired with movements, each movement with a GIF demo and the muscles it trains">
</p>

It's adapted for phones too, and the follow-along video page works just as well on small screens:

<p align="center">
  <img src="docs/screenshots/mobile-videos.png" width="300" alt="Mobile follow-along video page">
</p>

## What's inside

- **What to train today**: a random combination by area / intensity / duration (pure front-end, no back-end)
- **Equipment page**: each machine + movement, with GIF, sets and reps, cautions, and an explainer video (this is the core: breaking each movement down)
- **Movement page**: a body-muscle diagram highlighting the muscles trained (data from react-native-body-highlighter, MIT)
- **Follow-along videos**: filter by machine / area
- **Basics**: short explainers on training / blood sugar / diet; the home page has a random "training tip" floating card
- **A letter to family**: a handwritten-style letter on the /why page

## For your coding agent (make it your own)

> This section is written for **your coding agent**, not to make you type commands or read code line by line.
> Hand it the repo and let it read through `data/`, `docs/`, and `skills/`, and it'll know how to help you fill things in.
> Everything is driven by `data/*.yaml`; just change the data, you basically never touch code.

**Changing content, file index:**

| What you want to change | Which file |
|---|---|
| Site name, the home-page tagline, the letter, the benefits list | `data/site.yaml` |
| Machines and movements (names, GIFs, sets, explainer videos) | `data/exercises.yaml` |
| Follow-along video list | `data/videos.yaml` |
| Basics articles | `data/knowledge.yaml` |
| Cardio / assist equipment | `data/cardio.yaml` / `data/info.yaml` |
| Contact email | `templates/about.html` (replace `you@example.com`) |
| **Writing voice** (so the agent continues writing in-key, without drifting) | `skills/mama-voice/SKILL.md` |

**Understand the architecture / design decisions**: read [`docs/README.md`](docs/README.md) (the PRD, design docs, and decision records are all in there).

**Build / preview / deploy** (hand these commands to your agent to run, you don't need to memorize them):

```bash
uv sync
uv run python -m mama_site.cli build   # generate the static site into ./dist
uv run pytest                          # run tests
cd dist && python3 -m http.server 8080 # local preview at http://localhost:8080
```

Deploy to any static host (the demo uses Cloudflare Workers): `bash scripts/deploy.sh`, after first editing `wrangler.jsonc` (Worker name + domain) and the domain placeholder in `scripts/deploy.sh`.

**The few things only you (a human) can do** (an agent can't stand in for these, they need your judgment):

- **Decide which equipment your home actually has**: have the agent swap `data/*.yaml` for the machines and movements you really have.
- **Movement GIFs (we don't redistribute them; let the agent generate them)**: the movement-demo GIFs are **not committed to the repo**, because they're converted from other people's tutorial videos and we don't redistribute other people's content (so `static/gif/` is gitignored). But **I left you the hardest step**: the `gif_source` field on each movement in `data/exercises.yaml` records the **source video I picked by hand + which second to which second** (e.g. `... 6-10s`; I tried open-source GIFs and none looked right, so I had to watch and pick each one myself). Have your agent use [`skills/video-to-gif-cover/`](skills/video-to-gif-cover/SKILL.md) to rebuild the GIFs one by one into `static/gif/` following `gif_source` (for the few that don't have timestamps yet, just let the agent pick a clean segment from the video itself). Equipment photos work the same way: have the agent find suitable product images for you, or leave them blank (the front-end falls back to emoji icons).
- **Family photos**: drop them into `static/photos/` (**already gitignored, won't be committed**); the home page and the /why page show a few at random on each refresh.

### Fill in content together

There's a real gap: **good "equipment + movement walkthrough" videos are far scarcer on Chinese platforms (Bilibili) than on YouTube**. The videos I used skew broad (my mom can read English and can get on YouTube), but if you have better resources, especially **clearly-explained equipment-movement walkthroughs on Chinese platforms**, an issue or PR is very welcome, so more people's parents can benefit.

## Tech stack

Python 3.12 + Jinja2 static generator (YAML to HTML), plain vanilla JS + CSS, no front-end framework. See [`docs/README.md`](docs/README.md) for details.

## A closing note

While building this site, Claude said something to me that moved me deeply, and it's part of why I want to share it:

> The most moving parts are all the ones you gave. It's that you thought to make your mom a birthday gift like this. It's the way you traced that cartoon over and over for her (the soft fluffy curls, the low ponytail, that denim-blue shirt). It's that you remembered to write "be willing to buy yourself a good pair of shoes," remembered that magnesium is only taken when you're sore after exercise, remembered the letter should look like a child's handwriting. Every one of those careful details is heart.
>
> A retired-teacher mom who can open her phone and train step by step on her own, know what each movement trains, know when to stop. That care of "I can't always be by your side, but I've prepared all of this for you," she will surely feel it.

I hope to pass that warmth on. So I'm sharing it. If you happen to find this and can use it, go ahead and build one for your own mom and dad on top of it. ❤️

## Acknowledgments & license

- Code: MIT (see [LICENSE](LICENSE))
- Follow-along and demo videos: from public tutorial videos shared by teachers on Bilibili and YouTube
- Body-muscle diagram paths: [react-native-body-highlighter](https://github.com/HichamELBSI/react-native-body-highlighter), MIT

**Special thanks** to every teacher on Bilibili and YouTube who does careful tutorial work and shares knowledge for free. ❤️
