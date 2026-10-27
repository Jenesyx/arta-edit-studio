"""Word-level Farsi transcription via local Whisper.

Produces two artifacts in the work dir:
  audio.wav        48 kHz mono, what everything downstream measures against
  transcript.json  flat word array: [{ "text", "start", "end", "prob" }, ...]

The flat-word shape is deliberate -- it is what hyperframes' talking-head-recut
and captions.py both expect, and it is the only shape the cut logic can work on.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import config as C


def extract_audio(src: Path, out: Path) -> Path:
    C.ensure_ffmpeg()
    C.run([
        "ffmpeg", "-y", "-v", "error", "-i", str(src),
        "-vn", "-ac", "1", "-ar", str(C.SAMPLE_RATE),
        "-c:a", "pcm_s16le", str(out),
    ])
    return out


def transcribe(audio: Path, model_name: str = C.WHISPER_MODEL,
               initial_prompt: str | None = None) -> dict:
    import torch
    import whisper

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"[transcribe] model={model_name} device={device}", flush=True)

    # Prefer the cached .pt BY PATH. Passing a bare model name sends whisper
    # through _download(), which verifies the checksum by reading all 2.9 GB into
    # a single contiguous bytes object -- that raises MemoryError on this machine
    # even with 16 GB free. A path argument skips the download path completely.
    import os
    cached = os.path.expanduser(f"~/.cache/whisper/{model_name}.pt")
    target = cached if os.path.isfile(cached) else model_name

    def _load_cuda_fp16():
        # The stock loader builds fp32 on CPU (~6 GB) while the 2.9 GB checkpoint
        # is also resident -> exit 139 (commit limit), worst with Premiere open; an
        # fp32 build straight on CUDA OOMs the 12 GB card. So: mmap the checkpoint,
        # build the model in fp16 directly on the GPU, LayerNorms back to fp32
        # (whisper.LayerNorm computes in fp32), then load the weights.
        from whisper.model import ModelDimensions, Whisper
        ck = torch.load(target, map_location="cpu", mmap=True, weights_only=False)
        torch.set_default_dtype(torch.float16)
        try:
            with torch.device("cuda"):
                model = Whisper(ModelDimensions(**ck["dims"]))
        finally:
            torch.set_default_dtype(torch.float32)
        model.half()
        for m in model.modules():
            if isinstance(m, torch.nn.LayerNorm):
                m.float()
        model.load_state_dict(ck["model_state_dict"])
        del ck
        if model_name in whisper._ALIGNMENT_HEADS:
            model.set_alignment_heads(whisper._ALIGNMENT_HEADS[model_name])
        return model.eval()

    def _run(dev: str):
        if dev == "cuda" and os.path.isfile(target):
            model = _load_cuda_fp16()
        else:
            model = whisper.load_model(target, device=dev)
        return model.transcribe(
            str(audio),
            language=C.WHISPER_LANG,
            word_timestamps=True,
            fp16=(dev == "cuda"),
            # Persian benefits from a lower no-speech bar; the take is dense speech.
            no_speech_threshold=0.5,
            condition_on_previous_text=False,
            initial_prompt=initial_prompt,
            verbose=False,
        )

    try:
        return _run(device)
    except RuntimeError as exc:
        # cuBLAS on this machine intermittently returns CUBLAS_STATUS_NOT_SUPPORTED
        # even with the GPU idle and plenty of VRAM. Falling back to CPU is slow
        # but always finishes, which beats failing the whole edit.
        if device != "cuda":
            raise
        print(f"[transcribe] CUDA failed ({str(exc).splitlines()[0][:80]}); "
              f"retrying on CPU", flush=True)
        import torch as _t
        _t.cuda.empty_cache()
        return _run("cpu")


def flatten(result: dict) -> list[dict]:
    """Whisper's nested segments -> the flat word array everything else reads."""
    words: list[dict] = []
    for seg in result.get("segments", []):
        seg_words = seg.get("words") or []
        if not seg_words:
            # Segment came back without word timings -- keep it as one blob so the
            # timeline stays continuous rather than silently dropping speech.
            words.append({
                "text": seg["text"].strip(),
                "start": round(float(seg["start"]), 3),
                "end": round(float(seg["end"]), 3),
                "prob": 0.0,
                "degraded": True,
            })
            continue
        for w in seg_words:
            text = (w.get("word") or "").strip()
            if not text:
                continue
            words.append({
                "text": text,
                "start": round(float(w["start"]), 3),
                "end": round(float(w["end"]), 3),
                "prob": round(float(w.get("probability", 0.0)), 4),
            })
    # Whisper occasionally emits zero-or-negative-length words; give them one frame.
    for w in words:
        if w["end"] <= w["start"]:
            w["end"] = round(w["start"] + 1.0 / C.FPS, 3)
    words.sort(key=lambda w: w["start"])
    return words


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Transcribe a take to word-level Farsi JSON")
    ap.add_argument("video", help="video name (resolved against raw/) or a path")
    ap.add_argument("--model", default=C.WHISPER_MODEL)
    ap.add_argument("--prompt", default=None,
                    help="initial_prompt: names/jargon Whisper should spell right")
    ap.add_argument("--force", action="store_true", help="re-run even if transcript.json exists")
    args = ap.parse_args(argv)

    src = C.find_raw(args.video)
    name = src.stem
    wd = C.work_dir_for(name)

    audio = wd / "audio.wav"
    tpath = wd / "transcript.json"

    if tpath.exists() and not args.force:
        print(f"[transcribe] {tpath} exists -- use --force to redo")
        return 0

    if not audio.exists() or args.force:
        print(f"[transcribe] extracting audio -> {audio}", flush=True)
        extract_audio(src, audio)

    result = transcribe(audio, args.model, args.prompt)
    words = flatten(result)

    C.write_json(tpath, words)
    C.write_json(wd / "transcript.raw.json", result)

    dur = words[-1]["end"] if words else 0.0
    print(f"[transcribe] {len(words)} words, {dur:.1f}s -> {tpath}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
