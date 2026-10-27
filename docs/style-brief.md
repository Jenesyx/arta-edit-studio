# Style brief — template (Claude fills this in)

Write `work/<take>/style.md` after running `tools/moodboard.py <take>` and **looking at
every board sheet**. Every line must be traceable to the mood board, the creator's notes
or the brand config — never to "what usually looks good". Keep all section headings
(the builders check for them). Then show it to the creator and wait for their OK.

```markdown
# Style brief — <take>

## Mood
3–5 words from the creator's notes / references, e.g. "bold, playful, clean".

## Palette
Roles → hex, from palette.json + brand palette. Background / text / accent / highlight.
Say which board image each comes from. Max 1 accent + 1 highlight.

## Typography
Which config font for what, weights, case (UPPER for giant English words?), size scale
(e.g. giant 220–300 px, sticker 44–56 px, label 32–36 px). Max 2 families.

## Motion
Pace: cuts/min of the references (pace.json) → how often a beat changes here.
Character: snappy / soft / bouncy. Which helpers: arcIn, whip, settle, mblur, camTo
(docs/motion.md). Transitions allowed between cut-aways.

## Graphic language
What the elements look like: flat UI cards / hand-made stickers / bold blocks / outline
icons / 3D mascot… corner radius, border width, shadow style — one consistent system.

## Density
Max elements on screen at once, how much empty space, how long each holds.

## Do
- 3–6 concrete rules lifted from the board (e.g. "words land BEHIND the speaker like ref 4").

## Don't
- Everything the creator hates (notes.md), plus the anti-slop list below.

## References
- board image / video → which scene or technique it inspires.
```

## Anti-slop checklist (always in "Don't")

- No colours that are not in the palette above — no default purple-blue gradients or neon glows "because AI".
- No emoji, decorative icons or sparkles that don't mean something said in that second.
- No filler text, lorem, generic slogans or invented numbers.
- No more than one new idea per beat; no element without a cue word.
- No straight-line linear slides, no instant pops without easing (docs/motion.md).
- No mixed styles: one corner radius, one border width, one shadow, ≤ 2 fonts.
- Nothing inside Instagram's UI zones (docs/safe-zones.md).
