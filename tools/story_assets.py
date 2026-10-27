"""Asset prep for /reel-story takes. B-roll picks come from tools/story_<slug>.py.

    python tools/story_assets.py <take> catalog   B-roll contact strips + NOTES.md (cached per clip)
    python tools/story_assets.py <take> all       mascot + logo + broll + tiles into the project
    python tools/story_assets.py <take> matte     person cut-out of the take (~8 min, CPU)
    (single steps: mascot | broll | tiles)

  * mascot: every image in brand.mascot_dir (reel.config.json). PNGs that already
    have transparency are copied. Images with a BAKED background (AI image tools
    often paint a white or checkerboard "transparency") get one: background =
    low-saturation bright pixels connected to the border; 1px erode + feather.
    Images whose border is not light (a logo on a coloured square) are copied as-is.
    Optional brand.mascot_crops cuts poses out of a character sheet:
      "mascot_crops": {"owl-teacher": {"file": "sheet.png", "crop": [x, y, w, h]}}
    Output name = file stem (lower-case, spaces -> "-"); cached in work/_brand/.
  * logo: brand.logo -> assets/brand/logo.png in the composition.
  * B-roll: phone clips are often 4K HEVC with rotation metadata, variable fps and
    sometimes HLG HDR. Each pick is trimmed to H.264 1080x1920 CFR 30, muted (the
    take's own mix is the only audio), sped up / mirrored on request, HDR
    tone-mapped to BT.709, keyframe every second.
  * tiles: small stills for the mosaic zoom-out.
  * matte: hyperframes remove-background -> work/<take>/matte/fg.webm (VP9 alpha),
    the cut-out that lets giant words sit BEHIND the speaker.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import config as C  # noqa: E402
from story_build import slug, take_module  # noqa: E402

BRAND = C.CFG["brand"]
MASCOT_DIR = C.ROOT / BRAND.get("mascot_dir", "assets/mascot")
MASCOT_CACHE = C.WORK_DIR / "_brand" / "mascot"
CATALOG = C.WORK_DIR / "_catalog"

# One HLG-tagged clip makes HyperFrames auto-promote the WHOLE render to HDR
# (HEVC Main10 BT.2020, dim on SDR screens) via its layered-composite path --
# on which timed overlay clips also stopped hiding. Tone-map to BT.709 here.
HDR_TRC = {"arib-std-b67", "smpte2084"}
TONEMAP = ("zscale=t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,"
           "tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p,")
SDR_TAGS = ["-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709"]

NOTES_HEAD = """# {folder} — what each clip shows

Read this before picking B-roll; open a clip's strip (`<clip>.jpg`, 5 frames spread over
the clip, times printed by `story_assets.py <take> catalog`) only for clips not listed
or when a precise range matters. **Append a row for every new clip you inspect.**

| Clip | Len | Shows | Good for | Flags (HDR, mirrored, VFR) |
| --- | --- | --- | --- | --- |
"""


def out_name(stem: str) -> str:
    return re.sub(r"[^0-9a-z]+", "-", stem.lower()).strip("-")


def has_alpha(img: np.ndarray) -> bool:
    return img.ndim == 3 and img.shape[2] == 4 and int(img[..., 3].min()) < 250


def cutout(img: np.ndarray, out: Path) -> bool:
    """Remove a baked light background. False when the border isn't light (keep as-is)."""
    img = img[..., :3]
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    cand = ((hsv[..., 1] < 34) & (hsv[..., 2] > 214)).astype(np.uint8)
    border = np.concatenate([cand[0], cand[-1], cand[:, 0], cand[:, -1]])
    if border.mean() < 0.6:
        return False
    n, lab = cv2.connectedComponents(cand, connectivity=4)
    edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]])))
    edge.discard(0)
    alpha = np.where(np.isin(lab, list(edge)), 0, 255).astype(np.uint8)
    # drop specks of leftover checkerboard, then shave the white fringe
    alpha = cv2.morphologyEx(alpha, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    alpha = cv2.erode(alpha, np.ones((3, 3), np.uint8), iterations=1)
    alpha = cv2.GaussianBlur(alpha, (0, 0), 1.0)
    ys, xs = np.where(alpha > 8)
    pad = 6
    y0, y1 = max(ys.min() - pad, 0), min(ys.max() + pad, alpha.shape[0])
    x0, x1 = max(xs.min() - pad, 0), min(xs.max() + pad, alpha.shape[1])
    cv2.imencode(".png", np.dstack([img, alpha])[y0:y1, x0:x1])[1].tofile(str(out))
    return True


def read_img(p: Path) -> np.ndarray:
    return cv2.imdecode(np.fromfile(str(p), np.uint8), cv2.IMREAD_UNCHANGED)


def mascot(pub: Path) -> None:
    dst = pub / "mascot"
    dst.mkdir(parents=True, exist_ok=True)
    MASCOT_CACHE.mkdir(parents=True, exist_ok=True)
    jobs = [(out_name(p.stem), p, None) for p in sorted(MASCOT_DIR.glob("*"))
            if p.suffix.lower() in C.IMAGE_EXTS] if MASCOT_DIR.is_dir() else []
    jobs += [(name, MASCOT_DIR / spec["file"], spec["crop"])
             for name, spec in BRAND.get("mascot_crops", {}).items()]
    for name, src, crop in jobs:
        cached = MASCOT_CACHE / f"{name}.png"
        if not cached.exists() or cached.stat().st_mtime < src.stat().st_mtime:
            img = read_img(src)
            if crop:
                x, y, w, h = crop
                img = img[y:y + h, x:x + w]
            if has_alpha(img):
                how = "has alpha"
                cv2.imencode(".png", img)[1].tofile(str(cached))
            elif cutout(img, cached):
                how = "background removed"
            else:
                how = "kept as-is (non-light border)"
                cv2.imencode(".png", img)[1].tofile(str(cached))
            print(f"[mascot] {name}.png  <- {src.name}{' crop' if crop else ''}  ({how})")
        (dst / cached.name).write_bytes(cached.read_bytes())
    print(f"[mascot] {len(jobs)} images -> {dst}" if jobs else
          f"[mascot] none ({MASCOT_DIR} empty) -- scenes must not use owl()/mascot images")
    logo = C.ROOT / BRAND.get("logo", "")
    if BRAND.get("logo") and logo.is_file():
        (pub / "brand").mkdir(parents=True, exist_ok=True)
        cv2.imencode(".png", read_img(logo))[1].tofile(str(pub / "brand" / "logo.png"))
        print(f"[logo] {logo.name} -> {pub / 'brand' / 'logo.png'}")


def probe_v(src: Path, entries: str) -> str:
    return C.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                  entries, "-of", "csv=p=0", str(src)]).stdout.strip().strip(",")


def is_hdr(src: Path) -> bool:
    return probe_v(src, "stream=color_transfer") in HDR_TRC


def trim(src_dir: Path, pub: Path, name: str, clip: str, ss: float, dur: float, speed: float,
         mirrored: bool) -> None:
    out = pub / "broll" / f"{name}.mp4"
    src = src_dir / clip
    vf = TONEMAP if is_hdr(src) else ""
    vf += "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1"
    if speed != 1.0:
        vf += f",setpts=PTS/{speed}"
    if mirrored:
        vf += ",hflip"
    vf += ",fps=30"
    # keyframe every second: the renderer warns that sparse GOPs freeze on seek
    C.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{ss}", "-t", f"{dur}",
           "-i", str(src), "-vf", vf, "-an", "-c:v", "libx264",
           "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", "-g", "30",
           "-keyint_min", "30", *SDR_TAGS, "-movflags", "+faststart", str(out)])
    print(f"[broll] {out.name} <- {clip} @{ss}s x{speed} = {C.probe(out)['duration']:.2f}s")


def tile(src_dir: Path, pub: Path, i: int, clip: str, t: float) -> None:
    out = pub / "tiles" / f"t{i:02d}.jpg"
    src = src_dir / clip
    vf = (TONEMAP if is_hdr(src) else "") + "scale=270:480:force_original_aspect_ratio=increase,crop=270:480"
    C.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{t}", "-i", str(src),
           "-frames:v", "1", "-vf", vf, "-q:v", "3", str(out)])


def catalog(src_dir: Path) -> None:
    """One 5-frame strip per clip (cached by mtime) + sheets of 6 strips to look at."""
    out = CATALOG / src_dir.name
    out.mkdir(parents=True, exist_ok=True)
    notes = out / "NOTES.md"
    if not notes.exists():
        notes.write_text(NOTES_HEAD.format(folder=src_dir.relative_to(C.ROOT).as_posix()), encoding="utf-8")
    clips = sorted(p for p in src_dir.iterdir() if p.suffix.lower() in C.VIDEO_EXTS)
    if not clips:
        print(f"[catalog] no clips in {src_dir}")
        return
    for p in clips:
        strip = out / f"{p.stem}.jpg"
        dur = float(C.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                           "-of", "csv=p=0", str(p)]).stdout.strip())
        hdr = is_hdr(p)
        if not strip.exists() or strip.stat().st_mtime < p.stat().st_mtime:
            vf = (TONEMAP if hdr else "") + f"fps={5 / dur:.5f},scale=-2:300,tile=5x1"
            C.run(["ffmpeg", "-y", "-v", "error", "-i", str(p), "-vf", vf, "-frames:v", "1", str(strip)])
        print(f"[catalog] {p.name:<16} {dur:6.1f}s  {probe_v(p, 'stream=width,height,r_frame_rate')}"
              f"{'  HDR' if hdr else ''}  strip frames at "
              f"{', '.join(f'{dur * (k + .5) / 5:.1f}' for k in range(5))}s")
    for k in range(0, len(clips), 6):
        group = [out / f"{p.stem}.jpg" for p in clips[k:k + 6]]
        sheet = out / f"_sheet_{k // 6 + 1}.jpg"
        args = sum((["-i", str(g)] for g in group), [])
        graph = ("".join(f"[{i}]scale=840:300:force_original_aspect_ratio=decrease,pad=840:300:0:0[s{i}];"
                         for i in range(len(group)))
                 + "".join(f"[s{i}]" for i in range(len(group))) + f"vstack=inputs={len(group)}"
                 if len(group) > 1 else "[0]copy")
        C.run(["ffmpeg", "-y", "-v", "error", *args, "-filter_complex", graph, str(sheet)])
        print(f"[catalog] {sheet}  = {', '.join(p.stem for p in clips[k:k + 6])}")
    print(f"[catalog] notes: {notes}")


def matte(name: str) -> None:
    out = C.work_dir_for(name) / "matte" / "fg.webm"
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = f'npx hyperframes remove-background "{C.find_raw(name)}" -o "{out}" --quality best'
    print(f"[matte] {cmd}  (CPU, ~190 ms/frame -- do not run ffmpeg jobs alongside)")
    subprocess.run(cmd, shell=True, check=True, cwd=str(C.ROOT))
    print(f"[matte] {out}")


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__)
        return 2
    name, step = C.find_raw(argv[0]).stem, argv[1]
    try:
        mod = take_module(name)
    except ModuleNotFoundError:
        if step not in ("catalog", "matte"):
            sys.exit(f"tools/story_{slug(name)}.py missing -- write the take module first")
        mod = None
    src_dir = Path(getattr(mod, "BROLL_DIR", C.BROLL_DIR))
    pub = C.work_dir_for(name) / "sc" / "public" / "assets"
    for sub in ("broll", "tiles"):
        (pub / sub).mkdir(parents=True, exist_ok=True)
    if step == "catalog":
        catalog(src_dir)
    if step == "matte":
        matte(name)
    if step in ("mascot", "all"):
        mascot(pub)
    if step in ("broll", "all"):
        mirrored = getattr(mod, "MIRRORED", set())
        for n, (clip, ss, dur, speed) in getattr(mod, "BROLL", {}).items():
            trim(src_dir, pub, n, clip, ss, dur, speed, n in mirrored)
    if step in ("tiles", "all"):
        tiles = getattr(mod, "TILES", [])
        for i, (clip, t) in enumerate(tiles):
            tile(src_dir, pub, i, clip, t)
        print(f"[tiles] {len(tiles)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
