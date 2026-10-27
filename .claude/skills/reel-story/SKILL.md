---
name: reel-story
description: Use when the user runs /reel-story, or asks for the full-frame, motion-heavy Reel edit — speaker full-screen, cut-aways to their own B-roll clips, stickers and widgets popping on spoken words, a mascot, giant words behind the speaker, no subtitles — on a talking-head take in raw/.
argument-hint: <take name in raw/> <what the video is about, comment keyword, names>
---

# Reel — Story edit (full-frame motion)

The speaker stays full-frame. The story is told by cut-aways to the creator's own
clips, stickers/cards/widgets that pop on spoken words, a mascot reacting, and
**depth moments** where giant words or a branded backdrop sit *behind* the speaker
(person matte). Worked example: `examples/story/story_stoodi_inviteraw.py`.

Arguments: `$ARGUMENTS`

## Defaults (change only if the user says so)

Read `reel.config.json` first (falls back to `reel.config.example.json`).

| Thing | Default |
| --- | --- |
| Subtitles | **None.** Key-word graphics are fine; never a running transcript |
| Audio | Take's own mix, untouched — `finish.py` remuxes it. No SFX, no music bed |
| Take | Assume already cut, graded, music added → don't cut or grade. Raw/uncut → ask first |
| B-roll | `broll_dir` from the config; descriptions in `work/_catalog/<folder>/NOTES.md` |
| Brand | `brand` + `palette` from the config. No mascot files → no mascot scenes |
| CTA | Comment keyword huge on screen; follow card = `@<creator.handle>` text only, never a face crop |
| Language | `language` from the config (Whisper + which text class to use) |
| Taste | **The creator's mood board decides the look** — never a default AI style. No approved style brief, no build |
| Safe zones | Nothing to read or see inside Instagram's UI zones (`instagram_safe_zones`, docs/safe-zones.md) |
| Motion | Eased, curved, motion-blurred, overlapping — docs/motion.md, helpers in `tools/motion.js` |

## Inputs

Take name + topic come from the arguments. Ask once, in one message, only what's
missing: is the take already cut/graded/with music; comment keyword; names or
jargon Whisper may mishear; clips they want in or out.

## Pipeline

`PY` = `.venv/Scripts/python.exe -X utf8` (Windows) or `.venv/bin/python -X utf8` (macOS/Linux). Long steps in background.

| # | Step | Command / action | Check |
| --- | --- | --- | --- |
| 1 | Look | ffprobe the take; contact sheet `ffmpeg -i raw/<take> -vf fps=1/5,scale=216:384,tile=9x2 -frames:v 1 work/<take>/sheet.jpg` and look at it | headroom above head, text in frame mirrored?, already graded? |
| 2 | Transcribe | `$PY tools/transcribe.py <take> --prompt "<names, jargon>"` | proofread names; word gaps > 3 s → re-transcribe that window |
| 3 | Face | `$PY tools/face_track.py <take>` | prints `FACE = (x, y)` and head top |
| 3a | **Mood board** | `$PY tools/moodboard.py <take>`. Exit 2 = none exists → **stop and ask the creator to make one** (explain [docs/moodboard.md](../../../docs/moodboard.md) in their language: 5–15 screenshots of Reels they love, 1–3 short clips of motion they like, `notes.md` with mood words, likes, dislikes). Then look at **every** `board_N.jpg`, read `summary.md` | |
| 3b | **Style brief** | write `work/<take>/style.md` from [docs/style-brief.md](../../../docs/style-brief.md) — every line traceable to the board, notes or brand; anti-slop list in Don't. **Show it to the creator and wait for OK** | builders refuse without it |
| 4 | B-roll | `$PY tools/story_assets.py <take> catalog`; read `NOTES.md`; look at the strips of clips not described yet and **add their rows to NOTES.md** | HDR / mirrored / VFR flags |
| 5 | Beat sheet | write `work/<take>/beats.md`: `time \| words \| mode \| what \| board ref`. Rules below, techniques in [references/techniques.md](references/techniques.md), style from `style.md` | every beat pinned to a word |
| 6 | Matte | if any depth moment: `$PY tools/story_assets.py <take> matte` (~8 min CPU for 80 s, background, no parallel ffmpeg) | `work/<take>/matte/fg.webm` |
| 7 | Take module | copy `examples/story/story_stoodi_inviteraw.py` → `tools/story_<slug>.py` (slug: take name, non-alphanumerics → `_`); set `NAME`, `FACE`, `BROLL`, `TILES`, `MIRRORED`, scenes, `SCENES` (`DUR` optional — probed). Mascot names = the files in `assets/mascot` (lower-case, spaces → `-`) | |
| 8 | Assets | `$PY tools/story_assets.py <take> all` (mascot, logo, B-roll trims, tiles) | |
| 9 | Build | `$PY tools/story_build.py <take> --guides`; in `work/<take>/sc`: `npx hyperframes lint public` → 0 errors (`nested_structure` warnings are expected); `npx hyperframes snapshot public -o ../snaps --no-end --describe false --at <every beat>`; read the sheets **with the Instagram zones drawn in**, fix, rebuild | |
| 9a | Checks | rebuild **without** `--guides`; `$PY tools/safezone.py check <take>` → 0 errors; `$PY tools/motion_check.py <take>` → explain or fix every `linear` / `jerky` | `finish.py` blocks on safe-zone errors |
| 10 | Quick render | `$PY tools/finish.py <take> --seconds 12`; read `quick_sheet.jpg` and `quick_sheet_guides.jpg`; watch `quick.mp4` for motion | overlays enter **and leave**; colours not dim; moves smooth |
| 11 | Full render | `$PY tools/finish.py <take>` (~12 min for 80 s, background) → `final/<take>/`, verify, `qa/sheet.jpg` | read the sheet frame by frame |
| 12 | Report | path, length, beats, clips used, anything flipped/tone-mapped, verify result. If something new was learned, add it to this skill | |

## Beat rules

- Something changes every 2–4 s; never more than ~5 s of bare speaker.
- Mix the modes: speaker + stickers · B-roll cut-away (~25–30 % of runtime) · depth moment (4–6 per reel) · full-screen graphic with the speaker as a facecam bubble (1–2 max).
- Cue = start time of the spoken word in `transcript.json`. Each element leaves before the next beat.
- Depth words go **above the head** (head top from step 3): one giant word at a time, the previous word flies out. Stacked lines end up hidden behind the head.
- Safe zones (defaults; the config is the truth): header y < 200, footer y > 1520, action rail x > 920 between y 1000–1520. Text, stickers, cards, mascots and logos stay out; full-screen pictures may run under. Place text between y 220–1480 and x 60–900.
- Motion: entrances `EASE.enter`, exits `EASE.exit` (shorter), cross-screen moves on a curve with blur (`arcIn` / `arcOut` / `whip`), giant words `settle`, camera `camTo`; never `ease:"none"` on a move; overlap with `STAGGER`.
- Look follows `style.md`: its palette, fonts, graphic language and density. Something the board doesn't support doesn't go in.
- Numbers shown as facts must come from the take. Illustrative labels are fine.
- Farsi / Arabic text: `.fa` class (RTL scoped to the element — never `dir="rtl"` on `<html>`, it renders black), `letter-spacing: 0`, digits via `fa()`, a big zero as Latin `0` (Persian zero is a dot). Latin text: `.en`; giant display words: `.blk`.

## Engine contract — bugs already paid for

- Scene = `def scene(c: Comp)`: `c.clip(layer, id, start, end, html, track)`, `c.broll(name, a, b, mstart)`, `c.matte(n, a, b)`, `c.j(js...)`. Layers: `under` (behind the bubble), `tiles`, `behind` (between take and matte), `fw`, `broll`, `over`, `fx`.
- Clip divs get id `k-<id>`; animate `#<id>-i` or inner ids — never a `.clip` itself.
- Anything that slides in from off-screen needs `autoAlpha:0` in its from-state, or it peeks early.
- First tween of an element sets its initial state (`fromTo` renders immediately); later tweens: `.to` or `immediateRender:false`.
- Never `from:"random"` staggers or `Math.random` — shuffle DOM order in Python with `random.Random(seed)`.
- Same property, same element: one tween must end before the next starts (lint `overlapping_gsap_tweens`).
- `#cam` scale/x/y/clipPath/borderRadius drive punch-ins, bubble and mosaic. The matte lives inside `#cam`, so depth moments stay aligned at any camera scale.
- Front-camera B-roll with readable text in frame → add to `MIRRORED`. Never flip the main take.
- HLG/HDR sources are tone-mapped by `story_assets.py`. If `finish.py` stops on "HDR auto-promotion", a source escaped that path.
- `hyperframes snapshot` is not proof of the render — that is what step 10 is for.
- `--guides` builds are for looking only: `finish.py` refuses to render them.
- Motion helpers (`arcIn`, `settle`) set start states with `gsap.set`; don't add another `fromTo` for the same properties. `mblur` owns the element's CSS `filter` while it moves.
- Renderer dies mid-capture with no error = low RAM (Premiere, games, browsers). `finish.py` retries with 1 worker; if it still dies, ask the creator to close heavy apps (or set `PRODUCER_LOW_MEMORY_MODE=1`).
