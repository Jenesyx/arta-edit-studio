"""Worked example for /reel-story -- the Stoodi founder story + invite (Oct 2026).

An 82.6 s Farsi take by Arta Bidkhori: where the Stoodi idea came from, what it
does (learn / teach / earn), nine months in, first event, a rep at every
German university, comment JOIN. 25 scenes, ~25 % B-roll, 6 depth moments.

Read it as a catalogue, then copy it to tools/story_<slug>.py and replace NAME,
the B-roll picks and the scenes. It will not run as-is on your machine: it
expects the original take, the creator's B-roll clips (IMG_*.MOV) and a mascot
folder whose files are named owl-wave.png, owl-think.png, owl-sad.png,
owl-party.png, owl-angry.png, owl-head.png, owl-flat.png, owl-welcome.png, plus
brand.mascot_crops for owl-hero / owl-stressed / owl-teacher (from a character
sheet) and brand.logo.

Cue times are absolute on the take's own timeline, pinned to spoken words in
work/<take>/transcript.json.
"""

from __future__ import annotations

import math
import random

from story_build import *  # noqa: F401,F403 -- palette, pieces, Comp, effects

NAME = "stoodi-inviteraw"
DUR = 82.6
FACE = (500, 800)        # face centre in the take; the camera pivots here

# out name -> (source clip, media start s, source duration s, speed)
BROLL = {
    "street":   ("IMG_7287.MOV", 0.5, 1.2, 1.0),
    "lab":      ("IMG_6337.MOV", 0.2, 1.3, 1.0),
    "lecture":  ("IMG_7339.MOV", 0.0, 7.4, 3.0),
    "home":     ("IMG_5180.MOV", 7.3, 2.5, 1.0),
    "library":  ("IMG_6436.MOV", 2.5, 2.6, 1.0),
    "tutor":    ("IMG_6353.MOV", 17.5, 3.8, 1.0),
    "m-figma":  ("IMG_5190.MOV", 1.0, 0.6, 1.0),
    "m-db":     ("IMG_5191.MOV", 3.0, 0.6, 1.0),
    "m-board":  ("IMG_5187.MOV", 2.0, 0.6, 1.0),
    "m-claude": ("IMG_4542.MOV", 1.0, 0.6, 1.0),
    "m-keys":   ("IMG_5182.MOV", 10.0, 0.7, 1.0),
    "event":    ("IMG_7814.MOV", 0.2, 3.9, 1.0),   # mirrored selfie: flipped in trim()
    "train":    ("IMG_6384.MOV", 1.0, 2.9, 1.0),
}

# front-camera clips whose on-screen text (the Stoodi banner) reads backwards
MIRRORED = {"event"}

# mosaic tile stills: (clip, time)
TILES = [("IMG_6440.MOV", 2.0), ("IMG_5181.MOV", 6.0), ("IMG_6393.MOV", 4.0),
         ("IMG_6323.MOV", 12.0), ("IMG_5182.MOV", 20.0), ("IMG_7339.MOV", 3.0),
         ("IMG_6436.MOV", 30.0), ("IMG_5188.MOV", 1.0), ("IMG_6421.MOV", 4.0),
         ("IMG_7287.MOV", 2.5), ("IMG_6337.MOV", 5.8), ("IMG_5184.MOV", 6.0),
         ("IMG_7814.MOV", 3.6), ("IMG_6353.MOV", 3.0), ("IMG_5180.MOV", 1.0),
         ("IMG_5185.MOV", 9.0)]


# ------------------------------------------------------------------- scenes ---

def hook(c: Comp):
    """0-3.6  map of Germany behind the speaker, pins, one pin, 'تو'."""
    p = projector(1300, 70, 250)
    pins = []
    for k, (lat, lon) in enumerate(UNIS):
        x, y = p(lat, lon)
        pid = ' id="h-one"' if k == BERLIN else ""
        pins.append(f'<i{pid} class="pin h-pin" style="left:{x - 13:.0f}px;top:{y - 13:.0f}px;"></i>')
    random.Random(2).shuffle(pins)          # scattered pop order with a plain stagger
    bx, by = p(*UNIS[BERLIN])
    inner = f'''
<div class="flood" style="background:radial-gradient(circle at 50% 36%,#3B1D9A 0%,#1A0E4D 60%,#0C0628 100%);"></div>
<div class="flood dots"></div>
<svg class="abs" style="left:0;top:0;" width="1080" height="1920" viewBox="0 0 1080 1920">
  <path id="h-map" d="{de_path(p)}" pathLength="1" class="ink" fill="{LILAC}" fill-opacity="0"
    stroke="{LILAC}" stroke-width="8" stroke-linejoin="round"/></svg>
{"".join(pins)}
<i id="h-ring1" class="ring" style="left:{bx - 60:.0f}px;top:{by - 60:.0f}px;"></i>
<i id="h-ring2" class="ring" style="left:{bx - 60:.0f}px;top:{by - 60:.0f}px;"></i>
<div id="h-me" class="disc abs" style="left:{bx - 46:.0f}px;top:{by - 46:.0f}px;width:92px;height:92px;
  background:{YELLOW};border:6px solid #fff;">{icon("user", 50, INK, sw=2.6)}</div>
<div id="h-you" class="abs fa" style="left:0;right:0;top:70px;text-align:center;font-size:420px;
  line-height:1.1;color:{YELLOW};text-shadow:0 16px 0 {IRIS};">تو</div>'''
    c.clip("behind", "h", 0, 3.62, inner, 2)
    c.matte(1, 0, 3.62)
    c.j('draw("#h-map",0.05,0.9);',
        'tl.to("#h-map",{attr:{"fill-opacity":0.16},duration:0.4},0.7);',
        'tl.fromTo(".h-pin",{scale:0,autoAlpha:0},{scale:1,autoAlpha:1,duration:0.22,'
        'ease:"back.out(2.5)",stagger:0.016},0.3);',
        'tl.to(".h-pin:not(#h-one)",{opacity:0.22,duration:0.25},1.14);',
        'pop("#h-me",1.2,{duration:0.35});',
        'tl.fromTo(["#h-ring1","#h-ring2"],{scale:0.3,opacity:0.9},{scale:2.4,opacity:0,'
        'duration:0.8,ease:"power1.out",stagger:0.4,repeat:1},1.25);',
        'tl.to(["#h-map",".h-pin","#h-me"],{opacity:0.25,duration:0.2},2.82);',
        'tl.fromTo("#h-you",{scale:1.9,autoAlpha:0},{scale:1,autoAlpha:1,duration:0.3,'
        'ease:"power4.out"},2.86);',
        # VHS glitch-out into the rewind
        'tl.set("#h-i",{opacity:0.35,x:-18},3.26);', 'tl.set("#h-i",{opacity:1,x:10},3.31);',
        'tl.set("#h-i",{opacity:0.5,x:-8},3.36);', 'tl.set("#h-i",{opacity:0.15,x:22},3.42);',
        'tl.set("#h-i",{opacity:0.6,x:0},3.47);', 'tl.to("#h-i",{opacity:0,duration:0.1},3.5);',
        'tl.fromTo("#cam",{scale:1},{scale:1.05,duration:3.2,ease:"sine.inOut"},0);')


def rewind(c: Comp):
    """3.26-4.95  VHS rewind into the story."""
    lines = "".join(f'<i class="scan" style="top:{y}px;"></i>' for y in range(0, 1920, 8))
    inner = f'''
<div class="flood" style="opacity:.55;">{lines}</div>
<div id="rw-chip" class="abs row en" style="left:70px;top:190px;gap:16px;font-size:58px;color:#fff;
  text-shadow:3px 0 0 rgba(255,0,80,.7),-3px 0 0 rgba(0,220,255,.7);">{icon("rewind", 70, "#fff", fill=True)}REWIND</div>
<div id="rw-bar" class="abs" style="left:0;top:0;width:1080px;height:150px;background:rgba(255,255,255,.08);"></div>'''
    c.clip("fx", "rw", 3.26, 4.95, inner, 7)
    c.j('tl.fromTo("#rw-chip",{autoAlpha:0},{autoAlpha:1,duration:0.05,repeat:6,yoyo:true},3.4);',
        'tl.fromTo("#rw-bar",{y:-160},{y:1940,duration:0.7,ease:"none",repeat:1},3.3);',
        'tl.to("#cam",{x:16,duration:0.04,yoyo:true,repeat:7,ease:"none"},3.26);',
        'tl.set("#cam",{x:0},3.6);',
        'flash(4.9);')


def arrival(c: Comp):
    """4.95-7.05  came to Germany (street) -> started Informatik (lab)."""
    c.broll("street", 4.95, 6.0)
    c.broll("lab", 6.0, 7.05, 0.1)
    loc = stk("ar-loc", 0, 1300, icon("map-pin", 62, PURPLE, fill=True) +
              en("Deutschland", 58, PURPLE), "cx")
    inf = stk("ar-inf", 0, 1320, icon("laptop", 62, "#fff") + en("Informatik", 58, "#fff"), "cx p")
    c.clip("over", "ar", 4.95, 7.05, loc + inf, 5)
    c.j('gsap.set("#ar-loc",{rotation:-4});', 'gsap.set("#ar-inf",{rotation:3});',
        'pop("#ar-loc",5.38);', 'out("#ar-loc",5.92,0.08);',
        'tl.fromTo("#bw-lab",{y:1920,filter:"blur(20px)"},{y:0,filter:"blur(0px)",duration:0.2,'
        'ease:"power3.out"},6.0);',
        'pop("#ar-inf",6.08);',
        'tl.to("#cam",{scale:1,duration:0.01},7.0);',
        # speaker beat after: punch on "فهمیدم"
        'tl.to("#cam",{scale:1.1,duration:0.22,ease:"power3.out"},7.84);')


def lecture(c: Comp):
    """8.55-11.02  lecture at 3x: fast-forward badge, speed lines, speedometer."""
    c.broll("lecture", 8.55, 11.02)
    lines = []
    rnd = random.Random(7)
    for k in range(14):
        y = rnd.randint(150, 1750)
        w = rnd.randint(180, 520)
        lines.append(f'<i class="spd" style="top:{y}px;width:{w}px;left:1100px;"></i>')
    c.clip("fx", "lsp", 8.55, 11.02, "".join(lines), 7)
    ff = stk("lc-ff", 740, 200, icon("fast-forward", 54, YELLOW, fill=True) + en("3x", 56, "#fff"),
             "ink")
    # gauge: centre (300,300) radius 230, -90..+90 deg
    def arc(a0, a1, col):
        r, cx, cy = 230, 300, 300
        x0, y0 = cx + r * math.sin(math.radians(a0)), cy - r * math.cos(math.radians(a0))
        x1, y1 = cx + r * math.sin(math.radians(a1)), cy - r * math.cos(math.radians(a1))
        return (f'<path d="M{x0:.1f} {y0:.1f} A{r} {r} 0 0 1 {x1:.1f} {y1:.1f}" stroke="{col}" '
                f'stroke-width="38" fill="none"/>')
    gauge = f'''
<div id="lc-g" class="crd" style="left:230px;top:1150px;width:620px;height:420px;">
  <svg class="abs" style="left:10px;top:10px;" width="600" height="340" viewBox="0 0 600 340">
    {arc(-90, -32, "#22C55E")}{arc(-28, 28, YELLOW)}{arc(32, 90, RED)}
  </svg>
  <div id="lc-needle" class="abs" style="left:302px;top:96px;width:16px;height:220px;border-radius:8px;
    background:{INK};transform-origin:8px 214px;"></div>
  <div class="abs disc" style="left:286px;top:286px;width:48px;height:48px;background:{INK};"></div>
  <div class="abs row" style="left:0;right:0;top:342px;justify-content:center;gap:18px;">
    <span class="flag"><i style="background:#111"></i><i style="background:#DD0000"></i><i style="background:#FFCE00"></i></span>
    {fa("سرعت آلمانی", 52, INK)}</div>
</div>'''
    stressed = owl("lc-owl", "owl-stressed", 800, 1010, 240)
    c.clip("over", "lc", 8.55, 11.02, ff + gauge + stressed, 5)
    c.j('tl.to("#cam",{scale:1,duration:0.01},8.55);',
        'tl.fromTo("#bw-lecture",{scale:1.35,filter:"blur(14px)"},{scale:1,filter:"blur(0px)",'
        'duration:0.3,ease:"power3.out"},8.55);',
        'pop("#lc-ff",8.7);',
        'tl.to("#lc-ff",{scale:1.12,duration:0.18,yoyo:true,repeat:5,ease:"sine.inOut"},9.1);',
        'tl.fromTo("#lsp-i .spd",{x:0},{x:-1900,duration:0.42,ease:"none",repeat:5,'
        'stagger:0.06},8.6);',
        'inUp("#lc-g",9.9);',
        'tl.fromTo("#lc-needle",{rotation:-84},{rotation:78,duration:0.5,ease:"power4.in"},10.1);',
        'tl.to("#lc-needle",{rotation:70,duration:0.06,yoyo:true,repeat:5},10.6);',
        'pop("#lc-owl",10.3);',
        'flash(10.98);')


def home(c: Comp):
    """11.02-15.0  home: learning bar fills then drains to 0, sad owl."""
    c.broll("home", 11.02, 13.34)
    card = f'''
<div id="hm-c" class="crd" style="left:110px;top:210px;width:860px;height:200px;">
  <div class="abs row" style="right:40px;top:26px;gap:14px;">{fa("یادگیری", 54, INK)}
    {icon("brain", 54, PURPLE)}</div>
  <div id="hm-pct" class="abs en" style="left:40px;top:22px;font-size:62px;color:{INK};">0%</div>
  <div class="abs" style="left:40px;top:122px;width:780px;height:42px;border-radius:21px;background:#ECE6FA;
    overflow:hidden;"><div id="hm-bar" style="width:780px;height:42px;border-radius:21px;
    background:{PURPLE};transform-origin:0 50%;"></div></div>
</div>'''
    sad = owl("hm-owl", "owl-sad", 40, 1170, 330)
    c.clip("over", "hm", 11.02, 15.0, card + sad, 5)
    c.j('inUp("#hm-c",11.5);',
        'tl.fromTo("#hm-bar",{scaleX:0},{scaleX:0.18,duration:0.55,ease:"power2.out"},11.96);',
        'count("#hm-pct",0,18,11.96,0.55,v=>Math.round(v)+"%");',
        'tl.to("#hm-bar",{scaleX:0,duration:0.45,ease:"power2.in"},12.72);',
        'count("#hm-pct",18,0,12.72,0.45,v=>Math.round(v)+"%");',
        f'tl.to("#hm-pct",{{color:"{RED}",duration:0.1}},13.1);',
        'tl.to("#hm-c",{x:-14,duration:0.05,yoyo:true,repeat:5},13.15);',
        'out("#hm-c",14.0);',
        'tl.fromTo("#hm-owl",{y:620,autoAlpha:0},{y:0,autoAlpha:1,duration:0.45,ease:"back.out(1.4)"},13.34);',
        'tl.to("#hm-owl",{y:520,duration:0.3,ease:"power2.in"},14.7);',
        'tl.fromTo("#cam",{scale:1},{scale:1.06,duration:2.4,ease:"sine.inOut",immediateRender:false},13.34);')


def not_prof(c: Comp):
    """16.1-18.45  not the professor, not the book: notes get crossed out."""
    def note(nid, x, y, bg, ic, word):
        return f'''
<div id="{nid}" class="note" style="left:{x}px;top:{y}px;background:{bg};">
  <i class="tape"></i>
  <div class="abs" style="left:0;right:0;top:38px;display:flex;justify-content:center;">{icon(ic, 120, INK, sw=1.6)}</div>
  <div class="abs fa" style="left:0;right:0;top:170px;text-align:center;font-size:52px;color:{INK};">{word}</div>
  <svg class="abs" style="left:-10px;top:-10px;" width="280" height="280" viewBox="0 0 280 280">
    <path class="ink {nid}-x" pathLength="1" d="M40 40 L240 240" stroke="{RED}" stroke-width="20" stroke-linecap="round" fill="none"/>
    <path class="ink {nid}-x" pathLength="1" d="M240 40 L40 240" stroke="{RED}" stroke-width="20" stroke-linecap="round" fill="none"/>
  </svg></div>'''
    inner = note("np-a", 40, 230, "#FFE66D", "presentation", "استاد") + \
        note("np-b", 780, 250, "#E4D4FF", "book-open", "کتاب")
    c.clip("over", "np", 16.1, 18.5, inner, 5)
    c.j('gsap.set("#np-a",{rotation:-7});', 'gsap.set("#np-b",{rotation:6});',
        'pop("#np-a",16.4);', 'draw(".np-a-x",16.98,0.2);',
        'tl.to("#np-a",{x:-8,duration:0.04,yoyo:true,repeat:3},17.1);',
        'pop("#np-b",17.55);', 'draw(".np-b-x",18.05,0.2);',
        'tl.to(["#np-a","#np-b"],{autoAlpha:0,scale:0.8,duration:0.15},18.3);',
        'tl.fromTo("#cam",{scale:1.06},{scale:1,duration:0.3,ease:"power2.out",immediateRender:false},16.1);')


def student(c: Comp):
    """18.45-20.85  library B-roll: 'a student' + BESTANDEN stamp."""
    c.broll("library", 18.45, 20.85)
    s = stk("st-s", 0, 1360, icon("user-check", 62, GREEN, sw=2.4) + fa("یه دانشجو", 56, INK), "cx")
    stamp = (f'<div id="st-stamp" class="abs en stamp" style="left:250px;top:1060px;">'
             f'BESTANDEN {icon("check", 70, GREEN, sw=4)}</div>')
    c.clip("over", "st", 18.45, 20.85, s + stamp, 5)
    c.j('tl.fromTo("#bw-library",{clipPath:"circle(0px at 540px 1400px)"},'
        '{clipPath:"circle(1500px at 540px 1400px)",duration:0.32,ease:"power2.in"},18.45);',
        'gsap.set("#st-s",{rotation:-3});', 'gsap.set("#st-stamp",{rotation:-12});',
        'pop("#st-s",18.6);',
        'tl.fromTo("#st-stamp",{scale:2.4,autoAlpha:0},{scale:1,autoAlpha:1,duration:0.16,'
        'ease:"power4.in"},20.0);',
        'tl.to("#bw-library",{x:12,duration:0.04,yoyo:true,repeat:3},20.16);',
        'tl.to("#bw-library",{y:1920,duration:0.24,ease:"power2.in"},20.62);')


def chat(c: Comp):
    """20.85-22.8  explained 'in our own language': two chat bubbles."""
    a = (f'<div id="ch-a" class="bub" style="left:70px;top:1150px;background:#EFEBF8;color:{INK};'
         f'border-radius:44px 44px 44px 10px;">{fa("ببین، خیلی ساده‌ست...", 50)}</div>')
    b = (f'<div id="ch-b" class="bub row" style="right:110px;top:1310px;background:{PURPLE};color:#fff;'
         f'gap:14px;border-radius:44px 44px 10px 44px;">{icon("sparkles", 46, YELLOW, fill=True)}'
         f'{fa("آهااا! حالا فهمیدم", 50)}</div>')
    c.clip("over", "ch", 20.85, 22.8, a + b, 5)
    c.j('inUp("#ch-a",20.96);', 'inUp("#ch-b",21.72);',
        'tl.to(["#ch-a","#ch-b"],{autoAlpha:0,y:-30,duration:0.18},22.6);')


def why(c: Comp):
    """22.84-25.62  thinking owl + big question mark, slow push."""
    q = (f'<div id="wy-q" class="abs fa" style="left:90px;top:170px;font-size:300px;line-height:1;'
         f'color:{YELLOW};text-shadow:0 12px 0 {IRIS};">؟</div>')
    o = owl("wy-owl", "owl-think", 720, 1110, 330)
    c.clip("over", "wy", 22.84, 25.62, q + o, 5)
    c.j('tl.fromTo("#wy-owl",{x:420,autoAlpha:0},{x:0,autoAlpha:1,duration:0.45,ease:"back.out(1.3)"},23.4);',
        'pop("#wy-q",24.14);',
        'tl.to("#wy-q",{rotation:12,duration:0.18,yoyo:true,repeat:5,ease:"sine.inOut"},24.4);',
        'tl.to(["#wy-q","#wy-owl"],{autoAlpha:0,duration:0.15},25.45);',
        'tl.fromTo("#cam",{scale:1},{scale:1.13,duration:2.7,ease:"sine.in",immediateRender:false},22.84);',
        'tl.to("#cam",{scale:1,duration:0.35,ease:"power3.out"},25.62);')


def reveal(c: Comp):
    """25.62-29.2  'I started Stoodi': purple world behind the speaker, wordmark."""
    inner = f'''
<div id="lg-fl" class="flood" style="background:radial-gradient(circle at 50% 30%,{LILAC} 0%,{PURPLE} 45%,{IRIS} 100%);">
  <div id="lg-rays" class="abs rays" style="left:-460px;top:-700px;"></div>
  <div class="flood dots"></div>
  <div class="abs en" style="left:0;right:0;top:120px;text-align:center;font-size:250px;line-height:1.2;
    color:#fff;letter-spacing:-8px;text-shadow:0 14px 0 rgba(26,14,77,.35);">{wordmark("lg", 250)}</div>
</div>'''
    c.clip("behind", "lg", 26.2, 29.25, inner, 2)
    c.matte(2, 26.2, 29.25)
    cf = confetti(c, "lgc", 540, 420, 26.55, seed=3)
    wave = owl("lg-owl", "owl-wave", 700, 1130, 340)
    c.clip("over", "lgo", 26.4, 29.2, cf + wave, 5)
    c.j('tl.fromTo("#lg-fl",{clipPath:"circle(0px at 500px 800px)"},{clipPath:"circle(1700px at 500px 800px)",'
        'duration:0.45,ease:"power2.in"},26.22);',
        'tl.fromTo("#lg-rays",{rotation:0},{rotation:50,duration:3,ease:"none"},26.2);',
        'tl.fromTo(".lg",{y:160,autoAlpha:0},{y:0,autoAlpha:1,duration:0.4,ease:"back.out(2)",stagger:0.05},26.42);',
        'tl.to("#cam",{scale:1.05,duration:0.12,yoyo:true,repeat:1},26.42);',
        'tl.fromTo("#lg-owl",{y:700,rotation:12,autoAlpha:0},{y:0,rotation:0,autoAlpha:1,duration:0.5,ease:"back.out(1.5)"},27.98);',
        'tl.to("#lg-owl",{rotation:-8,duration:0.2,yoyo:true,repeat:3,ease:"sine.inOut"},28.5);',
        'tl.to("#lg-owl",{y:600,duration:0.25,ease:"power2.in"},28.95);',
        'tl.to("#lg-fl",{clipPath:"circle(0px at 500px 800px)",duration:0.28,ease:"power3.in"},28.95);')


def connect(c: Comp):
    """29.2-31.9  connects one student to another."""
    def av(aid, x, col, word):
        return (f'<div id="{aid}" class="abs" style="left:{x}px;top:22px;width:170px;">'
                f'<div class="disc" style="width:150px;height:150px;margin:0 auto;background:{col};'
                f'border:6px solid #fff;box-shadow:0 8px 0 {INK};">{icon("user", 84, "#fff", sw=2.2)}</div>'
                f'<div class="fa" style="text-align:center;font-size:40px;color:{INK};margin-top:6px;">{word}</div></div>')
    dots = "".join(f'<i class="cn-dot pkt" style="left:182px;top:96px;"></i>' for _ in range(3))
    inner = f'''
<div id="cn" class="crd" style="left:70px;top:140px;width:940px;height:300px;">
  <svg class="abs" style="left:0;top:0;" width="940" height="300" viewBox="0 0 940 300">
    <path id="cn-line" class="ink" pathLength="1" d="M200 110 Q470 -20 740 110" stroke="{PURPLE}"
      stroke-width="10" stroke-linecap="round" fill="none"/></svg>
  {dots}
  {av("cn-r", 735, PURPLE, "دانشجو")}{av("cn-l", 35, ORANGE, "دانشجو")}
  <img id="cn-owl" class="owl" src="assets/mascot/owl-flat.png" style="left:410px;top:20px;width:120px;"/>
</div>'''
    c.clip("over", "cn", 29.2, 31.92, inner, 5)
    c.j('inUp("#cn",29.25);', 'pop("#cn-r",30.04);', 'pop("#cn-l",30.76);',
        'draw("#cn-line",31.15,0.3);', 'pop("#cn-owl",31.3);',
        'tl.fromTo(".cn-dot",{x:540,y:14,autoAlpha:0},{x:0,y:14,autoAlpha:1,duration:0.45,ease:"none",'
        'stagger:0.12},31.35);',
        'tl.to("#cn",{y:-40,autoAlpha:0,duration:0.18},31.74);')


def exam(c: Comp):
    """31.92-36.36  failed (5,0 nicht bestanden) -> tutor who passed (bestanden)."""
    inner = f'''
<div id="ex" class="crd" style="left:90px;top:1100px;width:860px;height:450px;">
  <div id="ex-r1" class="abs row" style="left:36px;top:34px;gap:18px;">{icon("file-text", 76, INK, sw=1.8)}
    {en("Prüfung", 54, INK)}</div>
  <div id="ex-g1" class="abs en" style="right:40px;top:6px;font-size:80px;line-height:1.2;color:{RED};">5,0</div>
  <div id="ex-b1" class="abs badge en" style="right:36px;top:118px;background:{RED};">nicht bestanden</div>
  <div id="ex-ar" class="abs" style="left:395px;top:170px;">{icon("arrow-down", 72, PURPLE, sw=3)}</div>
  <div id="ex-r2" class="abs row" style="left:36px;top:268px;gap:18px;">
    <span class="disc" style="width:86px;height:86px;background:{GREEN};">{icon("user-check", 50, "#fff", sw=2.4)}</span>
    {en("Tutor", 54, INK)}</div>
  <div id="ex-chip" class="abs fa chip" style="left:36px;top:368px;">چند ترم پیش</div>
  <div id="ex-g2" class="abs en" style="right:40px;top:240px;font-size:80px;line-height:1.2;color:{GREEN};">1,3</div>
  <div id="ex-b2" class="abs badge en" style="right:36px;top:356px;background:{GREEN};">bestanden</div>
</div>'''
    c.clip("over", "ex", 31.92, 36.36, inner, 5)
    c.j('inUp("#ex",31.96);', 'gsap.set(["#ex-r2","#ex-g2","#ex-ar"],{autoAlpha:0});',
        'tl.fromTo("#ex-b1",{scale:2,autoAlpha:0},{scale:1,autoAlpha:1,duration:0.16,ease:"power4.in"},32.9);',
        'tl.to("#ex",{x:-12,duration:0.04,yoyo:true,repeat:3},33.06);',
        'pop("#ex-ar",33.3);', 'inUp("#ex-r2",33.8);', 'pop("#ex-g2",33.9);', 'pop("#ex-chip",34.84);',
        'tl.fromTo("#ex-b2",{scale:2,autoAlpha:0},{scale:1,autoAlpha:1,duration:0.16,ease:"power4.in"},35.8);',
        'tl.to("#ex",{y:60,autoAlpha:0,duration:0.2},36.2);')


def tutor(c: Comp):
    """36.36-41.8  you passed -> give a Tutorium -> earn (coins)."""
    c.broll("tutor", 36.36, 39.75)
    g = stk("tu-g", 650, 250, icon("star", 60, YELLOW, fill=True) + en("1,0", 60, INK))
    c.clip("over", "tug", 36.36, 39.75, g, 5)
    tut = (f'<div id="tu-t" class="stk p" style="left:0;right:0;margin:auto;width:fit-content;top:250px;'
           f'font-size:64px;padding:22px 46px 22px 140px;">{en("Tutorium", 70, "#fff")}</div>'
           + owl("tu-owl", "owl-teacher", 170, 170, 230))
    rnd = random.Random(11)
    coins = []
    for k in range(13):
        x = 70 + k * 72 + rnd.randint(-20, 20)
        y = rnd.randint(1180, 1500)
        coins.append(f'<div id="tu-c{k}" class="coin en" style="left:{x}px;top:{y}px;">€</div>')
        c.j(f'tl.fromTo("#tu-c{k}",{{y:{-y - 140}}},{{y:0,duration:0.42,ease:"bounce.out"}},{T(41.0 + k * 0.025)});',
            f'tl.to("#tu-c{k}",{{y:900,duration:0.2,ease:"power2.in"}},41.74);')
    c.clip("over", "tut", 39.75, 41.95, tut + "".join(coins), 5)
    c.j('tl.fromTo("#bw-tutor",{x:-1080,filter:"blur(20px)"},{x:0,filter:"blur(0px)",duration:0.22,'
        'ease:"power3.out"},36.36);',
        'gsap.set("#tu-g",{rotation:5});', 'pop("#tu-g",37.4);',
        'pop("#tu-t",39.82);',
        'tl.fromTo("#tu-owl",{x:120,autoAlpha:0},{x:0,autoAlpha:1,duration:0.35,ease:"back.out(1.6)"},39.95);',
        'tl.to(["#tu-t","#tu-owl"],{autoAlpha:0,y:-40,duration:0.18},41.6);')


def slogan(c: Comp):
    """41.75-44.8  Learn. Teach. Earn. huge behind the speaker."""
    words = [("LEARN.", LILAC), ("TEACH.", YELLOW), ("EARN.", ORANGE)]
    w = "".join(f'<div id="sl-w{k}" class="abs blk" style="left:0;right:0;top:215px;text-align:center;'
                f'font-size:235px;line-height:1;color:{col};text-shadow:0 14px 0 rgba(0,0,0,.35);">{txt}</div>'
                for k, (txt, col) in enumerate(words))
    inner = f'''
<div id="sl-fl" class="flood" style="background:linear-gradient(180deg,#120836 0%,{INK} 55%,#2A1470 100%);">
  <div class="flood dots"></div>{w}</div>'''
    c.clip("behind", "sl", 41.75, 44.85, inner, 2)
    c.matte(3, 41.75, 44.85)
    chips = [("یاد بگیر", LILAC, "#fff"), ("یاد بده", YELLOW, INK), ("درآمد داشته باش", ORANGE, "#fff")]
    row = "".join(f'<span id="sl-c{k}" class="chip2 fa" style="background:{bg};color:{fg};">{t}</span>'
                  for k, (t, bg, fg) in enumerate(chips))
    front = (f'<div class="abs row" style="left:0;right:0;top:1430px;justify-content:center;gap:20px;'
             f'direction:rtl;">{row}</div>' + owl("sl-owl", "owl-party", 735, 1060, 320)
             + confetti(c, "slc", 880, 1150, 44.0, n=22, seed=5))
    c.clip("over", "slf", 42.4, 44.85, front, 5)
    c.j('tl.fromTo("#sl-fl",{clipPath:"inset(100% 0% 0% 0%)"},{clipPath:"inset(0% 0% 0% 0%)",'
        'duration:0.35,ease:"power3.out"},41.8);')
    for k, t in enumerate((42.56, 43.18, 43.88)):
        if k:
            c.j(f'tl.to("#sl-w{k - 1}",{{y:-260,autoAlpha:0,duration:0.16,ease:"power2.in"}},{T(t - 0.04)});')
        c.j(f'tl.fromTo("#sl-w{k}",{{scale:1.7,autoAlpha:0}},{{scale:1,autoAlpha:1,duration:0.24,'
            f'ease:"power4.out"}},{T(t)});',
            f'pop("#sl-c{k}",{T(t + 0.02)});',
            f'tl.to("#cam",{{scale:1.04,duration:0.08,yoyo:true,repeat:1}},{T(t)});')
    c.j('tl.fromTo("#sl-owl",{y:700,autoAlpha:0},{y:0,autoAlpha:1,duration:0.4,ease:"back.out(1.5)"},43.95);',
        'tl.to("#sl-fl",{clipPath:"inset(0% 0% 100% 0%)",duration:0.18,ease:"power2.in"},44.62);',
        'tl.to(["#sl-owl",".chip2"],{autoAlpha:0,duration:0.12},44.66);',
        'flash(44.78);')


def montage(c: Comp):
    """44.8-46.85  nine months of building: five quick cuts + month counter."""
    names = ["m-figma", "m-db", "m-board", "m-claude", "m-keys"]
    t = 44.80
    for k, n in enumerate(names):
        b = t + 0.41 if k < 4 else 46.85
        c.broll(n, t, b, 0.05)
        if k:
            c.j(f'flash({T(t)},0.5);',
                f'tl.fromTo("#bw-{n}",{{scale:1.18}},{{scale:1,duration:0.4,ease:"power2.out"}},{T(t)});')
        t = b
    cnt = (f'<div id="mo-c" class="stk ink" style="left:0;right:0;margin:auto;width:fit-content;top:210px;">'
           f'{icon("calendar", 62, YELLOW, sw=2.2)}<span id="mo-n" class="fa" style="font-size:66px;'
           f'color:#fff;">۱ ماه</span></div>')
    c.clip("over", "mo", 44.8, 46.85, cnt, 5)
    c.j('pop("#mo-c",44.86);',
        'count("#mo-n",1,9,44.95,1.7,v=>fa(Math.round(v))+" ماه");',
        'tl.to("#mo-c",{scale:1.2,duration:0.12,yoyo:true,repeat:1},46.65);')


def team(c: Comp):
    """46.85-48.4  a few Instagram reels -> a team."""
    phones = "".join(
        f'<div id="tm-p{k}" class="phone" style="left:{150 + k * 175}px;top:175px;">'
        f'{icon("play", 64, "#fff", fill=True)}</div>' for k in range(3))
    badge = (f'<div id="tm-b" class="stk p" style="left:0;right:0;margin:auto;width:fit-content;top:230px;">'
             f'{icon("users", 64, "#fff", sw=2.2)}{fa("تیم", 64, "#fff")}</div>')
    c.clip("over", "tm", 46.85, 48.4, phones + badge, 5)
    c.j('tl.fromTo(".phone",{y:300,autoAlpha:0,rotation:0},{y:0,autoAlpha:1,rotation:function(i){return [-10,0,10][i];},'
        'duration:0.35,ease:"back.out(1.5)",stagger:0.08},46.88);',
        'tl.to("#tm-p0",{x:175,duration:0.25,ease:"power3.in"},47.6);',
        'tl.to("#tm-p2",{x:-175,duration:0.25,ease:"power3.in"},47.6);',
        'tl.to(".phone",{scale:0.3,autoAlpha:0,duration:0.15},47.82);',
        'pop("#tm-b",47.86);',
        'tl.to("#tm-b",{autoAlpha:0,duration:0.15},48.25);')


def event(c: Comp):
    """48.4-52.1  first event: their clip in a polaroid 'right here'."""
    c.L["over"].append(f'''
<div id="ev-pola" class="pola" style="left:665px;top:330px;width:390px;">
  <i class="tape" style="left:140px;"></i>
  <div style="width:350px;height:622px;overflow:hidden;border-radius:6px;background:#000;position:relative;">
    <video id="v-event" class="clip" src="assets/broll/event.mp4" data-start="48.550" data-duration="3.550"
      data-media-start="0.000" data-track-index="5" muted playsinline
      style="position:absolute;left:0;top:0;width:350px;height:622px;object-fit:cover;"></video></div>
  <div class="fa" style="text-align:center;font-size:44px;color:{INK};margin-top:16px;">اولین ایونت</div>
</div>''')
    arrow = f'''
<svg class="abs" style="left:0;top:0;" width="1080" height="1920" viewBox="0 0 1080 1920">
  <path id="ev-arr" class="ink" pathLength="1" d="M190 1230 C 240 1020, 450 930, 640 860" stroke="{YELLOW}"
    stroke-width="12" stroke-linecap="round" fill="none"/>
  <path id="ev-head" class="ink" pathLength="1" d="M592 828 L648 857 L612 912" stroke="{YELLOW}"
    stroke-width="12" stroke-linecap="round" stroke-linejoin="round" fill="none"/></svg>'''
    here = stk("ev-here", 70, 1250, fa("همینجا!", 60, INK), "y")
    c.clip("over", "ev", 48.4, 52.1, arrow + here, 5)
    c.j('tl.to("#cam",{scale:1.2,x:-110,duration:0.5,ease:"power2.inOut"},48.42);',
        'tl.fromTo("#ev-pola",{x:520,y:220,rotation:24,autoAlpha:0},{x:0,y:0,rotation:5,autoAlpha:1,'
        'duration:0.55,ease:"back.out(1.3)"},48.55);',
        'draw("#ev-arr",51.1,0.3);', 'draw("#ev-head",51.38,0.12);',
        'gsap.set("#ev-here",{rotation:-6});', 'pop("#ev-here",51.15);',
        'tl.to("#ev-pola",{x:620,y:-260,rotation:28,autoAlpha:0,duration:0.3,ease:"power2.in"},51.85);',
        'tl.to(["#ev-here","#ev-arr","#ev-head"],{autoAlpha:0,duration:0.15},51.9);',
        'tl.to("#cam",{scale:1.1,x:0,duration:0.3,ease:"power2.inOut"},52.0);')


def steps(c: Comp):
    """52.15-53.4  idea -> team -> event -> next step (RTL progress)."""
    xs = [740, 520, 300, 80]
    labels = ["ایده", "تیم", "ایونت", "قدم بعدی"]
    nodes = []
    for k, (x, lab) in enumerate(zip(xs, labels)):
        last = k == 3
        bg = "#fff" if last else GREEN
        ic = icon("flag", 40, PURPLE, sw=2.6) if last else icon("check", 44, "#fff", sw=3.4)
        nodes.append(f'<div id="sp-n{k}" class="abs" style="left:{x}px;top:30px;width:120px;">'
                     f'<div class="disc" style="width:84px;height:84px;margin:0 auto;background:{bg};'
                     f'border:6px solid {PURPLE if last else GREEN};">{ic}</div>'
                     f'<div class="fa" style="text-align:center;font-size:36px;color:{INK};margin-top:8px;'
                     f'white-space:nowrap;">{lab}</div></div>')
    inner = f'''
<div id="sp" class="crd" style="left:100px;top:1250px;width:880px;height:230px;">
  <div class="abs" style="left:140px;top:68px;width:660px;height:14px;border-radius:7px;background:#E7E2F4;"></div>
  <div id="sp-a" class="abs" style="left:360px;top:68px;width:440px;height:14px;border-radius:7px;background:{GREEN};transform-origin:100% 50%;"></div>
  <div id="sp-b" class="abs" style="left:140px;top:68px;width:220px;height:14px;border-radius:7px;background:{PURPLE};transform-origin:100% 50%;"></div>
  {"".join(nodes)}
  <i id="sp-ring" class="ring" style="left:102px;top:14px;width:116px;height:116px;border-color:{PURPLE};"></i>
</div>'''
    c.clip("over", "sp", 52.12, 53.42, inner, 5)
    c.j('inUp("#sp",52.14);',
        'tl.fromTo("#sp-a",{scaleX:0},{scaleX:1,duration:0.3,ease:"power2.out"},52.2);',
        'tl.fromTo(["#sp-n0","#sp-n1","#sp-n2"],{scale:0},{scale:1,duration:0.2,ease:"back.out(2)",stagger:0.08},52.18);',
        'tl.fromTo("#sp-b",{scaleX:0},{scaleX:1,duration:0.3,ease:"power2.inOut"},52.58);',
        'pop("#sp-n3",52.82);',
        'tl.fromTo("#sp-ring",{scale:0.8,opacity:1},{scale:1.7,opacity:0,duration:0.5,repeat:1},52.95);',
        'tl.to("#sp",{y:60,autoAlpha:0,duration:0.18},53.25);')


def germany(c: Comp):
    """53.4-60.6  speaker shrinks to a bubble; map: every uni gets a Stoodi owl."""
    p = projector(1150, 118, 170)
    pins, owls = [], []
    for k, (lat, lon) in enumerate(UNIS):
        x, y = p(lat, lon)
        pins.append(f'<i class="pin m-dot" style="left:{x - 13:.0f}px;top:{y - 13:.0f}px;"></i>')
        owls.append(f'<img class="owl m-owl" src="assets/mascot/owl-flat.png" style="left:{x - 27:.0f}px;'
                    f'top:{y - 27:.0f}px;width:54px;"/>')
    random.Random(4).shuffle(pins)
    random.Random(6).shuffle(owls)
    hearts = []
    for k in range(0, len(UNIS), 5):
        x, y = p(*UNIS[k])
        hearts.append(f'<div class="abs m-heart" style="left:{x - 26:.0f}px;top:{y - 60:.0f}px;">'
                      f'{icon("heart", 52, PINK, fill=True)}</div>')
    inner = f'''
<div class="flood" style="background:radial-gradient(circle at 50% 40%,#2E1680 0%,{INK} 62%,#0C0628 100%);"></div>
<div class="flood dots"></div>
<svg class="abs" style="left:0;top:0;" width="1080" height="1920" viewBox="0 0 1080 1920">
  <path id="m-map" d="{de_path(p)}" pathLength="1" class="ink" fill="{LILAC}" fill-opacity="0"
    stroke="{LILAC}" stroke-width="7" stroke-linejoin="round"/></svg>
{"".join(pins)}{"".join(owls)}{"".join(hearts)}
{stk("m-c1", 120, 190, '<img src="assets/mascot/owl-flat.png" style="width:60px;"/>' + fa("نماینده‌ی استودی", 48, INK))}
{stk("m-c2", 120, 300, icon("heart", 50, PINK, fill=True) + fa("ایرانی‌ها", 48, "#fff"), "p")}'''
    c.clip("under", "m", 53.3, 60.75, inner, 1)
    ring = (f'<i id="m-ring" class="abs" style="left:{540 - 172}px;top:{1490 - 172}px;width:344px;height:344px;'
            f'border-radius:50%;border:9px solid {YELLOW};box-sizing:border-box;"></i>')
    c.clip("over", "mr", 53.3, 60.75, ring, 5)
    c.j('tl.to("#cam",{clipPath:"circle(470px at 500px 800px)",scale:0.34,x:40,y:690,'
        'duration:0.6,ease:"power3.inOut"},53.4);',
        'tl.fromTo("#m-ring",{scale:0.6,autoAlpha:0},{scale:1,autoAlpha:1,duration:0.3,ease:"back.out(2)"},53.9);',
        'draw("#m-map",53.5,0.8);',
        'tl.to("#m-map",{attr:{"fill-opacity":0.14},duration:0.4},54.1);',
        'tl.fromTo(".m-dot",{scale:0,autoAlpha:0},{scale:1,autoAlpha:1,duration:0.2,ease:"back.out(2.5)",'
        'stagger:0.017},54.02);',
        'tl.to(".m-dot",{scale:0,duration:0.12,stagger:0.02},55.55);',
        'tl.fromTo(".m-owl",{scale:0,autoAlpha:0},{scale:1,autoAlpha:1,duration:0.25,ease:"back.out(2.2)",'
        'stagger:0.02},55.6);',
        'pop("#m-c1",55.7);',
        'tl.fromTo(".m-heart",{y:20,scale:0,autoAlpha:0},{y:-70,scale:1,autoAlpha:1,duration:0.45,'
        'ease:"power2.out",stagger:0.05},59.6);',
        'tl.to(".m-heart",{autoAlpha:0,duration:0.3},60.2);',
        'pop("#m-c2",59.62);',
        'tl.to("#m-ring",{autoAlpha:0,duration:0.15},60.4);',
        'tl.to("#cam",{clipPath:"circle(1400px at 500px 800px)",scale:1,x:0,y:0,duration:0.55,'
        'ease:"power3.inOut"},60.48);')


def community(c: Comp):
    """60.6-63.5  community: avatars ring the frame and link up."""
    pos = [(250, 175), (720, 175), (900, 520), (920, 860), (870, 1180), (760, 1450),
           (300, 1450), (90, 1180), (60, 860), (80, 520)]
    cols = [PURPLE, ORANGE, LILAC, YELLOW, PINK, PURPLE, ORANGE, LILAC, PINK, YELLOW]
    av = "".join(f'<div id="cm-a{k}" class="disc abs av" style="left:{x}px;top:{y}px;background:{col};">'
                 f'{icon("user", 60, "#fff" if col not in (YELLOW,) else INK, sw=2.4)}</div>'
                 for k, ((x, y), col) in enumerate(zip(pos, cols)))
    segs = []
    for k in range(len(pos)):
        (x0, y0), (x1, y1) = pos[k], pos[(k + 1) % len(pos)]
        segs.append(f'<path class="ink cm-l" pathLength="1" d="M{x0 + 60} {y0 + 60} L{x1 + 60} {y1 + 60}" '
                    f'stroke="#fff" stroke-width="6" stroke-dasharray="1" stroke-linecap="round" fill="none" opacity=".8"/>')
    inner = (f'<svg class="abs" style="left:0;top:0;" width="1080" height="1920" viewBox="0 0 1080 1920">'
             f'{"".join(segs)}</svg>{av}'
             + stk("cm-c", 0, 1330, icon("users", 60, "#fff", sw=2.2) + en("Community", 58, "#fff"), "cx p"))
    c.clip("over", "cm", 60.6, 63.5, inner, 5)
    c.j('tl.fromTo(".av",{scale:0,autoAlpha:0},{scale:1,autoAlpha:1,duration:0.3,ease:"back.out(2)",'
        'stagger:0.06},61.3);',
        'pop("#cm-c",61.4);',
        'tl.fromTo(".cm-l",{strokeDashoffset:1},{strokeDashoffset:0,duration:0.25,stagger:0.06},61.9);',
        'tl.to(["#cm-i"],{autoAlpha:0,duration:0.15},63.35);')


def bigger(c: Comp):
    """63.5-66.5  alongside study (train B-roll) -> zoom out: one tile of something bigger."""
    c.broll("train", 63.5, 65.3, 0.3)
    s = stk("bg-s", 0, 1330, icon("book-open", 60, PURPLE, sw=2) + fa("کنار درس", 56, INK), "cx")
    c.clip("over", "bgs", 63.5, 65.3, s, 5)
    c.j('tl.fromTo("#bw-train",{y:1920},{y:0,duration:0.24,ease:"power3.out"},63.5);',
        'gsap.set("#bg-s",{rotation:3});', 'pop("#bg-s",63.78);', 'out("#bg-s",65.15,0.12);',
        'tl.to("#world",{scale:0.205,duration:0.8,ease:"power3.inOut"},65.32);',
        'tl.to("#cam",{borderRadius:80,duration:0.4},65.32);',
        'tl.to("#camframe",{opacity:1,duration:0.3},65.6);',
        'tl.to("#world",{scale:0.19,duration:0.22,ease:"none"},66.12);',
        'tl.to("#world",{scale:1,duration:0.16,ease:"power4.in"},66.34);',
        'tl.to("#cam",{borderRadius:0,duration:0.1},66.4);',
        'tl.to("#camframe",{opacity:0,duration:0.08},66.36);',
        'flash(66.5);')
    # 5x5 grid around the camera tile
    tiles, k = [], 0
    owls = ["owl-party", "owl-wave", "owl-think", "owl-head", "owl-hero", "owl-angry", "owl-sad", "owl-party"]
    for r in range(5):
        for col in range(5):
            if (r, col) == (2, 2):
                continue
            x, y = (col - 2) * 1140, (r - 2) * 1980
            if k % 3 == 2 and owls:
                o = owls.pop(0)
                tiles.append(f'<div class="tile" style="left:{x}px;top:{y}px;background:radial-gradient('
                             f'circle at 50% 40%,{LILAC},{PURPLE} 55%,{IRIS});"><img src="assets/mascot/{o}.png" '
                             f'style="position:absolute;left:140px;top:560px;width:800px;"/></div>')
            else:
                tiles.append(f'<img class="tile" src="assets/tiles/t{k % 16:02d}.jpg" style="left:{x}px;top:{y}px;"/>')
            k += 1
    c.L["tiles"].append("".join(tiles))


def honest(c: Comp):
    """66.5-68.76  'honestly, this is not for everyone': grayscale + caution tape behind."""
    def tape(tid, y, rot, text, cls):
        rep = (text + " &nbsp;•&nbsp; ") * 6
        return (f'<div id="{tid}" class="tapeband {cls}" style="top:{y}px;">'
                f'<div class="tb-in">{rep}</div></div>', rot)
    a, ra = tape("hn-a", 600, -12, "NOT FOR EVERYONE", "blk")
    b, rb = tape("hn-b", 420, 9, "این برای همه نیست", "fa")
    inner = f'<div id="hn-dk" class="flood" style="background:rgba(12,6,34,.78);"></div>{a}{b}'
    c.clip("behind", "hn", 66.48, 68.78, inner, 2)
    c.matte(4, 66.48, 68.78)
    c.j('tl.set("#cam",{scale:1.28},66.5);',
        'tl.set(["#aw","#fw"],{filter:"grayscale(1) contrast(1.18)"},66.5);',
        f'gsap.set("#hn-a",{{rotation:{ra}}});', f'gsap.set("#hn-b",{{rotation:{rb}}});',
        'tl.fromTo("#hn-dk",{opacity:0},{opacity:1,duration:0.2},66.5);',
        'tl.fromTo("#hn-a",{x:-1900},{x:0,duration:0.3,ease:"power3.out"},67.42);',
        'tl.fromTo("#hn-b",{x:1900},{x:0,duration:0.3,ease:"power3.out"},67.62);',
        'tl.fromTo("#hn-a .tb-in",{x:0},{x:-260,duration:1.4,ease:"none"},67.42);',
        'tl.fromTo("#hn-b .tb-in",{x:-260},{x:0,duration:1.2,ease:"none"},67.62);',
        'tl.set(["#aw","#fw"],{filter:"none"},68.76);',
        'tl.to("#cam",{scale:1,duration:0.3,ease:"power3.out"},68.76);')


def fork(c: Comp):
    """68.8-77.05  two paths: curious -> follow / serious -> JOIN."""
    inner = f'''
<div id="fk" class="crd" style="left:60px;top:130px;width:960px;height:320px;">
  <div class="abs" style="left:478px;top:24px;width:4px;height:272px;background:repeating-linear-gradient(180deg,#CFC6EA 0 14px,transparent 14px 26px);"></div>
  <!-- right column: curious -->
  <div id="fk-r1" class="abs stk2" style="right:40px;top:26px;background:#EDE4FF;">{icon("eye", 50, PURPLE, sw=2.2)}{fa("کنجکاوی؟", 46, INK)}</div>
  <div id="fk-ok" class="abs" style="right:330px;top:120px;">{icon("thumbs-up", 58, GREEN, sw=2.2)}</div>
  <div id="fk-ar1" class="abs" style="right:205px;top:118px;">{icon("arrow-down", 60, "#9C8FC4", sw=3)}</div>
  <div id="fk-fol" class="abs btn en" style="right:60px;top:200px;background:{IG_BLUE};color:#fff;">Follow</div>
  <div id="fk-foling" class="abs btn en row" style="right:60px;top:200px;background:#EFEFEF;color:{INK};gap:10px;
    justify-content:center;">{icon("check", 36, INK, sw=3)}Following</div>
  <div id="fk-cur" class="abs" style="right:70px;top:236px;">{icon("mouse-pointer-2", 62, INK, fill=True,
    extra="filter:drop-shadow(0 4px 5px rgba(0,0,0,.3));")}</div>
  <!-- left column: serious -->
  <div id="fk-l1" class="abs stk2" style="left:40px;top:26px;background:#FFE9CC;">{icon("flame", 50, ORANGE, sw=2.2, fill=True)}{fa("جدی هستی؟", 46, INK)}</div>
  <div id="fk-us" class="abs disc" style="left:70px;top:116px;width:72px;height:72px;background:{PURPLE};">{icon("users", 42, "#fff", sw=2.2)}</div>
  <div id="fk-d1" class="abs row en" style="left:160px;top:120px;gap:8px;padding:6px 18px;border-radius:16px;background:{INK};
    color:{YELLOW};font-size:38px;">{icon("calendar-check", 38, YELLOW, sw=2.2)}DAY 1</div>
  <div id="fk-join" class="abs btn blk" style="left:60px;top:200px;background:{YELLOW};color:{INK};font-size:52px;">JOIN</div>
</div>'''
    c.clip("over", "fk", 68.8, 77.05, inner, 5)
    c.j('inUp("#fk",68.82);',
        'gsap.set(["#fk-foling"],{autoAlpha:0});',
        'pop("#fk-r1",69.22);', 'pop("#fk-ok",71.24);', 'pop("#fk-ar1",71.6);',
        'pop("#fk-fol",72.0);',
        'tl.fromTo("#fk-cur",{x:160,y:90,autoAlpha:0},{x:0,y:0,autoAlpha:1,duration:0.3,ease:"power2.out"},71.95);',
        'tl.to("#fk-fol",{scale:0.92,duration:0.07},72.3);',
        'tl.set("#fk-fol",{autoAlpha:0},72.38);', 'tl.set("#fk-foling",{autoAlpha:1},72.38);',
        'tl.to("#fk-cur",{autoAlpha:0,duration:0.2},72.7);',
        'pop("#fk-l1",73.08);',
        'tl.to("#cam",{scale:1.12,duration:0.3,ease:"power3.out"},73.08);',
        'pop("#fk-us",74.26);', 'pop("#fk-d1",75.22);',
        'pop("#fk-join",76.7);',
        'tl.to("#fk-join",{scale:1.12,duration:0.1,yoyo:true,repeat:1},76.85);',
        'tl.to("#fk",{y:-60,autoAlpha:0,duration:0.2},76.88);')


def join(c: Comp):
    """76.7-79.5  JOIN huge behind the speaker; comment typed + link reply; welcome owl."""
    letters = "".join(f'<span class="jl" style="display:inline-block;">{ch}</span>' for ch in "JOIN")
    inner = f'''
<div id="jn-fl" class="flood" style="background:radial-gradient(circle at 50% 30%,{LILAC} 0%,{PURPLE} 48%,{IRIS} 100%);">
  <div id="jn-rays" class="abs rays" style="left:-460px;top:-700px;"></div>
  <div class="flood dots"></div>
  <div class="abs blk" style="left:0;right:0;top:120px;text-align:center;font-size:300px;line-height:1;
    color:{YELLOW};text-shadow:0 16px 0 {INK};">{letters}</div></div>'''
    c.clip("behind", "jn", 76.65, 79.55, inner, 2)
    c.matte(5, 76.65, 79.55)
    typed = "".join(f'<span class="tj">{ch}</span>' for ch in "JOIN")
    card = f'''
<div id="jc" class="abs" style="left:90px;top:1120px;width:860px;height:400px;">
  <div id="jc-post" class="abs row crd" style="left:0;top:0;gap:18px;padding:14px 34px 14px 16px;border-radius:999px;">
    <span class="disc" style="width:76px;height:76px;background:#E4D4FF;">{icon("user", 44, PURPLE, sw=2.2)}</span>
    {en("JOIN", 50, INK)}
    <span id="jc-heart">{icon("heart", 40, RED, fill=True)}</span></div>
  <div id="jc-rep" class="abs row" style="left:90px;top:128px;gap:16px;">
    <img src="assets/mascot/owl-flat.png" style="width:64px;"/>
    <span class="row" style="gap:10px;padding:10px 24px;border-radius:24px;background:{PURPLE};color:#fff;">
      {icon("link", 38, "#fff", sw=2.4)}{fa("لینک گروه", 42, "#fff")}</span></div>
  <div id="jc-in" class="abs row crd" style="left:0;top:256px;width:860px;height:104px;border-radius:52px;
    padding:0 18px 0 40px;justify-content:space-between;">
    <span class="en" style="position:relative;font-size:44px;color:{INK};">
      <span id="jc-ph" style="position:absolute;left:0;top:0;color:#A49CBF;white-space:nowrap;">Add a comment...</span>{typed}<i id="jc-caret" class="caret"></i></span>
    <span id="jc-send" class="disc" style="width:62px;height:62px;background:{PURPLE};">{icon("send", 34, "#fff", sw=2.4)}</span>
  </div>
</div>'''
    wel = owl("jn-owl", "owl-welcome", 700, 700, 400)
    c.clip("over", "jc", 76.95, 79.5, card + wel, 5)
    c.j('tl.fromTo("#jn-fl",{clipPath:"circle(0px at 500px 800px)"},{clipPath:"circle(1700px at 500px 800px)",'
        'duration:0.4,ease:"power2.in"},76.68);',
        'tl.to("#cam",{scale:1,duration:0.3},76.68);',
        'tl.fromTo("#jn-rays",{rotation:0},{rotation:40,duration:2.9,ease:"none"},76.65);',
        'tl.fromTo(".jl",{y:-260,autoAlpha:0},{y:0,autoAlpha:1,duration:0.35,ease:"bounce.out",stagger:0.07},77.2);',
        'inUp("#jc",77.0);',
        'gsap.set(["#jc-post","#jc-rep"],{autoAlpha:0});',
        'tl.fromTo(".tj",{autoAlpha:0},{autoAlpha:1,duration:0.01,stagger:0.08},77.24);',
        'tl.to("#jc-ph",{autoAlpha:0,duration:0.01},77.22);',
        'tl.fromTo("#jc-caret",{opacity:1},{opacity:0,duration:0.12,yoyo:true,repeat:5},77.0);',
        'tl.to("#jc-send",{scale:0.82,duration:0.08,yoyo:true,repeat:1},77.78);',
        'tl.to(".tj",{autoAlpha:0,duration:0.08},77.9);', 'tl.set("#jc-caret",{opacity:0},77.9);', 'tl.to("#jc-ph",{autoAlpha:1,duration:0.1},78.0);',
        'inUp("#jc-post",77.92);', 'pop("#jc-heart",78.1);',
        'inUp("#jc-rep",78.36);',
        'tl.fromTo("#jn-owl",{y:700,rotation:10,autoAlpha:0},{y:0,rotation:0,autoAlpha:1,duration:0.45,ease:"back.out(1.5)"},78.5);',
        'tl.to(["#jc","#jn-owl"],{autoAlpha:0,duration:0.18},79.3);',
        'tl.to("#jn-fl",{clipPath:"circle(0px at 500px 800px)",duration:0.25,ease:"power3.in"},79.28);')


def outro(c: Comp):
    """79.5-82.6  like + follow, then the Stoodi lockup behind the speaker."""
    rnd = random.Random(21)
    minis = []
    for k in range(8):
        ang = k / 8 * 2 * math.pi
        dx, dy = math.cos(ang) * 170, math.sin(ang) * 170
        minis.append(f'<div id="ol-m{k}" class="abs" style="left:205px;top:1265px;">{icon("heart", 40, PINK, fill=True)}</div>')
        c.j(f'tl.fromTo("#ol-m{k}",{{x:0,y:0,scale:0.3,autoAlpha:1}},{{x:{dx:.0f},y:{dy:.0f},scale:1,'
            f'autoAlpha:0,duration:0.6,ease:"power2.out"}},80.68);')
    heart = f'<div id="ol-h" class="abs" style="left:120px;top:1180px;">{icon("heart", 210, RED, fill=True, extra="filter:drop-shadow(0 10px 0 rgba(26,14,77,.35));")}</div>'
    fol = f'''
<div id="ol-f" class="crd row" style="left:390px;top:1220px;padding:20px 26px;gap:22px;border-radius:30px;">
  {en("@" + HANDLE, 42, INK)}
  <span style="position:relative;display:inline-block;width:250px;height:76px;">
    <span id="ol-fol" class="btn en" style="position:absolute;inset:0;width:250px;height:76px;font-size:38px;background:{IG_BLUE};color:#fff;">Follow</span>
    <span id="ol-foling" class="btn en" style="position:absolute;inset:0;width:250px;height:76px;font-size:36px;background:#EFEFEF;color:{INK};">Following</span>
  </span></div>'''
    c.clip("over", "ol", 79.5, 82.0, "".join(minis) + heart + fol, 5)
    c.j('pop("#ol-h",80.6,{duration:0.35,ease:"back.out(2.6)"});',
        'tl.to("#ol-h",{scale:1.15,duration:0.12,yoyo:true,repeat:1},80.95);',
        'gsap.set("#ol-foling",{autoAlpha:0});',
        'inUp("#ol-f",81.0);',
        'tl.to("#ol-fol",{scale:0.92,duration:0.06},81.32);',
        'tl.set("#ol-fol",{autoAlpha:0},81.4);', 'tl.set("#ol-foling",{autoAlpha:1},81.4);',
        'tl.to(["#ol-h","#ol-f"],{autoAlpha:0,duration:0.18},81.8);')
    inner = f'''
<div id="en-fl" class="flood" style="background:radial-gradient(circle at 50% 28%,{LILAC} 0%,{PURPLE} 45%,{IRIS} 100%);">
  <div id="en-rays" class="abs rays" style="left:-460px;top:-760px;"></div>
  <div class="flood dots"></div>
  <div class="abs row" style="left:0;right:0;top:150px;justify-content:center;gap:34px;">
    <img id="en-icon" src="assets/brand/logo.png" style="width:210px;height:210px;border-radius:52px;
      box-shadow:0 12px 0 rgba(26,14,77,.35);"/>
    <div class="en" style="font-size:215px;line-height:1;color:#fff;letter-spacing:-7px;
      text-shadow:0 12px 0 rgba(26,14,77,.35);">{wordmark("enw", 215)}</div></div></div>'''
    c.clip("behind", "en", 81.6, DUR, inner, 2)
    c.matte(6, 81.6, DUR)
    c.j('tl.fromTo("#en-fl",{clipPath:"circle(0px at 500px 800px)"},{clipPath:"circle(1700px at 500px 800px)",'
        'duration:0.38,ease:"power2.in"},81.66);',
        'tl.fromTo("#en-rays",{rotation:0},{rotation:20,duration:1,ease:"none"},81.6);',
        'pop("#en-icon",81.86,{duration:0.3});',
        'tl.fromTo(".enw",{y:140,autoAlpha:0},{y:0,autoAlpha:1,duration:0.3,ease:"back.out(2)",stagger:0.04},81.92);')


SCENES = [hook, rewind, arrival, lecture, home, not_prof, student, chat, why, reveal, connect,
          exam, tutor, slogan, montage, team, event, steps, germany, community, bigger, honest,
          fork, join, outro]
