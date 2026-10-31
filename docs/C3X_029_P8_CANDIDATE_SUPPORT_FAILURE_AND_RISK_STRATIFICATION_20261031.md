# C3X 0.29-P8 — Candidate-Support Failure and Risk-Stratified Counterfactual Chess Choice

**2026-10-31 | Original pre-treatment Git-frozen 128-UCI registry joined with original native-result receipt. Analytic reanalysis; NO new Stockfish intervention.**

## Why this research exists

0.29-P7 restored the original source-level failure genealogy: K4 0/4 first-return root rescue was followed by a real second-return rescue and alpha-threshold one-point discontinuity in 0.20-B/C; 0.22 exact-UCI TWIC transfer predictions failed; I10 305-weight training did not outperform constant prevalence. The next actual research problem is not to invent more arbitrary chess predicates, but to diagnose what the **original forecasting action space** failed to represent.

Sources:
- [Pre-physical-intervention 128 exact UCI forecasts, committed with sealed StageA](../c3x/forecasts/c3x-022-P2-TWIC-puzzle32-exact-UCI-preregistered-stageA-20261010.json)
- [Real physical TT reader native StageB verdict, all original negative outcomes preserved](../c3x/receipts/c3x-022-P2-TWIC-puzzle32-stageB-literal-UCI-falsification-and-depth-20261010.json)
- [The detailed original failure and legal candidate analysis](C3X_022_P2_EXACT_UCI_FORECAST_FAILURE_20261010.md) (if this historical path is unavailable, use the receipt and the earlier original 0.22 named report; do not infer its exact pathname as a source)
- [Reproduction script](../tools/c3x_029_p8_archived_candidate_support_reanalysis.py) and [tests](../tests/test_c3x_029_p8_archived_candidate_support_reanalysis.py).

## P8 finding 1: baseline disagreement is a pre-treatment *risk marker*, not a deterministic switch rule

In original TWIC issue1656, 16 independent source chess game IDs, two search-order baseline worlds O and F and STRICT/BROAD source roles yielded 64 eligible role outcomes.

The earlier Git-frozen forecast registry directly defines:
- O/F BASELINE AGREEMENT: games `2,5,6,8,9,11,15,16` (8 games; 32 role cells).
- O/F BASELINE DISAGREEMENT: games `1,3,4,7,10,12,13,14` (8 games; 32 role cells).

The actual native receipt gives TT-FIRST final-choice flip games `1,4,7,10` only (4 games, 10 correlated role cells).

| Preintervention game stratum | Games | Changed bestmove in ≥1 source role | No bestmove change |
|---|---:|---:|---:|
| O/F disagree | 8 | 4 | 4 |
| O/F agree | 8 | 0 | 8 |

The observed game-level risk marker has apparent **4/4 changed-game recall** and **4/8 = 50% precision** in this very cohort. At the nested role-cell level its predicted-flip confusion is TP10/FP22/FN0/TN32, so precision = 10/32=31.25%. These denominators are DIFFERENT. Neither observed 100% recall nor 0 flips among agreeing games licenses a universal causal rule, particularly across different source ecologies or search depths.

**Negative controls:** all 16 puzzle games had O/F same baseline; among 28 eligible physical contacts, actual flips were 0. The puzzle 28/28 no-change predictions contain **zero positive flip cases**, not independent confirmation of a switch rule.

## P8 finding 2: original two-baseline-only output vocabulary was provably insufficient in this sample

A source forecast restricted to legal final answers `{bestmove_O, bestmove_F}` cannot output a third move, even with an oracle that perfectly chooses between these two labels.

Observed 64-role outcome decomposition, directly implied by archived receipt:
- 54 treated actions keep original condition's move;
- 6 treated actions flip to the other source-order baseline move;
- 4 treated actions flip to **neither** original baseline move.

The last fact follows because the 10 actual changed role outcomes include only 6 whose exactly predicted "other baseline" UCI was correct. All 10 actual flips were in O/F-disagreement strata; for the other 4, the changed action cannot equal the original baseline (it changed), nor the other baseline (exact forecast wrong). Examples in original receipt: game4 F chooses newly `c2d1`, baseline O/F `b5c3`/`c2c8`; game10 O chooses `f4g3`, baseline O/F `f8f7`/`a8e8`.

Therefore for the measured 64 roles **any two-baseline-only oracle exact-move accuracy is bounded by**

`(64-4)/64 = 60/64 = 93.75%`.

This is a **support misspecification ceiling** based on the realized sample, not a general population theorem or evidence a learned model can attain 93.75%. The actual frozen forecast achieved 38/64 exact UCI; always preserving the original move achieved 54/64 exact. The gap to the oracle reflects additional wrong switch/no-switch decisions as well as the 4 missing third actions.

## P8 finding 3: correct binary change-risk classification ≠ precise explanation

The original rule's binary "will the bestmove change?" accuracy is (TP+TN)/64=(10+32)/64=65.625%, whereas *precise final UCI* accuracy is (TN+6)/64=38/64=59.375%.

**Abstention diagnostic:** A pre-treatment policy that outputs the old legal bestmove *only if O/F agree*, and otherwise returns UNKNOWN, would cover 32/64=50% roles and happen to be correct in all 32 covered old cells. This is legitimate retrospective selective risk/coverage analysis, but **it abstains on all 10 actual flips**, thus supplies no useful *positive causal explanation*. It is not prospective calibrated confidence; must not be advertised as a solved predictor.

## Research diagnosis and next mechanism bridge

Failure of exact UCI restoration had at least two separate components:
1. **Change-event false positives:** 22/32 flagged roles never changed. The pre-treatment O/F difference predicts possible instability but not necessity.
2. **New-candidate emergence:** 4/10 actually changed roles could not be represented by the two already observed O/F baseline moves.

This creates an empirically motivated **candidate-support obligation**. A model that claims to explain a TT-induced root switch must first identify an admissible set of candidate root moves that includes the actually reachable winner after intervention. Simply giving a probability over two old moves is insufficient when the actual winner is a third move.

The 0.20-C alpha gate revealed a possible *mechanism class* for candidate survival: value crossing source alpha threshold changes gate and downstream search path; but 0.20-C game3 is different from TWIC games4/10, so no actual alpha-gate causal mechanism has been verified for the TWIC third-candidate observations. Existing TWIC native leader-depth divergence hints (game4 F changed depths9/10/12; game10 O 6/8/10/11/12) are observations, not complete parent-to-root mediators.

A scientifically credible next experiment should predeclare two separate endpoints on source-disjoint new full-game histories: (A) binary source-treatment flip, (B) *exact UCI across all legal candidates*, including out-of-baseline third moves or explicit abstention, with separate per-game and per-role scores. Then identify the first **source-exact candidate whose survival differs** under TT policy, actual child returned signed score, parent consumption and leader/root state, and a distinct legally checked chess-consequence explanation for root alternatives. No outcomes-only post-hoc vocabulary fitting.

**Boundaries:** existing native 0.27 game14 single-guard root rescue and 0.25 P13-R4 physical partial parent consumption remain real prior evidence. This P8 is original **archived data analysis**, not a new experimental replication, and is not new proof of natural TT->SEE mediation, semantic chess superiority or human transfer. No bot-written commits, no workflow dispatch, no claim of 0.29 empirical promotion.
