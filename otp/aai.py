"""Thin clients for the two AssemblyAI calls the harness makes.

Both keep the IDs AssemblyAI support asks for (`x-request-id` for TTS, `session_id`
for STT), so every row of a report can be traced back to one request.
"""

from __future__ import annotations

import json
import os
import random
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path

import httpx

TTS_URL = "https://tts.us.assemblyai.com/v1/speech"
STT_URL = "https://sync.assemblyai.com/v1/transcribe"
STT_MODEL = "universal-3-5-pro"
RETRY_STATUS = {429, 500, 502, 503, 504}


def api_key() -> str:
    key = os.environ.get("ASSEMBLYAI_API_KEY")
    if not key:
        env = Path(__file__).resolve().parent.parent / ".env"
        if env.exists():
            for line in env.read_text().splitlines():
                if line.startswith("ASSEMBLYAI_API_KEY="):
                    key = line.split("=", 1)[1].strip()
    if not key:
        raise SystemExit("Set ASSEMBLYAI_API_KEY or put it in .env")
    return key


class RateLimiter:
    """At most `per_minute` calls in any 60 s window, shared across threads."""

    def __init__(self, per_minute: int):
        self.interval = 60.0 / per_minute
        self.lock = threading.Lock()
        self.next_at = 0.0

    def wait(self) -> None:
        with self.lock:
            now = time.monotonic()
            at = max(now, self.next_at)
            self.next_at = at + self.interval
        time.sleep(max(0.0, at - now))


def _send(client: httpx.Client, limiter: RateLimiter, attempts: int = 6, **request) -> httpx.Response:
    for attempt in range(attempts):
        limiter.wait()
        try:
            resp = client.request(**request)
        except httpx.TransportError:
            if attempt == attempts - 1:
                raise
            time.sleep(2 ** attempt + random.random())
            continue
        if resp.status_code not in RETRY_STATUS or attempt == attempts - 1:
            return resp
        retry_after = resp.headers.get("retry-after")
        time.sleep(float(retry_after) if retry_after else 2 ** attempt + random.random())
    raise RuntimeError("unreachable")


@dataclass
class Speech:
    audio: bytes
    request_id: str
    billed_characters: int
    audio_duration_ms: int


@dataclass
class Transcript:
    text: str
    session_id: str
    request_time_ms: float
    words: list = field(default_factory=list)  # {"text", "start", "end"} ms, with timestamps


class AssemblyAI:
    def __init__(self, tts_per_minute: int = 40, stt_per_minute: int = 120):
        self.client = httpx.Client(headers={"Authorization": api_key()}, timeout=60)
        self.tts_limit = RateLimiter(tts_per_minute)
        self.stt_limit = RateLimiter(stt_per_minute)

    def speak(self, text: str, voice_id: str, encoding: str, sample_rate: int) -> Speech:
        body = {"text": text, "voice_id": voice_id, "encoding": encoding,
                "sample_rate": sample_rate, "container": "wav", "stream": False}
        resp = _send(self.client, self.tts_limit, method="POST", url=TTS_URL, json=body)
        if resp.status_code != 200:
            raise RuntimeError(f"TTS {resp.status_code}: {resp.text[:300]}")
        h = resp.headers
        return Speech(resp.content, h.get("x-request-id", ""),
                      int(h.get("x-tts-billed-characters", 0)),
                      int(h.get("x-tts-audio-duration-ms", 0)))

    def transcribe(self, wav: bytes, timestamps: bool = False) -> Transcript:
        files = {"audio": ("audio.wav", wav, "audio/wav")}
        if timestamps:
            files["config"] = (None, json.dumps({"timestamps": True}), "application/json")
        resp = _send(self.client, self.stt_limit, method="POST", url=STT_URL,
                     headers={"X-AAI-Model": STT_MODEL}, files=files)
        if resp.status_code != 200:
            raise RuntimeError(f"STT {resp.status_code}: {resp.text[:300]}")
        d = resp.json()
        return Transcript(d.get("text", ""), d.get("session_id", ""), d.get("request_time_ms", 0.0),
                          d.get("words", []))
