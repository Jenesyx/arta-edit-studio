---
name: reel-setup
description: Use when the user runs /reel-setup, has just cloned Arta Edit Studio, or a reel command fails because Python packages, Node packages, ffmpeg, fonts or reel.config.json are missing.
argument-hint: (optional) your name, Instagram handle, brand
---

# Arta Edit Studio — setup

Get a fresh clone ready for `/reel-story` and `/reel-split`, then personalise it.
Explain each step in one plain sentence before running it — many users are not
developers. **Ask before anything that downloads or installs** (packages, fonts,
model weights) and say roughly how big it is.

Arguments: `$ARGUMENTS`

## 1. Check the machine — report as a ✅ / ❌ table

| Need | Check | Fix if missing |
| --- | --- | --- |
| Python ≥ 3.10 | `python --version` | python.org |
| Node ≥ 18 | `node --version` | nodejs.org (LTS) |
| ffmpeg **with zscale** | `ffmpeg -hide_banner -filters` contains `zscale` | Windows: gyan.dev "full" build · macOS: `brew install ffmpeg` |
| NVIDIA GPU (optional) | `nvidia-smi` | none → Whisper runs on CPU, ~10× slower |
| Chrome for rendering | `npx hyperframes doctor` (after step 2) | doctor says what to do |

## 2. Install (ask first)

1. `python -m venv .venv`
2. PyTorch — the command from pytorch.org for this OS; with an NVIDIA GPU pick the CUDA build (~2.5 GB), else CPU.
3. `.venv/Scripts/python -m pip install -r requirements.txt` (macOS/Linux: `.venv/bin/python`).
4. `npm install` (HyperFrames renderer, GSAP, Lucide icons).
5. `npx hyperframes doctor` — fix what it flags.
6. Tell the user: the Whisper `large-v3` model (~3 GB) downloads on the first transcription.

## 3. Fonts

Read `fonts` in the config. For each file missing from `font/`, tell the user where
the free default comes from and offer to download it (ask first):
- Farsi `Vazirmatn-Medium.ttf` — github.com/rastikerdar/vazirmatn (releases), OFL
- Latin `Poppins-SemiBold.ttf` and display `Poppins-Black.ttf` — fonts.google.com/specimen/Poppins, OFL

Any other font works: put the file in `font/` and change the path in the config.

## 4. Personal config

If `reel.config.json` does not exist, copy `reel.config.example.json` to it, then ask
in one message (skip what the arguments already answered):
- name and Instagram handle (for the follow card)
- spoken language of the videos (`fa`, `en`, `ar`, `de`, …)
- brand / product name (optional) and its colours — or a logo file to pick colours from
- mascot / character images (optional) → put them in `assets/mascot/`; a logo → `assets/brand/logo.png`
- where their B-roll clips are (default `assets/broll/`)

Write the answers into `reel.config.json` (keep every key the example has).

## 5. Mood board

Explain (in the user's language) that every edit starts from **their** mood board, so the
result looks like them and not like generic AI: `moodboard/default/` for their general
style, `moodboard/<video-name>/` per video. 5–15 screenshots of Reels they love, 1–3
short screen recordings of motion they like, their brand, and a `notes.md` with mood
words + likes + dislikes (docs/moodboard.md). Offer to look at it with them once it's filled.

## 6. Smoke test

- `.venv/Scripts/python -X utf8 -c "import sys; sys.path.insert(0,'tools'); import config, story_build, showcase_build; print('tools ok')"`
- If a video is already in `raw/`: `$PY tools/face_track.py <take>` should print a face position.

## 7. Hand-off

Print a short "how to use" with one example each, in the user's language:
`/reel-story <take> <topic, comment keyword, names>` and `/reel-split <take> …`.
