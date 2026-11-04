"""Probe: does Universal-3.5 Pro turn "...900.99" amounts into "...999.99"?

    uv run python -m probes.money_900

full-v1 found `£7,900.99` transcribed as `£7,999.99` in 20 of 20 takes while
Whisper heard "7,900 pounds and 99 pence". This speaks a set of nearby amounts
with one voice and transcribes each with both listeners, to find the pattern.
"""

import json
from pathlib import Path

from otp import channel
from otp.aai import AssemblyAI
from otp.score import money_mentions
from otp.second_listener import whisper

AMOUNTS = ["£7,900.99", "£7,900.50", "£7,900", "£6,900.99", "£900.99", "£7,800.99",
           "£7,090.99", "$7,900.99", "€7,900.99", "£7,900.09"]

api = AssemblyAI()
out = Path("runs/probe-money-900.jsonl")
with out.open("w") as f:
    for amount in AMOUNTS:
        text = f"I can refund {amount} to your original payment method."
        speech = api.speak(text, "aai-nancy", **channel.TTS_FORMATS["pcm24"])
        wav = channel.apply("api24", speech.audio)
        aai = api.transcribe(wav)
        wh = whisper(wav)
        row = {"said": amount, "aai": aai.text, "aai_parsed": money_mentions(aai.text),
               "whisper": wh, "whisper_parsed": money_mentions(wh),
               "tts_request_id": speech.request_id, "stt_session_id": aai.session_id}
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
        print(f"{amount:>10}  AAI: {aai.text[13:-36]!r:28}  Whisper: {wh[13:-36]!r}")
