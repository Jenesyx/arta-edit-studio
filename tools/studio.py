"""Pieces both builders share: runtime scripts, the style-brief gate, preview guides.

  runtime(assets)      copy GSAP + MotionPathPlugin + CustomEase + motion.js into the
                       composition, return the <script> tags for <head>
  require_style(name)  stop unless work/<take>/style.md exists and is filled in -- the
                       brief written from the creator's mood board (tools/moodboard.py)
  guides_html(assets)  <img> overlay of Instagram's UI zones for snapshots / Studio
                       previews. finish.py refuses to render a composition that has it.
"""

from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import config as C  # noqa: E402

GSAP_DIST = C.ROOT / "node_modules" / "gsap" / "dist"
SCRIPTS = ["gsap.min.js", "MotionPathPlugin.min.js", "CustomEase.min.js"]
REQUIRED_SECTIONS = ["Mood", "Palette", "Typography", "Motion", "Graphic language", "Density",
                     "Do", "Don't", "References"]
GUIDES_ID = "ig-guides"


def runtime(assets: Path) -> str:
    C.gsap_js()                                   # clear error if npm install was skipped
    for s in SCRIPTS:
        shutil.copyfile(GSAP_DIST / s, assets / s)
    shutil.copyfile(Path(__file__).parent / "motion.js", assets / "motion.js")
    return "\n".join(f'<script src="assets/{s}"></script>' for s in SCRIPTS + ["motion.js"])


def require_style(name: str, skip: bool = False) -> Path | None:
    p = C.work_dir_for(name) / "style.md"
    if skip:
        print("[studio] WARNING: building without a style brief (--no-moodboard)")
        return None
    if not p.exists():
        sys.exit(f"[studio] no style brief at {p}.\n"
                 f"  1. the creator fills moodboard/{name}/ (or moodboard/default/) -- docs/moodboard.md\n"
                 f"  2. python tools/moodboard.py {name}\n"
                 f"  3. write work/{name}/style.md from docs/style-brief.md and get the creator's OK")
    text = p.read_text(encoding="utf-8")
    missing = [s for s in REQUIRED_SECTIONS
               if not re.search(rf"^#+\s*{re.escape(s)}\b", text, re.M | re.I)]
    if missing or re.search(r"<take>|TODO|\.\.\.\s*$", text, re.M):
        sys.exit(f"[studio] {p} is incomplete -- "
                 f"{'missing sections: ' + ', '.join(missing) if missing else 'template placeholders left'}")
    return p


def guides_html(assets: Path) -> str:
    from safezone import guides_png
    shutil.copyfile(guides_png(), assets / "ig-guides.png")
    return (f'<img id="{GUIDES_ID}" src="assets/ig-guides.png" style="position:absolute;left:0;top:0;'
            f'width:1080px;height:1920px;z-index:9999;pointer-events:none;"/>')
