"""Decide whether a transcript of the synthesized audio still carries the entity.

The transcript comes from speech-to-text, so the same entity can come back in many
written forms: "07700 900123", "0 7 7 0 0 9 0 0 1 2 3", "oh seven seven double oh...".
Each scorer first rewrites spelled-out numbers as digits, then compares a canonical
form of the transcript against the item's gold value.

A scorer returns (passed, heard): `heard` is the closest thing it found, kept for
the failure table in the report.
"""

from __future__ import annotations

import re

UNITS = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
    "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
    "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17,
    "eighteen": 18, "nineteen": 19,
}
TENS = {
    "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50,
    "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90,
}
ORDINALS = {
    "first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5, "sixth": 6,
    "seventh": 7, "eighth": 8, "ninth": 9, "tenth": 10, "eleventh": 11,
    "twelfth": 12, "thirteenth": 13, "fourteenth": 14, "fifteenth": 15,
    "sixteenth": 16, "seventeenth": 17, "eighteenth": 18, "nineteenth": 19,
    "twentieth": 20, "thirtieth": 30,
}
MONTHS = {
    m: i + 1 for i, m in enumerate([
        "january", "february", "march", "april", "may", "june", "july",
        "august", "september", "october", "november", "december",
    ])
}
MONTHS.update({m[:3]: i for m, i in list(MONTHS.items())})
MONTHS["sept"] = 9

# Letter-digit chunks stay whole ("sw1a", "k7m", "3rd"), and so do numbers with
# separators inside them ("1,248.50", "4:30").
_TOKEN = re.compile(r"[a-z]+'[a-z]+|[a-z0-9]+(?:[.,:][0-9]+)*|[^\sa-z0-9]", re.I)


def tokens(text: str) -> list[str]:
    return _TOKEN.findall(text.lower())


def spell_to_digits(text: str, amounts: bool = False) -> str:
    """Rewrite spelled numbers as digits, leaving everything else as it was.

    Units said one after another stay separate ("four one five" -> "4 1 5"), the way
    a phone number is read; a ten followed by a unit combines ("forty two" -> "42").
    "oh" next to a number is a zero, and "double"/"triple" repeat the next digit.
    With `amounts`, "hundred" and "thousand" are left in place for the money
    scorer to sum ("one thousand two hundred" stays "1 thousand 2 hundred").
    """
    words = tokens(text)
    out: list[str] = []
    i = 0

    def is_num(w: str | None) -> bool:
        return w is not None and (w.isdigit() or w in UNITS or w in TENS or w in ORDINALS)

    while i < len(words):
        w = words[i]
        nxt = words[i + 1] if i + 1 < len(words) else None
        prev = words[i - 1] if i > 0 else None
        if w in ("double", "triple") and nxt is not None and (is_num(nxt) or nxt == "oh"):
            digit = "0" if nxt == "oh" else str(UNITS.get(nxt, nxt))
            out.append(digit * (2 if w == "double" else 3))
            i += 2
            continue
        if w == "oh" and (is_num(nxt) or is_num(prev) or nxt in ("double", "triple")):
            out.append("0")
            i += 1
            continue
        if w in TENS:
            value = TENS[w]
            if nxt in UNITS and UNITS[nxt] < 10:
                value += UNITS[nxt]
                i += 1
            elif nxt in ORDINALS and ORDINALS[nxt] < 10:
                value += ORDINALS[nxt]
                i += 1
            out.append(str(value))
            i += 1
            continue
        if w in UNITS or w in ORDINALS:
            value = UNITS.get(w, ORDINALS.get(w))
            if nxt == "hundred" and not amounts:
                rest = words[i + 2] if i + 2 < len(words) else None
                if rest == "and":
                    i += 1
                    rest = words[i + 2] if i + 2 < len(words) else None
                if rest in TENS or (rest in UNITS and UNITS[rest] >= 10):
                    out.append(str(value))  # "four hundred fifteen" -> 4 + 15
                elif rest in UNITS:
                    out.append(f"{value}0")  # "four hundred five" -> 40 + 5
                else:
                    out.append(f"{value}00")
                i += 2
                continue
            out.append(str(value))
            i += 1
            continue
        out.append(w)
        i += 1
    return " ".join(out)


def _runs(text: str, keep) -> list[str]:
    """Join consecutive tokens that `keep` accepts into runs; anything else splits."""
    runs, current = [], []
    for tok in spell_to_digits(text).split():
        piece = keep(tok)
        if piece is None:
            if tok in "-.,()/+" and current:
                continue  # punctuation inside a number does not end it
            if current:
                runs.append("".join(current))
            current = []
        else:
            current.append(piece)
    if current:
        runs.append("".join(current))
    return runs


def digit_runs(text: str) -> list[str]:
    def keep(tok: str) -> str | None:
        stripped = re.sub(r"[.,:\-]", "", tok)
        return stripped if stripped.isdigit() else None
    return _runs(text, keep)


def alnum_runs(text: str) -> list[str]:
    """Runs of letter-digit chunks, for postcodes and references.

    A chunk counts when it holds a digit ("k7m", "SW1A"), is one letter ("K"), is
    written in capitals ("HYK"), or is a spelled digit ("one"). Any other word ends
    the run, so a run cannot borrow letters from the sentence around it. Case is
    read from the transcript as written, so this does not lowercase first.
    """
    runs, current = [], []
    for tok in re.findall(r"[A-Za-z0-9]+|[^\sA-Za-z0-9]", text):
        low = tok.lower()
        if low in UNITS and UNITS[low] < 10:
            current.append(str(UNITS[low]))
        elif any(c.isdigit() for c in tok) or len(tok) == 1 and tok.isalpha() or tok.isupper():
            current.append(tok.upper())
        elif tok in "-.," and current:
            continue  # "G9, 9SX": a pause read as a comma does not split a postcode
        else:
            if current:
                runs.append("".join(current))
            current = []
    if current:
        runs.append("".join(current))
    return runs


def score_digits(transcript: str, gold: dict) -> tuple[bool, str]:
    runs = digit_runs(transcript)
    target = gold["digits"]
    hit = next((r for r in runs if target in r), None)
    return (hit is not None, hit or " | ".join(runs))


def score_alnum(transcript: str, gold: dict) -> tuple[bool, str]:
    runs = alnum_runs(transcript)
    target = gold["alnum"].upper()
    hit = next((r for r in runs if target in r), None)
    return (hit is not None, hit or " | ".join(runs))


_MONEY_SYMBOL = re.compile(r"([$£€])\s?(\d[\d,]*)(?:\.(\d{1,2}))?")
_MONEY_WORDS = re.compile(
    r"(\d[\d,]*)(?:\.(\d{1,2}))?\s*(dollars?|bucks|pounds?|quid|euros?)"
    # "34 pounds 99" is how a Briton says 34.99, so the pence word is optional.
    r"(?:\s*(?:and\s*)?(\d{1,2})\b(?:\s*(?:cents?|pence|p)\b)?)?"
)
_CURRENCY = {"$": "USD", "£": "GBP", "€": "EUR", "dollar": "USD", "buck": "USD",
             "pound": "GBP", "quid": "GBP", "euro": "EUR"}


def _join_spoken_amount(text: str) -> str:
    """Turn "1 thousand 2 hundred 48" style leftovers into one number."""
    def repl(m: re.Match) -> str:
        parts = m.group(0).split()
        total, current = 0, 0
        for p in parts:
            if p == "thousand":
                total += (current or 1) * 1000
                current = 0
            elif p == "hundred":
                current = (current or 1) * 100
            elif p.isdigit():
                current += int(p)
        return str(total + current)
    return re.sub(r"\d+(?:\s+(?:thousand|hundred|\d+))+(?=\s*(?:dollars?|pounds?|euros?|quid|bucks))", repl, text)


def money_mentions(transcript: str) -> list[tuple[str, int]]:
    text = _join_spoken_amount(spell_to_digits(transcript, amounts=True))
    # spell_to_digits spaces out symbols; put "$ 34.99" back together.
    text = re.sub(r"([$£€])\s+(?=\d)", r"\1", text)
    found = []
    for sym, whole, frac in _MONEY_SYMBOL.findall(text):
        cents = int(whole.replace(",", "")) * 100 + (int(frac.ljust(2, "0")) if frac else 0)
        found.append((_CURRENCY[sym], cents))
    for whole, frac, unit, cents_word in _MONEY_WORDS.findall(text):
        cur = _CURRENCY[unit.rstrip("s")]
        frac = frac or cents_word
        cents = int(whole.replace(",", "")) * 100 + (int(frac.ljust(2, "0")) if frac else 0)
        found.append((cur, cents))
    return found


def score_money(transcript: str, gold: dict) -> tuple[bool, str]:
    found = money_mentions(transcript)
    ok = (gold["currency"], gold["cents"]) in found
    heard = ", ".join(f"{c} {v / 100:.2f}" for c, v in found)
    return ok, heard


def date_mentions(transcript: str) -> list[tuple[int, int]]:
    skip = {"st", "nd", "rd", "th", "of", "the", "on"}
    words = [w for w in spell_to_digits(transcript).replace(",", " ").split() if w not in skip]
    found = []
    for i, w in enumerate(words):
        month = MONTHS.get(w.rstrip("."))
        if month is None:
            continue
        after = words[i + 1:i + 2]
        before = words[max(0, i - 2):i]
        for cand in after + before[::-1]:
            m = re.fullmatch(r"(\d{1,2})(?:st|nd|rd|th)?", cand)
            if m and 1 <= int(m.group(1)) <= 31:
                found.append((month, int(m.group(1))))
                break
    for a, b, _ in re.findall(r"\b(\d{1,2})[/.-](\d{1,2})[/.-](\d{2,4})\b", transcript):
        a, b = int(a), int(b)
        if a <= 12:
            found.append((a, b))
        if b <= 12:
            found.append((b, a))
    for _, mo, d in re.findall(r"\b(\d{4})-(\d{1,2})-(\d{1,2})\b", transcript):
        found.append((int(mo), int(d)))
    return found


def score_date(transcript: str, gold: dict) -> tuple[bool, str]:
    found = date_mentions(transcript)
    ok = (gold["month"], gold["day"]) in found
    return ok, ", ".join(f"{m}/{d}" for m, d in found)


def time_mentions(transcript: str) -> list[tuple[int, int, bool]]:
    """(hour, minute, has_meridiem) for every time found, with hour in 24h when known."""
    text = spell_to_digits(transcript)
    text = re.sub(r"\b(\d{1,2}) (\d{2})\b", r"\1:\2", text)  # "4 30 pm" -> "4:30 pm"
    text = re.sub(r"\b(\d{1,2}) : (\d{2})\b", r"\1:\2", text)
    text = re.sub(r"\s*\bo'?clock\b", ":00", text)
    # "oh nine thirty" is often written "0930": a 24-hour time without its colon.
    text = re.sub(r"\b([01]\d|2[0-3])([0-5]\d)\b", r"\1:\2", text)
    found = []
    pat = re.compile(r"\b(\d{1,2})(?::\s?(\d{2}))?\s*(?:(a|p)\s?\.?\s?m\b\.?)?", re.I)
    for h, m, mer in pat.findall(text):
        if not m and not mer:
            continue
        h, m = int(h), int(m or 0)
        if h > 23 or m > 59:
            continue
        if mer:
            h = h % 12 + (12 if mer.lower() == "p" else 0)
        found.append((h, m, bool(mer)))
    return found


def score_time(transcript: str, gold: dict) -> tuple[bool, str]:
    found = time_mentions(transcript)
    gh, gm = gold["hour"], gold["minute"]
    ok = any(m == gm and (h == gh or (not mer and h == (gh % 12 or 12))) for h, m, mer in found)
    return ok, ", ".join(f"{h}:{m:02d}" for h, m, _ in found)


def spoken_email_to_written(transcript: str) -> str:
    text = spell_to_digits(transcript)
    for word, sym in ((" at ", "@"), (" dot ", "."), (" underscore ", "_"),
                      (" dash ", "-"), (" hyphen ", "-")):
        text = text.replace(word, sym)
    return re.sub(r"\s+", "", text)


def score_email(transcript: str, gold: dict) -> tuple[bool, str]:
    target = gold["email"].lower()
    squashed = spoken_email_to_written(transcript.lower())
    if target in squashed:
        return True, target
    written = re.search(r"[\w.+-]+@[\w.-]+\w", transcript.lower())
    return False, written.group(0) if written else squashed[-60:]


SCORERS = {
    "us_phone": score_digits,
    "uk_mobile": score_digits,
    "card_last4": score_digits,
    "us_zip": score_digits,
    "uk_postcode": score_alnum,
    "booking_ref": score_alnum,
    "price_usd": score_money,
    "price_gbp": score_money,
    "date": score_date,
    "time": score_time,
    "email": score_email,
}


def score(category: str, transcript: str, gold: dict) -> tuple[bool, str]:
    return SCORERS[category](transcript or "", gold)
