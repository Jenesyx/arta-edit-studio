"""Scene kinds for the 5skills-raw take -- five Claude skills for front-end work.

The panel is 1080x864 (45 %; speaker gets the lower 55 %). Every scene lives
inside the plan's safe box (952x672, starting 160px from the top of the frame)
so Instagram's top UI and the iPhone status bar never cover text. All
coordinates below are relative to that box. Cue times are absolute on the
take's own timeline and pinned to spoken words in work/5skills-raw/showcase.json.

Loaded by showcase_build.py through plan["scenes_module"].
"""

from __future__ import annotations

from showcase_build import (ACCENT, BAD, CREAM, DEEP, GOOD, IG_BLUE, IG_RED, INK, LINE,
                            MUTED, SOFT, T, icon)

W = 952                      # safe-box width
SCREEN = "#2A2F3B"
YELLOW = "#F2C14E"
SKY = "#8FB8FF"
MINT = "#9ED7A8"
LILAC = "#B9A7F5"
FA = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")


def fa(n) -> str:
    return str(n).translate(FA)


def hdr(i: int, n: int, name: str, size: int = 60) -> str:
    """Skill header: number disc on the right (read first), English name beside it."""
    return f'''
<div id="s{i}-h" class="abs row" style="left:0;right:0;top:0;height:100px;
  justify-content:center;gap:26px;">
  <span class="en" style="font-size:{size}px;font-weight:700;white-space:nowrap;">{name}</span>
  <span class="disc fa" style="width:96px;height:96px;background:{DEEP};color:#fff;
    font-size:58px;line-height:1;padding-top:10px;">{fa(n)}</span>
</div>'''


def thumb(id_: str, x: int, y: int, w: int, h: int, col: str, cls: str = "") -> str:
    """A tiny website mock used as a 'reference' tile."""
    return f'''
<div id="{id_}" class="abs thumb {cls}" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;">
  <i class="abs" style="left:0;right:0;top:0;height:22%;background:{col};"></i>
  <i class="abs" style="left:10%;top:34%;width:52%;height:12%;border-radius:4px;background:{INK};"></i>
  <i class="abs" style="left:10%;top:54%;width:76%;height:8%;border-radius:4px;background:{LINE};"></i>
  <i class="abs" style="left:10%;top:70%;width:30%;height:16%;border-radius:6px;background:{col};"></i>
</div>'''


def arrow_l(id_: str, x: int, y: int, w: int, col: str = INK) -> str:
    """Right-to-left arrow, drawn on with draw()."""
    return f'''
<div id="{id_}" class="abs" style="left:{x}px;top:{y}px;width:{w}px;height:80px;">
  <svg viewBox="0 0 {w} 80" fill="none" stroke="{col}" stroke-width="8"
    stroke-linecap="round" stroke-linejoin="round" style="width:100%;height:100%;">
    <path pathLength="1" class="ink" d="M{w - 10} 40 H16"/>
    <path pathLength="1" class="ink" d="M44 14 L14 40 L44 66"/></svg></div>'''


def badge(id_: str, x: int, y: int, ok: bool, size: int = 56) -> str:
    col, ic = (GOOD, "check") if ok else (BAD, "x")
    return (f'<div id="{id_}" class="abs disc" style="left:{x}px;top:{y}px;width:{size}px;'
            f'height:{size}px;background:{col};box-shadow:0 4px 0 rgba(32,36,47,.15);">'
            f'{icon(ic, int(size * 0.6), "#fff", sw=3)}</div>')


def winbar(label: str) -> str:
    return (f'<div class="winbar row en"><i class="dot" style="background:#FF5F57;"></i>'
            f'<i class="dot" style="background:#FEBC2E;"></i>'
            f'<i class="dot" style="background:#28C840;"></i>'
            f'<span style="margin-left:16px;">{label}</span></div>')


# ------------------------------------------------------------------ scenes ---

def sc_hook(i, s):
    """If you don't have these 5 Claude skills, you're wasting time."""
    c = s["cue"]
    icons = ["palette", "sparkles", "image", "list-checks", "monitor-play"]
    tiles = []
    for k in range(5):
        x = W - 32 - 160 - k * 182          # RTL: tile 1 on the right
        tiles.append(f'''
<div id="s{i}-t{k}" class="card abs" style="left:{x}px;top:140px;width:160px;height:210px;">
  <div class="abs disc" style="left:25px;top:28px;width:110px;height:110px;background:{SOFT};">
    {icon(icons[k], 58, DEEP)}</div>
  <div class="abs fa" style="left:0;right:0;top:146px;text-align:center;font-size:44px;
    color:{DEEP};">{fa(k + 1)}</div>
</div>''')
    html = f'''
<h1 id="s{i}-title" class="fa title abs cx" style="top:0;font-size:62px;">
  ۵ تا اسکیلِ <span class="en">Claude</span></h1>
{"".join(tiles)}
<div id="s{i}-chip" class="abs cx" style="top:430px;">
  <span class="chip fa" style="background:{BAD};font-size:46px;padding:18px 40px;">
    {icon("hourglass", 50, "#fff")}<span>نداریش؟ داری وقت تلف می‌کنی</span></span></div>'''
    js = [f'inUp("#s{i}-title",{T(c["title"])});']
    js += [f'pop("#s{i}-t{k}",{T(c["tiles"] + k * 0.1)});' for k in range(5)]
    js += [f'pop("#s{i}-chip",{T(c["time"])});']
    return html, js


def sc_notthese(i, s):
    """No, I don't mean UI UX Pro Max or the Frontend Design skill."""
    c = s["cue"]

    def card(key, x, ic, name):
        return f'''
<div id="s{i}-{key}" class="card abs" style="left:{x}px;top:140px;width:430px;height:320px;">
  <div class="abs disc" style="left:145px;top:36px;width:140px;height:140px;background:{SOFT};">
    {icon(ic, 74, DEEP)}</div>
  <div class="abs en" style="left:0;right:0;top:200px;text-align:center;font-size:44px;
    font-weight:700;">{name}</div>
  <div class="abs en" style="left:0;right:0;top:256px;text-align:center;font-size:28px;
    color:{MUTED};">skill</div>
  <svg id="s{i}-{key}x" class="abs" viewBox="0 0 430 320" fill="none" stroke="{BAD}"
    stroke-width="14" stroke-linecap="round" style="left:0;top:0;width:430px;height:320px;">
    <path pathLength="1" class="ink" d="M50 40 L380 280"/>
    <path pathLength="1" class="ink" d="M380 40 L50 280"/></svg>
</div>'''
    html = f'''
<h1 id="s{i}-title" class="fa title abs cx" style="top:0;font-size:62px;">منظورم اینا نیست!</h1>
{card("a", 522, "gem", "UI UX Pro Max")}
{card("b", 0, "layout-template", "Frontend Design")}
<div id="s{i}-chip" class="abs cx" style="top:530px;">
  <span class="chip fa">{icon("sparkles", 42, CREAM)}<span>پنج تا اسکیلِ دیگه</span></span></div>'''
    st = c["strike"]
    js = [f'inUp("#s{i}-title",{T(c["title"])});',
          f'inUp("#s{i}-a",{T(c["a"])});',
          f'inUp("#s{i}-b",{T(c["b"])});',
          f'draw("#s{i}-ax .ink",{T(st)},0.3);',
          f'draw("#s{i}-bx .ink",{T(st + 0.1)},0.3);',
          f'tl.to("#s{i}-a,#s{i}-b",{{opacity:0.6,duration:0.25}},{T(st + 0.35)});',
          f'pop("#s{i}-chip",{T(st + 0.3)});']
    return html, js


def sc_order(i, s):
    """I'll give you these five in the order I use them."""
    c = s["cue"]
    icons = ["palette", "sparkles", "image", "list-checks", "monitor-play"]
    nodes = []
    for k in range(5):
        cx = 856 - k * 190
        nodes.append(f'''
<div id="s{i}-n{k}" class="abs" style="left:{cx - 70}px;top:170px;width:140px;">
  <div class="disc" style="width:140px;height:140px;background:#FFFDFA;border:5px solid {INK};">
    {icon(icons[k], 64, DEEP)}</div>
  <div class="fa" style="text-align:center;font-size:48px;margin-top:14px;color:{DEEP};">{fa(k + 1)}</div>
</div>''')
    html = f'''
<h1 id="s{i}-title" class="fa title abs cx" style="top:0;font-size:58px;">به ترتیبی که خودم استفاده می‌کنم</h1>
<svg id="s{i}-line" class="abs" viewBox="0 0 952 20" fill="none" stroke="{ACCENT}" stroke-width="8"
  stroke-linecap="round" style="left:0;top:230px;width:952px;height:20px;">
  <path pathLength="1" class="ink" d="M856 10 H96"/></svg>
{"".join(nodes)}
<div id="s{i}-chip" class="abs cx" style="top:480px;">
  <span class="chip fa">{icon("user", 42, CREAM)}<span>اول تا آخرِ کارِ خودم</span></span></div>'''
    js = [f'inUp("#s{i}-title",{T(c["title"])});']
    js += [f'pop("#s{i}-n{k}",{T(c["nodes"] + k * 0.14)});' for k in range(5)]
    js += [f'draw("#s{i}-line .ink",{T(c["line"])},0.6);',
           f'pop("#s{i}-chip",{T(c["chip"])});']
    return html, js


def sc_awesome(i, s):
    """#1 Awesome Design: doesn't design, gathers thousands of references for other skills."""
    c = s["cue"]
    cols = [ACCENT, SKY, MINT, YELLOW, LILAC, INK, MINT, ACCENT, SKY]
    th = []
    for k in range(9):
        r, q = divmod(k, 3)
        x = W - 150 - q * 166
        th.append(thumb(f"s{i}-r{k}", x, 200 + r * 118, 150, 102, cols[k], f"s{i}-ref"))
    html = f'''{hdr(i, 1, "Awesome Design")}
<div id="s{i}-no" class="abs cx" style="top:110px;">
  <span class="chip fa" style="font-size:34px;padding:10px 28px;background:{MUTED};">
    {icon("pen-off", 36, "#fff")}<span>خودش طراحی نمی‌کنه</span></span></div>
{"".join(th)}
<div id="s{i}-lab" class="abs" style="left:{W - 482}px;top:568px;width:482px;text-align:center;">
  <span class="chip fa" style="background:{DEEP};">{icon("layers", 40, "#fff")}
    <span>هزاران هزار رفرنس</span></span></div>
{arrow_l(f"s{i}-ar", 372, 330, 90)}
<div id="s{i}-sk" class="card abs" style="left:0;top:200px;width:360px;height:340px;">
  <div id="s{i}-bulb" class="abs disc" style="left:110px;top:34px;width:140px;height:140px;
    background:{SOFT};">{icon("lightbulb", 76, DEEP)}</div>
  <div class="abs fa" style="left:20px;right:20px;top:196px;text-align:center;font-size:38px;
    line-height:1.45;">الهام برای<br/>اسکیل‌های دیگه</div>
</div>'''
    js = [f'inUp("#s{i}-h",{T(c["head"])});',
          f'pop("#s{i}-no",{T(c["no"])});',
          f'tl.from(".s{i}-ref",{{scale:0.5,autoAlpha:0,duration:0.26,ease:"back.out(1.5)",'
          f'stagger:0.07}},{T(c["refs"])});',
          f'pop("#s{i}-lab",{T(c["refs"] + 0.5)});',
          f'draw("#s{i}-ar .ink",{T(c["arrow"])},0.4);',
          f'inUp("#s{i}-sk",{T(c["skills"])});',
          f'tl.to("#s{i}-bulb",{{backgroundColor:"{YELLOW}",scale:1.08,duration:0.25,yoyo:true,'
          f'repeat:1}},{T(c["bulb"])});']
    return html, js


def sc_taste(i, s):
    """#2 Taste Skill: takes the site out of the 'AI-coded' look -> a site made for your brand."""
    c = s["cue"]
    cardsAI = "".join(
        f'<div class="abs disc" style="left:{56 + k * 172}px;top:262px;width:140px;height:100px;'
        f'border-radius:16px;background:rgba(255,255,255,.22);">{icon("sparkles", 44, "#fff")}</div>'
        for k in range(3))
    html = f'''{hdr(i, 2, "Taste Skill")}
<div id="s{i}-old" class="abs cx" style="top:110px;">
  <span class="chip fa" style="font-size:32px;padding:10px 28px;">{icon("history", 34, CREAM)}
    <span>همونی که چند ماه پیش معرفی کردم</span></span></div>
<div id="s{i}-site" class="abs" style="left:176px;top:200px;width:600px;height:400px;">
  <div id="s{i}-ai" class="abs mock" style="inset:0;background:linear-gradient(135deg,#7B5CFF,#B44CFF);">
    <div class="abs en" style="left:0;right:0;top:56px;text-align:center;font-size:40px;color:#fff;
      font-weight:700;">Welcome to Your App</div>
    <div class="abs en" style="left:0;right:0;top:114px;text-align:center;font-size:24px;
      color:rgba(255,255,255,.85);">The best solution for everything</div>
    <div class="abs" style="left:200px;top:168px;width:200px;height:52px;border-radius:26px;
      background:#fff;"></div>
    {cardsAI}
  </div>
  <div id="s{i}-new" class="abs mock" style="inset:0;background:#FFFDFA;">
    <div class="abs" style="left:0;right:0;top:0;height:64px;background:{INK};"></div>
    <div class="abs en" style="left:40px;top:96px;font-size:58px;font-weight:700;line-height:1.05;
      color:{INK};">Made for<br/>your brand.</div>
    <i class="abs" style="left:40px;top:236px;width:180px;height:14px;background:{ACCENT};"></i>
    <div class="abs" style="left:40px;top:290px;width:170px;height:62px;border-radius:12px;
      background:{INK};"></div>
    <div class="abs" style="left:350px;top:96px;width:210px;height:150px;border-radius:18px;
      background:{ACCENT};"></div>
    <div class="abs" style="left:350px;top:262px;width:100px;height:90px;border-radius:18px;
      background:{YELLOW};"></div>
    <div class="abs" style="left:462px;top:262px;width:98px;height:90px;border-radius:18px;
      background:{SKY};"></div>
  </div>
  <div class="abs" style="inset:0;border:4px solid {INK};border-radius:24px;"></div>
</div>
<div id="s{i}-tagai" class="abs" style="left:126px;top:170px;">
  <span class="chip en" style="background:{BAD};font-size:34px;padding:10px 26px;">
    {icon("bot", 38, "#fff")}<span>AI-coded</span></span></div>
<div id="s{i}-tagok" class="abs" style="left:126px;top:170px;">
  <span class="chip fa" style="background:{GOOD};font-size:34px;padding:10px 26px;">
    {icon("check", 38, "#fff", sw=3)}<span>خفن و مخصوصِ تو</span></span></div>
<div id="s{i}-brand" class="abs" style="left:640px;top:560px;">
  <span class="chip fa" style="background:{DEEP};font-size:34px;padding:10px 26px;">
    {icon("gem", 38, "#fff")}<span>برندِ تو</span></span></div>'''
    w = c["wipe"]
    js = [f'inUp("#s{i}-h",{T(c["head"])});',
          f'pop("#s{i}-old",{T(c["old"])});',
          f'inUp("#s{i}-site",{T(c["site"])});',
          f'tl.fromTo("#s{i}-new",{{clipPath:"inset(0% 0% 0% 100%)"}},'
          f'{{clipPath:"inset(0% 0% 0% 0%)",duration:0.6,ease:"power2.inOut"}},{T(w)});',
          f'pop("#s{i}-tagai",{T(c["ai"])});',
          f'tl.to("#s{i}-tagai",{{autoAlpha:0,duration:0.15}},{T(w)});',
          f'tl.set("#s{i}-tagai",{{autoAlpha:0}},{T(w + 0.15)});',
          f'pop("#s{i}-tagok",{T(w + 0.45)});',
          f'pop("#s{i}-brand",{T(c["brand"])});']
    return html, js


def sc_brandfit(i, s):
    """From all that inspiration, it picks what fits your brand and uses it."""
    c = s["cue"]
    cols = [ACCENT, SKY, YELLOW, LILAC, MINT, INK]
    good = [0, 2, 3]
    th, bd = [], []
    for k in range(6):
        r, q = divmod(k, 3)
        x = W - 150 - q * 166
        y = 150 + r * 150
        th.append(thumb(f"s{i}-r{k}", x, y, 150, 112, cols[k], f"s{i}-ref"))
        bd.append(badge(f"s{i}-b{k}", x + 112, y - 18, k in good, 52))
    sw = "".join(f'<i id="s{i}-sw{k}" class="abs" style="left:{40 + k * 98}px;top:250px;width:80px;'
                 f'height:80px;border-radius:50%;background:{cols[g]};border:4px solid #fff;'
                 f'box-shadow:0 0 0 3px {INK};"></i>' for k, g in enumerate(good))
    html = f'''
<h1 id="s{i}-title" class="fa title abs cx" style="top:0;font-size:54px;">چی به برندِ تو می‌خوره؟</h1>
{"".join(th)}{"".join(bd)}
{arrow_l(f"s{i}-ar", 380, 260, 82)}
<div id="s{i}-card" class="card abs" style="left:0;top:150px;width:370px;height:380px;">
  <div class="abs disc" style="left:125px;top:34px;width:120px;height:120px;background:{SOFT};">
    {icon("gem", 64, DEEP)}</div>
  <div class="abs fa" style="left:0;right:0;top:170px;text-align:center;font-size:42px;">برندِ تو</div>
  {sw}
</div>'''
    ck = c["check"]
    js = [f'inUp("#s{i}-title",{T(c["title"])});',
          f'tl.from(".s{i}-ref",{{scale:0.5,autoAlpha:0,duration:0.26,ease:"back.out(1.5)",'
          f'stagger:0.08}},{T(c["refs"])});',
          f'inUp("#s{i}-card",{T(c["card"])});']
    for k in range(6):
        js.append(f'pop("#s{i}-b{k}",{T(ck + k * 0.08)});')
    bad = ",".join(f"#s{i}-r{k}" for k in range(6) if k not in good)
    js += [f'tl.to("{bad}",{{opacity:0.35,duration:0.25}},{T(ck + 0.5)});',
           f'draw("#s{i}-ar .ink",{T(c["use"])},0.35);']
    js += [f'pop("#s{i}-sw{k}",{T(c["use"] + 0.35 + k * 0.12)});' for k in range(3)]
    return html, js


def sc_dsys(i, s):
    """...and finally hands you a complete design system."""
    c = s["cue"]
    sw = "".join(f'<i class="abs" style="left:{40 + k * 92}px;top:110px;width:72px;height:72px;'
                 f'border-radius:16px;background:{col};"></i>'
                 for k, col in enumerate([INK, ACCENT, DEEP, YELLOW, SKY]))
    html = f'''
<h1 id="s{i}-title" class="fa title abs cx" style="top:0;font-size:56px;">یه دیزاین سیستمِ کامل</h1>
<div id="s{i}-card" class="card abs" style="left:96px;top:120px;width:760px;height:420px;">
  <div class="abs en" style="left:40px;top:36px;font-size:32px;color:{MUTED};">Colors</div>
  {sw}
  <div class="abs en" style="left:540px;top:36px;font-size:32px;color:{MUTED};">Type</div>
  <div class="abs en" style="left:540px;top:90px;font-size:110px;font-weight:700;line-height:1;">Aa</div>
  <div class="abs" style="left:40px;top:220px;right:40px;height:3px;background:{LINE};"></div>
  <div class="abs en" style="left:40px;top:250px;font-size:32px;color:{MUTED};">Components</div>
  <div class="abs btn en" style="left:40px;top:306px;width:220px;height:74px;font-size:32px;
    background:{INK};color:{CREAM};">Button</div>
  <div class="abs btn en" style="left:282px;top:306px;width:220px;height:74px;font-size:32px;
    border:4px solid {INK};">Button</div>
  <div class="abs" style="left:530px;top:306px;width:190px;height:74px;border-radius:37px;
    background:{LINE};"><i class="abs disc" style="left:122px;top:6px;width:62px;height:62px;
    background:{ACCENT};"></i></div>
</div>
<div id="s{i}-ok" class="abs" style="left:812px;top:92px;">{badge(f"s{i}-okb", 0, 0, True, 84)}</div>'''
    js = [f'inUp("#s{i}-title",{T(c["title"])});',
          f'inUp("#s{i}-card",{T(c["card"])});',
          f'pop("#s{i}-ok",{T(c["done"])});']
    return html, js


def sc_img2code(i, s):
    """#3 Image to Code: give it a picture, get code back."""
    c = s["cue"]
    lines = [(SKY, 180), (YELLOW, 260), (MINT, 210), ("#F09A72", 300), (SKY, 150), (MINT, 240)]
    code = "".join(
        f'<i class="abs s{i}-ln" style="left:{40 + (24 if k in (1, 2, 3, 4) else 0)}px;'
        f'top:{96 + k * 40}px;width:{w}px;height:16px;border-radius:8px;background:{col};"></i>'
        for k, (col, w) in enumerate(lines))
    html = f'''{hdr(i, 3, "Image to Code")}
<div id="s{i}-img" class="card abs" style="left:560px;top:150px;width:392px;height:320px;overflow:hidden;">
  <div class="abs" style="left:0;right:0;top:0;height:60px;background:{SOFT};"></div>
  <div class="abs disc" style="left:136px;top:90px;width:120px;height:120px;background:{SOFT};">
    {icon("image", 66, DEEP)}</div>
  <div class="abs" style="left:40px;top:236px;width:180px;height:20px;border-radius:10px;background:{LINE};"></div>
  <div class="abs" style="left:40px;top:270px;width:120px;height:20px;border-radius:10px;background:{LINE};"></div>
</div>
<div id="s{i}-imgl" class="abs fa" style="left:560px;top:490px;width:392px;text-align:center;
  font-size:42px;">عکس</div>
{arrow_l(f"s{i}-ar", 440, 270, 110, ACCENT)}
<div id="s{i}-code" class="abs win" style="left:0;top:150px;width:430px;height:340px;">
  {winbar("index.html")}
  {code}
</div>
<div id="s{i}-codel" class="abs fa" style="left:0;top:510px;width:430px;text-align:center;
  font-size:42px;">کد</div>'''
    js = [f'inUp("#s{i}-h",{T(c["head"])});',
          f'inUp("#s{i}-img",{T(c["img"])});',
          f'inUp("#s{i}-imgl",{T(c["img"] + 0.1)});',
          f'draw("#s{i}-ar .ink",{T(c["img"] + 0.35)},0.35);',
          f'inUp("#s{i}-code",{T(c["code"])});',
          f'inUp("#s{i}-codel",{T(c["code"] + 0.1)});',
          f'tl.from(".s{i}-ln",{{scaleX:0,transformOrigin:"0 50%",duration:0.22,stagger:0.1,'
          f'ease:"power2.out"}},{T(c["code"] + 0.3)});']
    return html, js


def _mock(i: int, key: str, broken: bool) -> str:
    """A small UI card. broken=True: misaligned button, cramped padding, overflowing text."""
    if broken:
        inner = f'''
  <div class="abs" style="left:8px;top:8px;width:110px;height:110px;border-radius:14px;background:{SKY};"></div>
  <div class="abs en" style="left:134px;top:14px;font-size:40px;font-weight:700;white-space:nowrap;">Pricing Pla</div>
  <div class="abs" style="left:134px;top:74px;width:400px;height:16px;border-radius:8px;background:{LINE};"></div>
  <div class="abs" style="left:24px;top:150px;width:330px;height:16px;border-radius:8px;background:{LINE};"></div>
  <div class="abs" style="left:12px;top:180px;width:420px;height:16px;border-radius:8px;background:{LINE};"></div>
  <div class="abs btn en" style="left:250px;top:232px;width:220px;height:70px;font-size:30px;
    background:{ACCENT};color:#fff;transform:rotate(-4deg);">Buy now</div>'''
    else:
        inner = f'''
  <div class="abs" style="left:40px;top:40px;width:100px;height:100px;border-radius:20px;background:{SKY};"></div>
  <div class="abs en" style="left:168px;top:44px;font-size:40px;font-weight:700;">Pricing Plan</div>
  <div class="abs" style="left:168px;top:106px;width:300px;height:16px;border-radius:8px;background:{LINE};"></div>
  <div class="abs" style="left:40px;top:172px;width:440px;height:16px;border-radius:8px;background:{LINE};"></div>
  <div class="abs" style="left:40px;top:202px;width:360px;height:16px;border-radius:8px;background:{LINE};"></div>
  <div class="abs btn en" style="left:40px;top:244px;width:220px;height:70px;font-size:30px;
    background:{ACCENT};color:#fff;">Buy now</div>'''
    return (f'<div id="s{i}-{key}" class="card abs" style="left:412px;top:180px;width:540px;'
            f'height:350px;overflow:hidden;">{inner}</div>')


def sc_claudealone(i, s):
    """Doesn't Claude do this itself? It does -- but misses details, padding, margin."""
    c = s["cue"]

    def tag(key, y, ic, label, en=False):
        cls = "en" if en else "fa"
        return (f'<div id="s{i}-{key}" class="abs" style="left:0;top:{y}px;">'
                f'<span class="chip {cls}" style="background:{BAD};font-size:34px;padding:12px 26px;">'
                f'{icon(ic, 38, "#fff")}<span>{label}</span></span></div>')
    html = f'''
<h1 id="s{i}-title" class="fa title abs cx" style="top:0;font-size:52px;">خودِ <span class="en">Claude</span> این کارو نمی‌کنه؟</h1>
<div id="s{i}-yes" class="abs cx" style="top:88px;">
  <span class="chip fa" style="font-size:34px;padding:10px 28px;">چرا، می‌کنه... ولی</span></div>
{_mock(i, "mock", True)}
<svg id="s{i}-pad" class="abs" viewBox="0 0 540 350" fill="none" stroke="{BAD}" stroke-width="5"
  stroke-linecap="round" style="left:412px;top:180px;width:540px;height:350px;">
  <path pathLength="1" class="ink" d="M4 120 V176 M-2 128 L4 120 L10 128 M-2 168 L4 176 L10 168"/>
  <circle pathLength="1" class="ink" cx="360" cy="268" r="140"/></svg>
{tag("t1", 200, "eye-off", "دیتیل‌ها رو نمی‌بینه")}
{tag("t2", 300, "triangle-alert", "اشتباه می‌کنه")}
{tag("t3", 400, "ruler", "padding / margin", en=True)}'''
    js = [f'inUp("#s{i}-title",{T(c["title"])});',
          f'pop("#s{i}-yes",{T(c["yes"])});',
          f'inUp("#s{i}-mock",{T(c["mock"])});',
          f'pop("#s{i}-t1",{T(c["details"])});',
          f'pop("#s{i}-t2",{T(c["mistakes"])});',
          f'draw("#s{i}-pad circle",{T(c["mistakes"] + 0.2)},0.45);',
          f'pop("#s{i}-t3",{T(c["padding"])});',
          f'draw("#s{i}-pad path",{T(c["padding"] + 0.2)},0.35);']
    return html, js


def sc_fixed(i, s):
    """This skill is made so Claude stops making those mistakes."""
    c = s["cue"]
    html = f'''
<h1 id="s{i}-title" class="fa title abs cx" style="top:0;font-size:52px;">
  <span class="en">Image to Code</span> مخصوصِ همینه</h1>
{_mock(i, "bad", True)}
{_mock(i, "good", False)}
<div id="s{i}-ok" class="abs" style="left:0;top:220px;">
  <span class="chip fa" style="background:{GOOD};font-size:36px;padding:14px 28px;">
    {icon("circle-check", 40, "#fff")}<span>بدون اشتباه</span></span></div>
{badge(f"s{i}-okb", 900, 150, True, 80)}'''
    f = c["fix"]
    js = [f'inUp("#s{i}-title",{T(c["title"])});',
          f'tl.fromTo("#s{i}-good",{{clipPath:"inset(0% 0% 0% 100%)"}},'
          f'{{clipPath:"inset(0% 0% 0% 0%)",duration:0.6,ease:"power2.inOut"}},{T(f)});',
          f'pop("#s{i}-okb",{T(f + 0.6)});',
          f'pop("#s{i}-ok",{T(c["chip"])});']
    return html, js


def sc_like(i, s):
    c = s["cue"]
    html = f'''
<div id="s{i}-heart" class="abs stack" style="left:346px;top:40px;width:260px;height:260px;">
  {icon("heart", 260, INK, sw=1.6)}
  {icon("heart", 260, IG_RED, fill=True, cls="fillon", extra="position:absolute;left:0;top:0;")}</div>
<div id="s{i}-txt" class="abs cx fa" style="top:350px;font-size:70px;font-weight:800;">حتماً لایک کن</div>
<div id="s{i}-sub" class="abs cx fa" style="top:470px;font-size:40px;color:{MUTED};">اگه تا اینجا دیدی</div>'''
    js = [f'pop("#s{i}-heart",{T(c["heart"])});',
          f'inUp("#s{i}-sub",{T(c["heart"] + 0.15)});',
          f'inUp("#s{i}-txt",{T(c["txt"])});',
          f'tl.set("#s{i}-heart .fillon",{{autoAlpha:0,scale:0.4}},{T(s["start"])});',
          f'tl.to("#s{i}-heart .fillon",{{autoAlpha:1,scale:1,duration:0.25,ease:"back.out(1.6)"}},'
          f'{T(c["like"])});',
          f'tl.to("#s{i}-heart",{{scale:1.12,duration:0.15,yoyo:true,repeat:1}},{T(c["like"] + 0.2)});']
    return html, js


def sc_wdg(i, s):
    """#4 Web Design Guidelines: reviews Claude's build -- what's right, what's not."""
    c = s["cue"]
    rows = [("Spacing", True), ("Contrast", False), ("Alignment", True), ("Mobile layout", False)]
    out = []
    for k, (lab, ok) in enumerate(rows):
        y = 92 + k * 78
        out.append(f'''
  <div id="s{i}-r{k}" class="abs row en" style="left:36px;right:36px;top:{y}px;height:64px;gap:18px;
    font-size:36px;"><i class="dot" style="width:16px;height:16px;background:{MUTED};"></i>{lab}</div>
  {badge(f"s{i}-b{k}", 560, y + 4, ok, 56)}''')
    html = f'''{hdr(i, 4, "Web Design Guidelines", 52)}
<div id="s{i}-card" class="card abs" style="left:136px;top:130px;width:680px;height:420px;">
  <div class="abs row en" style="left:36px;top:24px;gap:16px;font-size:34px;color:{MUTED};">
    {icon("scan-search", 40, MUTED)}<span>Design review</span></div>
  {"".join(out)}
</div>
<div id="s{i}-chip" class="abs cx" style="top:584px;">
  <span class="chip fa" style="font-size:34px;padding:10px 28px;">چی درسته، چی نه</span></div>'''
    js = [f'inUp("#s{i}-h",{T(c["head"])});',
          f'inUp("#s{i}-card",{T(c["card"])});']
    js += [f'tl.from("#s{i}-r{k}",{{x:30,autoAlpha:0,duration:0.25}},{T(c["card"] + 0.3 + k * 0.12)});'
           for k in range(4)]
    for k, (_, ok) in enumerate(rows):
        js.append(f'pop("#s{i}-b{k}",{T((c["right"] if ok else c["wrong"]) + k * 0.06)});')
    js.append(f'pop("#s{i}-chip",{T(c["right"])});')
    return html, js


def sc_todo(i, s):
    """It writes Claude a to-do list, Claude redoes them -- no need to check by hand."""
    c = s["cue"]
    items = ["Fix contrast", "Fix mobile layout", "Re-check spacing"]
    rows = []
    for k, lab in enumerate(items):
        y = 96 + k * 76
        rows.append(f'''
  <div class="abs row en" style="left:36px;top:{y}px;gap:20px;font-size:36px;">
    <span class="stack" style="width:48px;height:48px;border:4px solid {INK};border-radius:10px;">
      <span id="s{i}-c{k}" class="abs" style="left:2px;top:2px;">{icon("check", 36, GOOD, sw=3.5)}</span></span>
    <span id="s{i}-l{k}">{lab}</span></div>''')
    html = f'''
<h1 id="s{i}-title" class="fa title abs cx" style="top:0;font-size:54px;">یه <span class="en">To-Do List</span> برای <span class="en">Claude</span></h1>
<div id="s{i}-card" class="card abs" style="left:236px;top:110px;width:600px;height:360px;">
  <div class="abs row en" style="left:36px;top:24px;gap:16px;font-size:34px;color:{MUTED};">
    {icon("list-todo", 40, MUTED)}<span>todo.md</span></div>
  {"".join(rows)}
</div>
<div id="s{i}-bot" class="abs disc" style="left:80px;top:160px;width:130px;height:130px;background:{DEEP};">
  {icon("bot", 72, "#fff")}</div>
<div id="s{i}-chip" class="abs cx" style="top:520px;">
  <span class="chip fa" style="background:{GOOD};">{icon("eye-off", 42, "#fff")}
    <span>لازم نیست خودت چک کنی</span></span></div>'''
    js = [f'inUp("#s{i}-title",{T(c["title"])});',
          f'inUp("#s{i}-card",{T(c["card"])});',
          f'pop("#s{i}-bot",{T(c["bot"])});',
          f'tl.to("#s{i}-bot",{{rotation:-8,duration:0.18,yoyo:true,repeat:3}},{T(c["bot"] + 0.35)});']
    for k in range(3):
        t = c["ticks"] + k * 0.35
        js.append(f'tl.from("#s{i}-c{k}",{{scale:0,autoAlpha:0,duration:0.2,ease:"back.out(2)"}},{T(t)});')
        js.append(f'tl.to("#s{i}-l{k}",{{opacity:0.45,duration:0.2}},{T(t + 0.1)});')
    js.append(f'pop("#s{i}-chip",{T(c["chip"])});')
    return html, js


def sc_playwright(i, s):
    """#5 Playwright CLI: opens the browser, clicks and tests everything, checks every device."""
    c = s["cue"]

    def dev(key, y, ic, label):
        return f'''
<div id="s{i}-{key}" class="card abs row fa" style="left:652px;top:{y}px;width:300px;height:118px;
  padding:0 22px;gap:18px;font-size:36px;">{icon(ic, 58, INK)}<span>{label}</span>
  <span id="s{i}-{key}k" style="margin-right:auto;">{icon("circle-check", 46, GOOD)}</span></div>'''
    html = f'''{hdr(i, 5, "Playwright CLI")}
<div id="s{i}-win" class="abs win" style="left:0;top:130px;width:620px;height:440px;background:#FFFDFA;
  border:4px solid {INK};">
  {winbar("localhost:3000")}
  <div class="abs" style="left:40px;top:100px;width:300px;height:26px;border-radius:13px;background:{INK};"></div>
  <div class="abs" style="left:40px;top:146px;width:440px;height:16px;border-radius:8px;background:{LINE};"></div>
  <div class="abs" style="left:40px;top:176px;width:380px;height:16px;border-radius:8px;background:{LINE};"></div>
  <div id="s{i}-btn" class="abs btn en" style="left:40px;top:226px;width:220px;height:70px;font-size:30px;
    background:{ACCENT};color:#fff;">Sign up</div>
  <div id="s{i}-ok" class="abs row en" style="left:40px;top:330px;gap:12px;font-size:32px;color:{GOOD};">
    {icon("circle-check", 40, GOOD)}<span>All tests passed</span></div>
  <div id="s{i}-cur" class="abs" style="left:200px;top:258px;">
    {icon("mouse-pointer-2", 60, INK, fill=True, extra="filter:drop-shadow(0 4px 6px rgba(0,0,0,.3));")}</div>
</div>
{dev("ph", 130, "smartphone", "موبایل")}
{dev("tb", 270, "tablet", "تبلت")}
{dev("dt", 410, "monitor", "دسکتاپ")}'''
    k = c["click"]
    js = [f'inUp("#s{i}-h",{T(c["head"])});',
          f'inUp("#s{i}-win",{T(c["browser"])});',
          f'tl.from("#s{i}-cur",{{x:260,y:120,autoAlpha:0,duration:0.4,ease:"power2.out"}},{T(k - 0.45)});',
          f'tl.to("#s{i}-btn",{{scale:0.9,duration:0.1,yoyo:true,repeat:1}},{T(k)});',
          f'tl.from("#s{i}-ok",{{y:16,autoAlpha:0,duration:0.25}},{T(c["test"])});',
          f'inUp("#s{i}-ph",{T(c["phone"])});',
          f'inUp("#s{i}-tb",{T(c["tablet"])});',
          f'inUp("#s{i}-dt",{T(c["desktop"])});']
    js += [f'pop("#s{i}-{d}k",{T(c["check"] + n * 0.12)});' for n, d in enumerate(["ph", "tb", "dt"])]
    return html, js


def sc_report(i, s):
    """Claude tests too but still has issues; this skill checks everything precisely."""
    c = s["cue"]

    def col(key, x, title, results, en_title=True):
        rows = []
        for k, ok in enumerate(results):
            y = 96 + k * 62
            rows.append(f'''
    <div class="abs" style="left:30px;top:{y + 18}px;width:300px;height:18px;border-radius:9px;
      background:{LINE};"></div>
    {badge(f"s{i}-{key}{k}", 356, y + 2, ok, 50)}''')
        return f'''
<div id="s{i}-{key}" class="card abs" style="left:{x}px;top:110px;width:450px;height:420px;">
  <div class="abs {"en" if en_title else "fa"}" style="left:0;right:0;top:26px;text-align:center;
    font-size:38px;font-weight:700;">{title}</div>
  {"".join(rows)}
</div>'''
    alone = [True, False, True, False, True]
    html = f'''
<h1 id="s{i}-title" class="fa title abs cx" style="top:0;font-size:52px;">خودِ <span class="en">Claude</span> هم تست می‌کنه، ولی...</h1>
{col("a", 502, "Claude", alone)}
{col("b", 0, "+ Playwright CLI", [True] * 5)}
<div id="s{i}-chip" class="abs cx" style="top:566px;">
  <span class="chip fa" style="background:{GOOD};">{icon("circle-check", 42, "#fff")}
    <span>همه‌چیز درست کار می‌کنه</span></span></div>'''
    js = [f'inUp("#s{i}-title",{T(c["title"])});',
          f'inUp("#s{i}-a",{T(c["a"])});']
    js += [f'pop("#s{i}-a{k}",{T((c["issues"] if not ok else c["a"] + 0.4) + k * 0.1)});'
           for k, ok in enumerate(alone)]
    js += [f'inUp("#s{i}-b",{T(c["b"])});']
    js += [f'pop("#s{i}-b{k}",{T(c["exact"] + k * 0.12)});' for k in range(5)]
    js += [f'pop("#s{i}-chip",{T(c["chip"])});']
    return html, js


def sc_nomanual(i, s):
    """No need to open the browser yourself to see what works and what doesn't."""
    c = s["cue"]
    html = f'''
<h1 id="s{i}-title" class="fa title abs cx" style="top:0;font-size:54px;">دیگه لازم نیست خودت تست کنی</h1>
<div id="s{i}-me" class="card abs" style="left:532px;top:130px;width:420px;height:400px;">
  <div class="abs disc" style="left:130px;top:46px;width:160px;height:160px;background:#F6DEDA;">
    {icon("mouse-pointer-click", 84, BAD)}</div>
  <div class="abs fa" style="left:0;right:0;top:236px;text-align:center;font-size:40px;">تستِ دستی</div>
  <div class="abs fa" style="left:0;right:0;top:300px;text-align:center;font-size:30px;color:{MUTED};">
    کلیک‌به‌کلیک توی مرورگر</div>
  <svg id="s{i}-x" class="abs" viewBox="0 0 420 400" fill="none" stroke="{BAD}" stroke-width="13"
    stroke-linecap="round" style="left:0;top:0;width:420px;height:400px;">
    <path pathLength="1" class="ink" d="M50 50 L370 350"/><path pathLength="1" class="ink" d="M370 50 L50 350"/></svg>
</div>
<div id="s{i}-bot" class="card abs" style="left:0;top:130px;width:420px;height:400px;border-color:{GOOD};">
  <div class="abs disc" style="left:130px;top:46px;width:160px;height:160px;background:#DDF0E6;">
    {icon("bot", 84, GOOD)}</div>
  <div class="abs en" style="left:0;right:0;top:236px;text-align:center;font-size:40px;font-weight:700;">Playwright CLI</div>
  <div class="abs fa" style="left:0;right:0;top:300px;text-align:center;font-size:30px;color:{MUTED};">
    خودش انجامش می‌ده</div>
</div>'''
    js = [f'inUp("#s{i}-title",{T(c["title"])});',
          f'inUp("#s{i}-me",{T(c["me"])});',
          f'draw("#s{i}-x .ink",{T(c["strike"])},0.3);',
          f'tl.to("#s{i}-me",{{opacity:0.55,duration:0.3}},{T(c["strike"] + 0.35)});',
          f'inUp("#s{i}-bot",{T(c["bot"])});']
    return html, js


def sc_comment(i, s):
    """Comment the word 'اسکیل' and I'll send you all five."""
    c = s["cue"]
    icons = ["palette", "sparkles", "image", "list-checks", "monitor-play"]
    tiles = "".join(
        f'<div id="s{i}-p{k}" class="card abs disc" style="left:{W - 26 - 150 - k * 172}px;top:400px;'
        f'width:150px;height:150px;border-radius:30px;">{icon(icons[k], 70, DEEP)}</div>'
        for k in range(5))
    html = f'''
<div id="s{i}-cm" class="abs" style="left:26px;top:0;width:900px;height:340px;">
  <div class="abs" style="left:0;top:0;width:900px;height:290px;border-radius:44px;background:{DEEP};
    box-shadow:0 14px 0 rgba(32,36,47,.14);"></div>
  <div class="abs" style="left:120px;top:268px;width:0;height:0;border-left:30px solid transparent;
    border-right:30px solid transparent;border-top:52px solid {DEEP};"></div>
  <div id="s{i}-w" class="abs fa" style="left:30px;top:15px;width:390px;height:260px;font-size:136px;
    color:#fff;line-height:260px;text-align:center;">اسکیل</div>
  <div class="abs fa" style="right:56px;top:60px;width:380px;text-align:right;font-size:76px;
    color:#fff;line-height:1.3;">کامنت کن</div>
  <div class="abs fa" style="right:56px;top:180px;width:440px;text-align:right;font-size:34px;
    color:#FBE3D6;white-space:nowrap;">تا هر ۵ تا رو برات بفرستم</div>
</div>
{tiles}'''
    js = [f'tl.from("#s{i}-cm",{{y:60,autoAlpha:0,scale:0.9,duration:0.4,ease:"power3.out"}},{T(c["bub"])});']
    js += [f'pop("#s{i}-p{k}",{T(c["five"] + k * 0.1)});' for k in range(5)]
    js += [f'tl.from("#s{i}-w",{{scale:0.3,autoAlpha:0,duration:0.32,ease:"back.out(1.7)"}},{T(c["word"])});',
           f'tl.to("#s{i}-w",{{scale:1.1,duration:0.2,ease:"sine.inOut",yoyo:true,repeat:1}},'
           f'{T(c["word"] + 0.4)});']
    return html, js


def sc_follow(i, s):
    """Liked it and want more on programming & AI -> follow. Handle text only, no avatar."""
    c = s["cue"]
    h = s["handle"]
    html = f'''
<div id="s{i}-k" class="abs cx" style="top:0;">
  <span class="chip fa" style="font-size:38px;">{icon("code-xml", 40, CREAM)}
    <span>برنامه‌نویسی و <span class="en">AI</span></span></span></div>
<div id="s{i}-card" class="card abs" style="left:26px;top:110px;width:900px;height:300px;">
  <div class="abs en" style="left:0;right:0;top:48px;text-align:center;font-size:68px;
    font-weight:700;">@{h}</div>
  <div id="s{i}-fol" class="abs btn en" style="left:285px;top:164px;background:{IG_BLUE};
    color:#fff;">Follow</div>
  <div id="s{i}-foling" class="abs btn en row" style="left:285px;top:164px;background:#EFEFEF;
    color:{INK};gap:12px;justify-content:center;visibility:hidden;">{icon("check", 40, INK, sw=3)}Following</div>
  <div id="s{i}-cur" class="abs" style="left:500px;top:196px;">
    {icon("mouse-pointer-2", 70, INK, fill=True, extra="filter:drop-shadow(0 4px 6px rgba(0,0,0,.3));")}</div>
</div>
<div id="s{i}-row" class="abs row" style="left:0;right:0;top:450px;justify-content:center;gap:110px;">
  <span class="act">
    <span class="stack" style="width:84px;height:84px;">{icon("heart", 84, INK)}
      {icon("heart", 84, IG_RED, fill=True, cls="fillon", extra="position:absolute;left:0;top:0;")}</span>
    <span class="fa">لایک</span></span>
  <span class="act">
    <span class="stack" style="width:84px;height:84px;">{icon("message-circle", 84, INK)}</span>
    <span class="fa">کامنت</span></span>
  <span class="act">
    <span class="stack" style="width:84px;height:84px;">{icon("bookmark", 84, INK)}</span>
    <span class="fa">سیو</span></span>
</div>'''
    f = c["follow"]
    js = [f'inUp("#s{i}-card",{T(c["card"])});',
          f'tl.from("#s{i}-row .act",{{y:24,autoAlpha:0,duration:0.3,stagger:0.08,ease:"power3.out"}},'
          f'{T(c["row"])});',
          f'tl.set("#s{i}-row .fillon",{{autoAlpha:0,scale:0.4}},{T(s["start"])});',
          f'tl.to("#s{i}-row .fillon",{{autoAlpha:1,scale:1,duration:0.25,ease:"back.out(1.6)"}},'
          f'{T(c["like"])});',
          f'pop("#s{i}-k",{T(c["k"])});',
          f'tl.from("#s{i}-cur",{{x:240,y:120,autoAlpha:0,duration:0.35,ease:"power2.out"}},{T(f - 0.35)});',
          f'tl.to("#s{i}-fol",{{scale:0.92,duration:0.08}},{T(f + 0.02)});',
          f'tl.set("#s{i}-fol",{{autoAlpha:0}},{T(f + 0.1)});',
          f'tl.set("#s{i}-foling",{{autoAlpha:1}},{T(f + 0.1)});',
          f'tl.from("#s{i}-foling",{{scale:0.92,duration:0.16,ease:"power2.out",immediateRender:false}},'
          f'{T(f + 0.1)});',
          f'tl.to("#s{i}-cur",{{autoAlpha:0,duration:0.2}},{T(f + 0.3)});']
    return html, js


RENDER = {"hook": sc_hook, "notthese": sc_notthese, "order": sc_order, "awesome": sc_awesome,
          "taste": sc_taste, "brandfit": sc_brandfit, "dsys": sc_dsys, "img2code": sc_img2code,
          "claudealone": sc_claudealone, "fixed": sc_fixed, "like": sc_like, "wdg": sc_wdg,
          "todo": sc_todo, "playwright": sc_playwright, "report": sc_report,
          "nomanual": sc_nomanual, "comment": sc_comment, "follow": sc_follow}


CSS = """
.thumb{background:#FFFDFA;border:3px solid #20242F;border-radius:14px;overflow:hidden;}
.mock{border-radius:24px;overflow:hidden;}
.win{background:#2A2F3B;border-radius:26px;overflow:hidden;box-shadow:0 14px 0 rgba(32,36,47,.12);}
.winbar{position:absolute;left:0;right:0;top:0;height:62px;background:#20242F;color:#F7EEE7;
  padding:0 24px;font-size:28px;gap:10px;}
"""
