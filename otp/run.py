"""Synthesize every (item, voice) case, pass it through each channel, transcribe, score.

    uv run python -m otp.run --name pilot --per-category 3

Rows are appended to runs/<name>/results.jsonl as they finish, and a rerun with the
same name skips the rows already there, so an interrupted run resumes without paying
for the same synthesis twice. TTS audio is cached on disk until its case is scored;
afterwards it is kept only for failures and a fixed 5% sample, since disk is tight.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import subprocess
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from otp import channel
from otp.aai import AssemblyAI
from otp.entities import CATEGORIES, build_items
from otp.score import score
from otp.speakable import speakable

# Accent of each voice, from the starter table at docs/tts/voices.
VOICES = {
    "aai-audrey": "US", "aai-titus": "US", "aai-sara": "US", "aai-ewald": "US",
    "aai-nancy": "UK", "aai-buford": "UK", "aai-carrie": "UK", "aai-percival": "UK",
    "aai-steven": "AU", "aai-troy": "Scottish",
}
DEFAULT_VOICES = ["aai-audrey", "aai-titus", "aai-nancy", "aai-buford"]
ROOT = Path(__file__).resolve().parent.parent


def locale_for(item) -> str:
    """The locale the agent speaks for: a UK business for UK entities, else the US."""
    uk = item.category in ("uk_postcode", "uk_mobile", "price_gbp") or item.gold.get("style") == "uk_numeric"
    return "en-GB" if uk else "en-US"


def keep_sample(case_id: str) -> bool:
    return int(hashlib.sha1(case_id.encode()).hexdigest(), 16) % 20 == 0


def git_sha() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT,
                              capture_output=True, text=True).stdout.strip() or "uncommitted"
    except OSError:
        return "unknown"


class Run:
    def __init__(self, args: argparse.Namespace):
        self.dir = ROOT / "runs" / args.name
        self.audio_dir = self.dir / "audio"
        self.audio_dir.mkdir(parents=True, exist_ok=True)
        self.results = self.dir / "results.jsonl"
        self.conditions = args.conditions
        self.keep_all = args.keep_audio == "all"
        self.variant = args.variant
        self.api = AssemblyAI(tts_per_minute=args.tts_per_minute, stt_per_minute=args.stt_per_minute)
        self.lock = threading.Lock()
        self.done = set()
        if self.results.exists():
            for line in self.results.read_text().splitlines():
                row = json.loads(line)
                self.done.add((row["case_id"], row["condition"]))

    def write(self, row: dict) -> None:
        with self.lock, self.results.open("a") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    def tts(self, case_id: str, text: str, voice: str, fmt: str) -> tuple[bytes, dict]:
        path = self.audio_dir / f"{case_id}.{fmt}.wav"
        meta_path = path.with_suffix(".json")
        if path.exists() and meta_path.exists():
            return path.read_bytes(), json.loads(meta_path.read_text())
        speech = self.api.speak(text, voice, **channel.TTS_FORMATS[fmt])
        meta = {"tts_request_id": speech.request_id, "billed_characters": speech.billed_characters,
                "tts_audio_duration_ms": speech.audio_duration_ms}
        path.write_bytes(speech.audio)
        meta_path.write_text(json.dumps(meta))
        return speech.audio, meta

    def case(self, item, voice: str) -> list[dict]:
        case_id = f"{item.id}.{voice}"
        todo = [c for c in self.conditions if (case_id, c) not in self.done]
        rows = []
        text = speakable(item.text, locale_for(item)) if self.variant == "speakable" else item.text
        for cond in todo:
            fmt = channel.SOURCE[cond]
            audio, meta = self.tts(case_id, text, voice, fmt)
            heard_wav = channel.apply(cond, audio, seed=case_id)
            tr = self.api.transcribe(heard_wav)
            passed, heard = score(item.category, tr.text, item.gold)
            row = {
                "case_id": case_id, "item_id": item.id, "category": item.category,
                "voice": voice, "accent": VOICES.get(voice, "?"), "condition": cond,
                "text": item.text, "spoken_text": text, "variant": self.variant,
                "surface": item.surface, "gold": item.gold,
                "transcript": tr.text, "heard": heard, "pass": passed,
                "stt_session_id": tr.session_id, "stt_request_time_ms": tr.request_time_ms,
                **meta, "at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
            }
            if not passed and not self.keep_all:
                (self.audio_dir / f"{case_id}.{cond}.heard.wav").write_bytes(heard_wav)
            self.write(row)
            rows.append(row)
        self.tidy(case_id)
        return rows

    def tidy(self, case_id: str) -> None:
        """Drop a case's cached TTS audio once every condition passed, unless it is sampled."""
        if self.keep_all or keep_sample(case_id):
            return
        mine = [json.loads(line) for line in self.results.read_text().splitlines()
                if line.startswith(f'{{"case_id": "{case_id}"')]
        if len(mine) >= len(self.conditions) and all(r["pass"] for r in mine):
            for p in self.audio_dir.glob(f"{case_id}.*"):
                p.unlink()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--name", required=True, help="run folder under runs/")
    ap.add_argument("--per-category", type=int, default=20)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--categories", type=lambda s: s.split(","), default=CATEGORIES)
    ap.add_argument("--voices", type=lambda s: s.split(","), default=DEFAULT_VOICES)
    ap.add_argument("--conditions", type=lambda s: s.split(","), default=channel.CONDITIONS)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--tts-per-minute", type=int, default=40, help="free plan allows 50")
    ap.add_argument("--stt-per-minute", type=int, default=120)
    ap.add_argument("--keep-audio", choices=["failures", "all"], default="failures")
    ap.add_argument("--variant", choices=["raw", "speakable"], default="raw",
                    help="speakable: rewrite each sentence with otp.speakable first")
    args = ap.parse_args()

    run = Run(args)
    items = build_items(args.per_category, args.seed, args.categories)
    cases = [(item, voice) for item in items for voice in args.voices]
    manifest = {**{k: v for k, v in vars(args).items()}, "git": git_sha(),
                "cases": len(cases), "started": dt.datetime.now().isoformat(timespec="seconds")}
    (run.dir / "manifest.json").write_text(json.dumps(manifest, indent=2))

    todo = [(i, v) for i, v in cases
            if any((f"{i.id}.{v}", c) not in run.done for c in args.conditions)]
    print(f"{len(cases)} cases x {len(args.conditions)} conditions; {len(todo)} cases to do")
    passed = failed = errors = 0
    with ThreadPoolExecutor(args.workers) as pool:
        futures = {pool.submit(run.case, i, v): f"{i.id}.{v}" for i, v in todo}
        for n, fut in enumerate(as_completed(futures), 1):
            try:
                for row in fut.result():
                    passed += row["pass"]
                    failed += not row["pass"]
                    if not row["pass"]:
                        print(f"  FAIL {row['condition']:<10} {row['case_id']}: "
                              f"{row['surface']!r} heard {row['heard']!r}")
            except Exception as exc:  # one bad case must not stop the run
                errors += 1
                print(f"  ERROR {futures[fut]}: {exc}")
            if n % 20 == 0 or n == len(todo):
                print(f"[{n}/{len(todo)}] pass {passed} fail {failed} errors {errors}")


if __name__ == "__main__":
    main()
