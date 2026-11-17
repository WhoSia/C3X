# C3X 0.30 R23 — Explainable Stockfish

C3X's primary goal is to explain a move that the actual full engine chooses. The trace should show which search produced the public verdict, which alternative failed to replace that move, and what legal board resources the decision leads to. A user should be able to change one condition, predict the consequence and replay it. When the available evidence is only a legal witness or a local engine observation, the explanation should say so.

## R23 evidence

[Live native replay](C3X_030_R23_NATIVE_PROVENANCE_RESULTS_20261117.md) joins identity, bound, raw value and UCI result on ten tested scenarios from two exposed games. [Stopping intervention](C3X_030_R23_STOP_BUDGET_RESULTS_20261117.md) reproduces a change in final bestmove on the untouched and traced executables. [Korean examples](../product/README.md#r23--explainable-stockfish-decision-cards) reconstruct the exact selected move alongside legally verified board resources.

Earlier fixed two-root experiments remain useful for diagnosing rival explanations. In R21 1.2 default-NNUE Stockfish selected h4 from the two named moves and Bd2 from the full menu, so a two-root verdict cannot substitute for the full-engine verdict. R22's independently scored future replies help test strategic claims, and they remain independent of the UCI producer. The newly traced cases are comparisons on exposed development games.

## Replay

[Drive evidence archive](https://drive.google.com/file/d/1XYWXYcFsFqwhg-XNB-_eVqqo3AB-aRFj/view), SHA-256 `71e61b0bb0e3011a280b86bec46e480c59562b7195005f71ff3baed2ec54ea1e`. The downloaded archive and every internal manifest entry verified. It includes the patch, compiler logs, case inputs, raw UCI and stderr for the complete comparison, stop-budget controls and the two rendered cards.

Build two checkouts at the [pinned upstream commit](https://github.com/official-stockfish/Stockfish/commit/68e1e9b3811e16cad014b590d7443b9063b3eb52), apply `patches/stockfish16/R23-root-producer.patch` to one, and run `make build ARCH=x86-64` in each `src`. Match the [engine-build receipt](../receipts/C3X_030_R23_NATIVE_BUILD_20261117.json). Run `harness/c3x_030_r23_native_replay.py CLEAN TRACED NNUE EVIDENCE/cases.json NEW_OUTPUT`. For the bracket compare, run `harness/c3x_030_r23_stop_counterfactual.py EVIDENCE/cases.json EVIDENCE/suite.json --clean CLEAN --trace TRACED --net NNUE --freeze EVIDENCE/stop-freeze.json --output NEW_OUTPUT`.

## Next evidence gates

1. **Whole-engine transport.** Freeze fresh game histories, keep the full legal root list, and reproduce the producer join and the counterfactual forecast. Add a time-based and then a parallel regime only with dedicated non-interference checks.
2. **Mechanistic semantics.** Connect a specific TT, pruning or evaluator intervention to the recorded producer under the actual NNUE engine. Predeclare a targeted event and sham control and preserve legality, candidate set and node budget. Record a failure to change the choice as such.
3. **Chess meaning and use.** Require a legal explanatory claim that predicts at least one new opposing defense, including one that refutes it, and check that prediction independently. A causal claim about a neural feature requires an additional feature- or value-specific comparison. Human comprehension still needs testing on an unseen defense.
