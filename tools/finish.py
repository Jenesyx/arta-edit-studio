"""Render + package a built Reel (both /reel-story and /reel-split).

    python tools/finish.py <take> --seconds 12   quick REAL render of the first N s -> sc/quick.mp4
    python tools/finish.py <take>                full render -> final/<take>/ + verify + QA sheet
    python tools/finish.py <take> --skip-render  re-package an existing sc/designed.mp4

Expects the composition at work/<take>/sc/public/index.html. Bakes in what
broke earlier renders:
  * lint errors abort before a 12-minute render starts
  * Node gets a 12 GB heap: with ~20 videos the frame injection blew the 4 GB
    default and the render died silently mid-capture (0xC0000409 / exit 127)
  * "HDR auto-promotion" in the log = some source is still HDR-tagged; the
    output is then HEVC 10-bit and timed overlays stop hiding -> hard fail
  * the take's own audio is remuxed untouched (the render re-mixes it)
  * nothing renders while overlays sit in Instagram's UI zones (tools/safezone.py)
    or while the --guides preview overlay is still in the composition
  * motion lint warnings (tools/motion_check.py) are printed first
Snapshots are not proof: always look at the quick render / QA sheet.
"""

from __future__ import annotations

import argparse
import importlib
import inspect
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import config as C  # noqa: E402

ROOT_DUR = re.compile(r'(data-composition-id="main" data-start="0" data-duration=")([0-9.]+)(")')


def npx(args: str, cwd: Path, log: Path) -> int:
    env = dict(os.environ, NODE_OPTIONS=f"--max-old-space-size={C.CFG['render']['node_heap_mb']}")
    with open(log, "w", encoding="utf-8", errors="replace") as fh:
        return subprocess.run(f"npx {args}", shell=True, cwd=str(cwd), env=env,
                              stdout=fh, stderr=subprocess.STDOUT).returncode


def lint(sc: Path) -> None:
    log = sc / "lint.log"
    npx("hyperframes lint public", sc, log)
    m = re.search(r"(\d+) error\(s\)", log.read_text(encoding="utf-8", errors="replace"))
    if not m or int(m.group(1)):
        sys.exit(f"[finish] lint errors -- see {log}")
    print(f"[finish] lint: 0 errors")


def render(sc: Path, out: str, workers: int) -> Path:
    log = sc / ("render.log" if out == "designed.mp4" else "quick.log")
    while True:
        print(f"[finish] rendering -> {sc / out}  ({workers} worker(s), log {log})", flush=True)
        rc = npx(f"hyperframes render public -q delivery --video-frame-format png -w {workers} -o {out}", sc, log)
        text = log.read_text(encoding="utf-8", errors="replace")
        if "HDR auto-promotion" in text:
            sys.exit("[finish] FAIL: HDR auto-promotion -- a source is still HDR-tagged. Re-trim it through "
                     "story_assets.py (tone-maps HLG/PQ) and render again.")
        if rc == 0 and "Render complete" in text:
            break
        # A renderer that vanishes mid-capture with no error text ran out of memory
        # (Windows fail-fast 0xC0000409, or 127 from the shell). Fewer workers = less RAM.
        died = "Capturing frame" in text and not any(w in text for w in ("Error:", "[ERROR]"))
        if died and workers > 1:
            print(f"[finish] renderer died mid-capture (exit {rc}) -- low memory; retrying with 1 worker. "
                  f"Closing games / editors / browsers helps.", flush=True)
            workers = 1
            continue
        sys.exit(f"[finish] FAIL: render exit {rc} -- tail of {log}:\n" + "\n".join(text.splitlines()[-8:]))
    mp4 = sc / out
    v = C.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
               "stream=codec_name,pix_fmt,color_transfer", "-of", "csv=p=0", str(mp4)]).stdout.strip()
    print(f"[finish] {mp4.name}: {v}")
    return mp4


def sheet(mp4: Path, out: Path, every: float, cols: int = 10, guides: bool = False) -> Path:
    """Contact sheet; guides=True draws Instagram's UI zones over every frame."""
    out.parent.mkdir(parents=True, exist_ok=True)
    tile = f"fps=1/{every},scale=180:320,tile={cols}x3"
    if guides:
        from safezone import guides_png
        C.run(["ffmpeg", "-y", "-v", "error", "-i", str(mp4), "-i", str(guides_png()), "-filter_complex",
               f"[0:v][1:v]overlay=0:0,{tile}", "-frames:v", "1", str(out)])
    else:
        C.run(["ffmpeg", "-y", "-v", "error", "-i", str(mp4), "-vf", tile, "-frames:v", "1", str(out)])
    return out


def preflight(sc: Path, name: str, allow_safezone: bool) -> None:
    """Everything that must hold before spending minutes on a render."""
    if 'id="ig-guides"' in (sc / "public" / "index.html").read_text(encoding="utf-8"):
        sys.exit("[finish] the composition still has the --guides overlay -- rebuild without --guides")
    lint(sc)
    import motion_check
    import safezone
    issues = motion_check.check(name)
    if issues:
        print(f"[finish] motion: {len(issues)} warning(s) -- python tools/motion_check.py {name}")
    if safezone.report(safezone.check(name)) and not allow_safezone:
        sys.exit("[finish] FAIL: content inside Instagram's UI zones (see above). Move it, or pass "
                 "--allow-safezone if the creator explicitly accepts it.")


def plan_file(name: str, fd: Path) -> None:
    """Copy the edit plan beside the mp4 (verify.py keys the format off it)."""
    wd = C.work_dir_for(name)
    if (wd / "showcase.json").exists():
        shutil.copyfile(wd / "showcase.json", fd / "showcase.json")
        return
    slug = re.sub(r"[^0-9a-zA-Z]+", "_", name).strip("_").lower()
    mod = importlib.import_module(f"story_{slug}")
    plan = {"take": f"raw/{C.find_raw(name).name}",
            "builder": f"tools/story_build.py + tools/story_{slug}.py",
            "audio": "original take mix, remuxed untouched",
            "scenes": [{"scene": f.__name__, "what": inspect.getdoc(f)} for f in mod.SCENES],
            "broll": {k: {"clip": v[0], "from_s": v[1], "dur_s": v[2], "speed": v[3]}
                      for k, v in getattr(mod, "BROLL", {}).items()},
            "mirrored_flipped": sorted(getattr(mod, "MIRRORED", set()))}
    (fd / "overlay.json").write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Render and package a built Reel")
    ap.add_argument("take")
    ap.add_argument("--seconds", type=float, help="quick real render of the first N seconds only")
    ap.add_argument("--skip-render", action="store_true")
    ap.add_argument("--workers", type=int, default=int(C.CFG["render"]["workers"]))
    ap.add_argument("--allow-safezone", action="store_true",
                    help="render even if overlays sit in Instagram's UI zones")
    args = ap.parse_args(argv)

    take = C.find_raw(args.take)
    name = take.stem
    sc = C.work_dir_for(name) / "sc"
    index = sc / "public" / "index.html"
    if not index.exists():
        sys.exit(f"[finish] {index} missing -- build the composition first")

    if args.seconds:
        html = index.read_text(encoding="utf-8")
        if not ROOT_DUR.search(html):
            sys.exit("[finish] root data-duration not found in index.html")
        preflight(sc, name, args.allow_safezone)
        try:
            index.write_text(ROOT_DUR.sub(rf"\g<1>{args.seconds:g}\g<3>", html, count=1), encoding="utf-8")
            mp4 = render(sc, "quick.mp4", min(args.workers, 2))
        finally:
            index.write_text(html, encoding="utf-8")
        every = max(0.5, round(args.seconds / 30, 2))
        print(f"[finish] quick sheet ({every}s apart): {sheet(mp4, sc / 'quick_sheet.jpg', every)}")
        print(f"[finish] with Instagram zones: {sheet(mp4, sc / 'quick_sheet_guides.jpg', every, guides=True)}")
        return 0

    if not args.skip_render:
        preflight(sc, name, args.allow_safezone)
        render(sc, "designed.mp4", args.workers)
    designed = sc / "designed.mp4"
    fd = C.final_dir_for(name)
    fd.mkdir(parents=True, exist_ok=True)
    final = fd / f"{name}.mp4"
    C.run(["ffmpeg", "-y", "-v", "error", "-i", str(designed), "-i", str(take), "-map", "0:v",
           "-map", "1:a", "-c", "copy", "-movflags", "+faststart", str(final)])
    shutil.copyfile(C.work_dir_for(name) / "transcript.json", fd / "transcript.json")
    C.write_json(fd / "config-snapshot.json", C.CFG)
    plan_file(name, fd)
    for extra in ("style.md", "safezone.json"):
        if (C.work_dir_for(name) / extra).exists():
            shutil.copyfile(C.work_dir_for(name) / extra, fd / extra)
    print(f"[finish] {final}  ({final.stat().st_size / 1e6:.1f} MB, original audio)")
    shutil.rmtree(fd / "qa", ignore_errors=True)
    rc = subprocess.run([sys.executable, "-X", "utf8", str(Path(__file__).parent / "verify.py"), name,
                         "--frames", "10"]).returncode
    print(f"[finish] QA sheet (3 s apart): {sheet(final, fd / 'qa' / 'sheet.jpg', 3)}")
    print(f"[finish] with Instagram zones: {sheet(final, fd / 'qa' / 'sheet_guides.jpg', 3, guides=True)}")
    print("[finish] true-peak FAIL on a pre-mixed take is the creator's own mix -- report it, don't fix unasked")
    return rc


if __name__ == "__main__":
    sys.exit(main())
