"""Heard As: what a caller will hear when a voice agent says this text over a phone.

    check(text, voice="aai-audrey", locale="en-US") -> dict

The text is spoken by AssemblyAI-TTS-1, passed through a phone channel from
`otp.channel`, and heard by two independent listeners: AssemblyAI's Universal-3.5
Pro (what your call logs and any LLM downstream will read) and Whisper small.en (a
model that shares nothing with it). Every entity `otp.detect` finds gets a verdict:

- `clear`: both listeners got it.
- `caller`: both got it wrong, the same way a person writing it down would. The
  voice said it wrong or it can't be told apart by ear; this is what Speakable fixes.
- `logs`: Whisper got it but Universal-3.5 Pro didn't. The caller probably heard it
  right, but the transcript of the call is wrong (the £7,900.99 -> £7,999.99 bug).
- `unsure`: only Whisper missed it. Whisper alone misses about 12% of correct clips
  in the benchmark, so this is most likely fine.

`compare(text, ...)` checks the text as written and as Speakable rewrites it, in
parallel, and reports each entity before and after.
"""

from __future__ import annotations

import base64
import re
from concurrent.futures import ThreadPoolExecutor

from otp import channel
from otp.aai import AssemblyAI
from otp.detect import detect, scorer_category
from otp.entities import MONTHS
from otp.score import date_mentions, money_mentions, score
from otp.second_listener import whisper
from otp.speakable import speakable

_api: AssemblyAI | None = None
_pool = ThreadPoolExecutor(6)


def api() -> AssemblyAI:
    global _api
    if _api is None:
        _api = AssemblyAI(tts_per_minute=40, stt_per_minute=120)
    return _api


def verdict(aai_ok: bool, whisper_ok: bool) -> str:
    if aai_ok and whisper_ok:
        return "clear"
    if not aai_ok and not whisper_ok:
        return "caller"
    return "logs" if whisper_ok else "unsure"


def readable(category: str, transcript: str, heard: str, surface: str) -> str:
    """The scorer's `heard` turned into what a person would write down."""
    if category == "date":
        dates = date_mentions(transcript)
        return ", ".join(f"{MONTHS[m - 1]} {d}" for m, d in dates[:2]) or "(no date)"
    if category in ("price", "price_usd", "price_gbp"):
        sym = {"USD": "$", "GBP": "£", "EUR": "€"}
        found = money_mentions(transcript)
        return ", ".join(f"{sym[c]}{v / 100:,.2f}" for c, v in found[:2]) or "(no amount)"
    if category == "email":
        spoken = re.sub(r"\s+dot\s+", ".", transcript.lower())
        spoken = re.sub(r"(?<=\b\w)-(?=\w\b)", "", spoken)  # "t-p-a-t-e-l" -> "tpatel"
        spoken = re.sub(r"\s+at\s+", "@", spoken)
        # "an email at tpatel at acme.com" has two "at"s; the address is the last match
        # whose domain has a dot in it.
        found = re.findall(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+", spoken)
        return found[-1] if found else "(no address)"
    return heard.split(" | ")[0] if heard else "(not heard)"


def _listen(text: str, voice: str, condition: str) -> dict:
    speech = api().speak(text, voice, **channel.TTS_FORMATS["pcm24"])
    heard_wav = channel.apply(condition, speech.audio, seed=speech.request_id)
    aai_job = _pool.submit(api().transcribe, heard_wav)
    whisper_text = whisper(heard_wav)
    aai = aai_job.result()
    return {"spoken_text": text, "audio": base64.b64encode(heard_wav).decode(),
            "aai_transcript": aai.text, "whisper_transcript": whisper_text,
            "tts_request_id": speech.request_id, "stt_session_id": aai.session_id,
            "seconds": round(channel.duration_ms(heard_wav) / 1000, 1)}


def _judge(spans, heard: dict, text: str) -> list[dict]:
    out = []
    for s in spans:
        cat = scorer_category(s)
        a_ok, a_heard = score(cat, heard["aai_transcript"], s.gold)
        w_ok, w_heard = score(cat, heard["whisper_transcript"], s.gold)
        out.append({
            "verdict": verdict(a_ok, w_ok),
            "aai_heard": readable(s.category, heard["aai_transcript"], a_heard, text[s.start:s.end]),
            "whisper_heard": readable(s.category, heard["whisper_transcript"], w_heard, text[s.start:s.end]),
        })
    return out


def compare(text: str, voice: str = "aai-audrey", locale: str = "en-US",
            condition: str = "resampled8") -> dict:
    spans = detect(text, locale)
    fixed_text = speakable(text, locale)
    before_job = _pool.submit(_listen, text, voice, condition)
    after_job = _pool.submit(_listen, fixed_text, voice, condition) if fixed_text != text else None
    before = before_job.result()
    after = after_job.result() if after_job else before
    b, a = _judge(spans, before, text), _judge(spans, after, text)
    entities = [{"start": s.start, "end": s.end, "surface": text[s.start:s.end],
                 "category": s.category, "before": bv, "after": av}
                for s, bv, av in zip(spans, b, a)]
    return {"text": text, "fixed_text": fixed_text, "voice": voice, "locale": locale,
            "condition": condition, "entities": entities, "before": before, "after": after}
