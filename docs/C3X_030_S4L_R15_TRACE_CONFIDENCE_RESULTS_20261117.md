# C3X 0.30 S4-L/R15 — Internal root switches as an uncertainty warning

2026-11-17 KST. The [follow-up rule](C3X_030_S4L_R15_TRACE_CONFIDENCE_PROTOCOL_20261117.md) was specified after observing R14's zero deeper-trace coverage and [frozen](../receipts/C3X_030_S4L_R14_R15_LEAGUE1_FORECAST_FREEZE_20261117.json) before either reference search. It uses exactly the same 16 source searches. All arms retain the same most probable rank label. The comparison measures three-class Brier loss at eight shared questions, with lower being better.

| Warning policy | Mean loss at depth 16 | Mean loss at depth 18 |
| --- | ---: | ---: |
| Constant 0.75 on forecast sign | 0.40625 | 0.40625 |
| Downgrade on public UCI warning | 0.4326171875 | 0.4326171875 |
| Downgrade on public warning or internal switch | 0.447265625 | 0.447265625 |

The public condition fires on five questions. A trace-only switch changes one additional probability vector. Round 2.1 is the sole incremental case. After Nc3 …Qe7 the same root invocation initially updates Qc2, then Rac1, then Qd2. The independent result still favors the competing Bc5 line after …Qe7 by 772 cp at depth 16 and 752 cp at depth 18. The public fixed-reply forecast already favored Bc5 (26 vs 656 cp), so reducing the probability of its correct direction worsens mean loss by 0.0146484375. The rule treats a move change inside either branch as cross-branch uncertainty. This example exposes how those two notions diverge.

The confidence projection reproduces exactly from the independent source rerun. The probabilities are heuristic; this eight-question pilot does not estimate a general calibration curve. The next candidate rule must represent uncertainty in the difference between the two candidate branches and account for the public margin before crediting any source warning. An event-disjoint test must define such a rule before reading its source and reference outcomes. An additional line of work is query-specific branch evidence for a concrete chess predicate, following the Wilkins mate-witness precedent. [Raw traces and losses](https://drive.google.com/file/d/1HFathAD2eGoPYRX5p9ciQm91uCMOao0R/view) · [same-search directional test](C3X_030_S4L_R14_MATCHED_TRACE_RESULTS_20261117.md).
