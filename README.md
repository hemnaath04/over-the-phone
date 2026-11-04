# Over the Phone

**Does AssemblyAI-TTS-1 still say the hard parts right once the audio goes down a phone line?**

AssemblyAI launched [AssemblyAI-TTS-1](https://www.assemblyai.com/blog/text-to-speech-api) on
Oct 27, 2026 with 93.7% entity accuracy on phone numbers, codes, dates and drug names,
measured over the API at 24 kHz. Voice agents don't talk to callers at 24 kHz. They talk
through 8 kHz G.711 mu-law, the codec of the phone network. In the launch thread, a
developer asked for exactly this:
"I'd love to see that 91.7% re-run over a real phone line"
([@MiclauMarius](https://x.com/AssemblyAI/status/2115470615583056042)).

This repo does that: 880 agent sentences, each built around one hard entity, spoken
by four voices and heard through five channel conditions. That's 4,400 transcripts,
each traceable to a TTS `x-request-id` and an STT `session_id`.

## Results at a glance

| | as an LLM writes it | with Speakable |
|---|---|---|
| Entities that reach the listener intact (2,640 transcripts: 24 kHz, 8 kHz phone, lossy line) | **96.8%** | **99.1%** |
| Failures the phone line itself caused (same take, 24 kHz vs 8 kHz mu-law) | **0 of 880** | — |
| UK dates, postcodes and card numbers | 93.8–98.8% | **100%** |
| Emails | 83.3% | **97.5%** |

- **The phone line is not the problem; the text is.** A UK date is read as an American one,
  even by British voices, and surnames in emails can't be spelled from sound.
- **Universal-3.5 Pro turns 7,900.99 into 7,999.99**, in £, $ and €, however the amount is
  written. That's a transcription bug, confirmed by a second, independent listener.
- **Speakable**, a 140-line rewrite layer, fixes the voice-side errors. One rule from the
  prompting guide (dashing phone digits) made things worse, so we measured it and took it out.
- **[Heard As](#heard-as)** turns all of it into a tool: paste what your agent will say, and see
  what the caller hears and what your call logs will say, before and after the fix.
- A real call over a LiveKit phone number to the agent here worked end to end.

## What was measured

**Entities** (`otp/entities.py`, seeded, 20 sentences per category): US phone numbers,
UK mobiles, UK postcodes, booking references, $ and £ prices, dates in five written
styles, 12- and 24-hour times, emails, card last-4 and ZIP codes. Every number comes
from a range reserved for fiction (US 555-01xx, UK 07700 900xxx).

**Voices:** Audrey and Titus (American), Nancy and Buford (British).

**Channels** (`otp/channel.py`):

| condition | what the listener hears |
|---|---|
| `api24` | the API's default 24 kHz PCM: how AssemblyAI's own benchmark heard the model |
| `resampled8` | that same take, downsampled and G.711 mu-law encoded at 8 kHz |
| `lossy8` | that same take, telephone band (300–3400 Hz), mu-law 8 kHz, 3% of 20 ms packets lost (zero-filled, a worst case) |
| `native8` | a separate take requested as `pcm_mulaw` at 8 kHz, as a telephony integration should |
| `retake24` | a second 24 kHz take of the same text, to measure take-to-take variation |

`api24`, `resampled8` and `lossy8` share one synthesis, so comparing them isolates the
channel. TTS-1 is not deterministic, so the separate takes (`native8`, `retake24`) are
compared at the population level only.

**Listener:** Universal-3.5 Pro over the [Sync API](https://www.assemblyai.com/docs/sync-stt/getting-started/quickstart),
scored per entity by `otp/score.py` (spelled-out numbers, "oh"/"double", spelled
letters, money in words, and so on; 80+ unit tests).

**Second listener:** an AssemblyAI model grading an AssemblyAI model is circular, so every failure, plus a 5%
sample of passes, was re-heard by Whisper `small.en` running locally (`otp/second_listener.py`).
When both listeners hear the same wrong thing, the voice said it wrong. When Whisper hears
it right, the transcriber misheard. On clips AssemblyAI passed, Whisper agreed 88% of the time
(154/175), and all of its misses there were in £ prices and times (formatting style), none in
emails, postcodes or dates.

## Findings

### 1. The phone line is not the problem

With the same take on both sides, converting to 8 kHz mu-law caused **0 failures in
880**. The worst-case lossy channel caused **1**: `MU6MRF` was heard as `MU6MRS`. Both
listeners heard the S, and F/S is the classic confusion of a 3.4 kHz band.
Overall pass rates sit between 96.6% and 97.3% in every condition
([`runs/full-v1/report.md`](runs/full-v1/report.md)).

### 2. A UK date is read as an American one, even by a British voice

`05/08/2026`, meaning 5 August, was spoken as "May 8th" in **20 of 20 takes**,
across all four voices including the British ones. Both listeners agree. Unambiguous
UK dates like `25/10/2026` are read correctly, so the normalizer swaps only when it
must. Where both readings are valid, it assumes month-first. The `language`
parameter takes `english` with no region, and the [prompting guide](https://www.assemblyai.com/docs/tts/prompting-guide)
shows only a US example (`10/24/2026`). A UK agent has no way to say which it means.
Example: TTS `7e9d8c67-167b-40d7-9271-b58fa9cf073f`, STT `b98bd449-ffaa-48d6-953a-73bf43370c6f`.

### 3. Universal-3.5 Pro turns 7,900.99 into 7,999.99 (an STT bug, not a TTS one)

`£7,900.99` was transcribed as `£7,999.99` in 20 of 20 takes. Whisper heard
"7,900 pounds and 99 pence" every time, so the voice said it right. The probe in
[`probes/money_900.py`](probes/money_900.py) narrows it down
([`runs/probe-money-900.jsonl`](runs/probe-money-900.jsonl)):

| said | Universal-3.5 Pro | Whisper |
|---|---|---|
| £7,900.99 | **£7,999.99** | £7,900.99 |
| £6,900.99 | **£6,999.99** | £6,900.99 |
| $7,900.99 | **$7,999.99** | $7,900.99 |
| €7,900.99 | **€7,999.99** | 7,900 euros and 99 cents |
| £7,900.09 | **£7,909.09** | £7,900.09 |
| £7,800.99 | £7,800.99 | £7,800 and 99 pence |
| £7,090.99 | £7,090.99 | £7,090.99 |
| £900.99 | £900.99 | £900.99 |

Any thousands amount with 900 in the hundreds folds its cents into the number. That
matters wherever these transcripts feed an LLM: a refund, an invoice or a call summary.
It doesn't depend on how the agent writes the amount: "£7,900.99", "7,900 pounds and 99 pence"
and "seven thousand nine hundred pounds and ninety-nine pence" all come back as £7,999.99. So it
can only be fixed in the transcriber, not worked around in the text.
STT sessions: `b80078e3…`, `39071ce0…`, `2975e450…` (full IDs in the jsonl).

### 4. Emails are the weakest category, and the voice isn't to blame

Emails passed 81–89%. Surnames are spoken clearly but can't be spelled from sound:
Okafor came back as okafur, okafour and ocafor; Patel as paytel; Wong as wang; and
`jwong` as juwang or jdwong. Both listeners fail the same way, as a human writing it
down would.

### 5. Letters that rhyme

`SE14` was heard as `SC14` by both listeners, and the card `8091` as `1891` with the
British voices only.

## The fix: Speakable

[`otp/speakable.py`](otp/speakable.py) applies AssemblyAI's own
[prompting guide](https://www.assemblyai.com/docs/tts/prompting-guide) as code, aimed at
what full-v1 found:

| rewrite | example |
|---|---|
| numeric dates in words, for the business's locale | `05/08/2026` → "the 5th of August" (UK) |
| email local parts spelled out | `noah.okafor@…` → "N-O-A-H dot O-K-A-F-O-R at …" |
| references and postcodes spelled, with a phonetic note for letters a phone band blurs | `MU6-MRF` → "M-U-6-M-R-F, that's M for Mike, F for Foxtrot" |
| card and ZIP digits one at a time | `8091` → "8-0-9-1" |
| 24-hour times in 12-hour form (US) | `16:15` → "4:15 PM" |

It runs on text alone, so it fits between any LLM and any TTS session. In the LiveKit agent it
runs per sentence as the reply streams.

**Result** (`runs/speakable-v1` + `runs/speakable-v2` vs `runs/full-v1`, the same 880 cases;
[`compare.md`](runs/speakable-v1/compare.md)):

| condition | raw | Speakable | fixed | broken |
|---|---|---|---|---|
| 24 kHz | 96.6% | 99.1% | 26 | 4 |
| 8 kHz phone, lossy | 96.6% | 99.1% | 26 | 4 |
| 8 kHz phone, native | 97.3% | 99.2% | 20 | 3 |

Of the 23 transcripts still failing, the second listener puts 18 on the transcriber (12 of them
are the £7,900.99 bug) and 5 on the voice. "A-I-S-H-A" in the Buford voice is heard as "aisaj"
by both listeners, and one take drops a 5 from "555".

**A rule that hurt.** The prompting guide says dashes make digits read one by one. Applied to
phone numbers ("2-2-5, 5-5-5, 0-1-3-1"), TTS-1 dropped a digit wherever four 5s ran together
(area code ending in 5, then 555), in all three conditions, and both listeners agree
(`speakable-v1`, us_phone-015/017/019). The plain written number scored 99.6%, because the server's
normalizer already reads it right. Speakable now leaves phone numbers alone (`speakable-v2`).

## Heard As

[`heardas/`](heardas/) is the research as a tool. Paste a reply your agent is about to speak, and it:

1. finds every phone number, code, postcode, date, time, price and email (`otp/detect.py`);
2. speaks it with AssemblyAI-TTS-1 and sends it down a simulated 8 kHz phone line;
3. has both listeners write down what came through;
4. marks each entity **clear**, **caller mishears** (both listeners wrong), **logs wrong** (the
   caller hears it, the transcript doesn't), or **probably fine** (only Whisper missed it);
5. does it all again for the Speakable rewrite, and plays both versions the way a caller hears them.

```bash
uv run python -m heardas.server     # http://127.0.0.1:8765
```

A check costs two TTS calls and four transcriptions, and takes about 5 seconds.

## A phone agent with the fix built in

[`agent/phone_agent.py`](agent/phone_agent.py) is a LiveKit agent on the all-AssemblyAI stack
(Universal-3.6 Pro STT, LLM Gateway, AssemblyAI-TTS-1), following AssemblyAI's
[LiveKit guide](https://www.assemblyai.com/docs/tts/livekit). It overrides `tts_node`
so every sentence passes through Speakable as it streams, without waiting for the whole reply.

- `AGENT_MODE=receptionist`: a dental front desk that confirms an appointment and reads back
  a code, a phone number and an email.
- `AGENT_MODE=reader`: reads [`agent/reader_script.json`](agent/reader_script.json), 12 hard
  entities, each raw and rewritten, with no LLM and no interruptions. Score a recording with
  `python -m otp.score_call recording.m4a --name call-1`.

Over LiveKit's WebRTC path ([`agent/room_listener.py`](agent/room_listener.py), `runs/webrtc-1`)
the reader scored 11/12 raw and 12/12 with Speakable; the one raw miss is the UK date. A real call to a
LiveKit phone number reached the agent, which answered in about 3 s and read the script over the
phone network.

## Reproduce

```bash
uv sync                                   # httpx + pytest, ~10 MB
echo "ASSEMBLYAI_API_KEY=..." > .env
uv run pytest -q                          # 95 tests
uv run python -m otp.run --name mine --per-category 2 --voices aai-audrey,aai-nancy
uv run python -m otp.report runs/mine
uv run python -m otp.second_listener runs/mine   # needs whisper.cpp + ggml-small.en.bin (WHISPER_MODEL=...)
```

The full run cost about 113K TTS characters (about $1.70 at $15 per 1M) plus about
6 hours of Sync STT audio.

## Limits

- The listener is a speech-to-text model, not a person. The second listener and the paired
  design reduce the circularity but don't remove it.
- `lossy8` zero-fills lost packets; real networks conceal them, so real calls should do better.
- One real call has been made, but not yet recorded and scored, so the carrier path is checked
  by the 8 kHz simulation only. Mobile networks may carry wideband audio (AMR-WB), so a real
  call may sound better than the simulation.
- Four voices of 4,000+, English only, 11 entity types.
