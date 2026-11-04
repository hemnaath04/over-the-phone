"""Join a LiveKit room as a silent listener and record what the agent says.

    uv run --group agent python agent/room_listener.py --seconds 200 --out runs/webrtc-1/agent.wav

Joining an empty room dispatches the agent (automatic dispatch, no agent name), so
with the worker in reader mode this records the whole script over LiveKit's WebRTC
path, with no phone in between. Score the file like a phone recording:

    uv run python -m otp.score_call runs/webrtc-1/agent.wav --name webrtc-1

It is the check that reader mode works before a real call, and the LiveKit baseline
the phone recording is compared with.
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
import time
import uuid
from pathlib import Path

from dotenv import load_dotenv
from livekit import api, rtc

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from otp.channel import wav_from_pcm  # noqa: E402

load_dotenv(ROOT / ".env")
RATE = 24000


async def main(seconds: int, out: Path) -> None:
    room_name = f"otp-listen-{uuid.uuid4().hex[:6]}"
    token = (api.AccessToken(os.environ["LIVEKIT_API_KEY"], os.environ["LIVEKIT_API_SECRET"])
             .with_identity("listener").with_grants(api.VideoGrants(room_join=True, room=room_name))
             .to_jwt())
    room = rtc.Room()
    pcm = bytearray()
    first_audio = None

    async def record(track: rtc.Track) -> None:
        nonlocal first_audio
        async for event in rtc.AudioStream(track, sample_rate=RATE, num_channels=1):
            if first_audio is None:
                first_audio = time.monotonic()
            pcm.extend(event.frame.data.tobytes())

    @room.on("track_subscribed")
    def on_track(track: rtc.Track, _pub, participant: rtc.RemoteParticipant) -> None:
        if track.kind == rtc.TrackKind.KIND_AUDIO:
            print(f"recording {participant.identity}")
            asyncio.ensure_future(record(track))

    joined = time.monotonic()
    await room.connect(os.environ["LIVEKIT_URL"], token)
    print(f"joined {room_name}; listening for {seconds} s")
    await asyncio.sleep(seconds)
    await room.disconnect()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(wav_from_pcm(bytes(pcm), RATE))
    lag = f"{first_audio - joined:.1f} s after joining" if first_audio else "never"
    print(f"wrote {out} ({len(pcm) / 2 / RATE:.0f} s of audio); first agent audio {lag}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--seconds", type=int, default=200)
    ap.add_argument("--out", type=Path, default=ROOT / "runs" / "webrtc-1" / "agent.wav")
    args = ap.parse_args()
    asyncio.run(main(args.seconds, args.out))
