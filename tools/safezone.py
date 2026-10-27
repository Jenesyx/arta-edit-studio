"""Instagram Reels safe zones: guide overlay + automatic check.

    python tools/safezone.py guides           -> work/_guides/ig-safe.png (overlay for previews)
    python tools/safezone.py check <take>     -> scan the built composition, list overlays that sit
                                                 in Instagram's UI zones (exit 1 on errors)

Zones (x0, y0, x1, y1 on the 1080x1920 frame) come from `instagram_safe_zones` in
reel.config.json:
  header   status bar, "Reels" title, camera button
  actions  like, comment, share, send, more (right rail)
  footer   @username, Follow, caption, audio
Full-screen pictures (B-roll, floods, maps) may run under the UI; what must stay
out is anything the viewer has to read or see: text, stickers, cards, buttons,
mascots, logos.

The check loads work/<take>/sc/public/index.html in the renderer's own headless
Chrome, steps the timeline every 0.2 s, applies each clip's data-start/duration
window and measures every visible content element. Something that only crosses a
zone in passing (< 0.4 s, e.g. flying in) is ignored.
  error    text, or a sticker/card/button box, inside a zone
  warning  an image or drawn shape inside a zone (mascot, arrow, map) -- look at it
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import config as C  # noqa: E402

LABELS = {"header": ["HEADER", "status bar - Reels - camera"],
          "actions": ["like", "comment", "share", "send", "more"],
          "footer": ["FOOTER", "@name - Follow - caption - audio"]}
GUIDES = C.WORK_DIR / "_guides" / "ig-safe.png"


def zones() -> dict[str, list[int]]:
    return {k: list(v) for k, v in C.CFG["instagram_safe_zones"].items()}


def _text(img, s, org, scale=1.0, th=2):
    cv2.putText(img, s, org, cv2.FONT_HERSHEY_SIMPLEX, scale, (20, 20, 20, 255), th + 4, cv2.LINE_AA)
    cv2.putText(img, s, org, cv2.FONT_HERSHEY_SIMPLEX, scale, (255, 255, 255, 255), th, cv2.LINE_AA)


def guides_png(force: bool = False) -> Path:
    """Transparent 1080x1920 PNG: red UI zones, 120 px grid, thirds, centre, margins."""
    if GUIDES.exists() and not force and GUIDES.stat().st_mtime > (C.ROOT / "reel.config.example.json").stat().st_mtime:
        return GUIDES
    W, H = C.WIDTH, C.HEIGHT
    img = np.zeros((H, W, 4), np.uint8)
    for x in range(0, W + 1, 120):
        cv2.line(img, (x, 0), (x, H), (255, 255, 0, 45), 1)
    for y in range(0, H + 1, 120):
        cv2.line(img, (0, y), (W, y), (255, 255, 0, 45), 1)
    for x in (W // 3, 2 * W // 3):
        cv2.line(img, (x, 0), (x, H), (255, 255, 0, 110), 2)
    for y in (H // 3, 2 * H // 3):
        cv2.line(img, (0, y), (W, y), (255, 255, 0, 110), 2)
    for k in range(0, H, 24):                                   # dashed centre lines
        cv2.line(img, (W // 2, k), (W // 2, k + 12), (255, 255, 255, 140), 2)
    for k in range(0, W, 24):
        cv2.line(img, (k, H // 2), (k + 12, H // 2), (255, 255, 255, 140), 2)
    cv2.rectangle(img, (60, 0), (W - 60, H), (0, 220, 255, 120), 2)   # side margins
    fill = img.copy()
    for name, (x0, y0, x1, y1) in zones().items():
        cv2.rectangle(fill, (x0, y0), (x1, y1), (40, 40, 235, 90), -1)
    img = np.where(fill[..., 3:] > img[..., 3:], fill, img)
    for name, (x0, y0, x1, y1) in zones().items():
        cv2.rectangle(img, (x0, y0), (x1 - 1, y1 - 1), (40, 40, 255, 230), 3)
        lab = LABELS.get(name, [name.upper()])
        if x1 - x0 < 300:                                       # narrow rail: one word per icon slot
            step = (y1 - y0) // (len(lab) + 1)
            for i, s in enumerate(lab):
                cy = y0 + step * (i + 1)
                cv2.circle(img, ((x0 + x1) // 2, cy - 30), 26, (255, 255, 255, 200), 3)
                _text(img, s, (x0 + 8, cy + 18), 0.7, 2)
        else:
            _text(img, lab[0], (x0 + 30, y0 + (y1 - y0) // 2), 1.4, 3)
            if len(lab) > 1:
                _text(img, lab[1], (x0 + 30, y0 + (y1 - y0) // 2 + 50), 0.9, 2)
    GUIDES.parent.mkdir(parents=True, exist_ok=True)
    cv2.imencode(".png", img)[1].tofile(str(GUIDES))
    return GUIDES


def overlay_filter() -> str:
    """ffmpeg filter_complex fragment: [0:v] + guides -> [g] (guides scaled to the video)."""
    return "[1:v]format=rgba[gd];[0:v][gd]scale2ref[v0][gd2];[v0][gd2]overlay=0:0[g]"


def chrome() -> str:
    out = subprocess.run("npx hyperframes browser ensure", shell=True, cwd=str(C.ROOT),
                         capture_output=True, text=True, encoding="utf-8", errors="replace")
    out = subprocess.run("npx hyperframes browser path", shell=True, cwd=str(C.ROOT),
                         capture_output=True, text=True, encoding="utf-8", errors="replace")
    path = [ln.strip() for ln in out.stdout.splitlines() if ln.strip()]
    if not path or not Path(path[-1]).exists():
        sys.exit("[safezone] could not find the renderer's Chrome -- run `npx hyperframes browser ensure`")
    return path[-1]


def check(name: str, step: float = 0.2) -> dict:
    pub = C.work_dir_for(name) / "sc" / "public"
    index = pub / "index.html"
    if not index.exists():
        sys.exit(f"[safezone] {index} missing -- build first")
    html = index.read_text(encoding="utf-8")
    import re
    m = re.search(r'data-composition-id="main"[^>]*data-duration="([0-9.]+)"', html)
    dur = float(m.group(1)) if m else C.probe(C.find_raw(name))["duration"]
    proc = subprocess.run(["node", str(Path(__file__).parent / "safezone_check.mjs"), str(pub),
                           json.dumps(zones()), f"{dur}", f"{step}", chrome()],
                          cwd=str(C.ROOT), capture_output=True, text=True, encoding="utf-8",
                          errors="replace")
    if proc.returncode != 0:
        sys.exit(f"[safezone] checker failed:\n{proc.stderr[-2000:]}")
    res = json.loads(proc.stdout.strip().splitlines()[-1])
    C.write_json(C.work_dir_for(name) / "safezone.json", res)
    return res


def report(res: dict) -> int:
    errs = [v for v in res["violations"] if v["severity"] == "error"]
    warns = [v for v in res["violations"] if v["severity"] == "warning"]
    for v in errs + warns:
        x0, y0, x1, y1 = v["rect"]
        print(f"[safezone] {v['severity'].upper():<7} {v['from']:6.2f}-{v['to']:6.2f}s  {v['zone']:<7} "
              f"{v['key'][:60]:<60} box {x0},{y0}-{x1},{y1}")
    print(f"[safezone] {res['samples']} samples: {len(errs)} error(s), {len(warns)} warning(s)")
    return 1 if errs else 0


def main(argv: list[str]) -> int:
    if not argv or argv[0] not in ("guides", "check"):
        print(__doc__)
        return 2
    if argv[0] == "guides":
        print(f"[safezone] {guides_png(force=True)}")
        return 0
    if len(argv) < 2:
        sys.exit("usage: python tools/safezone.py check <take>")
    return report(check(C.find_raw(argv[1]).stem))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
