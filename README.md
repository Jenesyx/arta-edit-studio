<div align="center">

# 🎬 Arta Edit Studio

**Turn a talking-head phone video into a finished, animated Instagram Reel — by typing one command to Claude.**

**English** · [فارسی](README.fa.md)

Built by **Arta Bidkhori** · Instagram [@artabidkhori](https://www.instagram.com/artabidkhori) · MIT licensed, free forever

</div>

---

## Table of contents

1. [What is this?](#what-is-this)
2. [The two edit styles](#the-two-edit-styles)
3. [How it works](#how-it-works)
4. [Requirements](#requirements)
5. [Installation](#installation)
6. [Folder layout](#folder-layout)
7. [Configuration](#configuration-reelconfigjson)
8. [Preparing your media](#preparing-your-media)
9. [Using the commands](#using-the-commands)
10. [How to describe your video (prompting guide)](#how-to-describe-your-video-prompting-guide)
11. [Giving feedback after the first version](#giving-feedback-after-the-first-version)
12. [What you get](#what-you-get)
13. [Customising](#customising)
14. [Troubleshooting](#troubleshooting)
15. [Staying up to date](#staying-up-to-date)
16. [Credits and license](#credits-and-license)

---

## What is this?

Arta Edit Studio is a set of **skills (slash commands) for [Claude Code](https://claude.com/claude-code)**
plus the Python/Node tools they drive. You drop your video in a folder, type a command
like:

```
/reel-story my-video  I explain how my startup started. Already cut and coloured. Comment keyword: JOIN.
```

…and Claude acts as your video editor. It transcribes what you say, plans a beat for
every few seconds, picks moments from your own B-roll clips, writes the animations,
renders the final 1080×1920 video and checks it frame by frame before handing it over.

It was built for **Farsi (Persian)** creators first — right-to-left text, Persian digits,
Farsi fonts and Whisper settings are handled — but it works for any language Whisper
understands (English, Arabic, German, Turkish, …).

What it deliberately does **not** do:

- **No subtitles.** Both styles tell the story with graphics, not captions.
  Want burned-in Farsi captions? Use [persian-reel](https://github.com/aradazr/persian-reel) by Arad Azarpanah.
- **No cutting, colour grading or music.** It assumes you already edited your take
  (cuts, colour, music) in CapCut / Premiere / your phone. Your audio stays exactly as you mixed it.

---

## The two edit styles

| | `/reel-story` | `/reel-split` |
| --- | --- | --- |
| **Look** | You fill the whole screen. Cut-aways to your own clips, stickers and cards pop on your words, a mascot reacts, giant words appear **behind you**, the camera zooms, you shrink into a bubble over a map… | A cream panel with animated UI widgets fills the **top 45 %**. You sit underneath, still, the whole time. |
| **Best for** | Stories, announcements, startup / personal updates, invitations | "I found this tool", "5 tips", explainers, tutorials |
| **Uses** | Your B-roll folder, optional mascot + logo | Only your talking video |
| **Energy** | High — something changes every 2–4 s | Calm and clear — one idea per panel scene |
| **Ending** | Big comment keyword + follow card + logo lockup | Big comment keyword + follow card |

Both: no subtitles, no sound effects, your own audio untouched, Instagram-safe zones respected.

Signature tricks of `/reel-story` (all included as copyable examples):

- **Text behind you** — the tool cuts you out of your own video (AI person matte), so a giant word, your logo or a coloured world can sit *between* you and the wall.
- **Facecam bubble** — you shrink into a circle while a full-screen map or graphic takes over, then you grow back.
- **Mosaic zoom-out** — the camera pulls back until you are one tile in a wall of your own clips.
- **Fork card, comment typing, polaroid "right here", speed-ramped B-roll, exam stamps, coin rain, VHS rewind…** — 25 techniques in [`.claude/skills/reel-story/references/techniques.md`](.claude/skills/reel-story/references/techniques.md).

---

## How it works

```
raw/your-video.mp4
   │
   ├─ 1. Transcribe ........ Whisper large-v3 → every word with its exact time
   ├─ 2. Face tracking ..... OpenCV → where your face is (for zooms / framing)
   ├─ 3. B-roll catalogue .. contact sheets of your clips + a notes file Claude keeps
   ├─ 4. Beat plan ......... Claude pins a visual idea to a spoken word every few seconds
   ├─ 5. Assets ............ B-roll trimmed (HDR → SDR, mirrored selfies fixed),
   │                         mascot background removed, AI cut-out of you (matte)
   ├─ 6. Composition ....... Claude writes the animation as HTML + GSAP (HyperFrames)
   ├─ 7. Checks ............ lint, snapshots, then a 12-second REAL test render
   ├─ 8. Render ............ HyperFrames renders 1080×1920 @ 30 fps
   └─ 9. Package + QA ...... your original audio put back, loudness check,
                             contact sheet of the result → final/your-video/
```

Claude is the editor (it reads, plans, writes the scenes and looks at the frames);
the tools in `tools/` do the heavy lifting. Everything runs **on your computer** —
no upload, no subscription other than Claude itself.

---

## Requirements

| What | Why | Notes |
| --- | --- | --- |
| **Claude Code** | the editor | Desktop app, terminal CLI or VS Code / JetBrains extension, with a Claude plan |
| **Python 3.10+** | transcription, face tracking, asset prep | |
| **Node.js 18+** | HyperFrames renderer, GSAP, icons | |
| **FFmpeg with `zscale`** | video processing, HDR → SDR | Windows: the "full" build from gyan.dev · macOS: `brew install ffmpeg` |
| **NVIDIA GPU** (recommended) | Whisper ~10× faster | Works on CPU too, just slower |
| **~10 GB free disk** | Whisper model (3 GB), PyTorch, renders | |
| **16 GB RAM** (32 GB comfortable) | rendering many video layers | Close games / Premiere while rendering |

Tested on **Windows 11 + RTX 3080 Ti**. macOS and Linux should work (every path is
cross-platform) but are not tested yet — reports welcome.

---

## Installation

### Easiest: let Claude do it

```bash
git clone https://github.com/Jenesyx/arta-edit-studio.git
cd arta-edit-studio
```

Open the folder in Claude Code and type:

```
/reel-setup
```

It checks your machine, asks before installing anything, downloads the free fonts,
and creates your personal `reel.config.json` by asking a few questions (name,
Instagram handle, language, brand colours).

### Manual

```bash
# 1. Python environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate

# 2. PyTorch — copy the right command from https://pytorch.org
#    (NVIDIA GPU → choose a CUDA build). Example for CUDA 12.4:
pip install torch --index-url https://download.pytorch.org/whl/cu124

# 3. The rest
pip install -r requirements.txt
npm install
npx hyperframes doctor        # checks the renderer and its Chrome

# 4. Your settings
cp reel.config.example.json reel.config.json   # then edit it (see below)
```

Then put the fonts in `font/` (see [Fonts](#fonts)).

---

## Folder layout

```
arta-edit-studio/
├─ .claude/skills/
│  ├─ reel-setup/        /reel-setup  — install + personal config
│  ├─ reel-story/        /reel-story  — full-frame motion edit (+ techniques catalogue)
│  └─ reel-split/        /reel-split  — 45 % panel edit
├─ tools/                the Python tools the skills run
├─ examples/
│  ├─ story/             a real 82 s /reel-story edit (25 scenes) to learn from
│  └─ split/             a real 100 s /reel-split edit (18 scenes) to learn from
├─ raw/                  ← your videos to edit
├─ assets/
│  ├─ broll/             ← your B-roll clips (phone videos of your life/work)
│  ├─ mascot/            ← optional character images
│  └─ brand/             ← optional logo.png
├─ font/                 ← font files
├─ work/                 working files per video (safe to delete)
├─ final/                ← finished videos
├─ CLAUDE.md             tells Claude how to use this repo
├─ reel.config.example.json
└─ reel.config.json      your personal settings (not uploaded to git)
```

Your media folders and `reel.config.json` are in `.gitignore` — your videos never end up on GitHub.

---

## Configuration (`reel.config.json`)

Copy `reel.config.example.json` to `reel.config.json`. Any key you leave out falls back to the example.

| Key | What it does | Example |
| --- | --- | --- |
| `creator.name` / `creator.handle` | follow card at the end shows `@handle` | `"yourhandle"` |
| `language` | language you speak in the videos (Whisper code) | `"fa"`, `"en"`, `"ar"`, `"de"` |
| `whisper_model` | `large-v3` best; `medium`/`small` faster, worse for Farsi | `"large-v3"` |
| `broll_dir` | where your B-roll clips are | `"assets/broll"` |
| `brand.name` / `brand.wordmark` | brand reveal text (`/reel-story`) | `"stoodi"` |
| `brand.mascot_dir` | folder of character images | `"assets/mascot"` |
| `brand.mascot_crops` | cut poses out of a character sheet: `{"name": {"file": "sheet.png", "crop": [x, y, w, h]}}` | |
| `brand.logo` | square logo for lockups | `"assets/brand/logo.png"` |
| `palette.*` | `/reel-story` colours: `primary`, `secondary`, `ink`, `deep`, `accent`, `accent2`, `highlight`, `paper`, `red`, `green`, `pink`, `social` | hex colours |
| `split_palette.*` | `/reel-split` panel colours: `cream`, `ink`, `accent`, `accent_deep` (text on cream), `line` | hex colours |
| `fonts.fa` / `fonts.en` / `fonts.display` | font files for Farsi text, Latin text, giant display words | `"font/Vazirmatn-Medium.ttf"` |
| `split.panel_height` | panel height in px (864 = 45 %, 960 = 50 %) | `864` |
| `split.safe` | panel padding `[left, top, right, bottom]` — top keeps text clear of Instagram's header | `[64, 160, 64, 32]` |
| `render.workers` / `render.node_heap_mb` | render parallelism / memory for the renderer | `3` / `12288` |
| `loudness.lufs` / `loudness.true_peak` | targets the final check reports against | `-14` / `-1.5` |

### Fonts

Fonts are not included (licences). The defaults are free (SIL Open Font License):

| Config key | Default file | Download |
| --- | --- | --- |
| `fonts.fa` | `Vazirmatn-Medium.ttf` | [github.com/rastikerdar/vazirmatn](https://github.com/rastikerdar/vazirmatn/releases) |
| `fonts.en` | `Poppins-SemiBold.ttf` | [fonts.google.com/specimen/Poppins](https://fonts.google.com/specimen/Poppins) |
| `fonts.display` | `Poppins-Black.ttf` | same family |

Any `.ttf` / `.otf` / `.woff2` works — put it in `font/` and point the config at it.

---

## Preparing your media

1. **Your video → `raw/`.** Any name, `.mp4` or `.mov`. Vertical (9:16) phone video.
   Edit it first (cuts, colour, music) — Arta Edit Studio adds the picture layer only.
2. **B-roll → `assets/broll/`** (for `/reel-story`). Short phone clips of your life and
   work: walking, studying, typing, screens, events, food, your desk. 10–30 clips is
   plenty. iPhone HDR and mirrored selfies are handled automatically.
3. **Mascot → `assets/mascot/`** (optional). PNGs of a character in different moods
   (waving, thinking, sad, celebrating…). Images with a fake white/checkerboard
   background (typical for AI image tools) are cut out automatically. Name files by
   mood: `owl-wave.png`, `owl-think.png` — Claude reads the names.
4. **Logo → `assets/brand/logo.png`** (optional).

**Recording tips:** leave some empty wall above your head (that's where the "words
behind you" go) · face the light · lav mic if you can · don't mirror-flip your video ·
keep your face roughly in the middle of the frame.

---

## Using the commands

| Command | When |
| --- | --- |
| `/reel-setup` | once after cloning, or when something is missing |
| `/reel-story <video> <description>` | full-frame motion edit |
| `/reel-split <video> <description>` | 45 % panel edit |

`<video>` is the file name in `raw/` — extension, upper/lower case and dashes don't
matter (`StoodiInviteRaw` finds `stoodi-inviteraw.mp4`).

After you send the command, Claude:

1. asks once for anything missing (edited already? comment keyword? names?),
2. transcribes, looks at your video and B-roll, writes a beat plan,
3. builds, checks and test-renders,
4. renders the full video (≈ 10–15 min for 80 s) and checks the frames,
5. tells you where the file is and what's in it.

If you just say "edit my video" without a command, Claude asks which style you want.

---

## How to describe your video (prompting guide)

The more Claude knows up front, the fewer questions and the better the first version.

### The formula

```
/reel-story <file>  <What the video is about, in one or two sentences>.
<Already edited? (cut / colour / music)>. Comment keyword: <WORD>.
Names: <brand, people, tools Whisper may mishear>. <Any wishes>.
```

### What to include and why

| Include | Why it matters |
| --- | --- |
| **Topic in 1–2 sentences** | Claude plans visuals for the *message*, not just the words |
| **Edited already?** | if yes, nothing is cut or re-coloured; if no, Claude asks before touching it |
| **Comment keyword** | it appears huge at the end (`JOIN`, `5`, `موشن` …) |
| **Names and jargon** | Whisper spells them right (`Stoodi`, `HyperFrames`, `n8n`, `Tutorium`) |
| **Who it's for** | tone of stickers and words (students, developers, founders…) |
| **Must-have moments** | "show my event clip when I say *right here*", "logo when I say the name" |
| **Things to avoid** | "no mascot", "don't use the food clip", "no English text" |
| **Mood / reference** | "energetic like a startup launch", "calm and minimal" |

### Good examples

```
/reel-story stoodi-invite  I tell where the idea for my startup Stoodi came from and invite
Iranian students in Germany to join the promotion team. Already cut, coloured, music added.
Comment keyword: JOIN. Names: Stoodi, Tutorium, Hochschule. Show my first-event clip when I
say "I'll put the video right here". Use the owl a lot, it's our mascot.
```

```
/reel-split cursor-3-tips  Three Cursor features most people don't know: rules files,
background agents, MCP. Already edited. Comment keyword: 3. Names: Cursor, MCP, Claude.
Audience: beginner developers. Keep it calm.
```

```
/reel-story weekly-update  A casual weekly update about my study life in Germany.
Not edited yet — raw take. Comment keyword: VLOG. Names: Mensa, TU München.
```

### Weak examples (and the fix)

| Weak | Better |
| --- | --- |
| `/reel-story video1` | add topic, edited?, keyword, names |
| "make it cool" | "energetic, lots of cut-aways, logo reveal when I say Stoodi" |
| "use some B-roll" | "use the library and lecture clips when I talk about studying" |

### Writing in Farsi works too

```
/reel-story stoodi-invite  توی این ویدیو میگم ایده‌ی استارتاپم استودی از کجا اومد و
دانشجوهای ایرانی آلمان رو دعوت می‌کنم. کات و رنگ و موزیک انجام شده. کلمه‌ی کامنت: JOIN.
اسم‌ها: Stoodi، Tutorium.
```

---

## Giving feedback after the first version

Talk to Claude like you would to a human editor — the more precise, the better:

| You say | Claude does |
| --- | --- |
| "At 0:12 the sticker covers my face, move it lower" | moves that element, re-renders |
| "The logo reveal is too short, hold it until I finish the sentence" | extends that scene |
| "Use the train clip instead of the library at 0:19" | swaps the B-roll |
| "Too busy between 0:30 and 0:40, keep only the map" | removes elements |
| "Add a map of Iran with Tehran highlighted at 0:50" | builds a new scene |
| "Remember: never use English text in my videos" | follows it now **and** adds it to the skill for next time |

Timestamps (`0:12`) make feedback unambiguous. Ask for a quick test render
("render the first 15 seconds") when you only want to check a fix.

---

## What you get

```
final/<video>/
├─ <video>.mp4            1080×1920, 30 fps, H.264, your original audio
├─ qa/sheet.jpg           a frame every 3 s — the whole edit at a glance
├─ qa/frame_*.png         10 full-size check frames
├─ transcript.json        word-level transcript
├─ overlay.json / showcase.json   the edit plan (scenes, B-roll used)
└─ config-snapshot.json   the settings it was made with
```

The final check reports canvas, fps, loudness and true peak. If your own mix peaks
above −1.5 dBTP the check says so — your audio is never changed unless you ask.

---

## Customising

- **Colours / fonts / handle / language** → `reel.config.json`.
- **Your mascot** → images in `assets/mascot/`, named by mood.
- **New animation ideas** → describe them to Claude. If you like the result, say
  "add this to the reel-story techniques" and it becomes part of the catalogue.
- **Read the examples** in `examples/` — every scene is a small Python function
  that writes HTML + GSAP; copy and change.
- **Other countries' maps** → the map helper draws Germany from a (lat, lon) border
  list; add another country's border in the same format.

---

## Troubleshooting

| Problem | Cause → fix |
| --- | --- |
| Final video looks dark / washed, stickers never disappear | an HDR (HLG) clip got in untouched → `finish.py` now stops with "HDR auto-promotion"; re-run `story_assets.py <video> broll` (tone-maps HDR) |
| Render stops silently halfway | renderer ran out of memory → keep `render.node_heap_mb` at 12288, close games / Premiere, or lower `render.workers` |
| Whisper crashes (exit 139) or "CUDA out of memory" | another program holds the GPU or RAM (games, Premiere) → close it and retry |
| `font 'fa' not found` | put the font file in `font/` and check `fonts.*` in the config |
| Video renders completely black | `dir="rtl"` on `<html>` — Claude should never do this; tell it |
| Snapshot looked fine, render is wrong | expected sometimes — that's why there is a 12-second real test render; send Claude the timestamp |
| Text hidden under Instagram's top bar / buttons | tell Claude the timestamp; safe zones are in the skills |
| Text on my B-roll reads backwards | it was a mirrored selfie → Claude adds it to `MIRRORED` |
| `zscale` filter not found | your FFmpeg build lacks libzimg → install the "full" build |

---

## Staying up to date

- ⭐ **Star** and 👁 **Watch → Releases** on GitHub to get notified of new versions.
- Update with `git pull` (your `reel.config.json` and media are never touched).
- Changes are listed in [CHANGELOG.md](CHANGELOG.md).
- Found a bug or made a cool technique? Open an issue or a pull request — new
  techniques for the catalogue are especially welcome.

---

## Credits and license

**Built by Arta Bidkhori** — [@artabidkhori](https://www.instagram.com/artabidkhori) — and
edited with Claude Code. Released under the [MIT License](LICENSE): free to use, change
and share, including commercially.

Standing on the shoulders of:

- [Claude Code](https://claude.com/claude-code) by Anthropic — the editor
- [HyperFrames](https://github.com/heygen-com/hyperframes) by HeyGen (Apache-2.0) — HTML → video renderer, background removal
- [Whisper](https://github.com/openai/whisper) by OpenAI (MIT) — transcription
- [GSAP](https://gsap.com) (free "no charge" license) — animation
- [Lucide](https://lucide.dev) (ISC) — icons
- [OpenCV](https://opencv.org) (Apache-2.0) and [FFmpeg](https://ffmpeg.org) (LGPL/GPL)
- [persian-reel](https://github.com/aradazr/persian-reel) by Arad Azarpanah (MIT) — the captioned Farsi Reel skill that inspired this project
- Fonts: [Vazirmatn](https://github.com/rastikerdar/vazirmatn) by Saber Rastikerdar, [Poppins](https://fonts.google.com/specimen/Poppins) by Indian Type Foundry (OFL)
