# speakable-v2 vs full-v1

160 cases in both runs. Pass rate with 95% bootstrap interval.

## Overall

| condition | full-v1 | speakable-v2 | fixed | broken |
|---|---|---|---|---|
| api24 | 100.0% (100–100) | 99.4% (98–100) | 0 | 1 |
| lossy8 | 100.0% (100–100) | 99.4% (98–100) | 0 | 1 |
| native8 | 99.4% (98–100) | 100.0% (100–100) | 1 | 0 |

## By category (api24, lossy8, native8 pooled)

| category | full-v1 | speakable-v2 |
|---|---|---|
| uk_mobile | 100.0% (100–100) | 100.0% (100–100) |
| us_phone | 99.6% (99–100) | 99.2% (98–100) |

## Still failing or newly failing

| condition | case | spoken text | heard | was |
|---|---|---|---|---|
| api24 | us_phone-012.aai-nancy | If anything changes, just call us at 543-555-0169. | `543550169` | pass |
| lossy8 | us_phone-012.aai-nancy | If anything changes, just call us at 543-555-0169. | `543550169` | pass |
