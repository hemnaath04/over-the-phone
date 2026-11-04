"""Have a second, independent listener re-hear clips, to say which side made an error.

    uv run python -m otp.second_listener runs/full-v1

AssemblyAI's speech-to-text scores AssemblyAI's TTS, so a failure could be the voice
saying the entity wrong or the transcriber hearing it wrong. Whisper (small.en, run
locally through whisper.cpp) shares neither model, so:

- both listeners fail, on the same wrong reading: the voice most likely said it wrong;
- Whisper passes where AssemblyAI failed: most likely a transcription error.

Whisper is also run on every clip of the 5% sample that AssemblyAI passed, to measure
how often Whisper itself fails on correct audio; without that baseline, its
disagreement means little. Results go to second_listener.jsonl next to results.jsonl.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from otp import channel
from otp.run import keep_sample
from otp.score import score

MODEL = Path(os.environ.get(
    "WHISPER_MODEL",
    "~/Library/Application Support/LecRec/models/ggml-small.en.bin")).expanduser()


def whisper(wav: bytes) -> str:
    """Transcribe with whisper.cpp; it wants 16 kHz mono PCM."""
    with tempfile.NamedTemporaryFile(suffix=".wav") as f:
        f.write(channel.to_pcm16(wav, 16000))
        f.flush()
        out = subprocess.run(
            ["whisper-cli", "-m", str(MODEL), "-f", f.name, "-l", "en", "-nt", "-np", "-t", "4"],
            capture_output=True, text=True, check=True).stdout
    return " ".join(out.split())


def heard_audio(audio_dir: Path, row: dict) -> bytes | None:
    """The clip the first listener heard: saved for failures, rebuilt from the take otherwise."""
    saved = audio_dir / f"{row['case_id']}.{row['condition']}.heard.wav"
    if saved.exists():
        return saved.read_bytes()
    take = audio_dir / f"{row['case_id']}.{channel.SOURCE[row['condition']]}.wav"
    if take.exists():
        return channel.apply(row["condition"], take.read_bytes(), seed=row["case_id"])
    return None


def main(run_dir: str) -> None:
    run = Path(run_dir)
    rows = [json.loads(line) for line in (run / "results.jsonl").read_text().splitlines()]
    for r in rows:
        r["pass"], r["heard"] = score(r["category"], r["transcript"], r["gold"])
    todo = [r for r in rows if not r["pass"] or keep_sample(r["case_id"])]
    out_path = run / "second_listener.jsonl"
    done = set()
    if out_path.exists():
        done = {(d["case_id"], d["condition"]) for d in map(json.loads, out_path.read_text().splitlines())}
    todo = [r for r in todo if (r["case_id"], r["condition"]) not in done]
    print(f"{len(todo)} clips for the second listener ({MODEL.name})")

    def one(r: dict) -> dict | None:
        wav = heard_audio(run / "audio", r)
        if wav is None:
            return None
        text = whisper(wav)
        w_pass, w_heard = score(r["category"], text, r["gold"])
        return {"case_id": r["case_id"], "condition": r["condition"], "category": r["category"],
                "surface": r["surface"], "aai_pass": r["pass"], "aai_heard": r["heard"],
                "aai_transcript": r["transcript"], "whisper_pass": w_pass,
                "whisper_heard": w_heard, "whisper_transcript": text}

    with ThreadPoolExecutor(2) as pool, out_path.open("a") as f:
        for n, res in enumerate(pool.map(one, todo), 1):
            if res:
                f.write(json.dumps(res, ensure_ascii=False) + "\n")
                f.flush()
            if n % 25 == 0:
                print(f"[{n}/{len(todo)}]")
    summarize(out_path)


def summarize(path: Path) -> None:
    res = [json.loads(line) for line in path.read_text().splitlines()]
    base = [r for r in res if r["aai_pass"]]
    fails = [r for r in res if not r["aai_pass"]]
    print(f"\nWhisper on clips AssemblyAI passed: {sum(r['whisper_pass'] for r in base)}/{len(base)} pass")
    verdict = Counter("both fail" if not r["whisper_pass"] else "whisper passes" for r in fails)
    print(f"On AssemblyAI failures: {dict(verdict)}")
    by_item = {}
    for r in fails:
        item = r["case_id"].split(".")[0]
        by_item.setdefault(item, []).append(r)
    for item, rs in sorted(by_item.items()):
        w = sum(r["whisper_pass"] for r in rs)
        print(f"  {item:18s} {rs[0]['surface']!r:32s} whisper passes {w}/{len(rs)}; "
              f"whisper heard {rs[0]['whisper_transcript'][-60:]!r}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "runs/full-v1")
