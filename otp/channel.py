"""What happens to the agent's audio between the TTS API and the caller's ear.

Each condition takes the TTS output and returns 16-bit PCM WAV bytes, the form the
speech-to-text "listener" accepts:

- `api24`: the 24 kHz PCM the API returns by default. This is how AssemblyAI's own
  benchmark heard the model, and it is the baseline.
- `native8`: G.711 mu-law at 8 kHz, asked for from the API directly, the way a
  telephony integration should request it.
- `resampled8`: the 24 kHz audio downsampled and mu-law encoded here, the way many
  pipelines do it when they request the default format and convert it themselves.
- `lossy8`: the 24 kHz audio through a 300-3400 Hz telephone band filter, mu-law at
  8 kHz, with 3% of the 20 ms packets lost. Lost packets are zero-filled, which is
  harsher than the concealment a real network applies, so this is a worst case.
- `retake24`: a second 24 kHz synthesis of the same text. Synthesis is not
  deterministic, so this measures how much one take differs from the next.

`api24`, `resampled8` and `lossy8` share one synthesis, so comparing them isolates
the channel. `native8` and `retake24` are separate syntheses: a difference there
mixes the channel (for `native8`) with take-to-take variation.

Real calls over LiveKit SIP are recorded separately and checked against these.
"""

from __future__ import annotations

import io
import random
import subprocess
import wave

CONDITIONS = ["api24", "resampled8", "lossy8", "native8", "retake24"]
# The synthesis each condition is made from; the same name means the same audio.
SOURCE = {"api24": "pcm24", "resampled8": "pcm24", "lossy8": "pcm24",
          "native8": "mulaw8", "retake24": "pcm24b"}
SHARED_TAKE = {"resampled8", "lossy8"}  # conditions paired exactly with api24
TTS_FORMATS = {
    "pcm24": {"encoding": "pcm_s16le", "sample_rate": 24000},
    "pcm24b": {"encoding": "pcm_s16le", "sample_rate": 24000},
    "mulaw8": {"encoding": "pcm_mulaw", "sample_rate": 8000},
}


def ffmpeg(audio: bytes, *args: str, fmt: str = "wav") -> bytes:
    cmd = ["ffmpeg", "-v", "error", "-i", "pipe:0", *args, "-f", fmt, "pipe:1"]
    return subprocess.run(cmd, input=audio, capture_output=True, check=True).stdout


def wav_from_pcm(pcm: bytes, rate: int) -> bytes:
    out = io.BytesIO()
    with wave.open(out, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(pcm)
    return out.getvalue()


def to_pcm16(audio: bytes, rate: int, *filters: str) -> bytes:
    """Decode any WAV to mono 16-bit PCM at `rate`.

    ffmpeg writes placeholder sizes into a WAV header it streams to a pipe, which
    Python's wave module refuses, so ffmpeg emits raw samples and the header is
    written here.
    """
    args = ["-ac", "1", "-ar", str(rate), *filters, "-acodec", "pcm_s16le"]
    return wav_from_pcm(ffmpeg(audio, *args, fmt="s16le"), rate)


def drop_packets(pcm_wav: bytes, loss: float, seed: str, frame_ms: int = 20) -> bytes:
    """Zero out `loss` of the 20 ms frames, chosen by a seeded generator."""
    with wave.open(io.BytesIO(pcm_wav)) as r:
        params, data = r.getparams(), bytearray(r.readframes(r.getnframes()))
    step = params.framerate * frame_ms // 1000 * params.sampwidth
    rng = random.Random(seed)
    for start in range(0, len(data), step):
        if rng.random() < loss:
            data[start:start + step] = bytes(min(step, len(data) - start))
    return wav_from_pcm(bytes(data), params.framerate)


def apply(condition: str, tts_audio: bytes, seed: str = "0") -> bytes:
    """Turn the TTS WAV for `SOURCE[condition]` into the PCM WAV a listener hears."""
    if condition in ("api24", "retake24"):
        return to_pcm16(tts_audio, 24000)
    if condition == "native8":
        return to_pcm16(tts_audio, 8000)
    if condition == "resampled8":
        mulaw = ffmpeg(tts_audio, "-ar", "8000", "-ac", "1", "-acodec", "pcm_mulaw")
        return to_pcm16(mulaw, 8000)
    if condition == "lossy8":
        mulaw = ffmpeg(tts_audio, "-af", "highpass=f=300,lowpass=f=3400",
                       "-ar", "8000", "-ac", "1", "-acodec", "pcm_mulaw")
        return drop_packets(to_pcm16(mulaw, 8000), loss=0.03, seed=seed)
    raise ValueError(f"unknown condition {condition!r}")


def duration_ms(pcm_wav: bytes) -> int:
    with wave.open(io.BytesIO(pcm_wav)) as r:
        return round(r.getnframes() * 1000 / r.getframerate())


def sample_rate(pcm_wav: bytes) -> int:
    with wave.open(io.BytesIO(pcm_wav)) as r:
        return r.getframerate()
