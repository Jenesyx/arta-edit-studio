# Instagram safe zones

Instagram draws its own interface on top of every Reel. Anything important placed
under it is hidden or untappable. The zones (1080 × 1920 frame, `instagram_safe_zones`
in `reel.config.json`):

| Zone | Box (x0, y0 → x1, y1) | What Instagram puts there |
| --- | --- | --- |
| `header` | 0, 0 → 1080, 200 | phone status bar, "Reels" title, camera button |
| `actions` | 920, 1000 → 1080, 1520 | like, comment, share, send, more |
| `footer` | 0, 1520 → 1080, 1920 | @username, Follow button, caption, audio |

Plus a soft 60 px margin left and right (some phones crop).

**Allowed in the zones:** full-screen pictures — the speaker, B-roll, coloured
backgrounds, maps, floods behind the speaker.
**Not allowed:** text, stickers, cards, buttons, logos, mascots, anything the viewer must
read or see.

## Tools

| What | Command |
| --- | --- |
| Guide image (zones + 120 px grid + thirds + centre lines) | `python tools/safezone.py guides` → `work/_guides/ig-safe.png` |
| See the guides in snapshots / Studio preview | build with `--guides` (`story_build.py <take> --guides`) — never render that build |
| Automatic check | `python tools/safezone.py check <take>` — headless scan every 0.2 s |
| Guides on the rendered result | `finish.py` writes `quick_sheet_guides.jpg` / `qa/sheet_guides.jpg` |

The check reports **errors** (text or a sticker/card/button box inside a zone for 0.4 s
or longer) and **warnings** (an image or drawn shape inside a zone — look at it).
`finish.py` refuses to render while there are errors, unless the creator explicitly
accepts it (`--allow-safezone`). Something that only flies *through* a zone is ignored.

Placement guide for a 1080 × 1920 Reel:

- Main text and stickers: between **y 220 and y 1480**, **x 60 to x 900**.
- Big titles: above the head, but below y 220.
- Bottom cards: end above y 1500.
- Keep the right 180 px clear between y 1000 and y 1520.
