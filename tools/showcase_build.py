"""Build a 'tool showcase' Reel: permanent panel on top, still speaker below.

A sibling of pr_build.py for takes where the person asked for a plain layout:

  * the panel is ALWAYS on -- no full-frame beats, no layout switching
  * the speaker sits below the panel at scale 1 and never moves: no opening
    push, no ambient breathing, no zoom of any kind. plan["split"] sets the
    seam (960 = 50/50) and plan["speaker_y"] shifts the face into the lower part
  * no captions, no SFX, no music bed -- the voice is the only audio
  * the panel carries UI-style widgets (cards, meters, toggles, a follow card)
    rather than ink sketches, because the subject is a piece of software

The plan lives in work/<name>/showcase.json: one entry per scene with a `kind`,
start/end on the cut timeline, and named cue times pinned to spoken words.

    python tools/showcase_build.py <name>
"""

from __future__ import annotations

import argparse
import importlib
import json
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import config as C  # noqa: E402

ICON_ROOT = C.ROOT / "node_modules" / "lucide-static" / "icons"

CREAM = C.COLORS["cream"]
INK = C.COLORS["ink"]
ACCENT = C.COLORS["accent"]          # fills and shapes only
DEEP = C.COLORS["accent_deep"]       # anything carrying text
LINE = C.COLORS["line"]
MUTED = "#6B6257"                    # config's #8A8073 is 3.4:1 on cream; this is 5.3:1
CARD = "#FFFDFA"
SOFT = "#F6DCCD"                     # accent wash behind a selected row
GOOD = "#1E7F53"
BAD = "#C0392B"
IG_BLUE = "#0095F6"
IG_RED = "#ED4956"

FA_DIGITS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")


# ------------------------------------------------------------------ pieces ---

def icon(name: str, size: int, color: str = INK, draw: bool = False,
         fill: bool = False, sw: float = 1.8, extra: str = "", cls: str = "") -> str:
    """Inline a Lucide icon. draw=True tags strokes for a draw-on reveal;
    fill=True turns the outline into a solid glyph (filled heart / bookmark)."""
    p = ICON_ROOT / f"{name}.svg"
    if not p.exists():
        raise FileNotFoundError(f"lucide icon '{name}' missing")
    s = re.sub(r"<!--.*?-->", "", p.read_text(encoding="utf-8"), flags=re.S).strip()
    s = re.sub(r'\s*class="[^"]*"', "", s)
    s = re.sub(r'width="24"', 'width="100%"', s, count=1)
    s = re.sub(r'height="24"', 'height="100%"', s, count=1)
    s = re.sub(r'stroke-width="[^"]*"', f'stroke-width="{sw}"', s)
    if fill:
        s = s.replace('fill="none"', 'fill="currentColor"', 1)
    if draw:
        for tag in ("path", "circle", "rect", "line", "polyline", "polygon", "ellipse"):
            s = s.replace(f"<{tag} ", f'<{tag} pathLength="1" class="ink" ')
    s = re.sub(r"\s+", " ", s)
    return (f'<span class="ic {cls}" style="width:{size}px;height:{size}px;'
            f'color:{color};{extra}">{s}</span>')


def bars(prefix: str, n: int, w: int, h: int, color: str, gap: int = 8,
         seed: float = 0.0) -> str:
    """A static waveform: n rounded bars with deterministic heights."""
    import math
    bw = (w - gap * (n - 1)) / n
    out = []
    for k in range(n):
        amp = 0.25 + 0.75 * abs(math.sin(k * 0.9 + seed) * math.cos(k * 0.37 + seed * 0.5))
        bh = max(10, h * amp)
        out.append(f'<i class="bar {prefix}-b" style="left:{k * (bw + gap):.1f}px;'
                   f'top:{(h - bh) / 2:.1f}px;width:{bw:.1f}px;height:{bh:.1f}px;'
                   f'background:{color};"></i>')
    return (f'<div class="wave" style="width:{w}px;height:{h}px;">{"".join(out)}</div>')


def T(t: float) -> str:
    return f"{t:.3f}"


# ------------------------------------------------------------------ scenes ---
# Each returns (html, [js lines]). Ids are s{i}-*. Cue times are absolute.

def sc_hook(i, s):
    c = s["cue"]
    left = bars(f"s{i}l", 12, 300, 150, INK, seed=0.4)
    right = bars(f"s{i}r", 12, 300, 150, INK, seed=2.1)
    html = f'''
<h1 id="s{i}-t" class="fa title abs cx" style="top:96px;">کلون کردن صدای خودت</h1>
<div id="s{i}-w" class="abs" style="left:60px;top:255px;width:960px;height:170px;">
  <div class="abs" style="left:0;top:10px;">{left}</div>
  <div class="abs" style="right:0;top:10px;">{right}</div>
  <div id="s{i}-mic" class="abs disc" style="left:390px;top:-15px;width:180px;height:180px;
    background:{ACCENT};">{icon("mic", 96, "#fff")}</div>
</div>
<div id="s{i}-card" class="card abs" style="left:150px;top:500px;width:780px;height:300px;">
  <div class="row abs" style="left:56px;top:46px;gap:28px;direction:ltr;">
    <div class="disc" style="width:120px;height:120px;background:#F3E3DA;">
      {icon("lock-keyhole", 64, BAD)}</div>
    <div class="en" style="font-size:72px;font-weight:700;">ElevenLabs</div>
  </div>
  <div class="abs row" style="left:56px;right:56px;top:196px;justify-content:center;">
    <span class="chip fa" style="background:{BAD};">{icon("credit-card", 40, "#fff")}
      <span>فقط با اشتراک پولی</span></span></div>
  <div id="s{i}-q" class="abs disc" style="right:-38px;top:-48px;width:130px;height:130px;
    background:{DEEP};"><span class="fa" style="font-size:96px;color:#fff;
    line-height:1;margin-top:10px;">؟</span></div>
</div>'''
    js = [f'inUp("#s{i}-t",{T(c["title"])});',
          f'pop("#s{i}-mic",{T(c["title"] + 0.15)});',
          f'tl.from(".s{i}l-b,.s{i}r-b",{{scaleY:0.05,duration:0.3,ease:"power2.out",'
          f'stagger:{{each:0.02,from:"end"}}}},{T(c["title"] + 0.25)});',
          f'talk(".s{i}l-b,.s{i}r-b",{T(c["title"] + 1.1)},7);',
          f'inUp("#s{i}-card",{T(c["brand"] - 0.12)});',
          f'pop("#s{i}-q",{T(c["ask"])});']
    return html, js


def sc_repo(i, s):
    c = s["cue"]
    html = f'''
<div id="s{i}-chip" class="abs cx" style="top:96px;">
  <span class="chip en" style="background:{DEEP};font-size:40px;">
    {icon("code-xml", 40, "#fff")}<span>Open Source</span></span></div>
<div id="s{i}-card" class="card abs" style="left:70px;top:230px;width:940px;height:560px;">
  <div class="abs row en" style="left:50px;top:52px;gap:22px;">
    {icon("book-marked", 58, MUTED)}
    <span style="font-size:50px;color:{MUTED};">debpalash /</span>
    <span id="s{i}-name" style="font-size:58px;font-weight:700;position:relative;">VoiceStudio
      <i id="s{i}-u" class="abs" style="left:0;right:0;bottom:-10px;height:8px;
        border-radius:4px;background:{ACCENT};transform-origin:0 50%;"></i></span>
    <span style="font-size:28px;color:{MUTED};border:2px solid {LINE};border-radius:999px;
      padding:4px 18px;">Public</span>
  </div>
  <div class="abs fa" style="left:50px;right:50px;top:176px;font-size:44px;line-height:1.5;
    text-align:right;">جایگزینِ اوپن‌سورس و کاملاً لوکالِ <span class="en">ElevenLabs</span></div>
  <div class="abs" style="left:50px;right:50px;top:330px;height:3px;background:{LINE};"></div>
  <div class="abs row en" style="left:50px;top:385px;gap:46px;font-size:44px;">
    <span class="row" style="gap:14px;">{icon("star", 52, "#D99A1E", fill=True)}
      <b id="s{i}-stars">0</b></span>
    <span class="row" style="gap:14px;">{icon("git-fork", 48, MUTED)}
      <b id="s{i}-forks">0</b></span>
    <span class="row" style="gap:14px;">{icon("scale", 48, MUTED)}<span>AGPL-3.0</span></span>
    <span class="row" style="gap:12px;"><i style="display:inline-block;width:26px;height:26px;
      border-radius:50%;background:#3572A5;"></i><span>Python</span></span>
  </div>
</div>'''
    st, fk = s["stars"], s["forks"]
    js = [f'inUp("#s{i}-card",{T(c["card"])});',
          f'pop("#s{i}-chip",{T(c["chip"])});',
          f'count("#s{i}-stars",{st},{T(c["stats"])},0.8,v=>v.toFixed(1)+"k");',
          f'count("#s{i}-forks",{fk},{T(c["stats"] + 0.1)},0.8,v=>v.toFixed(1)+"k");',
          f'tl.from("#s{i}-u",{{scaleX:0,duration:0.32,ease:"power2.out"}},{T(c["name"])});']
    return html, js


def sc_local(i, s):
    c = s["cue"]
    wave = bars(f"s{i}", 22, 440, 120, ACCENT, gap=8, seed=1.3)
    html = f'''
<div id="s{i}-chip" class="abs cx" style="top:90px;">
  <span class="chip fa">{icon("laptop", 42, CREAM)}<span>روی سیستمِ خودت</span></span></div>
<div id="s{i}-lap" class="abs" style="left:190px;top:250px;width:700px;height:520px;">
  <div class="abs" style="left:40px;top:0;width:620px;height:410px;border:8px solid {INK};
    border-radius:26px;background:#fff;overflow:hidden;">
    <div class="abs row en" style="left:0;right:0;top:0;height:70px;background:{INK};
      color:{CREAM};padding:0 26px;gap:12px;font-size:30px;">
      <i class="dot" style="background:#FF5F57;"></i><i class="dot" style="background:#FEBC2E;"></i>
      <i class="dot" style="background:#28C840;"></i>
      <span style="margin-left:18px;">VoiceStudio</span></div>
    <div class="abs" style="left:82px;top:118px;">{wave}</div>
    <div class="abs row en" style="left:40px;right:40px;top:290px;gap:22px;">
      <div class="disc" style="width:70px;height:70px;background:{ACCENT};">
        {icon("play", 34, "#fff", fill=True)}</div>
      <div style="flex:1;height:10px;border-radius:5px;background:{LINE};position:relative;">
        <i id="s{i}-prog" class="abs" style="left:0;top:0;bottom:0;width:100%;border-radius:5px;
          background:{INK};transform-origin:0 50%;"></i></div>
      <span class="row" style="gap:10px;font-size:28px;color:{GOOD};">
        <i class="dot" style="background:{GOOD};"></i>Local</span>
    </div>
  </div>
  <div class="abs" style="left:0;top:410px;width:700px;height:34px;background:{INK};
    border-radius:4px 4px 22px 22px;"></div>
</div>
<div id="s{i}-free" class="abs" style="left:720px;top:300px;width:330px;height:200px;
  border:7px solid {GOOD};border-radius:26px;background:rgba(255,253,250,.94);
  display:flex;flex-direction:column;align-items:center;justify-content:center;">
  <span class="fa" style="font-size:70px;color:{GOOD};line-height:1.1;">رایگان</span>
  <span class="en" style="font-size:44px;color:{GOOD};font-weight:700;">$0</span></div>'''
    js = [f'inUp("#s{i}-lap",{T(c["screen"])});',
          f'tl.from(".s{i}-b",{{scaleY:0.05,duration:0.3,stagger:{{each:0.015}},'
          f'ease:"power2.out"}},{T(c["screen"] + 0.25)});',
          f'tl.from("#s{i}-prog",{{scaleX:0,duration:3.0,ease:"none"}},{T(c["screen"] + 0.4)});',
          f'talk(".s{i}-b",{T(c["screen"] + 0.95)},12);',
          f'pop("#s{i}-chip",{T(c["chip"])});',
          f'gsap.set("#s{i}-free",{{rotation:-9}});',
          f'tl.from("#s{i}-free",{{scale:1.7,autoAlpha:0,duration:0.28,ease:"power3.out"}},'
          f'{T(c["free"])});']
    return html, js


def sc_clone(i, s):
    c = s["cue"]
    win = bars(f"s{i}i", 14, 300, 120, INK, gap=8, seed=0.2)
    wout = bars(f"s{i}o", 14, 300, 120, ACCENT, gap=8, seed=0.2)
    html = f'''
<div id="s{i}-k" class="abs cx en" style="top:84px;font-size:30px;color:{DEEP};
  letter-spacing:6px;font-weight:700;">VOICE CLONING</div>
<h1 id="s{i}-t" class="fa title abs cx" style="top:126px;font-size:64px;">کلونِ صدا با یه نمونه</h1>
<div id="s{i}-in" class="card abs" style="left:620px;top:280px;width:380px;height:380px;">
  <div class="abs row fa" style="right:34px;top:34px;gap:16px;font-size:38px;">
    {icon("mic", 46, INK)}<span>صدای خودت</span></div>
  <div class="abs" style="left:40px;top:150px;">{win}</div>
  <div class="abs cx fa" style="bottom:30px;font-size:32px;color:{MUTED};">نمونه‌ی تمیز</div>
</div>
<div id="s{i}-arrow" class="abs" style="left:470px;top:410px;width:140px;height:120px;">
  <svg viewBox="0 0 140 120" fill="none" stroke="{INK}" stroke-width="7"
    stroke-linecap="round" stroke-linejoin="round">
    <path pathLength="1" class="ink" d="M126 60 H22"/>
    <path pathLength="1" class="ink" d="M48 32 L18 60 L48 88"/></svg></div>
<div id="s{i}-magic" class="abs disc" style="left:494px;top:300px;width:92px;height:92px;
  background:{INK};">{icon("wand-sparkles", 50, CREAM)}</div>
<div id="s{i}-out" class="card abs" style="left:80px;top:280px;width:380px;height:380px;
  border-color:{ACCENT};">
  <div class="abs row fa" style="right:34px;top:34px;gap:16px;font-size:38px;color:{DEEP};">
    {icon("audio-lines", 46, DEEP)}<span>صدای کلون‌شده</span></div>
  <div class="abs" style="left:40px;top:150px;">{wout}</div>
  <div class="abs cx row en" style="bottom:28px;gap:10px;font-size:30px;color:{GOOD};">
    {icon("circle-check", 34, GOOD)}<span>Ready</span></div>
</div>
<div id="s{i}-chip" class="abs cx" style="top:735px;">
  <span class="chip fa" style="background:{GOOD};">{icon("check", 40, "#fff")}
    <span>به همین راحتی</span></span></div>'''
    js = [f'inUp("#s{i}-k",{T(c["title"])});',
          f'inUp("#s{i}-t",{T(c["title"] + 0.08)});',
          f'inUp("#s{i}-in",{T(c["input"])});',
          f'talk(".s{i}i-b",{T(c["input"] + 0.4)},4);',
          f'draw("#s{i}-arrow .ink",{T(c["magic"])},0.4);',
          f'pop("#s{i}-magic",{T(c["magic"] + 0.15)});',
          f'inUp("#s{i}-out",{T(c["output"] - 0.1)});',
          f'talk(".s{i}o-b",{T(c["output"] + 0.3)},1);',
          f'pop("#s{i}-chip",{T(c["chip"])});']
    return html, js


def sc_models(i, s):
    c = s["cue"]
    names = [("OmniVoice", "default"), ("CosyVoice 3", ""), ("IndexTTS 2.5", ""),
             ("VoxCPM2", "")]
    rows = []
    for k, (n, tag) in enumerate(names):
        t = (f'<span style="font-size:26px;color:{DEEP};border:2px solid {ACCENT};'
             f'border-radius:999px;padding:2px 14px;">{tag}</span>') if tag else ""
        rows.append(f'''
  <div id="s{i}-r{k}" class="abs row en" style="left:40px;right:40px;top:{118 + k * 104}px;
    height:92px;gap:22px;padding:0 24px;font-size:44px;">
    {icon("circle-play", 46, MUTED)}<span>{n}</span>{t}</div>''')
    html = f'''
<h1 id="s{i}-t" class="fa title abs cx" style="top:92px;font-size:62px;">بین مدل‌های مختلف جابه‌جا شو</h1>
<div id="s{i}-card" class="card abs" style="left:170px;top:230px;width:740px;height:560px;">
  <div class="abs row en" style="left:40px;right:40px;top:34px;justify-content:space-between;
    font-size:32px;color:{MUTED};"><span>Speech engine</span>{icon("chevron-down", 40, MUTED)}</div>
  <div class="abs" style="left:40px;right:40px;top:96px;height:3px;background:{LINE};"></div>
  <div id="s{i}-hl" class="abs" style="left:28px;right:28px;top:{118}px;height:92px;
    border-radius:20px;background:{SOFT};border:3px solid {ACCENT};"></div>
  {"".join(rows)}
  <div id="s{i}-cur" class="abs" style="left:600px;top:150px;">
    {icon("mouse-pointer-2", 60, INK, fill=True)}</div>
</div>
<div id="s{i}-chip" class="abs cx" style="top:820px;">
  <span class="chip fa">{icon("scale", 40, CREAM)}<span>مقایسه کن کدوم بهتره</span></span></div>'''
    js = [f'inUp("#s{i}-t",{T(c["title"])});',
          f'inUp("#s{i}-card",{T(c["card"])});']
    for k in range(4):
        js.append(f'tl.from("#s{i}-r{k}",{{x:-30,autoAlpha:0,duration:0.3,ease:"power3.out"}},'
                  f'{T(c["card"] + 0.2 + k * 0.12)});')
    for k, t in enumerate(c["moves"], 1):
        js.append(f'tl.to("#s{i}-hl",{{y:{k * 104},duration:0.24,ease:"power2.inOut"}},{T(t)});')
        js.append(f'tl.to("#s{i}-cur",{{y:{k * 104},duration:0.24,ease:"power2.inOut"}},{T(t)});')
    js.append(f'pop("#s{i}-chip",{T(c["compare"])});')
    return html, js


def sc_dub(i, s):
    c = s["cue"]
    html = f'''
<h1 id="s{i}-t" class="fa title abs cx" style="top:88px;font-size:84px;">فقط همین نیست!</h1>
<div id="s{i}-pl" class="abs" style="left:150px;top:250px;width:780px;height:470px;
  border-radius:30px;background:{INK};overflow:hidden;">
  <div class="abs disc" style="left:330px;top:150px;width:120px;height:120px;
    background:rgba(255,255,255,.14);">{icon("play", 58, "#fff", fill=True)}</div>
  <div id="s{i}-en" class="abs row" style="left:40px;top:40px;gap:16px;">
    <span class="tag en">EN</span><span class="bub en">Hello everyone!</span></div>
  <div id="s{i}-fa" class="abs row" style="left:40px;top:40px;gap:16px;">
    <span class="tag en" style="background:{ACCENT};">FA</span>
    <span class="bub fa">سلام به همه!</span></div>
  <div class="abs" style="left:40px;right:40px;bottom:46px;height:10px;border-radius:5px;
    background:rgba(255,255,255,.2);">
    <i id="s{i}-prog" class="abs" style="left:0;top:0;bottom:0;width:100%;border-radius:5px;
      background:{ACCENT};transform-origin:0 50%;"></i></div>
</div>
<div id="s{i}-chip" class="abs cx" style="top:765px;">
  <span class="chip fa">{icon("clapperboard", 42, CREAM)}<span>دوبله‌ی ویدیو</span></span></div>'''
    js = [f'pop("#s{i}-t",{T(c["title"])});',
          f'inUp("#s{i}-pl",{T(c["player"])});',
          f'tl.from("#s{i}-prog",{{scaleX:0,duration:1.2,ease:"none"}},{T(c["player"] + 0.2)});',
          f'tl.from("#s{i}-en",{{y:16,autoAlpha:0,duration:0.22}},{T(c["en"])});',
          f'tl.set("#s{i}-fa",{{autoAlpha:0}},0);',
          f'tl.to("#s{i}-en",{{autoAlpha:0,duration:0.14}},{T(c["fa"] - 0.14)});',
          f'tl.set("#s{i}-en",{{autoAlpha:0}},{T(c["fa"])});',
          f'tl.to("#s{i}-fa",{{autoAlpha:1,duration:0.18}},{T(c["fa"])});',
          f'pop("#s{i}-chip",{T(c["player"] + 0.15)});']
    return html, js


def sc_tools(i, s):
    c = s["cue"]
    wave = bars(f"s{i}", 10, 200, 80, ACCENT, gap=8, seed=2.4)
    # RTL: first-mentioned tile sits on the right; arrows point right-to-left.
    arrow = icon("arrow-left", 44, MUTED)
    tiles = [
        (720, "t1", "file-audio", "فایل صوتی",
         f'<div class="abs" style="left:50px;top:300px;">{wave}</div>'),
        (390, "t2", "type", "متن به صدا",
         f'<div class="abs row" style="left:0;right:0;top:300px;justify-content:center;gap:18px;">'
         f'{icon("audio-lines", 70, ACCENT)}{arrow}{icon("file-text", 70, INK)}</div>'),
        (60, "t3", "mic", "صدا به متن",
         f'<div class="abs row" style="left:0;right:0;top:300px;justify-content:center;gap:18px;">'
         f'{icon("file-text", 70, ACCENT)}{arrow}{icon("audio-lines", 70, INK)}</div>'),
    ]
    out = []
    for x, key, ic, label, mini in tiles:
        out.append(f'''
<div id="s{i}-{key}" class="card abs" style="left:{x}px;top:230px;width:300px;height:430px;">
  <div class="abs disc" style="left:85px;top:40px;width:130px;height:130px;background:{SOFT};">
    {icon(ic, 66, DEEP)}</div>
  <div class="abs cx fa" style="top:196px;font-size:40px;width:280px;text-align:center;">{label}</div>
  {mini}
</div>''')
    html = (f'<h1 id="s{i}-t" class="fa title abs cx" style="top:92px;font-size:62px;">'
            f'کلی ابزار دیگه</h1>' + "".join(out) + f'''
<div id="s{i}-chip" class="abs cx" style="top:720px;">
  <span class="chip fa" style="background:{GOOD};">{icon("check", 40, "#fff")}
    <span>همه‌ش رایگان</span></span></div>''')
    js = [f'inUp("#s{i}-t",{T(c["title"])});',
          f'inUp("#s{i}-t1",{T(c["t1"])});',
          f'tl.from(".s{i}-b",{{scaleY:0.05,duration:0.3,stagger:{{each:0.02}}}},{T(c["t1"] + 0.3)});',
          f'talk(".s{i}-b",{T(c["t1"] + 0.85)},6);',
          f'inUp("#s{i}-t2",{T(c["t2"])});',
          f'inUp("#s{i}-t3",{T(c["t3"])});',
          f'pop("#s{i}-chip",{T(c["free"])});']
    return html, js


def sc_langs(i, s):
    c = s["cue"]
    row1 = ["English", "Español", "Deutsch", "Français"]
    row2 = ["Türkçe", "Italiano", "Português", "Polski"]

    def chips(items, top, base):
        return "".join(
            f'<span id="s{i}-c{base + k}" class="lang en">{n}</span>'
            for k, n in enumerate(items)), top
    r1, _ = chips(row1, 0, 0)
    r2, _ = chips(row2, 0, 4)
    html = f'''
<div id="s{i}-k" class="abs cx" style="top:88px;">
  <span class="chip fa" style="font-size:34px;">{icon("book-marked", 36, CREAM)}
    <span>به گفته‌ی خودِ پروژه</span></span></div>
<div id="s{i}-num" class="abs row" style="left:0;right:0;top:190px;justify-content:center;
  gap:34px;direction:ltr;">
  {icon("earth", 170, DEEP, draw=True, sw=1.4)}
  <span id="s{i}-n" class="fa" style="font-size:200px;color:{DEEP};line-height:1;
    min-width:380px;text-align:center;">۰</span></div>
<div id="s{i}-lab" class="abs cx fa" style="top:410px;font-size:58px;">زبانِ دنیا</div>
<div class="abs row" style="left:40px;right:40px;top:530px;justify-content:center;gap:18px;">{r1}</div>
<div class="abs row" style="left:40px;right:40px;top:620px;justify-content:center;gap:18px;">{r2}</div>
<div id="s{i}-fa" class="abs cx" style="top:745px;">
  <span class="chip fa" style="background:{DEEP};font-size:56px;padding:18px 44px;">
    {icon("circle-check", 56, "#fff")}<span>حتی فارسی</span></span></div>'''
    js = [f'pop("#s{i}-k",{T(c["kicker"])});',
          f'draw("#s{i}-num .ink",{T(c["kicker"] + 0.2)},0.5);',
          f'tl.from("#s{i}-n",{{autoAlpha:0,duration:0.2}},{T(c["count"] - 0.1)});',
          f'count("#s{i}-n",646,{T(c["count"])},0.8,v=>fa(Math.round(v)));',
          f'inUp("#s{i}-lab",{T(c["count"] + 0.3)});']
    for k in range(8):
        js.append(f'pop("#s{i}-c{k}",{T(c["chips"] + k * 0.13)},{{duration:0.26}});')
    js.append(f'tl.to(".lang.s{i}",{{opacity:0.4,duration:0.25}},{T(c["farsi"])});')
    js.append(f'pop("#s{i}-fa",{T(c["farsi"])});')
    # tag the chips for the dim tween
    html = html.replace('class="lang en"', f'class="lang en s{i}"')
    return html, js


def sc_pillars(i, s):
    c = s["cue"]
    items = [(720, "a", "cloud-off", "کاملاً لوکال", "بدون سرورِ کس دیگه"),
             (390, "b", "badge-dollar-sign", "رایگان", "بدون اشتراک"),
             (60, "c", "laptop", "سیستمِ خودت", "اطلاعاتت پیش خودته")]
    out = []
    for x, key, ic, label, sub in items:
        out.append(f'''
<div id="s{i}-{key}" class="card abs" style="left:{x}px;top:250px;width:300px;height:440px;">
  <div class="abs disc" style="left:70px;top:46px;width:160px;height:160px;background:{SOFT};">
    {icon(ic, 84, DEEP)}</div>
  <div class="abs cx fa" style="top:236px;font-size:44px;width:280px;text-align:center;">{label}</div>
  <div class="abs cx fa" style="top:320px;font-size:30px;width:260px;text-align:center;
    color:{MUTED};">{sub}</div>
</div>''')
    html = (f'<h1 id="s{i}-t" class="fa title abs cx" style="top:96px;">قسمتِ جذابش؟</h1>'
            + "".join(out))
    js = [f'pop("#s{i}-t",{T(c["title"])});',
          f'inUp("#s{i}-a",{T(c["a"])});',
          f'inUp("#s{i}-b",{T(c["b"])});',
          f'inUp("#s{i}-c",{T(c["c"])});']
    return html, js


def sc_hardware(i, s):
    c = s["cue"]
    rows = [("cpu", "cpu", "CPU", 0.86), ("gpu", "gpu", "GPU", 0.92),
            ("ram", "memory-stick", "RAM", 0.8)]
    out = []
    for k, (key, ic, lab, frac) in enumerate(rows):
        out.append(f'''
<div id="s{i}-{key}" class="card abs row en" style="left:560px;top:{230 + k * 150}px;width:450px;
  height:124px;padding:0 28px;gap:20px;">
  {icon(ic, 56, INK)}<span style="font-size:42px;font-weight:700;width:96px;">{lab}</span>
  <div style="flex:1;height:22px;border-radius:11px;background:{LINE};position:relative;">
    <i id="s{i}-{key}f" class="abs" style="left:0;top:0;bottom:0;width:{frac * 100:.0f}%;
      border-radius:11px;background:{ACCENT};transform-origin:0 50%;"></i></div>
</div>''')
    # Gauge: 220deg arc. Needle pivots at the centre.
    html = f'''
<h1 id="s{i}-t" class="fa title abs cx" style="top:92px;font-size:64px;">سیستمِ قوی‌تر، نتیجه‌ی بهتر</h1>
{"".join(out)}
<div id="s{i}-g" class="abs" style="left:70px;top:220px;width:440px;height:400px;">
  <svg viewBox="0 0 440 400" fill="none" stroke-linecap="round" style="position:absolute;inset:0;">
    <path d="M 72.8 305 A 170 170 0 1 1 367.2 305" stroke="{LINE}" stroke-width="34"/>
    <path id="s{i}-arc" pathLength="1" d="M 72.8 305 A 170 170 0 1 1 367.2 305"
      stroke="{ACCENT}" stroke-width="34" style="stroke-dasharray:1;stroke-dashoffset:1;"/>
  </svg>
  <div id="s{i}-needle" class="abs" style="left:213px;top:60px;width:14px;height:160px;
    border-radius:7px;background:{INK};transform-origin:50% 100%;"></div>
  <div class="abs disc" style="left:194px;top:194px;width:52px;height:52px;background:{INK};"></div>
  <div class="abs cx row en" style="top:300px;gap:10px;font-size:34px;color:{MUTED};">
    {icon("gauge", 40, MUTED)}<span>Speed</span></div>
</div>
<div id="s{i}-fast" class="abs" style="left:96px;top:660px;">
  <span class="chip fa">{icon("zap", 40, "#FFC94D", fill=True)}<span>سریع‌تر</span></span></div>
<div id="s{i}-better" class="abs" style="left:96px;top:770px;">
  <span class="chip fa" style="background:{GOOD};">{icon("sparkles", 40, "#fff")}
    <span>کیفیتِ بهتر</span></span></div>'''
    js = [f'inUp("#s{i}-t",{T(c["title"])});',
          f'inUp("#s{i}-g",{T(c["title"] + 0.25)});',
          f'gsap.set("#s{i}-needle",{{rotation:-110}});',
          f'tl.set("#s{i}-needle",{{rotation:-110}},{T(s["start"])});',
          f'inUp("#s{i}-cpu",{T(c["cpu"])});',
          f'inUp("#s{i}-gpu",{T(c["gpu"])});',
          f'inUp("#s{i}-ram",{T(c["ram"])});',
          f'tl.from("#s{i}-cpuf,#s{i}-gpuf,#s{i}-ramf",{{scaleX:0,duration:0.6,'
          f'ease:"power2.out",stagger:0.15}},{T(c["fill"])});',
          f'tl.to("#s{i}-arc",{{strokeDashoffset:0.12,duration:0.7,ease:"power2.out"}},'
          f'{T(c["fast"] - 0.1)});',
          f'tl.to("#s{i}-needle",{{rotation:85,duration:0.7,ease:"power2.out"}},'
          f'{T(c["fast"] - 0.1)});',
          f'pop("#s{i}-fast",{T(c["fast"] + 0.1)});',
          f'pop("#s{i}-better",{T(c["better"])});']
    return html, js


def sc_nosub(i, s):
    c = s["cue"]
    html = f'''
<h1 id="s{i}-t" class="fa title abs cx" style="top:92px;font-size:64px;">دیگه لازم نیست پول بدی</h1>
<div id="s{i}-paid" class="card abs" style="left:570px;top:230px;width:440px;height:520px;">
  <div class="abs cx en" style="top:40px;font-size:54px;font-weight:700;">ElevenLabs</div>
  <div class="abs disc" style="left:150px;top:130px;width:140px;height:140px;background:#F6DEDA;">
    {icon("credit-card", 74, BAD)}</div>
  <div class="abs cx fa" style="top:300px;font-size:42px;">اشتراکِ ماهانه</div>
  <div class="abs cx row fa" style="top:368px;gap:12px;font-size:32px;color:{MUTED};">
    {icon("repeat", 34, MUTED)}<span>هر ماه پرداخت</span></div>
  <div id="s{i}-other" class="abs cx fa" style="top:440px;font-size:30px;color:{MUTED};
    white-space:nowrap;">+ برنامه‌های پولیِ دیگه</div>
  <svg id="s{i}-x" class="abs" viewBox="0 0 440 520" fill="none" stroke="{BAD}"
    stroke-width="12" stroke-linecap="round" style="left:0;top:0;width:440px;height:520px;">
    <path pathLength="1" class="ink" d="M60 70 L380 450"/>
    <path pathLength="1" class="ink" d="M380 70 L60 450"/></svg>
</div>
<div id="s{i}-free" class="card abs" style="left:70px;top:230px;width:440px;height:520px;
  border-color:{GOOD};">
  <div class="abs cx en" style="top:40px;font-size:54px;font-weight:700;">VoiceStudio</div>
  <div class="abs disc" style="left:150px;top:130px;width:140px;height:140px;background:#DDF0E6;">
    {icon("download", 74, GOOD)}</div>
  <div class="abs cx fa" style="top:300px;font-size:42px;color:{GOOD};">نصبِ رایگان</div>
  <div class="abs cx fa" style="top:368px;font-size:32px;color:{MUTED};
    white-space:nowrap;">روی سیستمِ خودت</div>
  <div id="s{i}-ok" class="abs disc" style="left:-30px;top:-34px;width:104px;height:104px;
    background:{GOOD};">{icon("check", 60, "#fff", sw=3)}</div>
</div>'''
    js = [f'inUp("#s{i}-t",{T(c["title"])});',
          f'inUp("#s{i}-paid",{T(c["paid"])});',
          f'tl.from("#s{i}-other",{{autoAlpha:0,y:12,duration:0.25}},{T(c["other"])});',
          f'draw("#s{i}-x .ink",{T(c["strike"])},0.3);',
          f'tl.to("#s{i}-paid",{{opacity:0.55,duration:0.3}},{T(c["strike"] + 0.3)});',
          f'inUp("#s{i}-free",{T(c["free"])});',
          f'pop("#s{i}-ok",{T(c["install"])});']
    return html, js


def rack(prefix: str, w: int = 300, unit_h: int = 86) -> str:
    units = []
    for k in range(3):
        units.append(f'''
  <div class="abs row" style="left:0;top:{k * (unit_h + 14)}px;width:{w}px;height:{unit_h}px;
    border:5px solid {INK};border-radius:16px;background:#fff;padding:0 22px;gap:14px;">
    <i class="led {prefix}-led" style="background:{LINE};"></i>
    <i class="led {prefix}-led" style="background:{LINE};"></i>
    <i style="flex:1;height:6px;border-radius:3px;background:{LINE};margin-left:20px;"></i>
  </div>''')
    return "".join(units)


def sc_server(i, s):
    c = s["cue"]
    html = f'''
<h1 id="s{i}-t" class="fa title abs cx" style="top:92px;font-size:64px;">فضای بیشتر می‌خوای؟</h1>
<div id="s{i}-lap" class="abs" style="left:740px;top:300px;width:260px;">
  {icon("laptop", 250, INK, sw=1.4)}
  <div class="fa" style="text-align:center;font-size:36px;margin-top:6px;">سیستمِ تو</div></div>
<div id="s{i}-path" class="abs" style="left:420px;top:390px;width:300px;height:80px;">
  <svg viewBox="0 0 300 80" fill="none" stroke="{ACCENT}" stroke-width="8"
    stroke-linecap="round" stroke-linejoin="round">
    <path pathLength="1" class="ink" d="M290 40 H18"/>
    <path pathLength="1" class="ink" d="M46 14 L16 40 L46 66"/></svg></div>
<div id="s{i}-pkg" class="abs" style="left:640px;top:300px;">{icon("package", 78, DEEP)}</div>
<div id="s{i}-srv" class="abs" style="left:90px;top:270px;width:300px;height:286px;">
  {rack(f"s{i}")}</div>
<div id="s{i}-srvl" class="abs fa" style="left:90px;top:570px;width:300px;text-align:center;
  font-size:36px;">سرورِ خودت</div>
<div id="s{i}-chip" class="abs cx" style="top:720px;">
  <span class="chip fa">{icon("server", 40, CREAM)}<span>هاستش کن روی سرور</span></span></div>'''
    js = [f'inUp("#s{i}-t",{T(c["title"])});',
          f'inUp("#s{i}-lap",{T(c["laptop"])});',
          f'draw("#s{i}-path .ink",{T(c["move"])},0.45);',
          f'tl.from("#s{i}-pkg",{{autoAlpha:0,duration:0.2}},{T(c["move"] + 0.2)});',
          f'tl.to("#s{i}-pkg",{{x:-330,duration:0.8,ease:"power1.inOut"}},{T(c["move"] + 0.4)});',
          f'tl.to("#s{i}-pkg",{{autoAlpha:0,duration:0.2}},{T(c["move"] + 1.1)});',
          f'tl.set("#s{i}-pkg",{{autoAlpha:0}},{T(c["move"] + 1.3)});',
          f'inUp("#s{i}-srv",{T(c["server"] - 0.15)});',
          f'inUp("#s{i}-srvl",{T(c["server"])});',
          f'tl.to(".s{i}-led",{{backgroundColor:"{GOOD}",duration:0.12,stagger:0.08}},'
          f'{T(c["server"] + 0.3)});',
          f'pop("#s{i}-chip",{T(c["chip"])});']
    return html, js


def sc_access(i, s):
    c = s["cue"]
    # server bottom-centre (540,410) -> laptop (830,600) and phone (250,600)
    html = f'''
<div id="s{i}-srv" class="abs" style="left:390px;top:96px;width:300px;height:286px;">
  {rack(f"s{i}")}</div>
<svg id="s{i}-lines" class="abs" viewBox="0 0 1080 960" fill="none" stroke="{INK}"
  stroke-width="6" stroke-dasharray="1" stroke-linecap="round"
  style="left:0;top:0;width:1080px;height:960px;">
  <path id="s{i}-l1" pathLength="1" class="ink" d="M560 395 L820 590"/>
  <path id="s{i}-l2" pathLength="1" class="ink" d="M520 395 L260 590"/></svg>
<div id="s{i}-pc" class="abs" style="left:715px;top:560px;width:240px;">
  {icon("laptop", 230, INK, sw=1.4)}</div>
<div id="s{i}-ph" class="abs" style="left:165px;top:560px;width:190px;">
  {icon("smartphone", 190, INK, sw=1.4)}</div>
<div id="s{i}-dots" class="abs" style="left:0;top:0;width:1080px;height:960px;">
  <i id="s{i}-d1" class="abs pkt" style="left:548px;top:383px;"></i>
  <i id="s{i}-d2" class="abs pkt" style="left:508px;top:383px;"></i></div>
<div id="s{i}-chip" class="abs cx" style="top:820px;">
  <span class="chip fa">{icon("wifi", 40, CREAM)}<span>دسترسی از هر کامپیوتر و گوشی</span></span></div>'''
    js = [f'inUp("#s{i}-srv",{T(c["server"])});',
          f'tl.to(".s{i}-led",{{backgroundColor:"{GOOD}",duration:0.1,stagger:0.05}},'
          f'{T(c["server"] + 0.3)});',
          f'draw("#s{i}-l1",{T(c["pc"] - 0.1)},0.35);',
          f'inUp("#s{i}-pc",{T(c["pc"])});',
          f'draw("#s{i}-l2",{T(c["phone"] - 0.1)},0.35);',
          f'inUp("#s{i}-ph",{T(c["phone"])});',
          # Packets: visibility is carried by hard sets on each dot, never by the
          # motion tween, so a seek before/after the run cannot leave one parked.
          f'tl.set("#s{i}-d1,#s{i}-d2",{{autoAlpha:0}},0);',
          f'tl.set("#s{i}-d1",{{autoAlpha:1}},{T(c["pc"] + 0.35)});',
          f'tl.fromTo("#s{i}-d1",{{x:0,y:0}},{{x:260,y:195,duration:0.6,immediateRender:false,'
          f'ease:"none",repeat:2,repeatDelay:0.15}},{T(c["pc"] + 0.35)});',
          f'tl.set("#s{i}-d1",{{autoAlpha:0}},{T(c["pc"] + 0.35 + 2.1)});',
          f'tl.set("#s{i}-d2",{{autoAlpha:1}},{T(c["phone"] + 0.35)});',
          f'tl.fromTo("#s{i}-d2",{{x:0,y:0}},{{x:-260,y:195,duration:0.6,immediateRender:false,'
          f'ease:"none",repeat:2,repeatDelay:0.15}},{T(c["phone"] + 0.35)});',
          f'tl.set("#s{i}-d2",{{autoAlpha:0}},{T(c["phone"] + 0.35 + 2.1)});',
          f'pop("#s{i}-chip",{T(c["chip"])});']
    return html, js


def sc_cta(i, s):
    c = s["cue"]
    h = s["handle"]
    html = f'''
<div id="s{i}-card" class="card abs" style="left:90px;top:84px;width:900px;height:300px;">
  <div class="abs en" style="left:0;right:0;top:48px;text-align:center;font-size:68px;
    font-weight:700;">@{h}</div>
  <div id="s{i}-fol" class="abs btn en" style="left:285px;top:164px;background:{IG_BLUE};
    color:#fff;">Follow</div>
  <div id="s{i}-foling" class="abs btn en row" style="left:285px;top:164px;background:#EFEFEF;
    color:{INK};gap:12px;justify-content:center;">{icon("check", 40, INK, sw=3)}Following</div>
  <div id="s{i}-cur" class="abs" style="left:500px;top:196px;">
    {icon("mouse-pointer-2", 70, INK, fill=True, extra="filter:drop-shadow(0 4px 6px rgba(0,0,0,.3));")}</div>
</div>
<div id="s{i}-row" class="abs row" style="left:0;right:0;top:418px;justify-content:center;gap:90px;">
  <span class="act">
    <span class="stack" style="width:84px;height:84px;">{icon("heart", 84, INK)}
      {icon("heart", 84, IG_RED, fill=True, cls="fillon", extra="position:absolute;left:0;top:0;")}</span>
    <span class="fa">لایک</span></span>
  <span class="act">
    <span class="stack" style="width:84px;height:84px;">{icon("message-circle", 84, INK)}</span>
    <span class="fa">کامنت</span></span>
  <span class="act">
    <span class="stack" style="width:84px;height:84px;">{icon("bookmark", 84, INK)}
      {icon("bookmark", 84, INK, fill=True, cls="fillon", extra="position:absolute;left:0;top:0;")}</span>
    <span class="fa">سیو</span></span>
</div>
<div id="s{i}-cm" class="abs" style="left:130px;top:600px;width:820px;height:300px;">
  <div class="abs" style="left:0;top:0;width:820px;height:250px;border-radius:44px;
    background:{DEEP};box-shadow:0 14px 0 rgba(32,36,47,.14);"></div>
  <div class="abs" style="left:110px;top:226px;width:0;height:0;border-left:30px solid transparent;
    border-right:30px solid transparent;border-top:50px solid {DEEP};"></div>
  <div id="s{i}-five" class="abs en" style="left:60px;top:8px;width:230px;height:234px;
    font-size:220px;font-weight:700;color:#fff;line-height:234px;text-align:center;">5</div>
  <div class="abs fa" style="right:56px;top:40px;width:470px;text-align:right;font-size:72px;
    color:#fff;line-height:1.3;">کامنت کن</div>
  <div class="abs fa" style="right:56px;top:146px;width:470px;text-align:right;font-size:38px;
    color:#FBE3D6;">تا برات بفرستم</div>
</div>'''
    js = [f'inUp("#s{i}-card",{T(c["card"])});',
          f'tl.set("#s{i}-foling",{{autoAlpha:0}},0);',
          f'tl.from("#s{i}-row .act",{{y:24,autoAlpha:0,duration:0.3,stagger:0.08,'
          f'ease:"power3.out"}},{T(c["row"])});',
          f'tl.set("#s{i}-row .fillon",{{autoAlpha:0,scale:0.4}},0);',
          # save, then like: fill in on the spoken word
          f'tl.to("#s{i}-row .act:nth-child(3) .fillon",{{autoAlpha:1,scale:1,duration:0.25,'
          f'ease:"back.out(1.6)"}},{T(c["save"])});',
          f'tl.to("#s{i}-row .act:nth-child(1) .fillon",{{autoAlpha:1,scale:1,duration:0.25,'
          f'ease:"back.out(1.6)"}},{T(c["like"])});',
          # cursor glides onto Follow, presses, button flips to Following
          f'tl.from("#s{i}-cur",{{x:240,y:120,autoAlpha:0,duration:0.35,ease:"power2.out"}},'
          f'{T(c["follow"] - 0.3)});',
          f'tl.to("#s{i}-fol",{{scale:0.92,duration:0.08}},{T(c["follow"] + 0.08)});',
          f'tl.set("#s{i}-fol",{{autoAlpha:0}},{T(c["follow"] + 0.16)});',
          f'tl.set("#s{i}-foling",{{autoAlpha:1}},{T(c["follow"] + 0.16)});',
          f'tl.from("#s{i}-foling",{{scale:0.92,duration:0.16,ease:"power2.out"}},'
          f'{T(c["follow"] + 0.16)});',
          f'tl.to("#s{i}-cur",{{autoAlpha:0,duration:0.2}},{T(c["follow"] + 0.45)});',
          f'tl.set("#s{i}-cur",{{autoAlpha:0}},{T(c["follow"] + 0.66)});',
          f'tl.from("#s{i}-cm",{{y:60,autoAlpha:0,scale:0.9,duration:0.4,ease:"power3.out"}},'
          f'{T(c["comment"])});',
          f'tl.from("#s{i}-five",{{scale:0.3,autoAlpha:0,duration:0.32,ease:"back.out(1.7)"}},'
          f'{T(c["comment"] + 0.25)});',
          f'tl.to("#s{i}-five",{{scale:1.12,duration:0.22,ease:"sine.inOut",yoyo:true,'
          f'repeat:3}},{T(c["pulse"])});']
    return html, js


RENDER = {"hook": sc_hook, "repo": sc_repo, "local": sc_local, "clone": sc_clone,
          "models": sc_models, "dub": sc_dub, "tools": sc_tools, "langs": sc_langs,
          "pillars": sc_pillars, "hardware": sc_hardware, "nosub": sc_nosub,
          "server": sc_server, "access": sc_access, "cta": sc_cta}


# --------------------------------------------------------------------- page ---

CSS = """
@font-face{font-family:"BrandFa";src:url("assets/fonts/__FAFONT__");font-display:block;}
@font-face{font-family:"LatinUI";src:url("assets/fonts/__ENFONT__");font-weight:300 700;
  font-display:block;}
*{margin:0;padding:0;box-sizing:border-box;}
html,body{width:1080px;height:1920px;overflow:hidden;background:#000;}
body{font-family:"BrandFa","LatinUI",sans-serif;color:__INK__;}
#speaker{position:absolute;left:0;top:0;width:1080px;height:1920px;object-fit:cover;}
#panel{position:absolute;left:0;top:0;width:1080px;height:__SPLIT__px;overflow:hidden;
  background-color:__CREAM__;
  background-image:radial-gradient(rgba(32,36,47,.10) 2.2px,transparent 2.6px);
  background-size:40px 40px;background-position:20px 20px;
  box-shadow:0 10px 30px rgba(0,0,0,.30);}
.scene{position:absolute;inset:0;}
.abs{position:absolute;}
.cx{left:0;right:0;margin-inline:auto;width:fit-content;}
.row{display:flex;align-items:center;}
/* RTL scoped to text elements. dir="rtl" on <html> renders a fully black video. */
.fa{direction:rtl;unicode-bidi:isolate;letter-spacing:0;word-spacing:0.1em;}
.en{font-family:"LatinUI",sans-serif;direction:ltr;unicode-bidi:isolate;}
.title{font-size:72px;font-weight:800;line-height:1.3;text-align:center;white-space:nowrap;}
.card{background:__CARD__;border:4px solid __INK__;border-radius:34px;
  box-shadow:0 14px 0 rgba(32,36,47,.10);}
.chip{display:inline-flex;align-items:center;gap:16px;padding:14px 32px;border-radius:999px;
  background:__INK__;color:__CREAM__;font-size:40px;white-space:nowrap;
  box-shadow:0 8px 20px rgba(32,36,47,.16);}
.disc{display:flex;align-items:center;justify-content:center;border-radius:50%;}
.ic{display:inline-block;flex:0 0 auto;}
.ic svg{width:100%;height:100%;display:block;}
.ink{stroke-dasharray:1;stroke-dashoffset:1;}
.wave{position:relative;}
.bar{position:absolute;display:block;border-radius:8px;transform-origin:50% 50%;}
.dot{display:inline-block;width:18px;height:18px;border-radius:50%;}
.led{display:inline-block;width:20px;height:20px;border-radius:50%;}
.tag{display:inline-block;font-size:30px;font-weight:700;color:#fff;background:#3C4454;
  border-radius:12px;padding:6px 16px;}
.bub{display:inline-block;font-size:40px;color:__INK__;background:#fff;border-radius:20px;
  padding:10px 26px;white-space:nowrap;}
.lang{display:inline-block;font-size:36px;padding:10px 26px;border-radius:999px;
  background:#fff;border:3px solid __INK__;white-space:nowrap;}
.pkt{display:block;width:24px;height:24px;border-radius:50%;background:__ACCENT__;
  box-shadow:0 0 0 6px rgba(224,123,83,.25);}
.btn{width:330px;height:84px;border-radius:18px;font-size:40px;font-weight:700;
  display:flex;align-items:center;justify-content:center;}
.act{display:inline-flex;flex-direction:column;align-items:center;gap:6px;font-size:32px;}
.stack{position:relative;display:inline-block;}
"""

JS_HELPERS = """
const fa = n => String(n).replace(/[0-9]/g, d => "۰۱۲۳۴۵۶۷۸۹"[d]);
function inUp(sel, t, o) {
  tl.from(sel, Object.assign({y: 40, autoAlpha: 0, duration: 0.36, ease: "power3.out"}, o || {}), t);
}
function pop(sel, t, o) {
  tl.from(sel, Object.assign({scale: 0.6, autoAlpha: 0, duration: 0.3, ease: "back.out(1.5)"}, o || {}), t);
}
function draw(sel, t, d) {
  tl.to(sel, {strokeDashoffset: 0, duration: d || 0.42, stagger: 0.04, ease: "power1.inOut"}, t);
}
function count(sel, to, t, dur, fmt) {
  const o = {v: 0}, el = document.querySelector(sel);
  tl.to(o, {v: to, duration: dur, ease: "power2.out",
            onUpdate: function () { el.textContent = fmt(o.v); }}, t);
}
// Speech-like bar motion. Finite repeats only -- repeat:-1 is banned.
function talk(sel, t, reps) {
  tl.to(sel, {scaleY: function (i) { return 0.3 + 0.7 * Math.abs(Math.sin(i * 1.37 + 0.6)); },
              duration: 0.2, ease: "sine.inOut", yoyo: true, repeat: reps,
              stagger: {each: 0.025, from: "center"}}, t);
}
"""


def build(name: str) -> Path:
    wd = C.work_dir_for(name)
    plan = json.loads((wd / "showcase.json").read_text(encoding="utf-8"))
    sc = wd / "sc"
    pub = sc / "public"
    (pub / "assets" / "fonts").mkdir(parents=True, exist_ok=True)

    gsap = C.gsap_js()
    latin = C.font("en")
    shutil.copyfile(gsap, pub / "assets" / "gsap.min.js")
    fafont = C.brand_font()
    shutil.copyfile(fafont, pub / "assets" / "fonts" / fafont.name)
    shutil.copyfile(latin, pub / "assets" / "fonts" / latin.name)
    video = wd / plan["video"]
    dst = pub / "assets" / video.name
    if not dst.exists() or dst.stat().st_mtime < video.stat().st_mtime:
        shutil.copyfile(video, dst)

    dur = round(C.probe(video)["duration"], 3)
    split = plan["split"]

    # A take can bring its own scene kinds: plan["scenes_module"] names a module
    # in tools/ exporting RENDER (and optionally CSS / JS helper strings).
    render = dict(RENDER)
    extra_css = extra_js = ""
    if plan.get("scenes_module"):
        mod = importlib.import_module(plan["scenes_module"])
        render.update(mod.RENDER)
        extra_css = getattr(mod, "CSS", "")
        extra_js = getattr(mod, "JS", "")

    body = [
        f'<video id="speaker" class="clip" src="assets/{video.name}" data-start="0" '
        f'data-duration="{dur}" data-track-index="0" muted playsinline></video>',
        f'<audio id="speaker-audio" class="clip" src="assets/{video.name}" data-start="0" '
        f'data-duration="{dur}" data-track-index="4" data-volume="1"></audio>',
    ]
    # Speaker framing is fixed for the whole piece: scale 1, shifted so the face
    # sits in the bottom half. Immediate gsap.set, not tl.set(...,0) -- a
    # zero-duration set at 0 does not render while the playhead sits on 0.
    js = [f'gsap.set("#speaker",{{y:{plan["speaker_y"]}}});']

    # plan["safe"] = [left, top, right, bottom] insets the scene content inside
    # the panel. Instagram's top UI (and the iPhone status bar) covers ~4-7 % of
    # the frame, so text placed flush with the panel top gets hidden.
    safe = plan.get("safe")

    scenes = plan["scenes"]
    inner = []
    for i, s in enumerate(scenes, 1):
        end = min(s["end"], dur)
        html, anims = render[s["kind"]](i, s)
        if safe:
            l, t, r, b = safe
            html = (f'<div class="abs" style="left:{l}px;top:{t}px;right:{r}px;'
                    f'bottom:{b}px;">{html}</div>')
        inner.append(
            f'<div id="s{i}" class="scene clip" data-start="{s["start"]:.3f}" '
            f'data-duration="{end - s["start"]:.3f}" data-track-index="2">'
            f'<div id="s{i}-inner" class="scene">{html}</div></div>')
        js += anims
        if i < len(scenes):
            fade = end - 0.25
            js.append(f'tl.to("#s{i}-inner",{{autoAlpha:0,duration:0.22,ease:"power2.in"}},{T(fade)});')
            js.append(f'tl.set("#s{i}-inner",{{autoAlpha:0}},{T(fade + 0.22)});')
    body.append(f'<div id="panel" class="clip" data-start="0" data-duration="{dur}" '
                f'data-track-index="1">{"".join(inner)}</div>')

    css = CSS + extra_css
    for tok, val in {"__CREAM__": CREAM, "__INK__": INK, "__ACCENT__": ACCENT,
                     "__CARD__": CARD, "__SPLIT__": str(split),
                     "__FAFONT__": fafont.name, "__ENFONT__": latin.name}.items():
        css = css.replace(tok, val)

    html = f"""<!doctype html>
<html lang="fa" data-resolution="portrait">
<head><meta charset="UTF-8"/><meta name="viewport" content="width=1080, height=1920"/>
<script src="assets/gsap.min.js"></script>
<style>{css}</style></head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{dur}"
     data-width="1080" data-height="1920">
{chr(10).join(body)}
</div>
<script>
window.__timelines = window.__timelines || {{}};
const tl = gsap.timeline({{ paused: true }});
{JS_HELPERS}
{extra_js}
{chr(10).join(js)}
window.__timelines["main"] = tl;
</script>
</body></html>
"""
    out = pub / "index.html"
    out.write_text(html, encoding="utf-8")
    holds = sorted(min(s["end"], dur) - s["start"] for s in scenes)
    print(f"[showcase] {out}")
    print(f"[showcase] {len(scenes)} scenes over {dur:.2f}s, median hold "
          f"{holds[len(holds) // 2]:.2f}s, longest {holds[-1]:.2f}s")
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Build a permanent-panel showcase Reel")
    ap.add_argument("video")
    args = ap.parse_args(argv)
    build(C.find_raw(args.video).stem)
    return 0


if __name__ == "__main__":
    sys.exit(main())
