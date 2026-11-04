"""Score a recording of a real phone call to the agent in reader mode.

    uv run python -m otp.score_call path/to/call-recording.m4a --name call-1

The reader agent says "Item N." before each line of agent/reader_script.json. This
transcribes the whole recording with both listeners (AssemblyAI Sync STT and local
Whisper), splits each transcript at the item markers, and scores every line against
its gold value. Results go to runs/<name>/call.jsonl and runs/<name>/call.md.

The recording is what reached the phone that dialled in, after the real network
and codec, so this is the check on the simulated `native8` and `lossy8` channels.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

from otp import channel
from otp.aai import AssemblyAI
from otp.score import UNITS, score
from otp.second_listener import whisper

ROOT = Path(__file__).resolve().parent.parent
MARKER = re.compile(r"\bitem\s+(\d{1,2}|[a-z]+(?:[- ][a-z]+)?)\s*[.,:]?", re.I)
TENS = {"twenty": 20}


def marker_number(word: str) -> int | None:
    word = word.lower().replace("-", " ")
    if word.isdigit():
        return int(word)
    parts = word.split()
    if parts and parts[0] in UNITS:
        return UNITS[parts[0]]
    if parts and parts[0] in TENS:
        return TENS[parts[0]] + (UNITS.get(parts[1], 0) if len(parts) > 1 else 0)
    return None


def split_items(transcript: str) -> dict[int, str]:
    marks = [(m.start(), m.end(), marker_number(m.group(1))) for m in MARKER.finditer(transcript)]
    marks = [m for m in marks if m[2] is not None]
    out = {}
    for i, (_, end, n) in enumerate(marks):
        stop = marks[i + 1][0] if i + 1 < len(marks) else len(transcript)
        out[n] = transcript[end:stop].strip()
    return out


def load_audio(path: Path) -> bytes:
    """Any container ffmpeg reads (an iPhone call recording is .m4a) to 8 kHz PCM WAV."""
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", "8000",
                          "-f", "s16le", "pipe:1"], capture_output=True, check=True).stdout
    return channel.wav_from_pcm(raw, 8000)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("recording")
    ap.add_argument("--name", required=True)
    args = ap.parse_args()
    script = json.loads((ROOT / "agent" / "reader_script.json").read_text())
    wav = load_audio(Path(args.recording))
    out_dir = ROOT / "runs" / args.name
    out_dir.mkdir(parents=True, exist_ok=True)

    aai = AssemblyAI().transcribe(wav)
    wh = whisper(wav)
    aai_items, wh_items = split_items(aai.text), split_items(wh)
    rows = []
    for line in script:
        a_text, w_text = aai_items.get(line["n"], ""), wh_items.get(line["n"], "")
        a_pass, a_heard = score(line["category"], a_text, line["gold"])
        w_pass, w_heard = score(line["category"], w_text, line["gold"])
        rows.append({**line, "aai_segment": a_text, "aai_pass": a_pass, "aai_heard": a_heard,
                     "whisper_segment": w_text, "whisper_pass": w_pass, "whisper_heard": w_heard,
                     "stt_session_id": aai.session_id})
    with (out_dir / "call.jsonl").open("w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    lines = [f"# Real call: {args.name}", "",
             f"Recording `{Path(args.recording).name}`, {channel.duration_ms(wav) / 1000:.0f} s. "
             f"AssemblyAI STT session `{aai.session_id}`.", "",
             "| variant | AssemblyAI pass | Whisper pass |", "|---|---|---|"]
    for v in ("raw", "speakable"):
        vs = [r for r in rows if r["variant"] == v]
        lines.append(f"| {v} | {sum(r['aai_pass'] for r in vs)}/{len(vs)} | "
                     f"{sum(r['whisper_pass'] for r in vs)}/{len(vs)} |")
    lines += ["", "| item | variant | said | AssemblyAI heard | Whisper heard |", "|---|---|---|---|---|"]
    for r in rows:
        mark = lambda ok: "✓" if ok else "✗"  # noqa: E731
        lines.append(f"| {r['n']} {r['item_id']} | {r['variant']} | `{r['surface']}` | "
                     f"{mark(r['aai_pass'])} `{r['aai_heard']}` | {mark(r['whisper_pass'])} `{r['whisper_heard']}` |")
    (out_dir / "call.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines[:8]))


if __name__ == "__main__":
    main()
