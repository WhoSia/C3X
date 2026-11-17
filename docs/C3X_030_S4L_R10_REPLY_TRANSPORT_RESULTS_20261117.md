# C3X 0.30 S4-L/R10 — Equal-request PV and reply tree on new game histories

2026-11-17 KST. [Pre-outcome protocol](C3X_030_S4L_R10_PROSPECTIVE_REPLY_PROTOCOL_20261117.md) · [Pre-judge endpoint amendment](C3X_030_S4L_R10_FORECAST_FREEZE_20261117.md) · [Forecast seal](../receipts/C3X_030_S4L_R10_PREJUDGE_20261117.json).

## Cohort and execution

TCEC S29 Division P, pinned official event archive [source](https://github.com/TCEC-Chess/tcecgames/blob/3dd69a40b3cf6ccc74144df7411ef4e8e2140286/master-archive/TCEC_Season_29_-_Division_P.pgn). The event contains 224 PGN games. The first eight eligible histories had distinct admitted 12-ply opening prefixes. The archive [prior C3X audit](archive/README_PRE_C3X016_CANONICAL_20261009.md) documents S29 Superfinal use. Division P is a different event. Cross-event opening independence was not established and earlier sealed cohorts were untouched.

The 30 cp cutoff applies to initial source nomination. Several Berserk all-reply gaps were much larger, so the following assessment is for Stockfish-nominated near pairs. It is not a set of independently verified near ties. Predictors share 48,000 requested nodes per candidate, including discovery for the tree. The pinned R4 Stockfish 16 build used classical evaluation and the pinned Berserk 14 source used its released NNUE. Both use one thread and 16 MiB hash. Actual reported source nodes across 16 candidates were 768,639 PV and 768,608 tree. Berserk performed 536 depth-12 reply searches and reported 20,814,278 nodes per pass. Two pairs are withheld by the frozen centipawn-only criterion because at least one candidate has a mate-valued branch. All legal replies were enumerated for all 16 candidates.

## What the comparison found

At the original strict endpoint, which takes the terminal UCI report only when both candidates have usable ordinary centipawn predictions, PV predicted 2/8 pairs and the tree predicted 0/8. Short 8k leaves frequently ended on a bound. Before target engine execution, froze the observed primary result and the secondary latest-unbounded reporting operator for both arms under the original budgets. This repair changes the depth at which a usable point prediction is taken, and retains actual terminal node cost separately. The extended forecast reproduces the terminal forecast fields exactly.

| Secondary metric on the same six eligible pairs | PV | Three-reply tree |
| --- | ---: | ---: |
| Correct sign of candidate gap | 4/6 | 5/6 |
| Exact minimizing-reply membership across twelve candidates | 5/12 | 7/12 |
| Mean absolute gap error vs Berserk | 32.0 cp | 38.5 cp |

Selection and all 536 referee searches were rerun in fresh engine processes. Both normalized outputs matched byte-for-byte. The two engines' cp scales are distinct. Gap errors are descriptive cross-engine discrepancies, not objective errors about optimal chess play. Discovery found a Berserk-minimizing reply 9/12 times. The tree's final reply recommendation retained it 7/12 times: three misses in discovery, two in leaf ordering. With Qb3 versus c4 (round 2.4), the tree correctly predicted Qb3 and missed the opponent reply Qc8 after it during leaf ranking even though Qc8 was in its three discovered moves. With Bxc5 versus Nd2 (round 1.4), the tree selected the correct worst reply for each candidate yet got the candidate ranking wrong (tree gap +12, judge gap -39). Thus correct branch identification and accurate cross-candidate valuation diverge even in the same position.

In a post-judge diagnostic, keeping exactly the three Stockfish-discovered replies and replacing their leaf values with the already recorded Berserk scores preserved the full-judge ranking for all six cases. Omitted replies still changed the restricted gap in three cases by 24, 1 and 7 cp in absolute value. This asks how much reply discovery alone lost under this referee, and uses referee labels unavailable to either predictor.

These results do not establish superiority or the causal transport of R9's internal mechanism. Candidate selection uses a source-engine near-tie screen, the six paired judgments come from one event and one referee configuration, and the revised endpoint addresses source-side censoring. A next experimental round can test redistributing discovery and leaf budgets on a separate event, with depth sensitivity and an explicit mate-order scoring rule frozen before predictions. Retain the exact PV arm and score coverage independently of accuracy.

## Reproduce

Run the [stage runner](../harness/c3x_030_s4l_r10_reply_transport.py) as `select`, `predict`, `judge` in that order. Each command takes engine path and input path. For the judge add `--net` with the pinned Berserk network. Use the [paired scorer](../harness/c3x_030_s4l_r10_score_transport.py) with cohort, extended forecast and judge files, then the [diagnostic](../harness/c3x_030_s4l_r10_diagnose_transport.py) with score, extended forecast, and judge. Existing receipt regression tests passed 25/25.

[Verified source PGN and experiment capsule](https://drive.google.com/file/d/148_MbQ-ePw9JWnhQn24mhTDGzqZA19nH/view). ZIP SHA-256 `aebd86ede5268e7e8fdacdf3883100298f7c9449ea0a44d43e4ceb7f797315de` confirmed by independent readback.
