"""Write agent/reader_script.json: the items full-v1 found hard, each raw and rewritten.

    uv run python agent/make_reader_script.py
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from otp.entities import build_items  # noqa: E402
from otp.run import locale_for  # noqa: E402
from otp.speakable import speakable  # noqa: E402

PICK = ["date-004", "email-016", "email-001", "uk_postcode-013", "uk_postcode-002", "booking_ref-015",
        "card_last4-004", "us_phone-007", "uk_mobile-000", "time-003", "us_zip-006", "price_usd-003"]

items = {i.id: i for i in build_items(20, 7)}
lines = []
for pid in PICK:
    item = items[pid]
    for variant in ("raw", "speakable"):
        text = item.text if variant == "raw" else speakable(item.text, locale_for(item))
        lines.append({"n": len(lines) + 1, "item_id": item.id, "category": item.category,
                      "variant": variant, "spoken_text": text, "gold": item.gold, "surface": item.surface})
(ROOT / "agent" / "reader_script.json").write_text(json.dumps(lines, indent=1, ensure_ascii=False) + "\n")
print(f"{len(lines)} lines")
