# Motion — how things move

Smooth motion is what separates an edit from a slideshow. Every composition loads
`tools/motion.js` (GSAP + MotionPathPlugin + CustomEase), so these are available in any
scene's timeline code. `tools/motion_check.py <take>` flags what breaks the rules;
`finish.py` prints its warnings before rendering.

## The five rules

1. **Nothing moves in a straight line at constant speed.** Use an ease — always.
   `ease:"none"` only for continuous loops (rotating rays, tickers).
2. **Arrive fast, land soft; leave by accelerating.** Entrances `EASE.enter`
   (≈ 0.45–0.6 s), exits `EASE.exit` (≈ 0.2–0.3 s). Exits are always shorter.
3. **Big moves travel on a curve and blur in the direction of travel** — `arcIn`,
   `arcOut`, `whip` do both.
4. **Weight: overshoot and settle.** Giant words and logos slam with `settle`; small
   stickers pop with `EASE.pop` (back.out). Never a bare scale 0 → 1 in a straight ease.
5. **Overlap, don't queue.** Stagger groups by `STAGGER` (0.06 s); start the next
   element before the previous has fully landed; camera moves begin slightly before
   the word they emphasise.

## Easing system (`EASE`, `DUR`)

| Name | Curve | Use | Typical duration |
| --- | --- | --- | --- |
| `EASE.enter` | "studio" — fast start, long soft landing | anything arriving | `DUR.enter` 0.5 s |
| `EASE.exit` | accelerate away | anything leaving | `DUR.exit` 0.24 s |
| `EASE.move` | smooth in-out | repositioning on screen | `DUR.move` 0.6 s |
| `EASE.pop` | back.out(1.6) | stickers, icons, small chips | `DUR.pop` 0.38 s |
| `EASE.cam` | smooth in-out | camera punch-ins / reframes | `DUR.cam` 0.8 s |
| `EASE.snap` | expo.out | whips, hard-hitting arrivals | 0.3 s |
| `EASE.float` | sine.inOut | idle secondary motion | 1.4 s per swing |

## Helpers

```js
arcIn("#card", 12.4, { from: [0, 340], bend: 0.22 });   // rises on an arc, blur on y
arcOut("#card", 15.1, { to: [-600, -120] });              // leaves left on an arc
whip("#bw-lecture", 8.55, { from: "right" });             // B-roll whips in with 30 px x-blur
mblur("#owl", 23.4, 0.45, "x", 18);                       // add blur to any move you wrote yourself
settle("#word", 42.56);                                   // slam: 1.6 → 0.95 → 1.03 → 1
kf("#logo", 26.4, [{ scale: 1.08, duration: 0.25 }, { scale: 1, duration: 0.35 }]);
floaty("#sticker", 13.0, 2.8, 8);                         // gentle bob AFTER its entrance
camTo(7.84, { scale: 1.1, dur: 0.5 });                    // story layout camera (#cam)
```

- `mblur` attaches an SVG directional blur (`stdDeviation "N 0"`) only while the element
  moves, so text is perfectly sharp at rest. Don't combine it with another tween on the
  same element's CSS `filter`.
- Helpers that set a start state (`arcIn`, `settle`) do it with `gsap.set` at build time —
  don't add a second `fromTo` for the same properties on that element.
- Camera: keep punch-ins ≤ 1.15× for emphasis, 1.25–1.3× only for a dramatic beat; return
  to 1.0 with the same ease before depth (text-behind-speaker) moments.

## Checklist before rendering

- [ ] Every entrance has a matching exit (or the clip ends while it is still and on purpose).
- [ ] No two tweens fight over one property of one element at the same time.
- [ ] Fast cross-screen moves use `arcIn` / `whip` / `mblur`.
- [ ] `motion_check.py` shows no `linear` or `jerky` warnings you can't explain.
- [ ] Watch the quick render (`finish.py --seconds 12`) at full speed — motion problems
      are invisible in still frames.
