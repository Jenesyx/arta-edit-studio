---
name: reel-split
description: Use when the user runs /reel-split, or asks for the split-screen explainer Reel — an animated widget panel on the top ~45 % of the frame, the speaker below it the whole time, no subtitles, no SFX — typical for "I found this tool / here are 5 tips" videos, on a talking-head take in raw/.
argument-hint: <take name in raw/> <what the video is about, comment keyword, names>
---

# Reel — Split edit (45 % panel over speaker)

A permanent cream panel fills the top of the frame (1080 × `split.panel_height`,
default 864 = 45 %) with UI-style widgets — cards, meters, toggles, terminals,
chips — that illustrate exactly what is being said. The speaker sits below at
scale 1 and **never moves**. Ending: the comment keyword big on screen, then a
follow card. Worked example: `examples/split/` (plan + scene module of a real
100 s video about five Claude skills).

Arguments: `$ARGUMENTS`

## Defaults (change only if the user says so)

Read `reel.config.json` first (falls back to `reel.config.example.json`).

| Thing | Default |
| --- | --- |
| Split | `"split": split.panel_height` (864 → panel 45 %, speaker 55 %; 960 = 50/50) |
| Speaker | scale 1, no zoom, no movement; face centred in the speaker region (`speaker_y`) |
| Safe box | `"safe": split.safe` = `[64, 200, 64, 32]` → scene content lives in 952 × 632 starting 200 px down, below Instagram's header zone (docs/safe-zones.md) |
| Taste | **The creator's mood board decides the look** — no approved `style.md`, no build |
| Motion | Eased, curved, motion-blurred, overlapping — docs/motion.md, helpers in `tools/motion.js` |
| Subtitles / SFX / music | **None** added. Audio = the take's own mix, remuxed by `finish.py` |
| Take | Assume already cut, graded, music added → use as-is. Raw/uncut → ask first |
| CTA | Comment keyword (word or number) huge in a speech-bubble card; follow card `"handle": creator.handle`, text only, never a face crop |
| Palette | `split_palette`: cream panel, ink text, accent fills; text on cream uses `accent_deep` (contrast) |

## Inputs

Take name + topic come from the arguments. Ask once, in one message, only what's
missing: is the take already cut/graded/with music; the comment keyword; names or
jargon Whisper may mishear (tool and product names).

## Pipeline

`PY` = `.venv/Scripts/python.exe -X utf8` (Windows) or `.venv/bin/python -X utf8` (macOS/Linux). Long steps in background.

| # | Step | Command / action | Check |
| --- | --- | --- | --- |
| 1 | Look | ffprobe; contact sheet `ffmpeg -i raw/<take> -vf fps=1/5,scale=216:384,tile=9x2 -frames:v 1 work/<take>/sheet.jpg` and look at it | empty wall above head? already edited? |
| 2 | Transcribe | `$PY tools/transcribe.py <take> --prompt "<names, jargon>"` | proofread tool names; gaps > 3 s → re-transcribe window |
| 3 | Face | `$PY tools/face_track.py <take> --split <panel_height>` | prints `speaker_y` |
| 3a | **Mood board** | `$PY tools/moodboard.py <take>`. Exit 2 = none exists → **stop and ask the creator to make one** ([docs/moodboard.md](../../../docs/moodboard.md), explained in their language). Look at every `board_N.jpg`, read `summary.md` | |
| 3b | **Style brief** | write `work/<take>/style.md` from [docs/style-brief.md](../../../docs/style-brief.md); **show it to the creator and wait for OK** | builders refuse without it |
| 4 | Beat plan | one scene per idea, typically 3–7 s, each widget pinned to a spoken word (cue = word start). Scenes change content, never layout | |
| 5 | Plan file | `work/<take>/showcase.json` from `examples/split/showcase.json`: `video` (`"../../raw/<file>"`), `split`, `speaker_y`, `safe`, `scenes_module`, `scenes[] {kind, start, end, cue{...}}`, `handle` on the follow scene; `_note` records the face numbers | |
| 6 | Scenes | `tools/scenes_<slug>.py` from `examples/split/scenes_5skills.py`: one `sc_<kind>(i, s) -> (html, js)` per kind, `RENDER` dict, optional `CSS`/`JS`. Coordinates inside the safe box (952 wide); ids `s{i}-*`; cue times absolute. `sc_comment`, `sc_follow` are the CTA | |
| 7 | Build | `$PY tools/showcase_build.py <take> --guides`; in `work/<take>/sc`: `npx hyperframes lint public` → 0 errors; `npx hyperframes snapshot public -o ../snaps --no-end --describe false --at <mid of every scene>`; read sheets (Instagram zones drawn in), fix | text inside the panel, nothing under the header |
| 7a | Checks | rebuild **without** `--guides`; `$PY tools/safezone.py check <take>` → 0 errors; `$PY tools/motion_check.py <take>` | `finish.py` blocks on safe-zone errors |
| 8 | Quick render | `$PY tools/finish.py <take> --seconds 12`; read `quick_sheet.jpg` + `quick_sheet_guides.jpg`, watch `quick.mp4` | moves smooth |
| 9 | Full render | `$PY tools/finish.py <take>` (background) → `final/<take>/`, verify, `qa/sheet.jpg` | read the sheet |
| 10 | Report | path, length, scenes, verify result. If something new was learned, add it to this skill | |

## Panel rules

- Widgets illustrate the sentence being spoken *right now*: a repo card when they name the repo, a meter when they compare, a strike-through when they say "not this".
- Each scene fades out 0.25 s before the next (the builder does it); inside a scene, elements arrive on their cue words.
- Motion: `inUp` / `pop` use the house eases; widgets crossing the panel use `arcIn` / `arcOut` (curve + motion blur); numbers and titles can `settle`; never `ease:"none"` on a move.
- Look follows `style.md` (palette, fonts, graphic language, density) — nothing the mood board doesn't support.
- Numbers on screen must be real counts from the take.
- The scene kinds built into `showcase_build.py` (`hook`, `repo`, `cta`, …) predate the 45 % safe box and can overflow it; write kinds in `tools/scenes_<slug>.py` based on `examples/split/scenes_5skills.py` instead.
- Farsi / Arabic text: `.fa` class (RTL on the element, never `dir="rtl"` on `<html>`), `letter-spacing: 0`, digits via `fa()`, a big zero as Latin `0`.
- No overlapping tweens on one property, no `Math.random` / `from:"random"`, slide-ins carry `autoAlpha:0` in the from-state.
- If any source clip is HDR (HLG), tone-map it first (`TONEMAP` in `tools/story_assets.py`) — `finish.py` stops on "HDR auto-promotion".
- `hyperframes snapshot` is not proof of the render — step 8 is.
