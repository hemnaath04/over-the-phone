"""Find the hard entities in free text, in the form the scorer checks against.

The benchmark builds its sentences around known entities; Heard As takes whatever
an agent is about to say, so it has to find them. Each detector returns spans with
a category and a `gold` value shaped like the ones in `otp.entities`, so
`otp.score.score` can judge a transcript of the spoken text against each of them.

Detectors run in order and a later one never claims characters an earlier one
took, so an email's digits are not also read as a phone number.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from otp.entities import MONTHS


@dataclass
class Span:
    start: int
    end: int
    category: str
    gold: dict

    @property
    def length(self) -> int:
        return self.end - self.start


def _email(m: re.Match, locale: str) -> dict:
    return {"email": m.group(0)}


def _us_phone(m: re.Match, locale: str) -> dict:
    return {"digits": re.sub(r"\D", "", m.group(0))[-10:]}


def _uk_mobile(m: re.Match, locale: str) -> dict:
    return {"digits": re.sub(r"\D", "", m.group(0))[-10:]}


def _postcode(m: re.Match, locale: str) -> dict:
    return {"alnum": m.group(0).replace(" ", "")}


def _money(m: re.Match, locale: str) -> dict:
    sym, whole, frac = m.group(1), m.group(2), m.group(3)
    cents = int(whole.replace(",", "")) * 100 + (int(frac) if frac else 0)
    return {"currency": {"$": "USD", "£": "GBP", "€": "EUR"}[sym], "cents": cents}


def _numeric_date(m: re.Match, locale: str) -> dict | None:
    a, b = int(m.group(1)), int(m.group(2))
    month, day = (b, a) if locale == "en-GB" else (a, b)
    if not (1 <= month <= 12):
        month, day = day, month
    if not (1 <= month <= 12 and 1 <= day <= 31):
        return None
    return {"month": month, "day": day, "style": "numeric"}


def _iso_date(m: re.Match, locale: str) -> dict:
    return {"month": int(m.group(2)), "day": int(m.group(3)), "style": "iso"}


def _word_date(m: re.Match, locale: str) -> dict:
    return {"month": MONTHS.index(m.group(1).capitalize()) + 1, "day": int(m.group(2)), "style": "words"}


def _time(m: re.Match, locale: str) -> dict:
    h, mi, mer = int(m.group(1)), int(m.group(2) or 0), (m.group(3) or "").lower()
    if mer.startswith("p") and h < 12:
        h += 12
    if mer.startswith("a") and h == 12:
        h = 0
    return {"hour": h, "minute": mi}


def _reference(m: re.Match, locale: str) -> dict:
    return {"alnum": m.group(2).replace("-", "")}


def _last4(m: re.Match, locale: str) -> dict:
    return {"digits": m.group(2)}


MONTH_WORDS = "|".join(MONTHS)
DETECTORS = [
    ("email", re.compile(r"\b[\w.+-]+@[\w-]+(?:\.[\w-]+)+\b"), _email),
    ("uk_mobile", re.compile(r"(?:\+44 ?7\d{3}|\b07\d{3}) ?\d{3} ?\d{3}\b"), _uk_mobile),
    ("us_phone", re.compile(r"\(\d{3}\) ?\d{3}-\d{4}\b|\b\d{3}[-.]\d{3}[-.]\d{4}\b"), _us_phone),
    ("uk_postcode", re.compile(r"\b[A-Z]{1,2}\d[A-Z\d]? \d[A-Z]{2}\b"), _postcode),
    ("price", re.compile(r"([$£€])(\d[\d,]*)(?:\.(\d{2}))?"), _money),
    ("date", re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b"), _iso_date),
    ("date", re.compile(r"\b(\d{1,2})/(\d{1,2})/(\d{2,4})\b"), _numeric_date),
    ("date", re.compile(rf"\b({MONTH_WORDS}) (\d{{1,2}})(?:st|nd|rd|th)?\b", re.I), _word_date),
    ("time", re.compile(r"\b(\d{1,2}):(\d{2})(?:\s?([AaPp])\.?[Mm]\b)?(?!\d)"), _time),
    ("time", re.compile(r"\b(\d{1,2})()\s?([AaPp])\.?[Mm]\b\.?"), _time),
    # Only the lead-in is case-insensitive: the code itself is capitals and digits,
    # so "booking reference is" never takes "reference" as the code.
    ("booking_ref", re.compile(
        r"\b((?i:reference|ref|code|confirmation|booking|order|ticket)(?i: number| no\.?)?(?i: is|:)?\s+)"
        r"([A-Z0-9]{2,5}-?[A-Z0-9]{2,5})\b"), _reference),
    ("card_last4", re.compile(r"\b(ending(?: in)?\s+)(\d{4})\b", re.I), _last4),
    ("us_zip", re.compile(r"\b((?:ZIP(?: code)?(?: is)?|deliver to)\s+)(\d{5})\b", re.I), _last4),
]
# The scorer judges prices by currency, so both money categories share one scorer.
SCORE_AS = {"price": "price_usd"}


def detect(text: str, locale: str = "en-US") -> list[Span]:
    taken = [False] * len(text)
    spans = []
    for category, pattern, make in DETECTORS:
        for m in pattern.finditer(text):
            # For "reference is K7M-4QX" the entity is the code, not the lead-in.
            start, end = (m.start(2), m.end(2)) if category in ("booking_ref", "card_last4", "us_zip") else m.span()
            if any(taken[start:end]):
                continue
            gold = make(m, locale)
            if gold is None:
                continue
            spans.append(Span(start, end, category, gold))
            for i in range(start, end):
                taken[i] = True
    return sorted(spans, key=lambda s: s.start)


def scorer_category(span: Span) -> str:
    return SCORE_AS.get(span.category, span.category)
