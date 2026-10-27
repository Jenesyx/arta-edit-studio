# Story-edit technique catalogue

Every entry was used in `examples/story/story_stoodi_inviteraw.py` — copy the named
scene function and change words, cues and positions. Times are examples from that take.

## Depth moments (layer `behind` + `c.matte`)

| Technique | Use when the speaker says… | Scene fn | Notes |
| --- | --- | --- | --- |
| Map + pins behind speaker, one pin becomes "you", giant word | a place / "in every X…" / "maybe it's you" | `hook` | `projector()` + `de_path()` draw Germany, `UNIS` = German university cities. Other country: add its border as a (lat, lon) list in the same format; VHS glitch-out exit |
| Brand reveal: purple circle-wipe flood from the face, rotating rays, wordmark letters, confetti | the product/brand name | `reveal` | `wordmark()`, `confetti()`; waving owl in `over` |
| Slogan, one giant word at a time + front chips | a slogan / list of 2–4 words | `slogan` | previous word flies up as the next lands |
| Grayscale + dark backdrop + caution tapes | "honestly…", warning, "not for everyone" | `honest` | `#aw`/`#fw` filter + cam punch to 1.28 |
| Giant CTA word + typed comment + reply with link | "comment X" | `join` | caret, send press, posted row, reply row, welcome owl |
| End lockup: app icon + wordmark behind | last second | `outro` | |

## Speaker + front graphics (layer `over`)

| Technique | Use for | Scene fn |
| --- | --- | --- |
| Sticky notes crossed out with red marker | "not A, not B" | `not_prof` |
| Chat bubbles (left grey / right purple) | "explained casually", dialogue | `chat` |
| Thinking owl slides in + big ؟ + slow push-in | "why…?", a question | `why` |
| Two avatars + curved line + mascot + packets | "connects X with Y" | `connect` |
| Exam card with German grades + slam badges | fail → pass, before → after | `exam` |
| Sticker + mascot peeking + coin rain | earning, money | `tutor` (2nd half) |
| Phone cards fan in, merge into a badge | "from a few reels → a team" | `team` |
| Polaroid playing a clip + hand-drawn arrow, camera shifts to make room | "I'll put the video right here" | `event` |
| RTL progress steps, last node pulses | "now the next step" | `steps` |
| Avatar ring around the frame + network lines | community, people | `community` |
| Fork card: two columns, each fills on its cue, Follow click | "if you're A do X, if B do Y" | `fork` |
| Heart burst + follow button | "like and follow" | `outro` (1st half) |

## Cut-aways (layer `broll`, each clip in `#bw-<name>`)

| Technique | Use for | Scene fn |
| --- | --- | --- |
| Hard cut / flash cut | default | `flash(t)` |
| Whip in (x or y from off-screen + blur) | energy, "then…" | `arrival`, `tutor` |
| Zoom-in from 1.35 + blur, 3x speed baked in trim, FF badge, speed lines, speedometer | speed, rush, overload | `lecture` |
| Progress bar that fills then drains to 0 % + sad owl | "learned nothing", failure | `home` |
| Iris from where the sticker sits + stamp slam + shake | proof, "passed", approval | `student` |
| 0.4 s cuts with flash + counter sticker | time passing, "9 months of work" | `montage` |
| Location / label sticker | where / what | `arrival` |

## Full-screen (layer `under` + `#cam` as bubble)

| Technique | Use for | Scene fn |
| --- | --- | --- |
| Speaker shrinks to a ringed circle at the bottom; full-screen map, pins turn into owls, hearts | scale: "every university", "everywhere" | `germany` |
| World zoom-out: speaker becomes one tile in a 5×5 wall of clips + owl tiles, snap back | "part of something bigger" | `bigger` |
| VHS rewind overlay (scanlines, ◀◀ REWIND blink, jitter) | "let me start from the beginning" | `rewind` |

## Mascot moods

After `story_assets.py <take> all`, every image in `assets/mascot/` is available as
`assets/mascot/<name>.png` (name = file stem, lower-case, spaces → `-`); `owl(id, name, x, y, w)`
places one. The example used the Stoodi owl with these names — map your own character the same way:

| File | Mood |
| --- | --- |
| `owl-wave` | hello, introducing |
| `owl-think` | question, "why" (has a ?) |
| `owl-sad` | failure, learned nothing |
| `owl-stressed` | pressure, speed (small: ≤ 260 px) |
| `owl-angry` | problem, frustration |
| `owl-party` | celebration, slogan (confetti baked in) |
| `owl-teacher` | teaching, Tutorium (small: ≤ 260 px) |
| `owl-welcome` | join / welcome (lots of transparent margin: use ~400 px wide) |
| `owl-flat` | flat icon: pins, avatars, small marks |
| `owl-head`, `owl-hero` | big tiles, hero shots |
| `assets/brand/logo.png` | your logo (`brand.logo`), rounded-square lockups |
