# Over the Phone: pilot

44 cases (item × voice), 220 scored transcripts, about 5,670 TTS characters billed.

Pass rate with 95% bootstrap interval. `api24` is the API's default 24 kHz PCM, the way AssemblyAI's own benchmark heard the model; the others are what a caller's phone line delivers.

## Overall

| condition | n | pass rate |
|---|---|---|
| api24 | 44 | 97.7% (93–100) |
| resampled8 | 44 | 97.7% (93–100) |
| lossy8 | 44 | 97.7% (93–100) |
| native8 | 44 | 95.5% (89–100) |
| retake24 | 44 | 97.7% (93–100) |

## Paired with api24

Per case: passes at 24 kHz but fails in the condition, and the reverse. For `resampled8` and `lossy8` the audio is the same take as `api24`, so a difference is caused by the phone channel alone. `native8` and `retake24` are separate syntheses, so their differences include take-to-take variation; `retake24` measures that variation by itself, and its "pass only" column is how often simply synthesizing again fixes a failure.

| condition | same take | paired cases | fail only here | pass only here |
|---|---|---|---|---|
| resampled8 | yes | 44 | 0 | 0 |
| lossy8 | yes | 44 | 0 | 0 |
| native8 | no | 44 | 1 | 0 |
| retake24 | no | 44 | 0 | 0 |

## By category

| category | n | api24 | resampled8 | lossy8 | native8 | retake24 |
|---|---|---|---|---|---|---|
| booking_ref | 4 | 100.0% (100–100) | 100.0% (100–100) | 100.0% (100–100) | 100.0% (100–100) | 100.0% (100–100) |
| card_last4 | 4 | 100.0% (100–100) | 100.0% (100–100) | 100.0% (100–100) | 100.0% (100–100) | 100.0% (100–100) |
| date | 4 | 100.0% (100–100) | 100.0% (100–100) | 100.0% (100–100) | 100.0% (100–100) | 100.0% (100–100) |
| email | 4 | 75.0% (25–100) | 75.0% (25–100) | 75.0% (25–100) | 50.0% (0–100) | 75.0% (25–100) |
| price_gbp | 4 | 100.0% (100–100) | 100.0% (100–100) | 100.0% (100–100) | 100.0% (100–100) | 100.0% (100–100) |
| price_usd | 4 | 100.0% (100–100) | 100.0% (100–100) | 100.0% (100–100) | 100.0% (100–100) | 100.0% (100–100) |
| time | 4 | 100.0% (100–100) | 100.0% (100–100) | 100.0% (100–100) | 100.0% (100–100) | 100.0% (100–100) |
| uk_mobile | 4 | 100.0% (100–100) | 100.0% (100–100) | 100.0% (100–100) | 100.0% (100–100) | 100.0% (100–100) |
| uk_postcode | 4 | 100.0% (100–100) | 100.0% (100–100) | 100.0% (100–100) | 100.0% (100–100) | 100.0% (100–100) |
| us_phone | 4 | 100.0% (100–100) | 100.0% (100–100) | 100.0% (100–100) | 100.0% (100–100) | 100.0% (100–100) |
| us_zip | 4 | 100.0% (100–100) | 100.0% (100–100) | 100.0% (100–100) | 100.0% (100–100) | 100.0% (100–100) |

## By voice accent

| accent | n | api24 | resampled8 | lossy8 | native8 | retake24 |
|---|---|---|---|---|---|---|
| UK | 22 | 100.0% (100–100) | 100.0% (100–100) | 100.0% (100–100) | 95.5% (86–100) | 100.0% (100–100) |
| US | 22 | 95.5% (86–100) | 95.5% (86–100) | 95.5% (86–100) | 95.5% (86–100) | 95.5% (86–100) |

## Failures

| condition | case | said | heard | transcript | TTS request | STT session |
|---|---|---|---|---|---|---|
| api24 | email-001.aai-audrey | `jwong@northwind.co.uk` | `juang@northwind.co.uk` | Can you confirm your email is juang@northwind.co.uk? | `cdf4b298-d628-474d-aa4e-a8b5a0850c09` | `27ba1ccb-1383-4534-977d-935a98c0f003` |
| lossy8 | email-001.aai-audrey | `jwong@northwind.co.uk` | `juang@northwind.co.uk` | Can you confirm your email is juang@northwind.co.uk? | `cdf4b298-d628-474d-aa4e-a8b5a0850c09` | `7e32fe22-48e6-49e5-942b-a6a11bb3721a` |
| native8 | email-001.aai-audrey | `jwong@northwind.co.uk` | `jawong@northwind.co.uk` | Can you confirm your email is jawong@northwind.co.uk? | `d9a4c3a6-96ee-45ec-b7c4-744d77936b1c` | `4612465b-1501-441d-90e5-530870156b8e` |
| resampled8 | email-001.aai-audrey | `jwong@northwind.co.uk` | `juang@northwind.co.uk` | Can you confirm your email is juang@northwind.co.uk? | `cdf4b298-d628-474d-aa4e-a8b5a0850c09` | `df97f643-961b-4797-99ef-563729a1154d` |
| retake24 | email-001.aai-audrey | `jwong@northwind.co.uk` | `juang@northwind.co.uk` | Can you confirm your email is juang@northwind.co.uk? | `004a0dd1-3725-436b-a4f2-a35637d77939` | `ecb7ec06-5979-40be-ba20-00d5ab42476c` |
| native8 | email-001.aai-nancy | `jwong@northwind.co.uk` | `jduong@northwind.co.uk` | Can you confirm your email is jduong@northwind.co.uk? | `30d3e0f9-9aa5-4c07-858b-612312065994` | `93ac96ed-aac4-4ce1-9a0e-ff0a98fa9c9b` |
