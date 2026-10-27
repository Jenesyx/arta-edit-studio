"""Motion lint: catch robotic or jerky animation before a 12-minute render.

    python tools/motion_check.py <take>

Reads the timeline script of work/<take>/sc/public/index.html and reports:
  linear     ease "none"/"linear" on a moving tween (x / y / scale / left / top) --
             looks mechanical. Fine only for continuous loops (rays, speed lines, tickers)
  jerky      a move shorter than 0.12 s that is not a deliberate shake (yoyo/repeat)
  jump       tl.set() teleporting x / y / scale mid-scene -- a hard jump, not a move
  defaults   a move with no ease at all (GSAP's default power1.out is weak)
and counts the smooth-motion helpers used (arcIn / arcOut / whip / mblur / settle / kf /
camTo). Rules and examples: docs/motion.md. Warnings only -- exit code is always 0.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import config as C  # noqa: E402

MOVE = re.compile(r"\b(x|y|scale|scaleX|scaleY|left|top|motionPath)\s*:")
LOOPS = re.compile(r"rays|spd|scan|bar|tick|marquee|tb-in|rotation:\s*\d+\s*,\s*duration:\s*[2-9]", re.I)
HELPERS = ["arcIn", "arcOut", "whip", "mblur", "settle", "kf", "camTo", "floaty"]


def tween_calls(js: str):
    """Yield (kind, text) for every tl.to/from/fromTo/set call, balanced on parentheses."""
    for m in re.finditer(r"\btl\.(to|from|fromTo|set)\(", js):
        depth, i = 1, m.end()
        while i < len(js) and depth:
            depth += {"(": 1, ")": -1}.get(js[i], 0)
            i += 1
        yield m.group(1), js[m.start():i]


def check(name: str) -> list[tuple[str, str]]:
    index = C.work_dir_for(name) / "sc" / "public" / "index.html"
    html = index.read_text(encoding="utf-8")
    js = html[html.rfind("<script>"):]
    issues = []
    for kind, call in tween_calls(js):
        to_part = call.split("},{", 1)[-1] if kind == "fromTo" else call
        if not MOVE.search(to_part):
            continue
        short = re.sub(r"\s+", " ", call)[:110]
        if kind == "set":
            if not re.search(r",\s*0(\.0+)?\s*\)$", call):
                issues.append(("jump", short))
            continue
        ease = re.search(r'ease\s*:\s*"([^"]+)"', to_part)
        dur = re.search(r"duration\s*:\s*([0-9.]+)", to_part)
        loop = bool(LOOPS.search(call)) or "repeat" in call
        if ease and ease.group(1) in ("none", "linear") and not loop:
            issues.append(("linear", short))
        if dur and float(dur.group(1)) < 0.12 and not loop:
            issues.append(("jerky", short))
        if not ease and "keyframes" not in call and "EASE." not in to_part:
            issues.append(("defaults", short))
    return issues


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print(__doc__)
        return 2
    name = C.find_raw(argv[0]).stem
    issues = check(name)
    js = (C.work_dir_for(name) / "sc" / "public" / "index.html").read_text(encoding="utf-8")
    used = {h: len(re.findall(rf"\b{h}\(", js[js.rfind('<script>'):])) for h in HELPERS}
    for kind, call in issues:
        print(f"[motion] {kind:<8} {call}")
    counts = {k: sum(1 for i in issues if i[0] == k) for k in ("linear", "jerky", "jump", "defaults")}
    print(f"[motion] {sum(counts.values())} warning(s): " + ", ".join(f"{k} {v}" for k, v in counts.items()))
    print("[motion] smooth helpers used: " + (", ".join(f"{h} {n}" for h, n in used.items() if n) or "none"))
    if not any(used.values()):
        print("[motion] WARNING: no curved motion, motion blur or keyframes used -- see docs/motion.md")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
