# C3X 0.31/P2 — TWIC1670 Original Source, 64 Legal Game Freeze, P1-Only Model Lock, and SF16 Native Build

**Date:** 2026-11-21. **Scientific status:** genuine new-issue data acquisition and *pre-treatment experimental apparatus* validated. No P2 treatment effect, prospective prediction accuracy or causal mediator is claimed in this stage. See pre-frozen [P2 protocol](C3X_031_P2_NEW_GAME_TRANSPORT_PREFREEZE_PROTOCOL_20261121.md).

## Source original and independently audited custody

The original publisher is **Mark Crowther, The Week in Chess**, [TWIC issue 1670, 2026-11-09](https://theweekinchess.com/html/twic1670.html), publisher source [zipped PGN](https://theweekinchess.com/zips/twic1670g.zip). Publisher source SHA256 is **`6e6866cfe57ea0db7849f9b686fded1c1fe9d1fcab783359030b97ace377eccf`**, 2,400,939 bytes; single PGN member `twic1670.pgn`, SHA256 `bb166b4813aca824d4455ee51d0bbe3be75405586b310639c3eedfe02a32b77d`, 8,470,978 bytes. SHA was validated from the [original source acquisition CI #44871735875](https://github.com/WhoSia/C3X/actions/runs/44871735875) and on readback from Google Drive.

Original source census: exactly **8,391** parsed PGN game records; **8,328** nonempty legal standard-start games, **8,283** distinct complete move histories, **45** within-issue duplicate complete histories, **63** empty games, **47** normalized event family headers. The parser did not silently classify 8,391 games as eligible test cases.

- [Private Drive original publisher ZIP](https://drive.google.com/file/d/1aYTJF5WYCP-GkWndWrdot20xeA5eVf3H/view)
- [Private Drive original publisher census](https://drive.google.com/file/d/1891oQFvQuhZVUF3unVW0QTVqO6xBEqPb/view)
- [Executed acquisition code](../harness/c3x_031_p2_source_audit.py)

TWIC is free for personal use with rights reserved. Do not commit original PGN bytes to GitHub or redistribute publisher archives with a claim of permission.

## Overlap exclusion and actual new-game prefreeze

The R33 original archive contains **78 previously excluded event families plus 16 selected R33 families**. Cross-comparing the original TWIC1670 event headers against their historic family identities rejected **30 of 47 event groups** containing **6,065** game records. Remaining **17 candidate event families** contain **2,326** raw game records. Event-family differences alone do not establish total game-history independence, particularly with rapid/blitz variants. The complete selected 64 game history hashes were also independently compared to original R33 selected 64 games: **0 identical full-game histories**, **0 identical four-field FEN checkpoints**, and **0 family overlaps**. Full source-hash comparison against every pre-R33 distinct individual game has not been carried out; do not claim that global stronger condition.

Actual pre-treatment, [read-only GitHub game-freeze CI #44872034069](https://github.com/WhoSia/C3X/actions/runs/44872034069), selected exactly **64 distinct complete legal games/checkpoints**, across **17 candidate event families**, with predetermined priority checkpoints `[40,41,50,51,60,61,70,71,80,81]` and frozen deterministic round-robin family ordering. Each source position has 2+ legal moves and a nonterminal legal board. Only untreated PGN metadata and legality was used, **no source intervention results** or model predictions. Four game records from the admitted family pool lacked a legal checkpoint, and 161 were shorter than the first checkpoint. The sampler did not alter the denominator to recover a desired signal.

- [Exact full-game private freeze, Drive ZIP](https://drive.google.com/file/d/1Aj02UgRoHYw6sKqPjwOmtDETfTnESpe8/view), private full-history JSON SHA256 `2a174dcf56a333408693785eb0a844a419f7f8ba090c0a00187f3dab483d57e4`.
- [Public non-PGN source freeze metadata in Drive](https://drive.google.com/file/d/1JomRK_quDvF0MC7Zc5ph1UpzzVqMPaUk/view).
- [Frozen original family-admission rule](../frozen/C3X_031_P2_TWIC1670_EVENT_ADMISSION_20261121.json) and [audited full-legal-history sampler](../harness/c3x_031_p2_freeze.py).
- **No P2 physical search event target was nominated by these legality checks.** Each such nomination must come from untouched native Stockfish source evidence later.

## Fit once on P1; do not use P2 outcomes

Original P1 R33 64-game/128-event development set has 11 actual final move switches. The fully-trained coefficients of M0 (prior prevalence), M1 (untouched public depth/score/bound/PV) and M2 (M1+pre-open native event depth/ply/slack/nodes/attempt/stratum/root) were **frozen before a new P2 source treatment**: [pre-outcome model JSON](../frozen/C3X_031_P2_FINAL_MODELS_PREOUTCOME_20261121.json), SHA256 `f27a89fd15efa3f35738ba8cf2a6d1243c8336268e4661c653bbd1e6c0bfee23`. Train source TSV SHA256 `6e5cd1215ab13ac3dba3c93447b577f305c06fad1fd00c2b4a5338c71e7a63ba`.

[Model lockcheck](../harness/c3x_031_p2_lockcheck.py) independently derives all means, scaling, coefficients and Jeffreys prior with the original fixed ridge `0.02`, 900 gradient iterations and step `0.10`. [Read-only CI #44872254412](https://github.com/WhoSia/C3X/actions/runs/44872254412) passed the P1-only seal and six negative guards. These are predictive correlations, *not* a sufficient causal state or external test.

## Pinned native executable build and future contact gate

Original official **Stockfish 16 `sf_16`** source commit `68e1e9b3811e16cad014b590d7443b9063b3eb52`. Seven exact in-repository original patch layers (R27 choice, R29 local/value, R30 picker, R31 scout/fail-low, R33 early-return) were applied and actually compiled in [GitHub Actions #44872367852](https://github.com/WhoSia/C3X/actions/runs/44872367852). Modified search source is not claimed to be the untouched Stockfish source; the only appropriate comparison is the matched original/pre-R33 reference executable plus observer-off R33 variant.

- Full SF16-R33 binary SHA256 `ce13b5899ab6862a621ee6033ac661f7ded0abf3f2b4ea073a163b0c3154afa1`.
- Original NNUE SHA256 `5af11540bbfefcb54e38c5dd000cab4b469dfa7599a1d55be5d2722c20a8929b`.
- Added pre-R33, R31-prefix source build and paired compiled artifact in [later no-treatment build run #44872473600](https://github.com/WhoSia/C3X/actions/runs/44872473600); reference binary SHA256 `78cae269c73eb080c8a508e839dcde15ce48888b3fc4317fa3311de49e5ee7bb`. It was separately compiled *before* applying R33. The native source patch's observational transparency on new games is not assumed from compilation success.

[Native source-only discovery harness](../harness/c3x_031_p2_native_discovery.py) and [read-only discovery workflow](../.github/workflows/c3x-031-p2-native-discovery.yml) require the exact frozen sample/model/binaries/NNUE, then execute one original R31 reference run, one R33 observer-disabled run and one R33 observer-enabled run on each of the 64 exact histories. No treatment flag is enabled. Only after strict UCI/root-producer parity is observed can physically contacted R33 events be nominated by the same untreated minimum-slack rule. Pre-outcome M0/M1/M2 predictions and exact native source event signatures must be sealed **before** executing any physically treated P2 counterfactuals.

If parity fails in any case, treat it as an experimental gate failure and **do not run new P2 intervention**, rather than letting newly modified instrumentation silently change the source world.

**Scientific court:** `P2_SOURCE_AND_GAME_FREEZE_CONFIRMED / P2_P1_ONLY_MODEL_CONFIRMED / P2_NATIVE_SOURCE_COMPILE_PASS / P2_INTERVENTION_OUTCOME_HOLD`. This status may be revised after actual source-only parity is computed, never before.
