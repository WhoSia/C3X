# C3X 0.29-P37/R5 — Actual Human Continuation After Sealed Three-Rival Forecasts: Independent-Label Negative

2026-11-05 KST — **ACTUAL ARCHIVAL COMPUTATION + INDEPENDENT READ-ONLY CI PASS; SCIENTIFIC TEST IS RETROSPECTIVE / EXPLORATORY.** This record does not upgrade the 3-ply C3X-inspired heuristic to the full mechanistic C3X model and does not establish chess-optimal root-move value.

## 1. Why a second outcome label is necessary

P37/R4 [actual eight-event result](C3X_029_P37_R4_EIGHT_EVENT_FORECAST_PV_DOMINANCE_AND_VALIDITY_CEILING_20261105.md) gave SF16 24k PV 11/15, foil-aware JSON 2/15 and C3X-inspired legal three-ply heuristic 4/15 when predicting **SF16 96k forced-root PV opponent move**. The later Stockfish reference was obtained *after* predictions were frozen, but same-engine agreement is not an independent chess-value oracle.

This secondary audit asks a different observable: if the game player actually chose the exact candidate root proposed by joint 24k MultiPV, did the three **pre-referee sealed** predictors anticipate the recorded opponent's next UCI move? No new model fitting, no new chess engine or prediction generation. Important: this audit is retrospectively defined after source and predictions were available; human UCI sequence lived in original PGN but was stripped from the first prediction job's model input. Therefore this is a secondary analysis, **not a prospectively registered scientific result**.

## 2. Original source and exact hash chain

- [Eight event-family original source R1 native CI #41968008046](https://github.com/WhoSia/C3X/actions/runs/41968008046); outer ZIP SHA256 `3f16f69c6cb01029c519aeb24654913303916ce79537c1a86497bb9c84b79191`; raw manifest member SHA256 `77ebaa409e7c2099cc6cce3419c2f55ded295d925ab441dc2d13c16b67c2c361`.
- [Pre-referee prediction R2 native CI #41969173637](https://github.com/WhoSia/C3X/actions/runs/41969173637); prediction ZIP SHA256 `721471da43d0bd973e2b084fc47070f5a5826d0add38cbc39a2ccfbca6a427f6`; raw prediction JSON SHA256 `da395f0eb16e7b294af2056dadd92b579770aa8f1ae288d1d358132685807051`.
- [Independent human-reply re-audit CI #41983790740](https://github.com/WhoSia/C3X/actions/runs/41983790740) SUCCESS: authentic member SHA256 checks, 8 original full-game history SHA256 recalculated, full ply-30 UCI prefix and FEN identities checked, two independent deliberate corruption tests (history byte and prediction prefix) correctly rejected, complete case count. The CI reads sources and produces artifact only.
- Original result ZIP: [Drive byte-sealed](https://drive.google.com/file/d/1CRVZqYBwf6fUWixnSvv6krF3zmdgfuMv/view). GitHub artifact ZIP SHA256 `b68aeac25cfb3be52ff6cb16ebfc8e31064636f45f137e92b8058372699b9b9d`; Drive was re-downloaded and its SHA256 exactly agrees. Internal output JSON SHA256 `ddc3a6dfc6a28c381ae5b56b064f3f22c77255cafbd5c575d6dcd4f09f7a4a33`.
- [Authenticated Github executable audit](../tools/c3x_029_p37_r5_real_human_continuation_court.py), [tamper/denominator tests](../tools/test_c3x_029_p37_r5_real_human_continuation_court.py), [read-only workflow](../.github/workflows/c3x-029-p37-r5-human-reply.yml). Original archive-backed local integration tests were 5/5 PASS; independent CI PASS.

## 3. Complete original denominator and human behavior observations

The eight original game source families are distinct; the exact realized player move at source ply31 is compared to both sealed Stockfish 24k root candidates (not a hypothetical root). Only **6/8 original games** have the actual player's next move in the two 24k candidates, leaving **2/8 counterfactual human response labels unobservable**. Do NOT impute a reply for an unplayed alternative, nor score it as wrong.

| Event family | Actual human root | Actual next human reply | PV forecast | Simple JSON | C3X 3-ply heuristic |
|---|---|---|---|---|---|
| Sahel | `e5f4` | `c8e6` | miss | miss | miss |
| KazChess Masters | `d2c2` | `g4f3` | hit | miss | miss |
| Chinese League | `f3d4` | `f5g6` | hit | miss | miss |
| Clutch Chess | `c4e3` | `c7c6` | hit | miss | miss |
| Freiburger | `c3a4` | `a5d2` | miss | hit | miss |
| Garcia-Palacios | `e5f6` | `g7f6` | hit | hit | hit |
| Magdeburg | `h1g1` not in proposed top2 | unobservable foil | censored | censored | censored |
| Greg Hjorth | `f2e2` not in proposed top2 | unobservable foil | censored | censored | censored |

For **6 comparable observed human replies**: SF16 24k PV **4/6 (66.7%)**, simple JSON **2/6 (33.3%)**, C3X legal 3-ply plan **1/6 (16.7%)**. Paired PV-vs-C3X: 3 PV-only correct, 0 C3X-only correct, 1 both correct, 2 neither correct. This is not a precision population estimate; the choice-conditioned n=6 is far too small. Individual cases within each named event remain original source-game development cases; historical C3X event exposure clearance remains incomplete.

## 4. Scientific adversarial conclusion

**FAIL for a narrow hypothesis:** The tested shallow C3X-inspired lawful material-plan heuristic does not outperform the single Stockfish PV in exact human opponent-reply prediction in these six observable cases. This agrees in direction with its failure to outperform PV against the deeper Stockfish-reference labels (the two labeled tasks must not be merged).

**NOT TESTED:** Whether a real source-native NNUE path mediator is chess-explanatory; whether human actions are optimal, whether C3X improves an independent action-conditioned **chess-value** prediction beyond strong PV and budget-equated foil-aware baselines, human teachability. Human responses are contingent on skill/psychology/time, not a solved minimax oracle. Full causal C3X never appeared in the three-rival pilot.

**Research decision:** Stop optimizing shallow 3-ply material-reply heuristics solely for matching opponent UCI. Next design must predefine a chess-valued consequence Q (not identical to the predictor construction), with a separately frozen verifier using chess-law invariants and where appropriate **a genuinely independent engine family** and abstention when referees conflict. Work on source/event independent validation and total computation matching; do not allow extra legal-reply expansions to C3X for free. Keep near-equal move preference as the principal difficult task, but require root candidate identity and margin stability across multiple budgets before declaring a stable near tie. Strong PV baseline must remain.

## 5. Mandatory provenance

All repository authorship `WhoSia`, Actions only compute/read/upload with `permissions: contents: read`, `github-actions[bot]` never commits/pushes/merges/tags/moves refs. GitHub executable and error history; Drive raw bytes; Notion semantic judgments. No retroactive erasure of P37/R4's 11/15 PV dominance or P36 negative near-margin results.
