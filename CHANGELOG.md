# Changelog

## 1.1.0 — 2026-10-27

- **Mood board (required).** `moodboard/default/` or `moodboard/<video>/` with screenshots,
  motion clips and notes. `tools/moodboard.py` builds contact sheets, dominant palette and
  reference pace (cuts/min); Claude writes `work/<video>/style.md` from
  `docs/style-brief.md` (with an anti-slop checklist) and the creator approves it. Both
  builders refuse to run without it.
- **Instagram safe zones.** `instagram_safe_zones` in the config (header / action rail /
  footer). `tools/safezone.py guides` draws zones + 120 px grid + thirds; `--guides` builds
  preview them; `tools/safezone.py check` scans the timeline headlessly every 0.2 s and
  `finish.py` blocks the render on errors. Contact sheets with guides after every render.
  `split.safe` top inset is now 200 px.
- **Smooth motion.** `tools/motion.js` in every composition: house easing curves, curved
  paths (`arcIn` / `arcOut`), directional SVG motion blur (`mblur`, `whip`),
  overshoot-and-settle, keyframes, idle float, camera moves. `tools/motion_check.py` flags
  linear, jerky and teleporting moves. Guide: `docs/motion.md`.
- `finish.py` retries with one render worker when the renderer dies from low memory.

## 1.0.0 — 2026-10-26

First public release by Arta Bidkhori.

- `/reel-story` — full-frame motion edit: B-roll cut-aways, stickers and widgets on spoken
  words, mascot, words behind the speaker (AI person matte), facecam bubble over full-screen
  graphics, mosaic zoom-out. 25 techniques documented with a real 82 s example.
- `/reel-split` — 45 % animated widget panel over a still speaker, with a real 100 s example.
- `/reel-setup` — machine check, install, fonts and personal config in one command.
- `reel.config.json` — handle, language, brand, palette, fonts, mascot, render settings.
- Tools: low-memory Whisper large-v3 loader (fp16 on GPU), Haar face tracking, B-roll
  catalogue with notes, automatic HDR (HLG/PQ) → SDR tone-mapping, mirrored-selfie fix,
  mascot background removal, one-command render + package + QA (`tools/finish.py`) with
  the fixes for renderer memory, HDR auto-promotion and audio remux.
