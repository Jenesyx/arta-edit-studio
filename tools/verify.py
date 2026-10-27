"""Post-render QA: measure the delivered file against the delivery contract.

    python tools/verify.py <video-name>

Checks canvas, fps, loudness, true peak, caption word ceiling, and that the
final folder carries every artifact. Exits non-zero if anything is off spec.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import config as C

REQUIRED_FILES = ["{name}.mp4", "subtitles/captions.fa.srt", "transcript.json",
                  "captions.json", "brand-snapshot.md"]
# Showcase Reels (showcase_build.py) carry no captions by request.
SHOWCASE_FILES = ["{name}.mp4", "showcase.json", "transcript.json", "config-snapshot.json"]
# Story Reels (story_build.py): full-frame speaker + B-roll, also caption-free.
OVERLAY_FILES = ["{name}.mp4", "overlay.json", "transcript.json", "config-snapshot.json"]


def loudness(path: Path) -> dict:
    proc = C.run([
        "ffmpeg", "-hide_banner", "-nostats", "-i", str(path),
        "-af", f"loudnorm=I={C.LUFS_TARGET}:TP={C.TRUE_PEAK}:LRA={C.LRA}:print_format=json",
        "-f", "null", "-",
    ])
    blob = re.findall(r"\{[^{}]*\"input_i\"[\s\S]*?\}", proc.stderr)
    if not blob:
        raise RuntimeError("could not measure loudness")
    return json.loads(blob[-1])


def frames(path: Path, out_dir: Path, times: list[float]) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    made = []
    for t in times:
        p = out_dir / f"frame_{t:06.2f}.png"
        C.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{t}", "-i", str(path),
               "-frames:v", "1", "-q:v", "2", str(p)])
        made.append(p)
    return made


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Verify a delivered Reel")
    ap.add_argument("video")
    ap.add_argument("--frames", type=int, default=6, help="how many QA stills to pull")
    args = ap.parse_args(argv)

    C.ensure_ffmpeg()
    name = C.find_raw(args.video).stem
    fd = C.final_dir_for(name)
    mp4 = fd / f"{name}.mp4"
    if not mp4.exists():
        print(f"FAIL  {mp4} does not exist", file=sys.stderr)
        return 1

    fails: list[str] = []
    meta = C.probe(mp4)

    def check(label: str, ok: bool, detail: str) -> None:
        print(f"{'PASS' if ok else 'FAIL'}  {label:<22} {detail}")
        if not ok:
            fails.append(label)

    check("canvas", meta["width"] == C.WIDTH and meta["height"] == C.HEIGHT,
          f"{meta['width']}x{meta['height']} (want {C.WIDTH}x{C.HEIGHT})")
    check("fps", abs(meta["fps"] - C.FPS) < 0.05, f"{meta['fps']:.3f} (want {C.FPS})")
    check("audio", meta["has_audio"], "present" if meta["has_audio"] else "MISSING")

    if meta["has_audio"]:
        ln = loudness(mp4)
        i, tp = float(ln["input_i"]), float(ln["input_tp"])
        check("loudness", abs(i - C.LUFS_TARGET) <= 1.0,
              f"{i:.2f} LUFS (want {C.LUFS_TARGET} +/- 1.0)")
        check("true peak", tp <= C.TRUE_PEAK + 0.3,
              f"{tp:.2f} dBTP (ceiling {C.TRUE_PEAK})")

    caps_path = fd / "captions.json"
    if caps_path.exists():
        raw = C.read_json(caps_path)
        # persian-reel writes a flat list; the older builder wrapped it in "groups".
        groups = raw["groups"] if isinstance(raw, dict) else raw
        # Lines are chunked on pauses now, so the meaningful cap is pill WIDTH,
        # not a word count -- a 4-word line of long words still overflows.
        worst = max((len(g.get("text", "")) for g in groups), default=0)
        check("caption width", worst <= 30,
              f"longest line {worst} chars (pill fits ~30)")

    cl_path = fd / "cutlist.json"
    if cl_path.exists() and "stats" in C.read_json(cl_path):
        st = C.read_json(cl_path)["stats"]
        long_pauses = [r for r in C.read_json(cl_path)["removed"]
                       if r["reason"] == "pause" and r["end"] - r["start"] > C.PAUSE_THRESHOLD]
        check("take cleaned", st["words_removed"] > 0 or long_pauses,
              f"{st['words_removed']} words + {len(long_pauses)} pauses removed, "
              f"{st['source_duration']:.1f}s -> {st['output_duration']:.1f}s")

    required = (SHOWCASE_FILES if (fd / "showcase.json").exists()
                else OVERLAY_FILES if (fd / "overlay.json").exists() else REQUIRED_FILES)
    missing = [f.format(name=name) for f in required
               if not (fd / f.format(name=name)).exists()]
    check("deliverables", not missing, "all present" if not missing else f"missing {missing}")

    # A same-basename .srt beside the mp4 makes players draw a SECOND set of
    # subtitles under the burned-in ones. It must live in subtitles/ instead.
    # Any subtitle file whose name starts with the video's basename will be
    # auto-loaded by players -- from this folder OR from subtitles/ / subs/.
    strays = [str(p.relative_to(fd)) for p in fd.rglob("*")
              if p.suffix.lower() in {".srt", ".vtt", ".ass", ".ssa"}
              and p.stem.lower().startswith(name.lower())]
    check("no sidecar subs", not strays,
          "no auto-loadable sidecar" if not strays
          else f"would double-render: {strays}")


    step = meta["duration"] / (args.frames + 1)
    stills = frames(mp4, fd / "qa", [round(step * (i + 1), 2) for i in range(args.frames)])
    print(f"\nQA stills: {stills[0].parent}  ({len(stills)} frames)")

    print("\n" + ("ALL CHECKS PASSED" if not fails else f"FAILED: {', '.join(fails)}"))
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
