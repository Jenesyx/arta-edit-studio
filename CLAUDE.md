# Arta Edit Studio — instructions for Claude

This repo turns talking-head phone videos into finished vertical Reels.
Settings (creator handle, language, brand, palette, fonts) live in `reel.config.json`
(fallback: `reel.config.example.json`). Read it before editing anything.

## Which edit? (decide before touching a take)

| User says | Use |
| --- | --- |
| `/reel-setup` | First-time install check + personal config. Skill `reel-setup` |
| `/reel-story <take> …` | Full-frame motion edit: speaker full-screen, own B-roll, stickers, mascot, words behind the speaker. Skill `reel-story` |
| `/reel-split <take> …` | Animated widget panel on the top ~45 %, speaker below, never moves. Skill `reel-split` |
| Asks to edit a take but names neither | Ask which of the two — one question, two options. Don't guess |

Both styles: no subtitles, no SFX, the take's own audio untouched. Someone who wants
burned-in captions should use the separate `persian-reel` skill (see README).

## Ground rules

- Python: the repo venv, `-X utf8` (Farsi on stdout). Windows `.venv/Scripts/python.exe`, macOS/Linux `.venv/bin/python`.
- Render and package only through `tools/finish.py <take>` (`--seconds 12` for a quick real render first). It carries the heap / HDR / audio fixes; a bare `npx hyperframes render` does not.
- Look at real rendered frames before calling anything done — snapshots have looked right while the render was wrong.
- `raw/` and `assets/` are the creator's files: read, never modify. Work goes in `work/<take>/`, deliverables in `final/<take>/`.
- When an edit teaches something new (a bug, a preference), add it to the matching skill in `.claude/skills/` so the next take starts from it.
