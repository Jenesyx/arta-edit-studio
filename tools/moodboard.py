"""Read a creator's mood board so the edit follows THEIR taste, not a generic AI look.

    python tools/moodboard.py <take>

Looks in moodboard/<take>/ first, then moodboard/default/ (folder set by
`moodboard_dir` in reel.config.json). A mood board is any mix of:
  images   screenshots of Reels, posts, designs, fonts, colours they like (.png .jpg .webp)
  videos   short screen recordings of motion / editing they like (.mp4 .mov), <= ~30 s each
  notes    notes.md / notes.txt: what they like, what they hate, 3-5 mood words
  links    links.txt: reference URLs (listed only; nothing is downloaded)

Writes to work/<take>/moodboard/:
  board_N.jpg    labelled contact sheets of everything (look at all of them)
  palette.json   dominant colours across the images + share, palette.png swatch strip
  pace.json      per reference video: cuts per minute and average motion (pace of edit)
  summary.md     everything above in one page, plus the notes text

Next step is NOT automatic: Claude writes work/<take>/style.md from this (template:
docs/style-brief.md) and the user approves it. The builders refuse to run without it.
Exit 2 when no mood board exists -- ask the creator to make one (docs/moodboard.md).
"""

from __future__ import annotations

import json
import re
import shutil
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import config as C  # noqa: E402

BOARD_ROOT = C.ROOT / C.CFG.get("moodboard_dir", "moodboard")
TILE_W, TILE_H, COLS = 300, 420, 4


def find_board(name: str) -> Path | None:
    for d in (BOARD_ROOT / name, BOARD_ROOT / "default"):
        if d.is_dir() and any(p.is_file() and not p.name.startswith(".") and p.name.lower() != "readme.md"
                              for p in d.rglob("*")):
            return d
    return None


def read_img(p: Path):
    img = cv2.imdecode(np.fromfile(str(p), np.uint8), cv2.IMREAD_COLOR)
    return img


def video_frames(p: Path, n: int = 4) -> list[np.ndarray]:
    dur = C.probe(p)["duration"]
    # through a temp file: C.run pipes are text-mode and would mangle PNG bytes
    tmp = C.WORK_DIR / "_tmp_mb"
    tmp.mkdir(parents=True, exist_ok=True)
    frames = []
    for k in range(n):
        t = dur * (k + 0.5) / n
        f = tmp / f"f{k}.png"
        C.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{t:.2f}", "-i", str(p), "-frames:v", "1",
               "-vf", "scale=-2:720", str(f)])
        frames.append(read_img(f))
    shutil.rmtree(tmp, ignore_errors=True)
    return frames


def pace(p: Path) -> dict:
    """Cuts per minute (scene changes) and mean frame-to-frame motion of a reference clip."""
    dur = C.probe(p)["duration"]
    log = C.run(["ffmpeg", "-hide_banner", "-i", str(p), "-vf",
                 "scale=270:-2,select='gt(scene,0.32)',showinfo", "-an", "-f", "null", "-"]).stderr
    cuts = len(re.findall(r"pts_time:", log))
    cap = cv2.VideoCapture(str(p))
    prev, diffs, k = None, [], 0
    while True:
        ok, fr = cap.read()
        if not ok:
            break
        if k % 3 == 0:
            g = cv2.cvtColor(cv2.resize(fr, (90, 160)), cv2.COLOR_BGR2GRAY).astype(np.float32)
            if prev is not None:
                diffs.append(float(np.abs(g - prev).mean()))
            prev = g
        k += 1
    cap.release()
    motion = float(np.mean(diffs)) if diffs else 0.0
    feel = "calm" if motion < 6 else "lively" if motion < 14 else "very energetic"
    return {"file": p.name, "seconds": round(dur, 1), "cuts_per_min": round(cuts / max(dur, 1) * 60, 1),
            "motion": round(motion, 1), "feel": feel}


def tile(img: np.ndarray, label: str) -> np.ndarray:
    h, w = img.shape[:2]
    s = min(TILE_W / w, (TILE_H - 34) / h)
    im = cv2.resize(img, (max(1, int(w * s)), max(1, int(h * s))), interpolation=cv2.INTER_AREA)
    t = np.full((TILE_H, TILE_W, 3), 32, np.uint8)
    y0, x0 = (TILE_H - 34 - im.shape[0]) // 2, (TILE_W - im.shape[1]) // 2
    t[y0:y0 + im.shape[0], x0:x0 + im.shape[1]] = im
    cv2.putText(t, label[:34], (6, TILE_H - 11), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (235, 235, 235), 1, cv2.LINE_AA)
    return t


def sheets(tiles: list[np.ndarray], out_dir: Path) -> list[Path]:
    paths = []
    per = COLS * 3
    for k in range(0, len(tiles), per):
        group = tiles[k:k + per]
        rows = []
        for r in range(0, len(group), COLS):
            row = group[r:r + COLS]
            row += [np.full((TILE_H, TILE_W, 3), 20, np.uint8)] * (COLS - len(row))
            rows.append(np.hstack(row))
        p = out_dir / f"board_{k // per + 1}.jpg"
        cv2.imencode(".jpg", np.vstack(rows), [cv2.IMWRITE_JPEG_QUALITY, 88])[1].tofile(str(p))
        paths.append(p)
    return paths


def palette(images: list[np.ndarray], k: int = 8) -> list[dict]:
    px = []
    for im in images:
        small = cv2.resize(im, (64, 64), interpolation=cv2.INTER_AREA).reshape(-1, 3)
        px.append(small)
    data = np.float32(np.vstack(px))
    crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.5)
    cv2.setRNGSeed(7)
    _, labels, centers = cv2.kmeans(data, k, None, crit, 4, cv2.KMEANS_PP_CENTERS)
    share = np.bincount(labels.ravel(), minlength=k) / len(labels)
    out = [{"hex": "#{:02X}{:02X}{:02X}".format(int(c[2]), int(c[1]), int(c[0])), "share": round(float(s), 3)}
           for c, s in zip(centers, share)]
    return sorted(out, key=lambda d: -d["share"])


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print(__doc__)
        return 2
    name = C.find_raw(argv[0]).stem
    board = find_board(name)
    if board is None:
        print(f"[moodboard] NO MOOD BOARD for '{name}'. Ask the creator to fill "
              f"{(BOARD_ROOT / name).relative_to(C.ROOT).as_posix()}/ (or moodboard/default/) with 5-15 "
              f"screenshots of Reels/designs they love, 1-3 short clips of motion they like and a notes.md "
              f"(mood words, likes, dislikes). Guide: docs/moodboard.md")
        return 2
    out = C.work_dir_for(name) / "moodboard"
    shutil.rmtree(out, ignore_errors=True)
    out.mkdir(parents=True)
    files = sorted(p for p in board.rglob("*") if p.is_file())
    tiles, imgs, paces, notes, links = [], [], [], [], []
    for p in files:
        ext = p.suffix.lower()
        if ext in C.IMAGE_EXTS:
            im = read_img(p)
            if im is not None:
                imgs.append(im)
                tiles.append(tile(im, p.name))
        elif ext in C.VIDEO_EXTS:
            for i, fr in enumerate(video_frames(p)):
                if fr is not None:
                    tiles.append(tile(fr, f"{p.name} [{i + 1}/4]"))
                    imgs.append(fr)
            paces.append(pace(p))
        elif p.name.lower().startswith("links"):
            links += [ln.strip() for ln in p.read_text(encoding="utf-8", errors="replace").splitlines() if ln.strip()]
        elif ext in (".md", ".txt") and p.name.lower() != "readme.md":
            notes.append(f"## {p.name}\n\n{p.read_text(encoding='utf-8', errors='replace').strip()}")
    if not tiles and not notes:
        print(f"[moodboard] {board} has no images, videos or notes")
        return 2
    sheet_paths = sheets(tiles, out) if tiles else []
    pal = palette(imgs) if imgs else []
    if pal:
        strip = np.zeros((120, 120 * len(pal), 3), np.uint8)
        for i, c in enumerate(pal):
            h = c["hex"].lstrip("#")
            strip[:, i * 120:(i + 1) * 120] = (int(h[4:6], 16), int(h[2:4], 16), int(h[0:2], 16))
        cv2.imencode(".png", strip)[1].tofile(str(out / "palette.png"))
    C.write_json(out / "palette.json", pal)
    C.write_json(out / "pace.json", paces)
    md = [f"# Mood board — {name}", "", f"Source: `{board.relative_to(C.ROOT).as_posix()}/` "
          f"({len(files)} files)", "", "## Sheets (look at every one)", ""]
    md += [f"- `{p.relative_to(C.ROOT).as_posix()}`" for p in sheet_paths] or ["- (no images)"]
    md += ["", "## Dominant colours", ""]
    md += [f"- `{c['hex']}` {c['share'] * 100:.0f} %" for c in pal] or ["- (no images)"]
    md += ["", "## Pace of reference videos", ""]
    md += [f"- {v['file']}: {v['cuts_per_min']} cuts/min, motion {v['motion']} ({v['feel']})"
           for v in paces] or ["- (no videos)"]
    md += ["", "## Links", ""] + ([f"- {u}" for u in links] or ["- (none)"])
    md += ["", "## Creator notes", ""] + (notes or ["(none — ask for mood words, likes and dislikes)"])
    (out / "summary.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"[moodboard] {board.relative_to(C.ROOT).as_posix()}: {len(imgs)} images/frames, "
          f"{len(paces)} videos, {len(notes)} notes, {len(links)} links")
    for p in sheet_paths:
        print(f"[moodboard] sheet {p}")
    print(f"[moodboard] palette {', '.join(c['hex'] for c in pal[:6])}")
    for v in paces:
        print(f"[moodboard] pace {v['file']}: {v['cuts_per_min']} cuts/min, {v['feel']}")
    print(f"[moodboard] summary {out / 'summary.md'}")
    print(f"[moodboard] NEXT: write work/{name}/style.md from docs/style-brief.md and get the creator's OK")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
