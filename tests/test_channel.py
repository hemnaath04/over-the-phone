import io
import math
import struct
import wave

import pytest

from otp import channel


def tone_wav(rate: int, seconds: float = 1.0, encoding: str = "pcm_s16le") -> bytes:
    n = int(rate * seconds)
    samples = b"".join(struct.pack("<h", int(8000 * math.sin(2 * math.pi * 440 * i / rate))) for i in range(n))
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(samples)
    wav = buf.getvalue()
    if encoding == "pcm_mulaw":
        wav = channel.ffmpeg(wav, "-acodec", "pcm_mulaw")
    return wav


@pytest.mark.parametrize("condition, src_rate, src_enc, out_rate", [
    ("api24", 24000, "pcm_s16le", 24000),
    ("native8", 8000, "pcm_mulaw", 8000),
    ("resampled8", 24000, "pcm_s16le", 8000),
    ("lossy8", 24000, "pcm_s16le", 8000),
    ("retake24", 24000, "pcm_s16le", 24000),
])
def test_conditions_produce_pcm16_at_the_right_rate(condition, src_rate, src_enc, out_rate):
    out = channel.apply(condition, tone_wav(src_rate, encoding=src_enc), seed="x")
    with wave.open(io.BytesIO(out)) as r:
        assert r.getsampwidth() == 2
        assert r.getnchannels() == 1
    assert channel.sample_rate(out) == out_rate
    assert abs(channel.duration_ms(out) - 1000) <= 20


def test_packet_loss_is_seeded_and_roughly_the_rate_asked():
    src = channel.to_pcm16(tone_wav(8000, seconds=10), 8000)
    a = channel.drop_packets(src, 0.03, seed="s")
    assert a == channel.drop_packets(src, 0.03, seed="s")
    with wave.open(io.BytesIO(a)) as r:
        data = r.readframes(r.getnframes())
    frame = 160 * 2  # 20 ms at 8 kHz, 16-bit
    silent = sum(1 for i in range(0, len(data), frame) if not any(data[i:i + frame]))
    assert 2 <= silent <= 35  # about 3% of 500 frames
