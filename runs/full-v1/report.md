# Over the Phone: full-v1

880 cases (item × voice), 4400 scored transcripts, about 113,376 TTS characters billed.

Pass rate with 95% bootstrap interval. `api24` is the API's default 24 kHz PCM, the way AssemblyAI's own benchmark heard the model; the others are what a caller's phone line delivers.

## Overall

| condition | n | pass rate |
|---|---|---|
| api24 | 880 | 96.6% (95–98) |
| resampled8 | 880 | 96.8% (96–98) |
| lossy8 | 880 | 96.6% (95–98) |
| native8 | 880 | 97.3% (96–98) |
| retake24 | 880 | 96.7% (95–98) |

## Paired with api24

Per case: passes at 24 kHz but fails in the condition, and the reverse. For `resampled8` and `lossy8` the audio is the same take as `api24`, so a difference is caused by the phone channel alone. `native8` and `retake24` are separate syntheses, so their differences include take-to-take variation; `retake24` measures that variation by itself, and its "pass only" column is how often simply synthesizing again fixes a failure.

| condition | same take | paired cases | fail only here | pass only here |
|---|---|---|---|---|
| resampled8 | yes | 880 | 0 | 2 |
| lossy8 | yes | 880 | 1 | 1 |
| native8 | no | 880 | 2 | 8 |
| retake24 | no | 880 | 8 | 9 |

## By category

| category | n | api24 | resampled8 | lossy8 | native8 | retake24 |
|---|---|---|---|---|---|---|
| booking_ref | 80 | 100.0% (100–100) | 100.0% (100–100) | 98.8% (96–100) | 100.0% (100–100) | 100.0% (100–100) |
| card_last4 | 80 | 98.8% (96–100) | 98.8% (96–100) | 98.8% (96–100) | 98.8% (96–100) | 98.8% (96–100) |
| date | 80 | 95.0% (90–99) | 95.0% (90–99) | 95.0% (90–99) | 95.0% (90–99) | 95.0% (90–99) |
| email | 80 | 81.2% (72–90) | 82.5% (74–90) | 81.2% (72–90) | 87.5% (80–94) | 88.8% (82–95) |
| price_gbp | 80 | 95.0% (90–99) | 95.0% (90–99) | 95.0% (90–99) | 95.0% (90–99) | 95.0% (90–99) |
| price_usd | 80 | 100.0% (100–100) | 100.0% (100–100) | 100.0% (100–100) | 100.0% (100–100) | 100.0% (100–100) |
| time | 80 | 100.0% (100–100) | 100.0% (100–100) | 100.0% (100–100) | 100.0% (100–100) | 100.0% (100–100) |
| uk_mobile | 80 | 100.0% (100–100) | 100.0% (100–100) | 100.0% (100–100) | 100.0% (100–100) | 100.0% (100–100) |
| uk_postcode | 80 | 92.5% (86–98) | 93.8% (88–99) | 93.8% (88–99) | 95.0% (90–99) | 91.2% (85–98) |
| us_phone | 80 | 100.0% (100–100) | 100.0% (100–100) | 100.0% (100–100) | 98.8% (96–100) | 98.8% (96–100) |
| us_zip | 80 | 100.0% (100–100) | 100.0% (100–100) | 100.0% (100–100) | 100.0% (100–100) | 96.2% (91–100) |

## By voice accent

| accent | n | api24 | resampled8 | lossy8 | native8 | retake24 |
|---|---|---|---|---|---|---|
| UK | 440 | 96.8% (95–98) | 96.8% (95–98) | 96.8% (95–98) | 97.0% (95–98) | 96.6% (95–98) |
| US | 440 | 96.4% (95–98) | 96.8% (95–98) | 96.4% (95–98) | 97.5% (96–99) | 96.8% (95–98) |

## Failures

| condition | case | said | heard | transcript | TTS request | STT session |
|---|---|---|---|---|---|---|
| lossy8 | booking_ref-015.aai-titus | `MU6MRF` | `I | A | MU6MRS` | I've opened a ticket for you, the reference is MU6MRS. | `3e61df5d-4423-4ff2-b80a-5c8063f6feff` | `552d33c5-06aa-432e-b469-b0269750c304` |
| retake24 | card_last4-004.aai-buford | `8091` | `1891` | The refund goes back to the card ending 1891. | `f6cc6de0-525e-43b5-b0d5-07aa777b46cd` | `43d427ef-62fa-4e2b-b3e3-5d5003b4e597` |
| api24 | card_last4-004.aai-nancy | `8091` | `1891` | The refund goes back to the card ending 1891. | `542a02a7-3c8f-45ac-a123-0121b7599aa8` | `3d49f06c-d791-444c-9312-5153b19c1de5` |
| lossy8 | card_last4-004.aai-nancy | `8091` | `1891` | The refund goes back to the card ending 1891. | `542a02a7-3c8f-45ac-a123-0121b7599aa8` | `40a70273-821e-4ea5-b288-202d8d810a91` |
| native8 | card_last4-004.aai-nancy | `8091` | `1891` | The refund goes back to the card ending 1891. | `f1b249e0-8096-44c2-858c-59e7070023d3` | `c98990b5-ce75-4a04-8a80-6f6253842d7c` |
| resampled8 | card_last4-004.aai-nancy | `8091` | `1891` | The refund goes back to the card ending 1891. | `542a02a7-3c8f-45ac-a123-0121b7599aa8` | `108f99ff-98f3-486f-82f5-8ae6ca87c5db` |
| api24 | date-004.aai-audrey | `05/08/2026` | `5/8` | Your next appointment is on May 8th, 2026. | `80c49bad-c4ea-43be-beb7-3d2864167785` | `47f1bc5d-20a8-404e-a1f6-9db613d22e9f` |
| lossy8 | date-004.aai-audrey | `05/08/2026` | `5/8` | Your next appointment is on May 8th, 2026. | `80c49bad-c4ea-43be-beb7-3d2864167785` | `3358e7ce-ae79-497d-b09d-2cf9b130fc0b` |
| native8 | date-004.aai-audrey | `05/08/2026` | `5/8` | Your next appointment is on May 8th, 2026. | `334bdfdb-253d-4a1f-919d-e2809ebead5c` | `a9f27541-9593-493c-bc0a-1a170490324a` |
| resampled8 | date-004.aai-audrey | `05/08/2026` | `5/8` | Your next appointment is on May 8th, 2026. | `80c49bad-c4ea-43be-beb7-3d2864167785` | `edab10a8-92aa-4bdc-b2dd-774716cc7406` |
| retake24 | date-004.aai-audrey | `05/08/2026` | `5/8` | Your next appointment is on May 8th, 2026. | `9a4cc7ff-f5e1-444b-8d67-a3f39c5145ab` | `cb58d762-d5e3-40d9-9791-91e58ce353ca` |
| api24 | date-004.aai-buford | `05/08/2026` | `5/8` | Your next appointment is on May 8th, 2026. | `cb21ebaf-2930-413b-945f-e42b6536205a` | `14da1270-a91e-40a8-9a3b-7baa435262c3` |
| lossy8 | date-004.aai-buford | `05/08/2026` | `5/8` | Your next appointment is on May 8th, 2026. | `cb21ebaf-2930-413b-945f-e42b6536205a` | `3428bfc2-89af-4722-b234-e9caaed448e1` |
| native8 | date-004.aai-buford | `05/08/2026` | `5/8` | Your next appointment is on May 8th, 2026. | `dbeac8d1-c4f7-4510-86c6-7b3eef2c4bda` | `01b1288e-a85b-48ec-b517-0eeae440ef68` |
| resampled8 | date-004.aai-buford | `05/08/2026` | `5/8` | Your next appointment is on May 8th, 2026. | `cb21ebaf-2930-413b-945f-e42b6536205a` | `508b1cce-818f-4bf5-a955-6d5fe94e3348` |
| retake24 | date-004.aai-buford | `05/08/2026` | `5/8` | Your next appointment is on May 8th, 2026. | `b9310f8a-931b-4aa9-9575-a6dced79ed94` | `a28e5710-1e90-4ac6-bd06-a6fb6b49641d` |
| api24 | date-004.aai-nancy | `05/08/2026` | `5/8` | Your next appointment is on May 8th, 2026. | `7e9d8c67-167b-40d7-9271-b58fa9cf073f` | `b98bd449-ffaa-48d6-953a-73bf43370c6f` |
| lossy8 | date-004.aai-nancy | `05/08/2026` | `5/8` | Your next appointment is on May 8th, 2026. | `7e9d8c67-167b-40d7-9271-b58fa9cf073f` | `d4a357c1-e150-4f90-b048-c0314b39bd5e` |
| native8 | date-004.aai-nancy | `05/08/2026` | `5/8` | Your next appointment is on May 8th, 2026. | `938254d3-a4ae-4955-9ab2-1dd6c8bd0a3f` | `a6513fec-9098-4a43-a737-940363b0a103` |
| resampled8 | date-004.aai-nancy | `05/08/2026` | `5/8` | Your next appointment is on May 8th, 2026. | `7e9d8c67-167b-40d7-9271-b58fa9cf073f` | `b7f3e8c4-87f0-4848-b2e2-6494ea5d49c4` |
| retake24 | date-004.aai-nancy | `05/08/2026` | `5/8` | Your next appointment is on May 8th, 2026. | `35556786-a744-48ec-884d-5f559c23885d` | `57da2374-6934-41b9-8785-6cd38bce4485` |
| api24 | date-004.aai-titus | `05/08/2026` | `5/8` | Your next appointment is on May 8th, 2026. | `adfc4598-5b4e-42fa-9d9a-d3ba5fc5ecc4` | `85323b77-2600-4551-9003-606405a82af1` |
| lossy8 | date-004.aai-titus | `05/08/2026` | `5/8` | Your next appointment is on May 8th, 2026. | `adfc4598-5b4e-42fa-9d9a-d3ba5fc5ecc4` | `bd7601e2-7a12-4e90-a061-5a545c4ebb04` |
| native8 | date-004.aai-titus | `05/08/2026` | `5/8` | Your next appointment is on May 8th, 2026. | `d124802b-cb2f-4e68-94b7-22b47ae0d136` | `765e2716-054e-4dc5-ba8e-fc7aa95bd386` |
| resampled8 | date-004.aai-titus | `05/08/2026` | `5/8` | Your next appointment is on May 8th, 2026. | `adfc4598-5b4e-42fa-9d9a-d3ba5fc5ecc4` | `1a1dc546-5881-4b71-b2b1-c762e1499c11` |
| retake24 | date-004.aai-titus | `05/08/2026` | `5/8` | Your next appointment is on May 8th, 2026. | `5d679010-7155-48c0-895a-424227665d8a` | `7189a7c4-5c4c-4de7-b610-533cc56e5bcf` |
| api24 | email-001.aai-audrey | `jwong@northwind.co.uk` | `juwang@northwind.co.uk` | Can you confirm your email is juwang@northwind.co.uk? | `942e283a-1249-4333-a97b-0a39b3e1e56a` | `48f4efad-f3c3-4de1-a740-fcd34263a131` |
| lossy8 | email-001.aai-audrey | `jwong@northwind.co.uk` | `juwang@northwind.co.uk` | Can you confirm your email is juwang@northwind.co.uk? | `942e283a-1249-4333-a97b-0a39b3e1e56a` | `22eca54c-adcd-4e32-b767-881c6d60bb5f` |
| resampled8 | email-001.aai-audrey | `jwong@northwind.co.uk` | `juwang@northwind.co.uk` | Can you confirm your email is juwang@northwind.co.uk? | `942e283a-1249-4333-a97b-0a39b3e1e56a` | `b58081ef-7f48-4247-8b2c-4980b92e9634` |
| api24 | email-001.aai-buford | `jwong@northwind.co.uk` | `juang@northwind.co.uk` | Can you confirm your email is juang@northwind.co.uk? | `60a613e2-b371-4a3f-84a5-df06e8db16de` | `49c3bfc6-c57c-48e4-8c34-55696faadb7b` |
| lossy8 | email-001.aai-buford | `jwong@northwind.co.uk` | `juang@northwind.co.uk` | Can you confirm your email is juang@northwind.co.uk? | `60a613e2-b371-4a3f-84a5-df06e8db16de` | `deb2f293-6565-4d82-914b-8c01e309cd11` |
| native8 | email-001.aai-buford | `jwong@northwind.co.uk` | `juang@northwind.co.uk` | Can you confirm your email is juang@northwind.co.uk? | `6a8c62a1-6cb8-449f-b02b-19592b15ca06` | `686b4673-d1a9-4505-99b9-11a4651a9c13` |
| resampled8 | email-001.aai-buford | `jwong@northwind.co.uk` | `juang@northwind.co.uk` | Can you confirm your email is juang@northwind.co.uk? | `60a613e2-b371-4a3f-84a5-df06e8db16de` | `d20cc33f-ca37-4332-8820-7962ca5cf177` |
| api24 | email-001.aai-nancy | `jwong@northwind.co.uk` | `juang@northwind.co.uk` | Can you confirm your email is juang@northwind.co.uk? | `cb89854e-8747-4a7e-bfa3-c4c8be9c7520` | `2eab0696-1a17-4c9e-a4a3-158c4d660478` |
| lossy8 | email-001.aai-nancy | `jwong@northwind.co.uk` | `juang@northwind.co.uk` | Can you confirm your email is juang@northwind.co.uk? | `cb89854e-8747-4a7e-bfa3-c4c8be9c7520` | `04ba6d66-3396-4cfd-9053-77a47da487e9` |
| native8 | email-001.aai-nancy | `jwong@northwind.co.uk` | `jdwang@northwind.co.uk` | Can you confirm your email is jdwang@northwind.co.uk? | `0846518c-4e5e-4fb0-8a34-3f8159f42b45` | `e28a2e8b-ce41-4510-8ca9-f9deda913016` |
| resampled8 | email-001.aai-nancy | `jwong@northwind.co.uk` | `juang@northwind.co.uk` | Can you confirm your email is juang@northwind.co.uk? | `cb89854e-8747-4a7e-bfa3-c4c8be9c7520` | `97e8eebf-92e0-411e-8500-f14ed73b97f7` |
| retake24 | email-001.aai-nancy | `jwong@northwind.co.uk` | `jduong@northwind.co.uk` | Can you confirm your email is jduong@northwind.co.uk? | `c6a5c3fa-d156-4000-8424-9ad7ed98fdb3` | `0861632a-2829-4e71-9239-9452bc480166` |
| api24 | email-001.aai-titus | `jwong@northwind.co.uk` | `jdwang@northwind.co.uk` | Can you confirm your email is jdwang@northwind.co.uk? | `dc2d8b3d-2432-4036-b0aa-03886369e138` | `7d468da5-c98d-42c5-996e-a021c9976455` |
| lossy8 | email-001.aai-titus | `jwong@northwind.co.uk` | `jdwong@northwind.co.uk` | Can you confirm your email is jdwong@northwind.co.uk? | `dc2d8b3d-2432-4036-b0aa-03886369e138` | `14f6ec93-9ac7-4190-8317-6545d8b43725` |
| resampled8 | email-001.aai-titus | `jwong@northwind.co.uk` | `jdwang@northwind.co.uk` | Can you confirm your email is jdwang@northwind.co.uk? | `dc2d8b3d-2432-4036-b0aa-03886369e138` | `38110403-c878-45a9-a745-a558775e9bfa` |
| api24 | email-003.aai-nancy | `tpatel@acme.com` | `tpaytel@acme.com` | I've sent a reset link to tpaytel@acme.com. | `5a8c2ad2-c719-4b7b-a65e-c459ce1a1c87` | `e81414b8-b77c-483b-9af4-751f47c2e8ea` |
| lossy8 | email-003.aai-nancy | `tpatel@acme.com` | `tpaytel@acme.com` | I've sent a reset link to tpaytel@acme.com. | `5a8c2ad2-c719-4b7b-a65e-c459ce1a1c87` | `3f8ba34c-b3ef-4e55-a85a-36727796ecf3` |
| resampled8 | email-003.aai-nancy | `tpatel@acme.com` | `tpaytel@acme.com` | I've sent a reset link to tpaytel@acme.com. | `5a8c2ad2-c719-4b7b-a65e-c459ce1a1c87` | `c2020c2e-a8f0-4298-b45a-a5503f04b1b9` |
| api24 | email-007.aai-audrey | `aisha.patel@brightdental.com` | `aisha.paytel@brightdental.com` | The receipt will go to aisha.paytel@brightdental.com. | `a4d9739c-2a69-4766-91dc-73633a0da2e8` | `80d5407c-d0e5-482d-b296-543933eceeb6` |
| lossy8 | email-007.aai-audrey | `aisha.patel@brightdental.com` | `aisha.paytel@brightdental.com` | The receipt will go to aisha.paytel@brightdental.com. | `a4d9739c-2a69-4766-91dc-73633a0da2e8` | `cc5d2533-c899-4955-aff5-31f643e9b6f0` |
| resampled8 | email-007.aai-audrey | `aisha.patel@brightdental.com` | `aisha.paytel@brightdental.com` | The receipt will go to aisha.paytel@brightdental.com. | `a4d9739c-2a69-4766-91dc-73633a0da2e8` | `349a4a07-1123-455d-91cf-dd17c205580d` |
| api24 | email-010.aai-audrey | `aisha.wong@northwind.co.uk` | `aisha.wang@northwind.co.uk` | I've sent a reset link to aisha.wang@northwind.co.uk. | `1dc318f0-2e39-4722-86cf-93aeed48689f` | `437ab3ce-bc68-4c81-9fd0-ae5b430f6ef6` |
| lossy8 | email-010.aai-audrey | `aisha.wong@northwind.co.uk` | `aisha.wang@northwind.co.uk` | I've sent a reset link to aisha.wang@northwind.co.uk. | `1dc318f0-2e39-4722-86cf-93aeed48689f` | `46f1c710-6310-4672-849b-6cb013c18052` |
| api24 | email-016.aai-audrey | `noah.okafor@brightdental.com` | `noah.okafur@brightdental.com` | The receipt will go to noah.okafur@brightdental.com. | `7f232372-724c-4014-bac4-1607b7e99fe3` | `f18a7ccb-f56b-479d-bf81-5d37e1b427ac` |
| lossy8 | email-016.aai-audrey | `noah.okafor@brightdental.com` | `noah.okafur@brightdental.com` | The receipt will go to noah.okafur@brightdental.com. | `7f232372-724c-4014-bac4-1607b7e99fe3` | `8ef242de-ce93-4d6b-976f-b81f3bd850dc` |
| native8 | email-016.aai-audrey | `noah.okafor@brightdental.com` | `noah.okafur@brightdental.com` | The receipt will go to noah.okafur@brightdental.com. | `07da3ff6-9823-4892-b803-199fb8092479` | `32ab6f95-ffa5-41bc-8cc3-4792302f7c5d` |
| resampled8 | email-016.aai-audrey | `noah.okafor@brightdental.com` | `noah.okafur@brightdental.com` | The receipt will go to noah.okafur@brightdental.com. | `7f232372-724c-4014-bac4-1607b7e99fe3` | `3aca71a7-2afc-449a-bde6-81f13daa029e` |
| retake24 | email-016.aai-audrey | `noah.okafor@brightdental.com` | `noah.okafur@brightdental.com` | The receipt will go to noah.okafur@brightdental.com. | `a3865327-2e95-4057-bde3-f92a3196c00a` | `f07dadd1-d49f-4b71-aa17-789e49a9b0f1` |
| api24 | email-016.aai-buford | `noah.okafor@brightdental.com` | `noah.okafur@brightdental.com` | The receipt will go to noah.okafur@brightdental.com. | `ea3d5f1d-6a5b-4b5b-93f8-a9be3dac0e51` | `9564376a-6c2a-480d-9db6-d8bac6b577d0` |
| lossy8 | email-016.aai-buford | `noah.okafor@brightdental.com` | `noah.okafur@brightdental.com` | The receipt will go to noah.okafur@brightdental.com. | `ea3d5f1d-6a5b-4b5b-93f8-a9be3dac0e51` | `eb38a230-9d85-41b5-a032-eae60aa4a9a8` |
| native8 | email-016.aai-buford | `noah.okafor@brightdental.com` | `noah.okafur@brightdental.com` | The receipt will go to noah.okafur@brightdental.com. | `58e7bcc5-e96d-4335-b049-74cc8e810bfb` | `fa4232a1-8f88-4cc7-a431-a293496dc144` |
| resampled8 | email-016.aai-buford | `noah.okafor@brightdental.com` | `noah.okafur@brightdental.com` | The receipt will go to noah.okafur@brightdental.com. | `ea3d5f1d-6a5b-4b5b-93f8-a9be3dac0e51` | `4a1b11f6-f3b8-4770-b759-b5431d388121` |
| retake24 | email-016.aai-buford | `noah.okafor@brightdental.com` | `noah.okafur@brightdental.com` | The receipt will go to noah.okafur@brightdental.com. | `97af6cc5-c02d-4af9-b2ff-9abe05ec2d5d` | `8b230db4-2967-41bc-9bbc-b97a18a43afb` |
| api24 | email-016.aai-nancy | `noah.okafor@brightdental.com` | `noah.okafur@brightdental.com` | The receipt will go to noah.okafur@brightdental.com. | `25dd71b2-2e21-409a-8d7f-bd8f75249bb8` | `939ccbbb-9e46-4e2f-a988-8949d8ab891e` |
| lossy8 | email-016.aai-nancy | `noah.okafor@brightdental.com` | `noah.okafur@brightdental.com` | The receipt will go to noah.okafur@brightdental.com. | `25dd71b2-2e21-409a-8d7f-bd8f75249bb8` | `0b7ac63f-fb12-49c3-ac21-726dfded34f8` |
| native8 | email-016.aai-nancy | `noah.okafor@brightdental.com` | `noah.okafur@brightdental.com` | The receipt will go to noah.okafur@brightdental.com. | `c44a9c6b-c421-4510-b7a5-90f1429fb037` | `d0d5da62-dfc7-4a0d-a457-b356c887aa27` |
| resampled8 | email-016.aai-nancy | `noah.okafor@brightdental.com` | `noah.okafur@brightdental.com` | The receipt will go to noah.okafur@brightdental.com. | `25dd71b2-2e21-409a-8d7f-bd8f75249bb8` | `03fb2500-ce01-40af-b73d-51542f6dee8f` |
| retake24 | email-016.aai-nancy | `noah.okafor@brightdental.com` | `noah.okafur@brightdental.com` | The receipt will go to noah.okafur@brightdental.com. | `31524071-734e-4139-bf6e-e15b4aae9091` | `b3e70b17-f515-4afa-97fc-32f90b34eb3f` |
| api24 | email-016.aai-titus | `noah.okafor@brightdental.com` | `noah.okafur@brightdental.com` | The receipt will go to noah.okafur@brightdental.com. | `cafae73a-4a7d-4581-aed1-d1f771031a46` | `ad47de87-2cfe-46b8-b3bb-eefe8a73d565` |
| lossy8 | email-016.aai-titus | `noah.okafor@brightdental.com` | `noah.okafur@brightdental.com` | The receipt will go to noah.okafur@brightdental.com. | `cafae73a-4a7d-4581-aed1-d1f771031a46` | `8b0ae7af-1299-4c7c-9e15-146c64ce9f01` |
| native8 | email-016.aai-titus | `noah.okafor@brightdental.com` | `noah.okafur@brightdental.com` | The receipt will go to noah.okafur@brightdental.com. | `1f02778f-be3b-4d40-951b-4c9738d45b81` | `f71a5cf1-16dd-46e5-8d13-c01f258dd00d` |
| resampled8 | email-016.aai-titus | `noah.okafor@brightdental.com` | `noah.okafur@brightdental.com` | The receipt will go to noah.okafur@brightdental.com. | `cafae73a-4a7d-4581-aed1-d1f771031a46` | `1731da4b-b4ac-4a21-b0ff-c4b1297d8fdb` |
| retake24 | email-016.aai-titus | `noah.okafor@brightdental.com` | `noah.okafur@brightdental.com` | The receipt will go to noah.okafur@brightdental.com. | `524ff8f6-e7ee-4ae5-bad3-d370b6de69c0` | `4dca566d-ced0-44ef-8b97-015cd83b40be` |
| api24 | email-018.aai-audrey | `maria.okafor@northwind.co.uk` | `maria.okafur@northwind.co.uk` | I've sent a reset link to maria.okafur@northwind.co.uk. | `79279ff1-8b45-415a-8bc9-5802ec39fc2a` | `56238349-d38d-4bac-bf16-743befca4814` |
| lossy8 | email-018.aai-audrey | `maria.okafor@northwind.co.uk` | `maria.okafur@northwind.co.uk` | I've sent a reset link to maria.okafur@northwind.co.uk. | `79279ff1-8b45-415a-8bc9-5802ec39fc2a` | `8bffe9b8-6bb5-45e6-8e18-cea4c8362df9` |
| native8 | email-018.aai-audrey | `maria.okafor@northwind.co.uk` | `maria.okafur@northwind.co.uk` | I've sent a reset link to maria.okafur@northwind.co.uk. | `d3de8d7f-20ee-489c-b407-24f5973cb17f` | `f1f60dcc-e699-45e4-8db6-8aa5e96f84db` |
| resampled8 | email-018.aai-audrey | `maria.okafor@northwind.co.uk` | `maria.okafur@northwind.co.uk` | I've sent a reset link to maria.okafur@northwind.co.uk. | `79279ff1-8b45-415a-8bc9-5802ec39fc2a` | `8c452ae9-4527-4f21-862b-81706cbe830f` |
| retake24 | email-018.aai-audrey | `maria.okafor@northwind.co.uk` | `maria.okafur@northwind.co.uk` | I've sent a reset link to maria.okafur@northwind.co.uk. | `771e51b4-2a80-4001-a3ca-b7edefae47b3` | `9f6872bb-f342-4f51-b024-c93e1f1a2143` |
| api24 | email-018.aai-buford | `maria.okafor@northwind.co.uk` | `maria.okafur@northwind.co.uk` | I've sent a reset link to maria.okafur@northwind.co.uk. | `b3292b91-c0d7-46a3-87d4-66bcba9846d8` | `44391d98-a5d1-401e-a7de-1815c6841c01` |
| lossy8 | email-018.aai-buford | `maria.okafor@northwind.co.uk` | `maria.okafur@northwind.co.uk` | I've sent a reset link to maria.okafur@northwind.co.uk. | `b3292b91-c0d7-46a3-87d4-66bcba9846d8` | `9bd5fc17-daa9-45b9-a8a1-6f6fc9e0ec37` |
| native8 | email-018.aai-buford | `maria.okafor@northwind.co.uk` | `maria.okafour@northwind.co.uk` | I've sent a reset link to maria.okafour@northwind.co.uk. | `4d27d0ee-f680-42f2-8f00-9b20e4c980a8` | `2b82b0ce-66d1-4e3c-99dc-b7cb50f3db6b` |
| resampled8 | email-018.aai-buford | `maria.okafor@northwind.co.uk` | `maria.okafur@northwind.co.uk` | I've sent a reset link to maria.okafur@northwind.co.uk. | `b3292b91-c0d7-46a3-87d4-66bcba9846d8` | `c78d5021-75b5-488c-9e1e-500d35ec7130` |
| retake24 | email-018.aai-buford | `maria.okafor@northwind.co.uk` | `maria.okafur@northwind.co.uk` | I've sent a reset link to maria.okafur@northwind.co.uk. | `2754103e-7091-4c2f-a97a-7c7057f6e01d` | `3179bc7b-cd4f-4e66-89a0-b6e0af729d78` |
| api24 | email-018.aai-nancy | `maria.okafor@northwind.co.uk` | `maria.okafur@northwind.co.uk` | I've sent a reset link to maria.okafur@northwind.co.uk. | `28236054-20c2-4e59-8adc-d9163c6acffd` | `04710b24-f99e-41bb-aa0e-63cc669442a5` |
| lossy8 | email-018.aai-nancy | `maria.okafor@northwind.co.uk` | `maria.okafour@northwind.co.uk` | I've sent a reset link to maria.okafour@northwind.co.uk. | `28236054-20c2-4e59-8adc-d9163c6acffd` | `9a9adccf-144c-4341-bc38-b132df10ec0c` |
| native8 | email-018.aai-nancy | `maria.okafor@northwind.co.uk` | `mariah.okafour@northwind.co.uk` | I've sent a reset link to mariah.okafour@northwind.co.uk. | `e732641e-defa-4507-8ff3-cee6f61a696c` | `4d688c7d-d86a-44b0-990f-cc6d8d65e1db` |
| resampled8 | email-018.aai-nancy | `maria.okafor@northwind.co.uk` | `maria.okafour@northwind.co.uk` | I've sent a reset link to maria.okafour@northwind.co.uk. | `28236054-20c2-4e59-8adc-d9163c6acffd` | `c099bd74-a5d6-49ac-92e5-8ebfb50b30af` |
| retake24 | email-018.aai-nancy | `maria.okafor@northwind.co.uk` | `maria.okafour@northwind.co.uk` | I've sent a reset link to maria.okafour@northwind.co.uk. | `f083ed23-44de-445a-8e4c-3b2aa6ad541c` | `4c75d783-79e6-48fd-85f7-fb2147a34797` |
| api24 | email-018.aai-titus | `maria.okafor@northwind.co.uk` | `maria.okafur@northwind.co.uk` | I've sent a reset link to maria.okafur@northwind.co.uk. | `56abe64d-a527-45ca-b8c2-f3ba5396fa63` | `4fbd4d5b-07df-479b-b144-e13374d53d19` |
| lossy8 | email-018.aai-titus | `maria.okafor@northwind.co.uk` | `maria.okafur@northwind.co.uk` | I've sent a reset link to maria.okafur@northwind.co.uk. | `56abe64d-a527-45ca-b8c2-f3ba5396fa63` | `f20ae2e9-d7f0-4388-b611-de1cae2bcbd2` |
| native8 | email-018.aai-titus | `maria.okafor@northwind.co.uk` | `maria.okafur@northwind.co.uk` | I've sent a reset link to maria.okafur@northwind.co.uk. | `fac502e9-7f0d-422c-8e46-2ac266547c2a` | `240bf030-4383-49d8-acb7-32882508fb91` |
| resampled8 | email-018.aai-titus | `maria.okafor@northwind.co.uk` | `maria.okafur@northwind.co.uk` | I've sent a reset link to maria.okafur@northwind.co.uk. | `56abe64d-a527-45ca-b8c2-f3ba5396fa63` | `03f8ccf6-04e1-45d7-b393-fa4886ac79b4` |
| retake24 | email-018.aai-titus | `maria.okafor@northwind.co.uk` | `maria.okafur@northwind.co.uk` | I've sent a reset link to maria.okafur@northwind.co.uk. | `ca5c5b67-0a8e-42ad-a38c-d105b5091504` | `c681c986-51e4-4d81-85df-c14fc9375ce8` |
| api24 | price_gbp-018.aai-audrey | `£7,900.99` | `GBP 7999.99` | I can refund £7,999.99 to your original payment method. | `a58bccf2-1080-472b-8e62-1ce481d0b90e` | `0d3802ca-3854-4d29-be9d-6525930dc31e` |
| lossy8 | price_gbp-018.aai-audrey | `£7,900.99` | `GBP 7999.99` | I can refund £7,999.99 to your original payment method. | `a58bccf2-1080-472b-8e62-1ce481d0b90e` | `d4964fc0-9bb3-4840-a43c-04fd0f0dffd8` |
| native8 | price_gbp-018.aai-audrey | `£7,900.99` | `GBP 7999.99` | I can refund £7,999.99 to your original payment method. | `1a512c67-a282-49da-9a79-38e30a97980b` | `821d5dd0-e072-45af-a027-c69d0d345728` |
| resampled8 | price_gbp-018.aai-audrey | `£7,900.99` | `GBP 7999.99` | I can refund £7,999.99 to your original payment method. | `a58bccf2-1080-472b-8e62-1ce481d0b90e` | `767f253f-81af-4331-8914-cd58b30b44c0` |
| retake24 | price_gbp-018.aai-audrey | `£7,900.99` | `GBP 7999.99` | I can refund £7,999.99 to your original payment method. | `ee229f7c-6d2d-4cd4-ba1f-b1693686e0e2` | `fb9dd536-5b34-4074-9f55-d773beb4b2da` |
| api24 | price_gbp-018.aai-buford | `£7,900.99` | `GBP 7999.99` | I can refund £7,999.99 to your original payment method. | `505eb64b-a62e-4288-ab9c-e9f3c733e136` | `bf871045-ac16-48ce-961f-eda108679aa1` |
| lossy8 | price_gbp-018.aai-buford | `£7,900.99` | `GBP 7999.99` | I can refund £7,999.99 to your original payment method. | `505eb64b-a62e-4288-ab9c-e9f3c733e136` | `b03a51f4-cd9a-4e2d-8d6a-c99a356e0cbd` |
| native8 | price_gbp-018.aai-buford | `£7,900.99` | `GBP 7999.99` | I can refund £7,999.99 to your original payment method. | `b7055dc5-7162-4d5a-834e-eaafe103718d` | `c5cdc25f-d25d-41f7-893e-6719561f52e4` |
| resampled8 | price_gbp-018.aai-buford | `£7,900.99` | `GBP 7999.99` | I can refund £7,999.99 to your original payment method. | `505eb64b-a62e-4288-ab9c-e9f3c733e136` | `c32a5b3c-8525-4d92-b2af-6c8eea50bd69` |
| retake24 | price_gbp-018.aai-buford | `£7,900.99` | `GBP 7999.99` | I can refund £7,999.99 to your original payment method. | `824ffa76-6f95-4997-b41a-a498d3fb7f06` | `4a6c4b02-777c-41c4-aae3-9e94394ef2ee` |
| api24 | price_gbp-018.aai-nancy | `£7,900.99` | `GBP 7999.99` | I can refund £7,999.99 to your original payment method. | `546aed71-8f65-484c-a2a0-9efbea897b16` | `efd28d2b-270b-42b6-bef3-7bea907e2d0d` |
| lossy8 | price_gbp-018.aai-nancy | `£7,900.99` | `GBP 7999.99` | I can refund £7,999.99 to your original payment method. | `546aed71-8f65-484c-a2a0-9efbea897b16` | `dd35be8c-df97-4d90-9e9f-4d88cc8caf0a` |
| native8 | price_gbp-018.aai-nancy | `£7,900.99` | `GBP 7999.99` | I can refund £7,999.99 to your original payment method. | `736e3dd9-0c6f-4549-bd57-07ed382091bd` | `656f3626-23ff-463a-866a-ac3f8ec19213` |
| resampled8 | price_gbp-018.aai-nancy | `£7,900.99` | `GBP 7999.99` | I can refund £7,999.99 to your original payment method. | `546aed71-8f65-484c-a2a0-9efbea897b16` | `50e7da55-94a1-47d0-8161-31bc2b776f4b` |
| retake24 | price_gbp-018.aai-nancy | `£7,900.99` | `GBP 7999.99` | I can refund £7,999.99 to your original payment method. | `19f8f5c9-d060-4eb5-a69e-40f2b86ffe42` | `a1d215b8-9234-4f1f-b0aa-d430577b7e9b` |
| api24 | price_gbp-018.aai-titus | `£7,900.99` | `GBP 7999.99` | I can refund £7,999.99 to your original payment method. | `355fdac9-7fa9-47ed-a398-b1822be87f2c` | `feb30152-5979-4110-b317-9449432d6a52` |
| lossy8 | price_gbp-018.aai-titus | `£7,900.99` | `GBP 7999.99` | I can refund £7,999.99 to your original payment method. | `355fdac9-7fa9-47ed-a398-b1822be87f2c` | `ec4dc5f5-9dd2-48e0-9663-a4a401d5eead` |
| native8 | price_gbp-018.aai-titus | `£7,900.99` | `GBP 7999.99` | I can refund £7,999.99 to your original payment method. | `81c319e0-ed61-43e2-8aae-fa9f17ecaccb` | `25332ef9-f0ea-46b7-8090-c95d98426c0b` |
| resampled8 | price_gbp-018.aai-titus | `£7,900.99` | `GBP 7999.99` | I can refund £7,999.99 to your original payment method. | `355fdac9-7fa9-47ed-a398-b1822be87f2c` | `d3b4f117-7a66-438d-8800-ff629c5b6737` |
| retake24 | price_gbp-018.aai-titus | `£7,900.99` | `GBP 7999.99` | I can refund £7,999.99 to your original payment method. | `c260301e-2a00-4ce6-8d4e-e16fd6cdb4a2` | `77beee7a-44a3-4d48-8e08-820c89e8efd1` |
| api24 | uk_postcode-002.aai-audrey | `BS20 5LJ` | `I | BS25LJ` | I've got the postcode as BS25LJ. | `368be613-dd6c-4397-92a9-2dab9a760c18` | `0e280c3f-9cec-4972-a46d-6c1e8455661a` |
| lossy8 | uk_postcode-002.aai-audrey | `BS20 5LJ` | `I | BS25LJ` | I've got the postcode as BS25LJ. | `368be613-dd6c-4397-92a9-2dab9a760c18` | `bdc098f5-d29f-44f3-891e-ca8af187f6ab` |
| resampled8 | uk_postcode-002.aai-audrey | `BS20 5LJ` | `I | BS25LJ` | I've got the postcode as BS25LJ. | `368be613-dd6c-4397-92a9-2dab9a760c18` | `f1ec8450-8e25-4c8b-a284-8708ec3e418e` |
| retake24 | uk_postcode-002.aai-audrey | `BS20 5LJ` | `I | BS25LJ` | I've got the postcode as BS25LJ. | `f601449f-b166-4d38-8575-757bf414564a` | `5e7824f7-887d-4ba8-a1d5-e5b45b297640` |
| api24 | uk_postcode-002.aai-buford | `BS20 5LJ` | `I | BS25LJ` | I've got the postcode as BS25LJ. | `05b08429-3eb2-4cde-baf9-7c9f63e826d8` | `e7feaf3a-a9d7-4e0c-97f2-212a6f7d3661` |
| lossy8 | uk_postcode-002.aai-buford | `BS20 5LJ` | `I | BS25LJ` | I've got the postcode as BS25LJ. | `05b08429-3eb2-4cde-baf9-7c9f63e826d8` | `255116be-2ec6-45b4-a43a-cf153196ff66` |
| native8 | uk_postcode-002.aai-buford | `BS20 5LJ` | `I | BS25LJ` | I've got the postcode as BS25LJ. | `7e3e3bb8-7abe-4e0b-96cd-145c8a4d5192` | `3462c66a-862e-4f80-b8b6-bfda5fcd4aea` |
| resampled8 | uk_postcode-002.aai-buford | `BS20 5LJ` | `I | BS25LJ` | I've got the postcode as BS25LJ. | `05b08429-3eb2-4cde-baf9-7c9f63e826d8` | `c0755eaf-e173-4258-ad64-d5d3878018ef` |
| retake24 | uk_postcode-002.aai-buford | `BS20 5LJ` | `I | BS25LJ` | I've got the postcode as BS25LJ. | `2719e3ea-9eb1-40a1-ba16-102f3c8e7ead` | `990216c9-77ab-455e-81d7-e5c9c5c048e4` |
| api24 | uk_postcode-002.aai-nancy | `BS20 5LJ` | `I | BS25LJ` | I've got the postcode as BS25LJ. | `4c567552-9dda-4a2f-9314-3565bdb8485e` | `a179a35f-087b-4070-9a7e-99bd9c55c9d0` |
| lossy8 | uk_postcode-002.aai-nancy | `BS20 5LJ` | `I | BS25LJ` | I've got the postcode as BS25LJ. | `4c567552-9dda-4a2f-9314-3565bdb8485e` | `d5341651-59dc-4b8a-b0ac-3519792ec1e0` |
| native8 | uk_postcode-002.aai-nancy | `BS20 5LJ` | `I | BS25LJ` | I've got the postcode as BS25LJ. | `41cc6a9e-de53-464b-805b-24a4416deb91` | `a3b8b5e1-9424-4c2c-bada-5fcb45d83cde` |
| resampled8 | uk_postcode-002.aai-nancy | `BS20 5LJ` | `I | BS25LJ` | I've got the postcode as BS25LJ. | `4c567552-9dda-4a2f-9314-3565bdb8485e` | `66ddd0a6-3d5a-45e6-8231-da85f6afb7ec` |
| retake24 | uk_postcode-002.aai-nancy | `BS20 5LJ` | `I | BS25LJ` | I've got the postcode as BS25LJ. | `b7f4dfeb-b74f-48b7-ad7f-8b471fb81fc5` | `4d57388a-5f03-445e-9d62-bb46d04c5db0` |
| api24 | uk_postcode-002.aai-titus | `BS20 5LJ` | `I | BS25LJ` | I've got the postcode as BS25LJ. | `9b99bc0e-5afe-4ae7-96af-61c5607eca40` | `5c2ba081-c1a4-4f7a-9e97-1c785286e20c` |
| lossy8 | uk_postcode-002.aai-titus | `BS20 5LJ` | `I | BS25LJ` | I've got the postcode as BS25LJ. | `9b99bc0e-5afe-4ae7-96af-61c5607eca40` | `944fbaf5-e820-447a-b3c5-d66db3b168a1` |
| native8 | uk_postcode-002.aai-titus | `BS20 5LJ` | `I | BS25LJ` | I've got the postcode as BS25LJ. | `e2599fbf-b2de-43cf-959e-09d33a07c742` | `2e60cebd-43a4-41f8-9336-8699bdf37940` |
| resampled8 | uk_postcode-002.aai-titus | `BS20 5LJ` | `I | BS25LJ` | I've got the postcode as BS25LJ. | `9b99bc0e-5afe-4ae7-96af-61c5607eca40` | `1b4c681b-617e-48f0-afec-c428fd35cc44` |
| retake24 | uk_postcode-002.aai-titus | `BS20 5LJ` | `I | BS25LJ` | I've got the postcode as BS25LJ. | `79fe86b6-b6d9-4f8f-8a2b-ffb169e52178` | `5b63545b-bf20-45c4-8be2-81f6534e3345` |
| retake24 | uk_postcode-012.aai-audrey | `SE14 6UU` | `SC146UU` | Your nearest branch is at SC14-6UU. | `e8502262-d323-44ad-87c4-103d2ff517e5` | `efa665fc-4805-4d7e-9cde-e65112ebade2` |
| api24 | uk_postcode-013.aai-audrey | `SE14 9PS` | `SC149PS` | Your nearest branch is at SC14, 9PS. | `2b9225fa-8889-441a-a86f-0c1b49c3fbb8` | `db201946-b762-42aa-8d28-501f474d9c11` |
| lossy8 | uk_postcode-013.aai-audrey | `SE14 9PS` | `SC149PS` | Your nearest branch is at SC14, 9PS. | `2b9225fa-8889-441a-a86f-0c1b49c3fbb8` | `00d4734b-0384-4420-994a-c8fbecaf70ec` |
| resampled8 | uk_postcode-013.aai-audrey | `SE14 9PS` | `SC149PS` | Your nearest branch is at SC14, 9PS. | `2b9225fa-8889-441a-a86f-0c1b49c3fbb8` | `219e64b8-e9b2-405e-80d6-2b4a82e0d786` |
| api24 | uk_postcode-016.aai-audrey | `SE11 4GY` | `SC114GY` | Your nearest branch is at SC11 4GY. | `d0a6190b-5136-4193-8f14-55a79d0c548d` | `720cc6ea-e49b-425f-ac55-c4bddb8b07e4` |
| retake24 | uk_postcode-016.aai-buford | `SE11 4GY` | `C114GY` | Your nearest branch is at C11-4GY. | `84837a6b-659a-4281-832f-ef663084489e` | `0b6c5094-6bf0-493c-85f4-6e4ec3eeb0bf` |
| retake24 | uk_postcode-016.aai-titus | `SE11 4GY` | `SC114GY` | Your nearest branch is at SC11 4GY. | `a26952ff-08f6-4e5e-a1c5-649a0eb674b4` | `43a70aac-c970-474b-b1e8-87abb466b75d` |
| native8 | uk_postcode-018.aai-titus | `B8 6TF` | `I | B86TS` | I've got the postcode as B86TS. | `af3aad5f-f741-4bcd-b055-49a797049330` | `b3a6bfb9-1bbd-46e7-87ab-62a2ce86f5c8` |
| native8 | us_phone-007.aai-audrey | `(452) 555-0118` | `452550118` | You can reach the front desk at 452-550-118. | `60892653-4e8e-4db3-b7b8-4bb9111a9ebd` | `86ca0640-f3a5-475c-a18f-6a5b5d774197` |
| retake24 | us_phone-007.aai-nancy | `(452) 555-0118` | `452550118` | You can reach the front desk at 452-550-118. | `9d1fc69c-13b3-476b-9f89-816ae199d805` | `8613a60f-a240-4d43-9352-71067c0f5753` |
| retake24 | us_zip-006.aai-audrey | `62826` | `6226` | We don't deliver to 6226 yet, unfortunately. | `2ec6a9a9-b06d-4484-aec0-a7ef05b64d0d` | `790d571d-6b18-4988-8b4b-7e0670263513` |
| retake24 | us_zip-006.aai-buford | `62826` | `622826` | We don't deliver to 622826 yet, unfortunately. | `f571a8e2-c6cc-4a3e-a8c1-a86772c94dca` | `8e1e54ed-68d9-4520-b532-34e7f13969f1` |
| retake24 | us_zip-006.aai-titus | `62826` | `622826` | We don't deliver to 622826 yet, unfortunately. | `aa93f219-c892-4a29-8c82-8e8b594437d5` | `6a3e5a63-19fe-4fd0-be63-71577abfc3ec` |
