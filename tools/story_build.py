"""Story-Reel engine: full-frame speaker, B-roll, mascot, depth layers.

Used by the /reel-story skill. The take arrives cut/graded/mixed; this builds
only the picture layer, as one HyperFrames composition:

  #under   full-screen scenes that show while the speaker is a facecam bubble
  #world   the "camera": #cam (speaker + behind-layer + matte) and the mosaic
           tiles that appear when the world zooms out
    #cam     punch-ins, bubble, grayscale. Inside it, in paint order:
             a-roll  ->  #behind (floods / giant words)  ->  #fw (person matte)
             so the giant words sit BEHIND the speaker
  #broll   full-frame B-roll cut-aways, each in its own animated wrapper
  #over    stickers, cards, owl, polaroid -- everything in front
  #fx      flashes, scanlines, speed lines

Everything specific to one take lives in tools/story_<slug>.py (slug = take
name, non-alphanumerics -> "_"): NAME, optional DUR / FACE, the B-roll picks
(BROLL / TILES / MIRRORED, read by story_assets.py), the scene functions and
SCENES. examples/story/story_stoodi_inviteraw.py is the worked example to copy.

No captions. No SFX. Audio is the take's own mix (tools/finish.py remuxes it).

    python tools/story_build.py <take-name>
"""

from __future__ import annotations

import importlib
import json
import math
import random
import re
import shutil
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import config as C  # noqa: E402
from showcase_build import icon  # noqa: E402

# Palette from reel.config.json. The short colour names are what scene code
# uses; they map onto the config roles (PURPLE = primary, LILAC = secondary...).
_P = C.CFG["palette"]
PURPLE, LILAC, INK, IRIS = _P["primary"], _P["secondary"], _P["ink"], _P["deep"]
ORANGE, GOLD, YELLOW, PAPER = _P["accent"], _P["accent2"], _P["highlight"], _P["paper"]
RED, GREEN, PINK, IG_BLUE = _P["red"], _P["green"], _P["pink"], _P["social"]
PRIMARY, SECONDARY, DEEP, ACCENT, HIGHLIGHT = PURPLE, LILAC, IRIS, ORANGE, YELLOW
HANDLE = C.HANDLE
BRAND_WORDMARK = C.CFG["brand"].get("wordmark") or C.CFG["brand"].get("name") or ""


FONTS = {"FA": C.font("fa"), "EN": C.font("en"), "BLK": C.font("display")}
FA_DIGITS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")


def T(t: float) -> str:
    return f"{t:.3f}"


# ----------------------------------------------------------------- germany ---
# Simplified border, (lat, lon) clockwise from the Danish border.
DE = [(54.91, 8.65), (54.80, 9.45), (54.47, 9.95), (54.40, 10.25), (54.45, 11.15),
      (54.03, 10.85), (53.95, 11.05), (54.00, 11.45), (54.18, 12.10), (54.43, 12.60),
      (54.40, 13.10), (54.68, 13.40), (54.45, 13.70), (54.10, 13.80), (53.95, 14.20),
      (53.45, 14.40), (52.97, 14.15), (52.60, 14.60), (52.33, 14.55), (51.85, 14.75),
      (51.45, 14.98), (51.15, 15.04), (50.87, 14.82), (50.86, 14.40), (50.73, 13.90),
      (50.62, 13.45), (50.48, 13.05), (50.40, 12.70), (50.32, 12.22), (50.22, 12.10),
      (50.05, 12.30), (49.80, 12.45), (49.55, 12.55), (49.35, 12.80), (49.10, 13.30),
      (48.85, 13.70), (48.75, 13.82), (48.57, 13.45), (48.30, 13.40), (48.15, 12.85),
      (47.80, 12.95), (47.55, 13.05), (47.70, 12.75), (47.65, 12.20), (47.58, 11.65),
      (47.45, 11.25), (47.40, 10.95), (47.55, 10.65), (47.27, 10.18), (47.55, 9.80),
      (47.65, 9.45), (47.75, 9.15), (47.70, 8.80), (47.80, 8.65), (47.60, 8.40),
      (47.58, 7.65), (47.90, 7.58), (48.25, 7.70), (48.60, 7.82), (48.97, 8.22),
      (49.10, 7.70), (49.15, 7.40), (49.10, 7.05), (49.18, 6.85), (49.40, 6.55),
      (49.47, 6.37), (49.75, 6.50), (50.05, 6.13), (50.30, 6.30), (50.60, 6.25),
      (50.75, 6.02), (51.05, 5.87), (51.25, 6.17), (51.50, 6.10), (51.80, 5.97),
      (51.85, 6.40), (52.05, 6.75), (52.25, 7.05), (52.45, 7.02), (52.65, 6.75),
      (52.85, 7.08), (53.20, 7.20), (53.55, 7.05), (53.70, 7.40), (53.70, 7.90),
      (53.55, 8.15), (53.70, 8.40), (53.88, 8.65), (53.85, 9.05), (54.05, 8.85),
      (54.33, 8.62), (54.48, 9.00), (54.75, 8.80)]

UNIS = [(52.52, 13.40), (53.55, 9.99), (48.14, 11.58), (50.94, 6.96), (50.11, 8.68),
        (48.78, 9.18), (50.78, 6.08), (51.05, 13.74), (51.34, 12.37), (52.37, 9.73),
        (53.08, 8.80), (51.96, 7.63), (49.40, 8.69), (49.01, 8.40), (49.87, 8.65),
        (51.48, 7.22), (51.23, 6.78), (47.99, 7.85), (51.54, 9.93), (54.32, 10.14),
        (54.09, 12.10), (50.93, 11.59), (49.79, 9.95), (49.45, 11.08), (50.00, 8.27),
        (50.73, 7.10), (51.51, 7.47), (51.31, 9.48), (52.13, 11.63), (48.57, 13.43),
        (49.01, 12.10), (48.37, 10.90), (48.40, 9.99), (50.87, 8.02), (51.72, 8.75),
        (52.02, 8.53), (52.28, 8.05), (53.14, 8.21), (53.87, 10.69), (54.10, 13.38),
        (50.83, 12.92), (49.59, 11.00), (47.66, 9.18), (48.52, 9.06), (49.44, 7.77),
        (49.24, 6.99), (49.75, 6.64), (52.39, 13.06), (51.76, 14.33), (51.48, 11.97),
        (50.98, 11.03)]
BERLIN = 0


def projector(h: float, left: float, top: float):
    s = h / 7.8
    return lambda lat, lon: (left + (lon - 5.85) * 0.6266 * s, top + (55.0 - lat) * s)


def de_path(p) -> str:
    pts = [p(lat, lon) for lat, lon in DE]
    return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + " Z"


# ------------------------------------------------------------------ pieces ---

def stk(sid: str, x: float, y: float, inner: str, cls: str = "", extra: str = "") -> str:
    return f'<div id="{sid}" class="stk {cls}" style="left:{x}px;top:{y}px;{extra}">{inner}</div>'


def fa(text: str, size: int = 48, color: str = "inherit", extra: str = "") -> str:
    return f'<span class="fa" style="font-size:{size}px;color:{color};{extra}">{text}</span>'


def en(text: str, size: int = 48, color: str = "inherit", extra: str = "") -> str:
    return f'<span class="en" style="font-size:{size}px;color:{color};{extra}">{text}</span>'


def owl(oid: str, name: str, x: float, y: float, w: float, extra: str = "") -> str:
    return (f'<img id="{oid}" class="owl" src="assets/mascot/{name}.png" '
            f'style="left:{x}px;top:{y}px;width:{w}px;{extra}"/>')


class Comp:
    def __init__(self):
        self.L = {k: [] for k in ("under", "tiles", "behind", "fw", "broll", "over", "fx")}
        self.js: list[str] = []

    def clip(self, layer: str, cid: str, a: float, b: float, inner: str, track: int):
        self.L[layer].append(
            f'<div id="k-{cid}" class="clip scene" data-start="{T(a)}" data-duration="{T(b - a)}" '
            f'data-track-index="{track}"><div id="{cid}-i" class="scene">{inner}</div></div>')

    def video(self, layer: str, vid: str, src: str, a: float, b: float, track: int,
              mstart: float = 0.0, cls: str = "full", style: str = ""):
        self.L[layer].append(
            f'<video id="{vid}" class="clip {cls}" src="{src}" data-start="{T(a)}" '
            f'data-duration="{T(b - a)}" data-media-start="{T(mstart)}" '
            f'data-track-index="{track}" muted playsinline style="{style}"></video>')

    def broll(self, name: str, a: float, b: float, mstart: float = 0.0):
        """B-roll video in its own (untimed) wrapper #bw-<name>."""
        self.L["broll"].append(
            f'<div id="bw-{name}" class="bw"><video id="v-{name}" class="clip full" '
            f'src="assets/broll/{name}.mp4" data-start="{T(a)}" data-duration="{T(b - a)}" '
            f'data-media-start="{T(mstart)}" data-track-index="4" muted playsinline></video></div>')

    def matte(self, n: int, a: float, b: float):
        # same frame range as the a-roll, so the cut-out lands pixel-exact on top
        self.video("fw", f"fg{n}", "assets/fg.webm", a, b, 3, mstart=a)

    def j(self, *lines: str):
        self.js.extend(lines)


# ---------------------------------------------------------------- effects ---

def confetti(c: Comp, cid: str, x0: float, y0: float, t: float, n: int = 34, seed: int = 1):
    rnd = random.Random(seed)
    cols = [YELLOW, ORANGE, LILAC, "#fff", PINK, "#22D3EE"]
    bits = []
    for k in range(n):
        w, h = rnd.randint(14, 26), rnd.randint(24, 44)
        bits.append(f'<i id="{cid}{k}" class="cf" style="left:{x0}px;top:{y0}px;width:{w}px;'
                    f'height:{h}px;background:{cols[k % len(cols)]};"></i>')
        ang = rnd.uniform(-math.pi, 0)
        sp = rnd.uniform(260, 620)
        dx, dy = math.cos(ang) * sp, math.sin(ang) * sp
        fall = rnd.uniform(500, 900)
        r1, r2 = rnd.randint(-360, 360), rnd.randint(-540, 540)
        c.j(f'tl.fromTo("#{cid}{k}",{{x:0,y:0,rotation:0,scale:0,autoAlpha:1}},{{x:{dx:.0f},'
            f'y:{dy:.0f},rotation:{r1},scale:1,duration:0.42,ease:"power3.out"}},{T(t)});',
            f'tl.to("#{cid}{k}",{{x:{dx * 1.25:.0f},y:{dy + fall:.0f},rotation:{r2},autoAlpha:0,'
            f'duration:1.0,ease:"power1.in"}},{T(t + 0.42)});')
    return "".join(bits)


def wordmark(wid: str, size: int, color: str = "#fff", text: str | None = None) -> str:
    """Brand name as per-letter spans (class lw + wid) for a staggered reveal."""
    return "".join(f'<span class="lw {wid}" style="display:inline-block;">{ch}</span>'
                   for ch in (text or BRAND_WORDMARK))


# --------------------------------------------------------------------- page ---

CSS = """
@font-face{font-family:"FA";src:url("assets/fonts/__FA__");font-display:block;}
@font-face{font-family:"EN";src:url("assets/fonts/__EN__");font-display:block;}
@font-face{font-family:"BLK";src:url("assets/fonts/__BLK__");font-display:block;}
*{margin:0;padding:0;box-sizing:border-box;}
html,body{width:1080px;height:1920px;overflow:hidden;background:__INK__;}
body{font-family:"FA","EN",sans-serif;color:__INK__;}
#root{position:relative;width:100%;height:100%;overflow:hidden;background-color:__INK__;
  background-image:radial-gradient(rgba(255,255,255,.10) 2.4px,transparent 2.8px);background-size:44px 44px;}
.layer{position:absolute;left:0;top:0;width:1080px;height:1920px;}
#world{transform-origin:540px 960px;}
#cam{position:absolute;left:0;top:0;width:1080px;height:1920px;overflow:hidden;transform-origin:__FACE__;
  background:#000;}
#camframe{position:absolute;left:-40px;top:-40px;width:1160px;height:2000px;border:40px solid __YELLOW__;
  border-radius:110px;opacity:0;}
#aw,#behind,#fw{position:absolute;inset:0;}
video.full{position:absolute;left:0;top:0;width:1080px;height:1920px;object-fit:cover;}
.scene{position:absolute;inset:0;}
.bw{position:absolute;inset:0;overflow:hidden;}
.flood{position:absolute;inset:0;}
.dots{background-image:radial-gradient(rgba(255,255,255,.13) 2.4px,transparent 2.8px);background-size:44px 44px;}
.rays{width:2000px;height:2000px;border-radius:50%;
  background:repeating-conic-gradient(rgba(255,255,255,.10) 0deg 9deg,transparent 9deg 18deg);}
.abs{position:absolute;}
.cx{left:0;right:0;margin-inline:auto;width:fit-content;}
.row{display:flex;align-items:center;}
.fa{font-family:"FA",sans-serif;direction:rtl;unicode-bidi:isolate;letter-spacing:0;word-spacing:0.1em;}
.en{font-family:"EN",sans-serif;direction:ltr;unicode-bidi:isolate;}
.blk{font-family:"BLK",sans-serif;direction:ltr;}
.ic{display:inline-block;flex:0 0 auto;}
.ic svg{width:100%;height:100%;display:block;}
.ink{stroke-dasharray:1;stroke-dashoffset:1;}
.disc{display:flex;align-items:center;justify-content:center;border-radius:50%;}
.owl{position:absolute;display:block;height:auto;filter:drop-shadow(0 14px 18px rgba(12,6,40,.35));}
.stk{position:absolute;display:flex;align-items:center;gap:18px;padding:16px 36px;border-radius:999px;
  background:#fff;color:__INK__;border:5px solid __INK__;box-shadow:0 9px 0 __INK__;white-space:nowrap;}
.stk.p{background:__PURPLE__;color:#fff;}
.stk.y{background:__YELLOW__;}
.stk.ink{background:__INK__;color:#fff;border-color:#fff;box-shadow:0 9px 0 rgba(0,0,0,.35);}
.stk2{display:flex;align-items:center;gap:14px;padding:10px 26px;border-radius:999px;white-space:nowrap;}
.crd{position:absolute;background:#fff;border:5px solid __INK__;border-radius:42px;box-shadow:0 12px 0 __INK__;}
.pin{position:absolute;display:block;width:26px;height:26px;border-radius:50%;background:__YELLOW__;
  border:5px solid #fff;box-shadow:0 0 0 6px rgba(255,210,63,.25);}
.ring{position:absolute;display:block;width:120px;height:120px;border-radius:50%;border:6px solid __YELLOW__;}
.scan{position:absolute;left:0;width:1080px;height:3px;background:rgba(0,0,0,.35);}
.spd{position:absolute;display:block;height:5px;border-radius:3px;background:rgba(255,255,255,.75);}
.flag{display:inline-flex;flex-direction:column;width:66px;height:42px;border-radius:6px;overflow:hidden;}
.flag i{display:block;flex:1;}
.note{position:absolute;width:250px;height:250px;border-radius:14px;box-shadow:0 14px 24px rgba(12,6,40,.30);}
.tape{position:absolute;left:75px;top:-22px;width:110px;height:40px;background:rgba(255,255,255,.55);
  transform:rotate(-4deg);}
.stamp{font-size:84px;color:__GREEN__;border:9px solid __GREEN__;border-radius:22px;padding:6px 26px;
  display:flex;align-items:center;gap:10px;background:rgba(255,255,255,.88);letter-spacing:2px;}
.bub{position:absolute;padding:24px 40px;box-shadow:0 10px 24px rgba(12,6,40,.28);white-space:nowrap;}
.pkt{position:absolute;display:block;width:22px;height:22px;border-radius:50%;background:__ORANGE__;
  box-shadow:0 0 0 6px rgba(255,154,0,.25);}
.badge{color:#fff;font-size:36px;padding:6px 22px;border-radius:999px;white-space:nowrap;}
.chip{font-size:36px;color:__INK__;background:#EDE4FF;padding:6px 22px;border-radius:999px;white-space:nowrap;}
.chip2{display:inline-block;font-size:42px;padding:12px 30px;border-radius:999px;border:5px solid __INK__;
  box-shadow:0 8px 0 __INK__;white-space:nowrap;}
.coin{position:absolute;width:96px;height:96px;border-radius:50%;background:__ORANGE__;color:#fff;
  border:7px solid __GOLD__;font-size:56px;display:flex;align-items:center;justify-content:center;
  box-shadow:0 8px 0 rgba(26,14,77,.35);}
.cf{position:absolute;display:block;border-radius:4px;}
.phone{position:absolute;width:150px;height:266px;border-radius:28px;border:6px solid #fff;
  background:linear-gradient(160deg,__LILAC__,__PURPLE__ 55%,__IRIS__);display:flex;align-items:center;
  justify-content:center;box-shadow:0 12px 24px rgba(12,6,40,.35);}
.pola{position:absolute;width:430px;padding:20px 20px 22px;background:#fff;border-radius:10px;
  box-shadow:0 24px 40px rgba(12,6,40,.45);}
.tile{position:absolute;width:1080px;height:1920px;border-radius:80px;overflow:hidden;object-fit:cover;}
.tapeband{position:absolute;left:-310px;width:1700px;height:120px;background:__YELLOW__;overflow:hidden;
  border-top:12px solid #111;border-bottom:12px solid #111;display:flex;align-items:center;}
.tapeband.blk .tb-in{font-family:"BLK",sans-serif;font-size:56px;color:#111;white-space:nowrap;}
.tapeband.fa .tb-in{font-family:"FA",sans-serif;direction:rtl;font-size:60px;color:#111;white-space:nowrap;}
.btn{width:300px;height:80px;border-radius:18px;font-size:40px;display:flex;align-items:center;
  justify-content:center;}
.av{width:120px;height:120px;border:6px solid #fff;box-shadow:0 8px 0 rgba(12,6,40,.35);}
.caret{display:inline-block;width:4px;height:44px;background:__PURPLE__;margin-left:4px;vertical-align:-6px;}
#flash{position:absolute;inset:0;background:#fff;opacity:0;}
"""

JS_HELPERS = """
const fa = n => String(n).replace(/[0-9]/g, d => "۰۱۲۳۴۵۶۷۸۹"[d]);
function pop(sel, t, o) {
  tl.fromTo(sel, {scale: 0.4, autoAlpha: 0},
    Object.assign({scale: 1, autoAlpha: 1, duration: 0.3, ease: "back.out(1.8)"}, o || {}), t);
}
function inUp(sel, t, o) {
  tl.fromTo(sel, {y: 50, autoAlpha: 0},
    Object.assign({y: 0, autoAlpha: 1, duration: 0.34, ease: "power3.out"}, o || {}), t);
}
function out(sel, t, d) { tl.to(sel, {autoAlpha: 0, duration: d || 0.2, ease: "power2.in"}, t); }
function draw(sel, t, d) {
  tl.fromTo(sel, {strokeDashoffset: 1}, {strokeDashoffset: 0, duration: d || 0.4, ease: "power1.inOut"}, t);
}
function flash(t, a) {
  tl.fromTo("#flash", {opacity: a || 0.85}, {opacity: 0, duration: 0.16, ease: "power1.out",
    immediateRender: false}, t);
}
function count(sel, a, b, t, dur, fmt) {
  const o = {v: a}, el = document.querySelector(sel);
  tl.fromTo(o, {v: a}, {v: b, duration: dur, ease: "power1.inOut", immediateRender: false,
    onUpdate: function () { el.textContent = fmt(o.v); }}, t);
}
"""


def slug(name: str) -> str:
    return re.sub(r"[^0-9a-zA-Z]+", "_", name).strip("_").lower()


def take_module(name: str):
    return importlib.import_module(f"story_{slug(name)}")


def face_centre(name: str) -> tuple[int, int]:
    """Median face centre from tools/face_track.py; a frame-centre guess without it."""
    p = C.work_dir_for(name) / "face.json"
    if not p.exists():
        print("[story] no face.json -- run tools/face_track.py; pivoting on (540, 800)")
        return (540, 800)
    rows = [r["face"] for r in json.loads(p.read_text(encoding="utf-8")) if r.get("face")]
    return (round(statistics.median(x + w / 2 for x, y, w, h in rows)),
            round(statistics.median(y + h / 2 for x, y, w, h in rows)))


def build(name: str) -> Path:
    mod = take_module(name)
    wd = C.work_dir_for(name)
    pub = wd / "sc" / "public"
    a = pub / "assets"
    (a / "fonts").mkdir(parents=True, exist_ok=True)
    shutil.copyfile(C.gsap_js(), a / "gsap.min.js")
    for f in FONTS.values():
        shutil.copyfile(f, a / "fonts" / f.name)
    take = C.find_raw(name)
    matte = wd / "matte" / "fg.webm"
    for src, dst in ((take, a / "take.mp4"), (matte, a / "fg.webm")):
        if src.exists() and (not dst.exists() or dst.stat().st_mtime < src.stat().st_mtime):
            shutil.copyfile(src, dst)

    dur = getattr(mod, "DUR", None) or round(C.probe(take)["duration"], 3)
    fx, fy = getattr(mod, "FACE", None) or face_centre(name)

    c = Comp()
    for scene in mod.SCENES:
        scene(c)
    if c.L["fw"] and not matte.exists():
        print("[story] WARNING: scenes use the person matte but work/<name>/matte/fg.webm is "
              "missing -- run: python tools/story_assets.py <name> matte")

    css = CSS
    for tok, val in {"__FA__": FONTS["FA"].name, "__EN__": FONTS["EN"].name, "__BLK__": FONTS["BLK"].name,
                     "__INK__": INK, "__PURPLE__": PURPLE, "__LILAC__": LILAC, "__IRIS__": IRIS,
                     "__YELLOW__": YELLOW, "__ORANGE__": ORANGE, "__GOLD__": GOLD,
                     "__GREEN__": GREEN, "__FACE__": f"{fx}px {fy}px"}.items():
        css = css.replace(tok, val)

    L = c.L
    body = f'''
<div id="under" class="layer">{"".join(L["under"])}</div>
<div id="world" class="layer">
  {"".join(L["tiles"])}
  <div id="camframe"></div>
  <div id="cam">
    <div id="aw"><video id="aroll" class="clip full" src="assets/take.mp4" data-start="0" data-duration="{dur}"
      data-track-index="0" muted playsinline></video></div>
    <div id="behind">{"".join(L["behind"])}</div>
    <div id="fw">{"".join(L["fw"])}</div>
  </div>
</div>
<div id="broll" class="layer">{"".join(L["broll"])}</div>
<div id="over" class="layer">{"".join(L["over"])}</div>
<div id="fx" class="layer">{"".join(L["fx"])}<div id="flash"></div></div>
<audio id="take-audio" class="clip" src="assets/take.mp4" data-start="0" data-duration="{dur}"
  data-track-index="8" data-volume="1"></audio>'''

    html = f"""<!doctype html>
<html lang="fa" data-resolution="portrait">
<head><meta charset="UTF-8"/><meta name="viewport" content="width=1080, height=1920"/>
<script src="assets/gsap.min.js"></script>
<style>{css}</style></head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{dur}" data-width="1080" data-height="1920">
{body}
</div>
<script>
const tl = gsap.timeline({{ paused: true }});
{JS_HELPERS}
gsap.set("#cam", {{clipPath: "circle(1400px at {fx}px {fy}px)"}});
{chr(10).join(c.js)}
window.__timelines["main"] = tl;
</script>
</body></html>
"""
    out = pub / "index.html"
    out.write_text(html, encoding="utf-8")
    print(f"[story] {out}  ({len(mod.SCENES)} scenes, {len(c.js)} timeline lines, pivot {fx},{fy})")
    return out


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: python tools/story_build.py <take-name>")
    build(C.find_raw(sys.argv[1]).stem)
