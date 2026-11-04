"""Rewrite agent text so a caller cannot mishear the entities in it.

AssemblyAI-TTS-1 has no SSML or pronunciation dictionary; its prompting guide says
the written form is the control ("4-3-2-1" is read digit by digit, dashes between
letters spell a word out). These rewrites apply that guide to the failures the
full-v1 run found:

- Numeric dates are spoken in words for the caller's locale, so `05/08/2026` is
  "the 5th of August" in the UK instead of the "May 8th" every voice says today.
- Email local parts are spelled letter by letter ("O-K-A-F-O-R"): a surname heard
  correctly still cannot be spelled from sound (Okafor came back as okafur, Patel
  as paytel, Wong as wang).
- Postcodes and booking references are spelled with dashes, and letters that a
  3.4 kHz phone band blurs together (F/S, E/C, B/D/P/T/V, M/N) get a phonetic
  clarifier, the way a person on the phone says "F for Foxtrot".
- Card and ZIP digits are dashed so each digit is read alone. Phone numbers are
  left as written: the server's normalizer already reads them digit by digit, and
  dashing them made the model drop a digit from runs like "5-5-5-5" (speakable-v1,
  us_phone-015/017/019: an area code ending in 5 followed by 555).
- 24-hour times become 12-hour times with AM/PM in the US locale.

`speakable(text, locale)` is pure text in, text out, so it can sit between an
LLM's output and any TTS session.
"""

from __future__ import annotations

import re

MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]
NATO = {"A": "Alpha", "B": "Bravo", "C": "Charlie", "D": "Delta", "E": "Echo",
        "F": "Foxtrot", "G": "Golf", "H": "Hotel", "J": "Juliet", "K": "Kilo",
        "L": "Lima", "M": "Mike", "N": "November", "P": "Papa", "Q": "Quebec",
        "R": "Romeo", "S": "Sierra", "T": "Tango", "U": "Uniform", "V": "Victor",
        "W": "Whiskey", "X": "X-ray", "Y": "Yankee", "Z": "Zulu"}
# Letters that sound alike once a phone line cuts everything above 3.4 kHz.
CONFUSABLE = set("FSECBDPTVMN")


def ordinal(n: int) -> str:
    suffix = "th" if 11 <= n % 100 <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def say_date(month: int, day: int, locale: str) -> str:
    if locale == "en-GB":
        return f"the {ordinal(day)} of {MONTHS[month - 1]}"
    return f"{MONTHS[month - 1]} {ordinal(day)}"


def dash(chars: str) -> str:
    return "-".join(chars)


def clarify(spoken: str, chars: str) -> str:
    """Append a phonetic note for confusable letters after the whole entity.

    'M-U-6-M-R-F' -> 'M-U-6-M-R-F, that's M for Mike, F for Foxtrot'. The note goes
    at the end so it never splits the entity the caller is writing down.
    """
    seen = []
    for c in chars:
        if c in CONFUSABLE and c not in seen:
            seen.append(c)
    if not seen:
        return spoken
    return spoken + ", that's " + ", ".join(f"{c} for {NATO[c]}" for c in seen)


def _dates(text: str, locale: str) -> str:
    def iso(m: re.Match) -> str:
        return say_date(int(m.group(2)), int(m.group(3)), locale)

    def numeric(m: re.Match) -> str:
        a, b = int(m.group(1)), int(m.group(2))
        month, day = (b, a) if locale == "en-GB" else (a, b)
        if not (1 <= month <= 12 and 1 <= day <= 31):
            month, day = day, month  # 25/10 in a US locale can only mean October 25th
        return say_date(month, day, locale)

    text = re.sub(r"\b(\d{4})-(\d{2})-(\d{2})\b", iso, text)
    return re.sub(r"\b(\d{1,2})/(\d{1,2})/(\d{2,4})\b", numeric, text)


def _times(text: str, locale: str) -> str:
    if locale == "en-GB":
        return text  # 24-hour times are normal speech in the UK

    def repl(m: re.Match) -> str:
        h, mi = int(m.group(1)), int(m.group(2))
        h12, ampm = h % 12 or 12, "AM" if h < 12 else "PM"
        return f"{h12}:{mi:02d} {ampm}" if mi else f"{h12} {ampm}"
    return re.sub(r"\b([01]\d|2[0-3]):([0-5]\d)\b(?!\s*[AaPp]\.?[Mm])", repl, text)


def _emails(text: str) -> str:
    def repl(m: re.Match) -> str:
        local, domain = m.group(1), m.group(2)
        parts = [dash(p.upper()) for p in local.split(".")]
        return " dot ".join(parts) + " at " + domain
    return re.sub(r"\b([A-Za-z0-9._]+)@([A-Za-z0-9-]+(?:\.[A-Za-z]{2,})+)\b", repl, text)


def _postcodes(text: str) -> str:
    def repl(m: re.Match) -> str:
        return clarify(f"{dash(m.group(1))}, {dash(m.group(2))}", m.group(1) + m.group(2))
    return re.sub(r"\b([A-Z]{1,2}\d[A-Z\d]?) (\d[A-Z]{2})\b", repl, text)


def _references(text: str) -> str:
    def repl(m: re.Match) -> str:
        ref = m.group(2).replace("-", "")
        return m.group(1) + clarify(dash(ref), ref)
    return re.sub(r"((?:reference|code|ref)(?: number)? is )([A-Z0-9]{3}-?[A-Z0-9]{3})\b", repl, text)


def _digits(text: str, dash_phones: bool = False) -> str:
    def group(m: re.Match) -> str:
        digits = re.sub(r"\D", "", m.group(0))
        lead = "+" if m.group(0).startswith("+") else ""
        if lead:  # +44 7700 900123 -> +4-4, 7-7-0-0, 9-0-0-1-2-3
            groups = [g for g in re.split(r"[\s.-]+", m.group(0)[1:]) if g]
            return "+" + ", ".join(dash(g) for g in groups)
        groups = [g for g in re.split(r"[\s().-]+", m.group(0)) if g]
        return ", ".join(dash(g) for g in groups) if len(groups) > 1 else dash(digits)

    if dash_phones:
        text = re.sub(r"\+\d{2} \d{4} \d{3} ?\d{3}", group, text)  # UK international
        text = re.sub(r"\(\d{3}\) \d{3}-\d{4}|\b\d{3}[-.]\d{3}[-.]\d{4}\b", group, text)  # US
        text = re.sub(r"\b0\d{4} \d{3} ?\d{3}\b", group, text)  # UK national
    text = re.sub(r"(card ending(?: in)? )(\d{4})\b", lambda m: m.group(1) + dash(m.group(2)), text)
    return re.sub(r"(ZIP code is |deliver to )(\d{5})\b", lambda m: m.group(1) + dash(m.group(2)), text)


def speakable(text: str, locale: str = "en-US", dash_phones: bool = False) -> str:
    """Rewrite `text`; `dash_phones` restores the v1 phone dashing, kept for comparison."""
    for step in (_emails, _postcodes, _references):
        text = step(text)
    text = _digits(text, dash_phones)
    return _times(_dates(text, locale), locale)
