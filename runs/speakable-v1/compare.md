# speakable-v1 vs full-v1

880 cases in both runs. Pass rate with 95% bootstrap interval.

## Overall

| condition | full-v1 | speakable-v1 | fixed | broken |
|---|---|---|---|---|
| api24 | 96.6% (95–98) | 98.9% (98–99) | 26 | 6 |
| lossy8 | 96.6% (95–98) | 98.9% (98–99) | 26 | 6 |
| native8 | 97.3% (96–98) | 99.1% (98–100) | 20 | 4 |

## By category (api24, lossy8, native8 pooled)

| category | full-v1 | speakable-v1 |
|---|---|---|
| booking_ref | 99.6% (99–100) | 98.8% (97–100) |
| card_last4 | 98.8% (97–100) | 100.0% (100–100) |
| date | 95.0% (92–98) | 100.0% (100–100) |
| email | 83.3% (78–88) | 97.5% (95–99) |
| price_gbp | 95.0% (92–98) | 95.0% (92–98) |
| price_usd | 100.0% (100–100) | 100.0% (100–100) |
| time | 100.0% (100–100) | 100.0% (100–100) |
| uk_mobile | 100.0% (100–100) | 100.0% (100–100) |
| uk_postcode | 93.8% (90–96) | 100.0% (100–100) |
| us_phone | 99.6% (99–100) | 97.1% (95–99) |
| us_zip | 100.0% (100–100) | 100.0% (100–100) |

## Still failing or newly failing

| condition | case | spoken text | heard | was |
|---|---|---|---|---|
| api24 | booking_ref-019.aai-audrey | I've opened a ticket for you, the reference is A-C-6-P-U-Q, that's C for Charlie, P for Papa. | `I | A | AC6PQ | SC | P` | pass |
| lossy8 | booking_ref-019.aai-audrey | I've opened a ticket for you, the reference is A-C-6-P-U-Q, that's C for Charlie, P for Papa. | `I | A | AC6PQ | SC | P` | pass |
| native8 | booking_ref-019.aai-audrey | I've opened a ticket for you, the reference is A-C-6-P-U-Q, that's C for Charlie, P for Papa. | `I | A | AC6PQ | SC | P` | pass |
| native8 | email-007.aai-buford | The receipt will go to A-I-S-H-A dot P-A-T-E-L at brightdental.com. | `aisaj.patel@brightdental.com` | pass |
| api24 | email-008.aai-buford | I've sent a reset link to A-I-S-H-A dot K-O-W-A-L-S-K-I at acme.com. | `aisaj.kowalski@acme.com` | pass |
| native8 | email-008.aai-buford | I've sent a reset link to A-I-S-H-A dot K-O-W-A-L-S-K-I at acme.com. | `aisaj.kowalski@acme.com` | pass |
| lossy8 | email-009.aai-titus | The receipt will go to J-A-M-E-S-4-1 at brightdental.com. | `jambes41@brightdental.com` | pass |
| api24 | email-010.aai-buford | I've sent a reset link to A-I-S-H-A dot W-O-N-G at northwind.co.uk. | `aisaj.wong@northwind.co.uk` | pass |
| lossy8 | email-010.aai-buford | I've sent a reset link to A-I-S-H-A dot W-O-N-G at northwind.co.uk. | `aisaj.wong@northwind.co.uk` | pass |
| api24 | price_gbp-018.aai-audrey | I can refund £7,900.99 to your original payment method. | `GBP 7999.99` | fail |
| lossy8 | price_gbp-018.aai-audrey | I can refund £7,900.99 to your original payment method. | `GBP 7999.99` | fail |
| native8 | price_gbp-018.aai-audrey | I can refund £7,900.99 to your original payment method. | `GBP 7999.99` | fail |
| api24 | price_gbp-018.aai-buford | I can refund £7,900.99 to your original payment method. | `GBP 7999.99` | fail |
| lossy8 | price_gbp-018.aai-buford | I can refund £7,900.99 to your original payment method. | `GBP 7999.99` | fail |
| native8 | price_gbp-018.aai-buford | I can refund £7,900.99 to your original payment method. | `GBP 7999.99` | fail |
| api24 | price_gbp-018.aai-nancy | I can refund £7,900.99 to your original payment method. | `GBP 7999.99` | fail |
| lossy8 | price_gbp-018.aai-nancy | I can refund £7,900.99 to your original payment method. | `GBP 7999.99` | fail |
| native8 | price_gbp-018.aai-nancy | I can refund £7,900.99 to your original payment method. | `GBP 7999.99` | fail |
| api24 | price_gbp-018.aai-titus | I can refund £7,900.99 to your original payment method. | `GBP 7999.99` | fail |
| lossy8 | price_gbp-018.aai-titus | I can refund £7,900.99 to your original payment method. | `GBP 7999.99` | fail |
| native8 | price_gbp-018.aai-titus | I can refund £7,900.99 to your original payment method. | `GBP 7999.99` | fail |
| api24 | us_phone-015.aai-nancy | If anything changes, just call us at 2-2-5, 5-5-5, 0-1-3-1. | `225550131` | pass |
| lossy8 | us_phone-015.aai-nancy | If anything changes, just call us at 2-2-5, 5-5-5, 0-1-3-1. | `225550131` | pass |
| native8 | us_phone-015.aai-nancy | If anything changes, just call us at 2-2-5, 5-5-5, 0-1-3-1. | `225550131` | pass |
| api24 | us_phone-017.aai-nancy | If anything changes, just call us at 8-5-4, 5-5-5, 0-1-9-6. | `854550196` | pass |
| lossy8 | us_phone-017.aai-nancy | If anything changes, just call us at 8-5-4, 5-5-5, 0-1-9-6. | `854550196` | pass |
| api24 | us_phone-019.aai-audrey | If anything changes, just call us at 7-3-5, 5-5-5, 0-1-0-7. | `735550107` | pass |
| lossy8 | us_phone-019.aai-audrey | If anything changes, just call us at 7-3-5, 5-5-5, 0-1-0-7. | `735550107` | pass |
