"""Shared paths, settings and helpers for Arta Edit Studio.

Settings come from reel.config.json at the repo root (copy it from
reel.config.example.json). Anything missing falls back to the example values,
so a fresh clone runs before you have personalised anything.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

# Farsi goes to stdout constantly. The Windows console defaults to cp1252, which
# raises UnicodeEncodeError mid-print -- and a crash inside a progress print can
# abort a tool after it has done its work but before it writes the result.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):  # pragma: no cover - non-tty streams
        pass

ROOT = Path(__file__).resolve().parent.parent

RAW_DIR = ROOT / "raw"
FONT_DIR = ROOT / "font"
FINAL_DIR = ROOT / "final"
WORK_DIR = ROOT / "work"
ASSETS_DIR = ROOT / "assets"

VIDEO_EXTS = {".mp4", ".mov", ".mkv", ".m4v", ".avi", ".webm", ".mts", ".mpg"}
FONT_EXTS = {".ttf", ".otf", ".woff2", ".woff"}
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp"}


def _merge(base: dict, over: dict) -> dict:
    out = dict(base)
    for k, v in over.items():
        out[k] = _merge(base[k], v) if isinstance(v, dict) and isinstance(base.get(k), dict) else v
    return out


def _load_config() -> dict:
    example = json.loads((ROOT / "reel.config.example.json").read_text(encoding="utf-8"))
    mine = ROOT / "reel.config.json"
    if mine.exists():
        return _merge(example, json.loads(mine.read_text(encoding="utf-8")))
    return example


CFG = _load_config()

# ---------------------------------------------------------------- delivery ---

WIDTH = 1080
HEIGHT = 1920
FPS = 30
SAMPLE_RATE = 48000

LUFS_TARGET = float(CFG["loudness"]["lufs"])
TRUE_PEAK = float(CFG["loudness"]["true_peak"])
LRA = 11.0
PAUSE_THRESHOLD = 0.30       # verify.py: what counts as a long pause in a cut list

HANDLE = CFG["creator"]["handle"]
BROLL_DIR = ROOT / CFG["broll_dir"]

# ------------------------------------------------------------------ split ---
# /reel-split panel palette: cream ground, ink type, warm accent.
COLORS = dict(CFG["split_palette"])

# -------------------------------------------------------------- whisper -----

WHISPER_MODEL = os.environ.get("REEL_WHISPER_MODEL", CFG["whisper_model"])
WHISPER_LANG = CFG["language"]


# ------------------------------------------------------------- utilities ----

def font(kind: str) -> Path:
    """Font file for 'fa' | 'en' | 'display' from the config, with a clear error."""
    p = ROOT / CFG["fonts"][kind]
    if not p.exists():
        raise FileNotFoundError(
            f"font '{kind}' not found at {p}. Put the file in font/ and set fonts.{kind} in "
            f"reel.config.json (see README > Fonts).")
    return p


def brand_font() -> Path:
    return font("fa")


def gsap_js() -> Path:
    p = ROOT / "node_modules" / "gsap" / "dist" / "gsap.min.js"
    if not p.exists():
        raise FileNotFoundError("node_modules/gsap missing -- run `npm install` in the repo root")
    return p


def ensure_ffmpeg() -> None:
    if not (shutil.which("ffmpeg") and shutil.which("ffprobe")):
        raise RuntimeError("ffmpeg/ffprobe not on PATH -- see README > Installation")


def run(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    """Run a command, raising with captured stderr on failure."""
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                          errors="replace", **kw)
    if proc.returncode != 0:
        tail = "\n".join((proc.stderr or "").splitlines()[-25:])
        raise RuntimeError(f"command failed ({proc.returncode}): {' '.join(cmd[:4])}...\n{tail}")
    return proc


def probe(path: Path) -> dict:
    """ffprobe a media file into a flat dict (geometry after rotation)."""
    ensure_ffmpeg()
    data = json.loads(run(["ffprobe", "-v", "error", "-print_format", "json",
                           "-show_streams", "-show_format", str(path)]).stdout)
    video = next((s for s in data["streams"] if s["codec_type"] == "video"), None)
    audio = next((s for s in data["streams"] if s["codec_type"] == "audio"), None)
    if video is None:
        raise RuntimeError(f"no video stream in {path}")
    num, _, den = video.get("r_frame_rate", "30/1").partition("/")
    # ffmpeg applies the display matrix while decoding, so report the EFFECTIVE
    # geometry -- a phone portrait clip must never be transposed twice.
    w, h = int(video["width"]), int(video["height"])
    if _rotation(video) in (90, 270):
        w, h = h, w
    return {"path": str(path), "width": w, "height": h, "fps": float(num) / float(den or 1),
            "duration": float(data["format"]["duration"]), "has_audio": audio is not None,
            "audio_channels": int(audio["channels"]) if audio else 0}


def _rotation(video: dict) -> int:
    for sd in video.get("side_data_list", []) or []:
        if "rotation" in sd:
            return int(sd["rotation"]) % 360
    try:
        return int((video.get("tags", {}) or {}).get("rotate", 0)) % 360
    except (TypeError, ValueError):
        return 0


def find_raw(name: str) -> Path:
    """Resolve a video name against raw/ (extension and case optional, substring ok)."""
    candidate = Path(name)
    if candidate.is_file():
        return candidate.resolve()
    if (RAW_DIR / name).is_file():
        return (RAW_DIR / name).resolve()
    vids = [p for p in RAW_DIR.iterdir() if p.is_file() and p.suffix.lower() in VIDEO_EXTS] \
        if RAW_DIR.is_dir() else []
    stem = Path(name).stem.lower().replace(" ", "").replace("-", "").replace("_", "")
    norm = lambda p: p.stem.lower().replace(" ", "").replace("-", "").replace("_", "")
    matches = [p for p in vids if norm(p) == stem] or [p for p in vids if stem in norm(p)]
    if not matches:
        raise FileNotFoundError(f"no video matching {name!r} in {RAW_DIR}. "
                                f"available: {sorted(p.name for p in vids) or '(none)'}")
    return matches[0].resolve()


def work_dir_for(name: str) -> Path:
    d = WORK_DIR / name
    d.mkdir(parents=True, exist_ok=True)
    return d


def final_dir_for(name: str) -> Path:
    d = FINAL_DIR / name
    d.mkdir(parents=True, exist_ok=True)
    return d


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))
