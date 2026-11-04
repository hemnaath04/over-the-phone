"""A LiveKit phone agent on the all-AssemblyAI stack, with Speakable before the TTS.

    uv run --group agent python agent/phone_agent.py console   # microphone, no LiveKit needed
    uv run --group agent python agent/phone_agent.py dev       # connect to LiveKit for calls

Two modes, picked with AGENT_MODE:

- `receptionist` (default): a dental front desk that confirms an appointment and
  reads back a confirmation code, a phone number and an email, with every reply
  rewritten by `otp.speakable` before it reaches AssemblyAI-TTS-1. This is the demo.
- `reader`: reads the numbered script in `agent/reader_script.json`, each entity
  once as an LLM would write it and once rewritten. Record the call on the phone
  that dialled in, then score the recording with `python -m otp.score_call`. This is
  the real-phone-line sample the simulated channels are checked against.

Set SPEAKABLE=0 to turn the rewrite off, for a side-by-side recording.
Wiring follows https://www.assemblyai.com/docs/tts/livekit (read Nov 4 2026).
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import AsyncIterable

from dotenv import load_dotenv
from livekit import rtc
from livekit.agents import (NOT_GIVEN, Agent, AgentServer, AgentSession, JobContext, JobProcess,
                            ModelSettings, TurnHandlingOptions, cli)
from livekit.plugins import assemblyai, openai, silero

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from otp.speakable import speakable  # noqa: E402

load_dotenv(ROOT / ".env")

MODE = os.environ.get("AGENT_MODE", "receptionist")
REWRITE = os.environ.get("SPEAKABLE", "1") != "0"
LOCALE = os.environ.get("AGENT_LOCALE", "en-US")
VOICE = os.environ.get("AGENT_VOICE", "49c443a4-8a1d-5f7e-b70b-98bdbd9823c3")  # Audrey
VAD_THRESHOLD = 0.2  # matches the STT's own VAD, as in AssemblyAI's guide
SENTENCE_END = re.compile(r"[.!?](?:\s+)")

RECEPTIONIST = """You are Sam, the front desk at Bright Dental. Keep every reply to one
or two short sentences, with no lists, markdown or emojis. The caller, Noah Okafor, is
confirming his cleaning. His appointment is on 11/17/2026 at 15:30 with Dr. Patel.
His confirmation code is MU6-MRF. The office number is (617) 555-0142 and receipts go
to noah.okafor@brightdental.com. Give these exactly as written above when asked or when
confirming; never invent other details."""


class SpeakableAgent(Agent):
    """Rewrites each sentence of the reply with Speakable before synthesis.

    Text arrives a few tokens at a time; a sentence is released to the TTS as soon
    as it ends, so the rewrite never waits for the whole reply.
    """

    async def tts_node(self, text: AsyncIterable[str], model_settings: ModelSettings) -> AsyncIterable[rtc.AudioFrame]:
        async def sentences() -> AsyncIterable[str]:
            buf = ""
            async for chunk in text:
                buf += chunk
                while (m := SENTENCE_END.search(buf)):
                    piece, buf = buf[:m.end()], buf[m.end():]
                    yield speakable(piece, LOCALE) if REWRITE else piece
            if buf.strip():
                yield speakable(buf, LOCALE) if REWRITE else buf

        async for frame in Agent.default.tts_node(self, sentences(), model_settings):
            yield frame


class Receptionist(SpeakableAgent):
    def __init__(self) -> None:
        super().__init__(instructions=RECEPTIONIST)

    async def on_enter(self) -> None:
        self.session.say("Hi, thanks for calling Bright Dental, this is Sam. How can I help?")


class Reader(SpeakableAgent):
    """Speaks the script verbatim: each line already holds the form it should test."""

    def __init__(self) -> None:
        super().__init__(instructions="Read the script. Do not reply to the caller.")
        global REWRITE
        REWRITE = False  # the script carries both forms itself
        self.lines = json.loads((ROOT / "agent" / "reader_script.json").read_text())

    async def on_enter(self) -> None:
        # No interruptions: a cough on the line must not cut an item short.
        say = lambda text: self.session.say(text, allow_interruptions=False)  # noqa: E731
        await say("Starting the test script. Please stay on the line.")
        for line in self.lines:
            await say(f"Item {line['n']}. {line['spoken_text']}")
        await say("End of the test script. Thank you, goodbye.")


server = AgentServer()


def prewarm(proc: JobProcess) -> None:
    proc.userdata["vad"] = silero.VAD.load(activation_threshold=VAD_THRESHOLD)


server.setup_fnc = prewarm


@server.rtc_session()
async def entrypoint(ctx: JobContext) -> None:
    tts = assemblyai.TTS(model="assemblyai-tts-1", voice=VOICE)
    tts.prewarm()
    # The reader only speaks its script, so it gets no LLM and cannot answer the caller.
    llm = NOT_GIVEN if MODE == "reader" else openai.LLM(
        model="gemma-4-31b", base_url="https://llm-gateway.assemblyai.com/v1",
        api_key=os.environ["ASSEMBLYAI_API_KEY"])
    session = AgentSession(
        stt=assemblyai.STT(model="universal-3-6-pro", mode="balanced", vad_threshold=VAD_THRESHOLD),
        llm=llm,
        tts=tts,
        vad=ctx.proc.userdata["vad"],
        turn_handling=TurnHandlingOptions(turn_detection="stt", endpointing={"min_delay": 0}),
        tts_text_transforms=["filter_emoji", "filter_markdown"],
        use_tts_aligned_transcript=True,
    )
    await session.start(agent=Reader() if MODE == "reader" else Receptionist(), room=ctx.room)


if __name__ == "__main__":
    cli.run_app(server)
