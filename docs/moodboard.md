# Mood board — show the editor what you like

Every edit starts from **your** taste. Before Claude designs anything, it looks at a
mood board you made. No mood board, no edit — this is what keeps your Reels from looking
like generic AI output.

## Where

```
moodboard/
├─ default/          ← used for every video (your general style)
└─ <video-name>/     ← optional, only for one video (overrides default)
```

`<video-name>` = the file name in `raw/` without extension, e.g. `moodboard/stoodi-invite/`.

## What to put in it (10 minutes is enough)

| What | How many | Examples |
| --- | --- | --- |
| **Screenshots of Reels you love** | 5–15 | pause a Reel at a moment you like and screenshot it: the stickers, the fonts, the colours, the layout |
| **Short screen recordings of motion you like** | 1–3, ≤ 30 s each | a Reel whose transitions / zooms / text animation you want; record it with your phone's screen recorder |
| **Your brand** | any | logo, colours, a post you are proud of |
| **Designs / fonts / colours** | any | Pinterest, Dribbble, Behance, a magazine page |
| **`notes.md`** | 1 | 3–5 mood words + what you like + what you hate (template below) |
| `links.txt` | optional | URLs of references (only listed, not downloaded) |

Images: `.png .jpg .jpeg .webp` · videos: `.mp4 .mov` · notes: `.md .txt`.

### `notes.md` template

```markdown
Mood words: bold, playful, clean, warm
Like: big yellow words, quick zooms on my face, stickers that look hand-made
Hate: neon glow, too many emojis, robotic sliding text, purple-blue gradients
Audience: Iranian students in Germany
Pace: fast, something new every 2 seconds
```

Farsi is fine:

```markdown
حال‌وهوا: شاد، تمیز، جسور
دوست دارم: کلمه‌های بزرگ زرد، زوم سریع روی صورتم
بدم میاد: نور نئونی، ایموجی زیاد، متنی که خشک و رباتی حرکت می‌کنه
```

## What happens with it

1. `python tools/moodboard.py <video>` makes contact sheets of everything, pulls the
   dominant colours and measures the **pace** of your reference videos (cuts per minute,
   how much motion).
2. Claude looks at all of it and writes a **style brief** (`work/<video>/style.md`):
   mood, palette, typography, motion, graphic language, density, do's and don'ts —
   each tied to a reference on your board.
3. You read the brief and say OK (or what to change). Only then does the edit start.
   The build tools refuse to run without an approved brief.

## Tips

- Pick references for **one** feeling. Ten different styles = a confused edit.
- Screenshots beat descriptions: "like this" is clearer than "modern".
- Put what you *don't* want in `notes.md` — it is the fastest way to avoid AI slop.
