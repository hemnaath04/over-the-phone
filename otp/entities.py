"""The test set: sentences a phone agent says, each built around one hard entity.

Every item carries the text the agent sends to TTS and a `gold` value the scorer
checks the transcript against. Generation is seeded, so a set is reproducible from
its seed alone.

Numbers come from ranges reserved for fiction (US 555-01xx, UK 07700 900xxx), so
no real person's number is ever synthesized or dialled.
"""

from __future__ import annotations

import random
from dataclasses import asdict, dataclass, field

# Letters and digits that a caller cannot confuse in writing (no 0/O, 1/I, 2/Z, 5/S,
# 8/B). Real booking systems drop the same characters for the same reason.
REF_CHARS = "ACDEFHJKLMNPQRTUVWXY34679"
# Letters Royal Mail allows in the last two characters of a postcode.
POSTCODE_TAIL = "ABDEFGHJLNPQRSTUWXYZ"
POSTCODE_AREAS = ["SW", "EC", "N", "M", "B", "LS", "G", "EH", "CF", "BS", "NW", "SE"]

MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
FIRST = ["james", "priya", "chen", "maria", "tom", "aisha", "liam", "sofia", "noah", "fatima"]
LAST = ["smith", "patel", "wong", "garcia", "okafor", "murphy", "kowalski", "nguyen"]
DOMAINS = ["acme.com", "northwind.co.uk", "example.org", "mailbox.io", "brightdental.com"]

CATEGORIES = [
    "us_phone", "uk_mobile", "uk_postcode", "booking_ref", "price_usd",
    "price_gbp", "date", "time", "email", "card_last4", "us_zip",
]


@dataclass(frozen=True)
class Item:
    id: str
    category: str
    text: str
    gold: dict = field(hash=False)
    surface: str  # the entity exactly as written in `text`

    def to_dict(self) -> dict:
        return asdict(self)


def _ordinal(n: int) -> str:
    suffix = "th" if 11 <= n % 100 <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def _us_phone(r: random.Random) -> tuple[str, dict, str]:
    area = f"{r.randint(2, 9)}{r.randint(0, 9)}{r.randint(0, 9)}"
    last = f"01{r.randint(0, 9)}{r.randint(0, 9)}"
    digits = f"{area}555{last}"
    surface = r.choice([f"({area}) 555-{last}", f"{area}-555-{last}", f"{area}.555.{last}"])
    text = r.choice([
        "You can reach the front desk at {}.",
        "If anything changes, just call us at {}.",
        "The pharmacy's direct line is {}.",
    ]).format(surface)
    return text, {"digits": digits}, surface


def _uk_mobile(r: random.Random) -> tuple[str, dict, str]:
    tail = f"{r.randint(0, 999):03d}"
    surface = r.choice([f"07700 900{tail}", f"07700 900 {tail}", f"+44 7700 900{tail}"])
    text = r.choice([
        "We'll text the confirmation to {}.",
        "The number we have on file is {}.",
        "Our engineer will call you from {}.",
    ]).format(surface)
    # Scored on the ten digits after the trunk prefix, so "0" and "+44" both pass.
    return text, {"digits": f"7700900{tail}"}, surface


def _uk_postcode(r: random.Random) -> tuple[str, dict, str]:
    area = r.choice(POSTCODE_AREAS)
    district = str(r.randint(1, 20))
    if area in ("SW", "EC", "NW", "SE") and r.random() < 0.3:
        district = f"{r.randint(1, 9)}{r.choice('ABEHMNPRVWXY')}"
    inward = f"{r.randint(1, 9)}{r.choice(POSTCODE_TAIL)}{r.choice(POSTCODE_TAIL)}"
    surface = f"{area}{district} {inward}"
    text = r.choice([
        "And the delivery postcode is {}, is that right?",
        "Your nearest branch is at {}.",
        "I've got the postcode as {}.",
    ]).format(surface)
    return text, {"alnum": surface.replace(" ", "")}, surface


def _booking_ref(r: random.Random) -> tuple[str, dict, str]:
    ref = "".join(r.choice(REF_CHARS) for _ in range(6))
    surface = r.choice([ref, f"{ref[:3]}-{ref[3:]}"])
    text = r.choice([
        "Your booking reference is {}.",
        "Your confirmation code is {}, so keep that handy.",
        "I've opened a ticket for you, the reference is {}.",
    ]).format(surface)
    return text, {"alnum": ref}, surface


def _money(r: random.Random, symbol: str, currency: str) -> tuple[str, dict, str]:
    kind = r.random()
    if kind < 0.4:
        cents = r.randint(100, 9999)  # $1.00 to $99.99
    elif kind < 0.8:
        cents = r.randint(10000, 999999)  # $100.00 to $9,999.99
    else:
        cents = r.randint(1, 99) * 100  # whole amounts
    whole, frac = divmod(cents, 100)
    surface = f"{symbol}{whole:,}" + (f".{frac:02d}" if frac else "")
    text = r.choice([
        "So your current balance is {}, and it's due on the 15th.",
        "That comes to {} including tax.",
        "I can refund {} to your original payment method.",
    ]).format(surface)
    return text, {"currency": currency, "cents": cents}, surface


def _date(r: random.Random) -> tuple[str, dict, str]:
    month = r.randint(1, 12)
    day = r.randint(1, 28)
    year = 2026
    style = r.choice(["words", "weekday", "us_numeric", "uk_numeric", "iso"])
    if style == "words":
        surface = f"{MONTHS[month - 1]} {_ordinal(day)}"
    elif style == "weekday":
        surface = f"{r.choice(WEEKDAYS)}, {MONTHS[month - 1]} {_ordinal(day)}"
    elif style == "us_numeric":
        surface = f"{month}/{day}/{year}"
    elif style == "uk_numeric":
        surface = f"{day:02d}/{month:02d}/{year}"
    else:
        surface = f"{year}-{month:02d}-{day:02d}"
    text = r.choice([
        "Perfect, you're all set for {}.",
        "Your next appointment is on {}.",
        "The parcel should arrive by {}.",
    ]).format(surface)
    gold = {"month": month, "day": day, "style": style}
    return text, gold, surface


def _time(r: random.Random) -> tuple[str, dict, str]:
    hour = r.randint(7, 19)
    minute = r.choice([0, 15, 30, 45, 5, 50])
    style = r.choice(["12h", "12h", "24h"])
    if style == "24h":
        surface = f"{hour:02d}:{minute:02d}"
    else:
        h12 = hour % 12 or 12
        ampm = "AM" if hour < 12 else "PM"
        surface = f"{h12}:{minute:02d} {ampm}" if minute else f"{h12} {ampm}"
    text = r.choice([
        "The technician will arrive at {}.",
        "We've moved your call to {}.",
        "Pickup is at {} sharp.",
    ]).format(surface)
    return text, {"hour": hour, "minute": minute, "style": style}, surface


def _email(r: random.Random) -> tuple[str, dict, str]:
    first, last = r.choice(FIRST), r.choice(LAST)
    local = r.choice([f"{first}.{last}", f"{first[0]}{last}", f"{first}{r.randint(10, 99)}"])
    surface = f"{local}@{r.choice(DOMAINS)}"
    text = r.choice([
        "I've sent a reset link to {}.",
        "The receipt will go to {}.",
        "Can you confirm your email is {}?",
    ]).format(surface)
    return text, {"email": surface}, surface


def _card_last4(r: random.Random) -> tuple[str, dict, str]:
    last4 = f"{r.randint(0, 9999):04d}"
    text = r.choice([
        "I'll charge the card ending in {}.",
        "The refund goes back to the card ending {}.",
    ]).format(last4)
    return text, {"digits": last4}, last4


def _us_zip(r: random.Random) -> tuple[str, dict, str]:
    # Leading zeros are the interesting case: New England ZIPs start with 0.
    zip5 = r.choice([f"0{r.randint(1000, 2799)}", f"{r.randint(10000, 99999)}"])
    text = r.choice([
        "And the ZIP code is {}?",
        "We don't deliver to {} yet, unfortunately.",
    ]).format(zip5)
    return text, {"digits": zip5}, zip5


_MAKERS = {
    "us_phone": _us_phone,
    "uk_mobile": _uk_mobile,
    "uk_postcode": _uk_postcode,
    "booking_ref": _booking_ref,
    "price_usd": lambda r: _money(r, "$", "USD"),
    "price_gbp": lambda r: _money(r, "£", "GBP"),
    "date": _date,
    "time": _time,
    "email": _email,
    "card_last4": _card_last4,
    "us_zip": _us_zip,
}


def build_items(per_category: int = 20, seed: int = 7, categories: list[str] | None = None) -> list[Item]:
    """Return `per_category` items for each category, the same list for the same seed."""
    items = []
    for category in categories or CATEGORIES:
        r = random.Random(f"{seed}:{category}")
        for i in range(per_category):
            text, gold, surface = _MAKERS[category](r)
            items.append(Item(f"{category}-{i:03d}", category, text, gold, surface))
    return items
