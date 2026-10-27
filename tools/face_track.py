"""Track the speaker's face through a take -> work/<take>/face.json + framing numbers.

    python tools/face_track.py <take> [--split 864]

Samples every 0.2 s with OpenCV's Haar frontal-face cascade (largest face per
frame; frames with none are skipped). Prints the median face centre -- the
pivot story_build.py uses for punch-ins / bubble / floods -- and, for a split
layout (/reel-split), the speaker_y that puts the face on the centre line of
the speaker region below the panel.

face.json rows: {"t": seconds, "face": [x, y, w, h]} in take pixels (1080x1920).
Needs opencv-python-headless < 5 in .venv (OpenCV 5 dropped CascadeClassifier).
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

import cv2

sys.path.insert(0, str(Path(__file__).parent))
import config as C  # noqa: E402

STEP = 0.2


def track(video: Path) -> list[dict]:
    det = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    cap = cv2.VideoCapture(str(video))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    rows, k = [], 0
    while k < n:
        cap.set(cv2.CAP_PROP_POS_FRAMES, k)
        ok, frame = cap.read()
        if not ok:
            break
        small = cv2.resize(frame, None, fx=0.5, fy=0.5)
        faces = det.detectMultiScale(cv2.cvtColor(small, cv2.COLOR_BGR2GRAY), 1.1, 6, minSize=(80, 80))
        if len(faces):
            x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
            rows.append({"t": round(k / fps, 2), "face": [int(x * 2), int(y * 2), int(w * 2), int(h * 2)]})
        k += max(1, round(STEP * fps))
    cap.release()
    return rows


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("take")
    ap.add_argument("--split", type=int, default=864, help="panel height for /reel-split (default 864 = 45%%)")
    args = ap.parse_args(argv)
    video = C.find_raw(args.take)
    rows = track(video)
    if not rows:
        print("[face] no face found -- set FACE / speaker_y by eye from a still")
        return 1
    out = C.work_dir_for(video.stem) / "face.json"
    out.write_text(json.dumps(rows), encoding="utf-8")
    cx = [x + w / 2 for x, y, w, h in (r["face"] for r in rows)]
    cy = [y + h / 2 for x, y, w, h in (r["face"] for r in rows)]
    q = statistics.quantiles(cy, n=20)
    mid = (args.split + C.HEIGHT) / 2
    print(f"[face] {out}  ({len(rows)} samples)")
    print(f"[face] centre median ({statistics.median(cx):.0f}, {statistics.median(cy):.0f}) "
          f"centre-y p5-p95 {q[0]:.0f}-{q[-1]:.0f}  head top ~{min(y for x, y, w, h in (r['face'] for r in rows)):.0f}")
    print(f"[face] story FACE = ({statistics.median(cx):.0f}, {statistics.median(cy):.0f})")
    print(f"[face] split {args.split}: speaker_y = {mid - statistics.median(cy):.0f} "
          f"(face centre -> speaker-region centre line y={mid:.0f})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
