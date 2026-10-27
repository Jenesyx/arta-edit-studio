# Changelog

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
