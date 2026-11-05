# C3X 0.29-P36/R4 — Native Stability Failures and Scientific Claim Ceiling

2026-11-05 KST. REAL pristine Stockfish16 native 24k→48k→96k observations, on eight fixed source-original March 2026 games. R4 48k/96k protocol was frozen BEFORE seeing those outcomes in commit 4c72c4a6aa1596e539484986d4275b9fd969934d. This is source-exposed exploratory research, not independent heldout explanation validation.

## Raw custody
Source-only frozen 8 cases: [Actions 41957706609](https://github.com/WhoSia/C3X/actions/runs/41957706609), official source SHA256 1a5ad83fc9f440dcdadde17b11cc81a953f4895aaf8b8588470b3078209dc7fc, [Drive source+manifest](https://drive.google.com/file/d/11szqoVSHKTeIaajHjxVgn9MoxVhUDBKY/view).
Native 24k joint MultiPV2: [Actions 41959284647](https://github.com/WhoSia/C3X/actions/runs/41959284647), eight-row JSON SHA256 5ce8ec253c95075cbba3a1b273236886756968778259363f1f1214fdb1c12d3f, [Drive](https://drive.google.com/file/d/1JnGMwA3_3YOOluAEfiVqF6HrI9j97s9p/view).
**Native R4 48k+96k: [Actions 41960341010](https://github.com/WhoSia/C3X/actions/runs/41960341010) SUCCESS**, pinned official Stockfish16 source 68e1e9b3811e16cad014b590d7443b9063b3eb52 and NNUE net SHA 5af11540bbfefcb54e38c5dd000cab4b469dfa7599a1d55be5d2722c20a8929b. Eight original game histories at two node budgets = 16 real engine processes. Six new plus five earlier tests passed.
R4 original output ZIP SHA256 b5f564f396099de1b874e094b873d3226f833461c5b934785b9c8d8f76cbd2f1; JSON SHA256 5b6c17934b615bf4cb01d6324a42d27e455cd9598cf1e39d7b354ca18eaee94a. [Permanent Drive ZIP](https://drive.google.com/file/d/1Bz1gyXcXRVnmnHNFtAuzCC5IYVct4p24/view). Re-downloaded Drive original and byte-verified exact ZIP SHA.

## P36/R4 primary result: 0/2 nominal near roots PASS
Case 00470a57672750d1 (American Cup Blitz) 24k f2f4 over d2c4 +190/+181 cp gap9, PV1 upperbound. At 48k same candidate pair +195/+167 gap28. At 96k same +195/+153 gap42, PV2 upperbound. Precommitted near stability FAIL (gap not <20 at both bigger budgets).
Case 01af9df4f5e8e39f 24k f3f4 over e2c1 -38/-48 gap10, PV1 upperbound. At 48k new runner-up e2g3 replaces e2c1, -42/-57 gap15. At 96k still e2g3, -34/-61 gap27, PV2 upperbound. Precommitted near stability FAIL both candidate-identity replacement and budget near-gap loss. Do not chart 24k/48k as the same fixed A/B pair.

## All eight cases retained
| Case | 24k roots, gap | 48k roots, gap | 96k roots, gap |
|---|---|---|---|
| 00090c4e53df5b2d | e1c1/f1g2 83 | same 155 | same 216 |
| 00470a57672750d1 | f2f4/d2c4 9 | same 28 | same 42 |
| 00846ac66ee43492 | e2d2/e2e3 63 | same 67 | same 57 |
| 00f04cd20636fdc2 | c3b2/h2h4: raw 77/93 (PV order discordant) | h2h4/c3b2 21 | same 10 |
| 01662a4d51803d33 | d4d5/e2f1 76 | same 99 | d4d5/c3b5 9 |
| 01af9df4f5e8e39f | f3f4/e2c1 10 | f3f4/e2g3 15 | same 27 |
| 01f4ddb70d4011c6 | c3b5/b1c1 22 | same 17 | c3b5/h2h4 23 |
| 02154be9fa2cf21d | d2d3/d4c5 576 | same 573 | d2d3/h2e5 548 |

Two apparent 96k near pairs are POST-OUTCOME (one prior-game-contaminated), never substitute as prespecified winners. Root PV1 output and cp estimates from bounded search are not ground-truth minimax values, even when no score bound flag appears.

## Exposure and future scientific falsifier
March2026 original archive was already in C3X on October 17; past C3X 0.20-C2 March16 source-only freeze [run 38038059013](https://github.com/WhoSia/C3X/actions/runs/38038059013) includes EXACT same full game for case 00f04cd20636fdc2, despite differing FEN due original ply30 versus ply34. Four/eight selected games same American Cup Blitz event; broad historical 0.28 64/source exclusion incomplete. July attempted 2026 source official SHA conflict and past M6 July64 exposure remain negative.
PI decision: **STOP near-gap overclaim and stop extra neural-instrumentation mini-versions**. Next experiment requires one independently evaluated opponent-response-conditioned chess consequence, frozen on a truly game/event-disjoint source, and equal forecast cardinality/node budgets among Stockfish score+PV, simple foil-aware plan JSON and C3X explanation. A small score difference at one budget is not an explanation. Report abstention and baseline wins. No C3X predictive advantage or human knowledge transfer established.

Notion semantic authority / Drive byte source / GitHub WhoSia human-authored code. github-actions[bot] repository writeback absolutely forbidden.