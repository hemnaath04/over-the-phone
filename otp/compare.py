"""Compare two runs of the same items: what a rewrite fixed and what it broke.

    uv run python -m otp.compare runs/full-v1 runs/speakable-v1

Both runs are re-scored from their transcripts. Cases are matched by case id
(item x voice) within each condition the two runs share. Writes compare.md into
the second run's folder.
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

from otp.channel import CONDITIONS
from otp.report import pct
from otp.score import score


def load(run: Path) -> dict:
    rows = {}
    for line in (run / "results.jsonl").read_text().splitlines():
        r = json.loads(line)
        r["pass"], r["heard"] = score(r["category"], r["transcript"], r["gold"])
        rows[(r["case_id"], r["condition"])] = r
    return rows


def main(base_dir: str, new_dir: str) -> None:
    base_run, new_run = Path(base_dir), Path(new_dir)
    base, new = load(base_run), load(new_run)
    keys = sorted(set(base) & set(new))
    conditions = [c for c in CONDITIONS if any(k[1] == c for k in keys)]

    lines = [f"# {new_run.name} vs {base_run.name}", "",
             f"{len({k[0] for k in keys})} cases in both runs. Pass rate with 95% bootstrap interval.", "",
             "## Overall", "", "| condition | " + base_run.name + " | " + new_run.name + " | fixed | broken |",
             "|---|---|---|---|---|"]
    for c in conditions:
        ks = [k for k in keys if k[1] == c]
        b = [base[k]["pass"] for k in ks]
        n = [new[k]["pass"] for k in ks]
        fixed = sum(not x and y for x, y in zip(b, n))
        broken = sum(x and not y for x, y in zip(b, n))
        lines.append(f"| {c} | {pct(b)} | {pct(n)} | {fixed} | {broken} |")

    lines += ["", "## By category (" + ", ".join(conditions) + " pooled)", "",
              "| category | " + base_run.name + " | " + new_run.name + " |", "|---|---|---|"]
    by_cat = defaultdict(lambda: ([], []))
    for k in keys:
        by_cat[base[k]["category"]][0].append(base[k]["pass"])
        by_cat[base[k]["category"]][1].append(new[k]["pass"])
    for cat in sorted(by_cat):
        b, n = by_cat[cat]
        lines.append(f"| {cat} | {pct(b)} | {pct(n)} |")

    lines += ["", "## Still failing or newly failing", "",
              "| condition | case | spoken text | heard | was |", "|---|---|---|---|---|"]
    for k in keys:
        if not new[k]["pass"]:
            was = "pass" if base[k]["pass"] else "fail"
            spoken = new[k].get("spoken_text", new[k]["text"]).replace("|", "/")
            lines.append(f"| {k[1]} | {k[0]} | {spoken} | `{new[k]['heard']}` | {was} |")
    (new_run / "compare.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines[:8 + len(conditions) + 4 + len(by_cat)]))


if __name__ == "__main__":
    main(*sys.argv[1:3])
