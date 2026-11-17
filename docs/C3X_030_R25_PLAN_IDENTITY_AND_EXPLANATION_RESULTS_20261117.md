# C3X 0.30 R25 — Explainable Stockfish: PV is not a plan certificate

## Result (existing exposed observations, newly audited)

R24 identified two different ways for a GUI's “best line” to change while the recommended move and displayed root score stay fixed. R25 turns these into a machine-readable evidence ledger rather than narrating a plan that has not been tested.

| Exposed position | Root move, displayed score | Native scores | What actually diverged | Independent judge at the same fork board |
| --- | --- | --- | --- | --- |
| Spanish after 4…Nf6 | O-O, +39 cp | 128 / 131 | **White's** next move after shared …Nxe4: d4 vs Re1 | White: depth 12 Re1 +68 vs d4 +56; depth 14 d4 +49 vs Re1 −12 |
| TCEC S28 L2 round 1.4 | Qxe2, +89 cp | **292 / 292** | **Black's predicted reply:** …Bh2+ vs …Be7 | Black: depth 12 …Be7 −95 vs …Bh2+ −111; depth 14 …Be7 −98 vs …Bh2+ −109 |

For the Spanish example, the independent branch ordering reverses with judge depth (12 cp versus 61 cp in opposite directions). For the TCEC example, the alternative reply …Be7 is better for the replying player by 16 and 11 cp at the tested depths. These are **conditional, forced-first-reply** assessments, not a proof of objectively best play at arbitrary depth.

Crucially, the first row is a variation in **White's own continuation**, while the second row changes **the opponent's anticipated move**. A viewer must not infer from the latter that “White changed its strategic plan.” Both observations can occur with an unchanged root decision and score.

## Implemented evidence firewall

- `product/c3x_plan_evidence.py` validates two already legally replayed R24 root reports: same legal root UCI, exact cp not a bound, in-window completed native producer, divergent PV rather than a prefix. It emits common prefix, first divergence, whose move changes, native values, and tested independent branch order.
- `receipts/C3X_030_R25_EXPOSED_FORK_EVIDENCE_20261117.json` is a **historical-exposed** read-only translation of the previously frozen R24 examples. It cites the exact R24 original archive; it is not a new engine cohort or independent raw-byte audit.
- `product/c3x_plan_evidence_report.py` renders Korean comparative observations with exact authority limits and a machine-readable future trial question. It explicitly labels fresh replay, TT/NNUE causality, opponent-plan survival, and human improvement as untested.
- `harness/test_c3x_030_r25_plan_evidence.py` and `harness/test_c3x_030_r25_fork_pipeline.py` reject incomplete evidence and assert that no internal mechanism or transferable plan was invented.

Run from the repository root with Python 3.10+:

```bash
python product/c3x_plan_evidence_report.py receipts/C3X_030_R25_EXPOSED_FORK_EVIDENCE_20261117.json
python product/c3x_plan_evidence_report.py receipts/C3X_030_R25_EXPOSED_FORK_EVIDENCE_20261117.json --format json
python -m unittest discover -s harness -p 'test_c3x_030_r25*.py' -v
```

No chess library or engine is needed for the **ledger reclassification**, because the underlying R24 legality and Stockfish results are cited as prior external evidence. This code does **not itself establish** chess legality, native event authenticity, or reproducibility. New source data still pass through the R23/R24 native+chess validators.

## What would turn this into a strategic explanation?

For a plan predicate \(P\), declare a defender reply set \(R\) and continuation bound \(h\) *before* independent judging. The distinction to measure is:

- **Observed PV witness:** \(\exists\) one searched sequence showing \(P\).
- **Adversarial survival:** for every listed legal defender response \(r\in R\), there is an allowed response strategy that reaches or preserves \(P\) within \(h\).
- **Value of pursuing it:** contrast the unconstrained best position value with the best value under the plan constraint; a successful plan may be too expensive to justify.
- **Native explanatory causality:** matched physical search intervention vs sham, with upstream child→parent→root propagation, on the *same full legal root menu*.
- **Human usefulness:** compare unseen-reply tasks with blind controls; correctness and recommendation agreement are not enough.

Do not promote a plan just because its line is legal, its score ties, or one independent engine favors its first branch. Retain negative and abstained trials.

## Immediate next experimental unit — breadth first

1. **R26-A, engine behavior:** freeze a new corpus covering Spanish/open games, closed pawn structures, middlegames, and endgames; classify root-stable / PV-unstable states, conditional on fixed engine and finite budget. Report position-level rates and clustering by game, not pairwise-report counts as independent trials.
2. **R26-B, decision causality:** choose *one* native event by a preregistered identifier in an eligible full-root source run. Compare targeted manipulation and irrelevant sham with producer receipts, not a score-only causal story.
3. **R26-C, chess meaning:** for a changed PV, predeclare a board predicate and opponent defenses before searching, and test its survival and opportunity cost using an independent judge.
4. **R26-D, learner outcome:** present same recommendation/score with (i) one PV, (ii) two qualified continuations, (iii) continuations plus validated motive and counterexample. Use new positions to test selecting an appropriate reply, not just liking the prose.

This is 0.30/D1 continuation. No version promotion; the earlier sealed 7/8 HOLD cohort and the original R24 cases retain their authority limits.

[Previous R24 replay](C3X_030_R24_PV_FORK_REPLAY_RESULTS_20261117.md) · [R25 claim gates](C3X_030_R25_EXPLAINABLE_STOCKFISH_CLAIM_GATES_20261117.md) · [Two-Track Constitution](C3X_TWO_TRACK_CONSTITUTION.md).
