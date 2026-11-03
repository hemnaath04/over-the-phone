"""Summarize a run: pass rates by condition, category and accent, and every failure.

    uv run python -m otp.report runs/pilot

Writes report.md and summary.json next to results.jsonl. Intervals are 95% bootstrap
intervals over cases (1,000 resamples), so a category with few cases shows a wide one.
The paired table counts cases that pass at 24 kHz and fail on the phone channel:
those are the failures the phone line causes, not ones the model makes anyway.

Every row is scored again from its saved transcript, so a scorer fix applies to an
old run without paying for its synthesis and transcription again.
"""

from __future__ import annotations

import json
import random
import sys
from collections import defaultdict
from pathlib import Path

from otp.channel import CONDITIONS, SHARED_TAKE
from otp.score import score


def bootstrap(values: list[bool], n: int = 1000, seed: int = 0) -> tuple[float, float]:
    if not values:
        return (0.0, 0.0)
    rng = random.Random(seed)
    k = len(values)
    means = sorted(sum(rng.choice(values) for _ in range(k)) / k for _ in range(n))
    return means[int(0.025 * n)], means[int(0.975 * n) - 1]


def pct(values: list[bool]) -> str:
    if not values:
        return "—"
    lo, hi = bootstrap(values)
    return f"{100 * sum(values) / len(values):.1f}% ({100 * lo:.0f}–{100 * hi:.0f})"


def table(rows: list[dict], key: str, conditions: list[str]) -> list[str]:
    groups = defaultdict(lambda: defaultdict(list))
    for r in rows:
        groups[r[key]][r["condition"]].append(r["pass"])
    lines = [f"| {key} | n | " + " | ".join(conditions) + " |",
             "|---|---|" + "---|" * len(conditions)]
    for g in sorted(groups):
        n = max(len(v) for v in groups[g].values())
        lines.append(f"| {g} | {n} | " + " | ".join(pct(groups[g][c]) for c in conditions) + " |")
    return lines


def main(run_dir: str) -> None:
    run = Path(run_dir)
    rows = [json.loads(line) for line in (run / "results.jsonl").read_text().splitlines()]
    for r in rows:
        r["pass"], r["heard"] = score(r["category"], r["transcript"], r["gold"])
    conditions = [c for c in CONDITIONS if any(r["condition"] == c for r in rows)]
    by_case = defaultdict(dict)
    for r in rows:
        by_case[r["case_id"]][r["condition"]] = r

    overall = {c: [r["pass"] for r in rows if r["condition"] == c] for c in conditions}
    paired = {}
    for c in conditions:
        if c == "api24":
            continue
        both = [v for v in by_case.values() if "api24" in v and c in v]
        paired[c] = {
            "cases": len(both),
            "phone_only_failures": sum(v["api24"]["pass"] and not v[c]["pass"] for v in both),
            "phone_only_fixes": sum(not v["api24"]["pass"] and v[c]["pass"] for v in both),
        }

    takes = {r["tts_request_id"]: r.get("billed_characters", 0) for r in rows if r.get("tts_request_id")}
    billed = sum(takes.values())
    lines = [
        f"# Over the Phone: {run.name}",
        "",
        f"{len(by_case)} cases (item × voice), {len(rows)} scored transcripts, "
        f"about {billed:,} TTS characters billed.",
        "",
        "Pass rate with 95% bootstrap interval. `api24` is the API's default 24 kHz PCM, "
        "the way AssemblyAI's own benchmark heard the model; the others are what a "
        "caller's phone line delivers.",
        "",
        "## Overall",
        "",
        "| condition | n | pass rate |",
        "|---|---|---|",
        *[f"| {c} | {len(overall[c])} | {pct(overall[c])} |" for c in conditions],
        "",
        "## Paired with api24",
        "",
        "Per case: passes at 24 kHz but fails in the condition, and the reverse. For "
        "`resampled8` and `lossy8` the audio is the same take as `api24`, so a difference "
        "is caused by the phone channel alone. `native8` and `retake24` are separate "
        "syntheses, so their differences include take-to-take variation; `retake24` "
        "measures that variation by itself, and its \"pass only\" column is how often "
        "simply synthesizing again fixes a failure.",
        "",
        "| condition | same take | paired cases | fail only here | pass only here |",
        "|---|---|---|---|---|",
        *[f"| {c} | {'yes' if c in SHARED_TAKE else 'no'} | {p['cases']} | "
          f"{p['phone_only_failures']} | {p['phone_only_fixes']} |" for c, p in paired.items()],
        "",
        "## By category",
        "",
        *table(rows, "category", conditions),
        "",
        "## By voice accent",
        "",
        *table(rows, "accent", conditions),
        "",
        "## Failures",
        "",
        "| condition | case | said | heard | transcript | TTS request | STT session |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in sorted((r for r in rows if not r["pass"]), key=lambda r: (r["category"], r["case_id"], r["condition"])):
        transcript = r["transcript"].replace("|", "/")
        lines.append(f"| {r['condition']} | {r['case_id']} | `{r['surface']}` | `{r['heard']}` | "
                     f"{transcript} | `{r.get('tts_request_id', '')}` | `{r['stt_session_id']}` |")
    (run / "report.md").write_text("\n".join(lines) + "\n")
    summary = {"cases": len(by_case), "rows": len(rows),
               "overall": {c: sum(v) / len(v) for c, v in overall.items()}, "paired": paired}
    (run / "summary.json").write_text(json.dumps(summary, indent=2))
    print("\n".join(lines[:22]))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "runs/pilot")
