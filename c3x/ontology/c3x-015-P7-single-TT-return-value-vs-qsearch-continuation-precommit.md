# C3X 0.15 P7 — Single-TT Return Versus Fail-Low Value: Qsearch Mechanism Separation (PRE-OUTCOME FOR P7)

**Date:** 2026-10-09. **Version stays C3X 0.15**. This is a post-P6-outcome targeted mechanism-reconstruction experiment (not blind new-source validation). Only original frozen TWIC R2 source worlds **#2 and #29** are targeted, selected because the first source-frozen exact TT return intervention demonstrated **opposing** root effects. All existing R2, P1 predictions, P2/P6 outcomes and negative conclusions are immutable.

## Scientific problem
Both native P6 cases were selected from a full64-key, last-writer-verified QSEARCH_TERMINAL return, stored BOUND_UPPER, depth 0, original reader (alpha,beta)=(130,131) at ply 4. Both cases showed a change in SEE-response identity when *one* early TT return was blocked. P6 does not tell us whether the influence arises from the content of the TT-return value or the search continuation that would have been skipped by the return.

## P7 distinct executable arms (per source world per SEE status)
- **I — IDENTITY_RETURN:** allow exact eligible TT return with original TT value. Must exactly reproduce P6's ALLOW native final output in BOTH SEE OFF and ON.
- **V — RETURN_ALPHA_AT_MATCH:** at exactly one P6S0-preselected full64-key TT edge (same physical slot, writer seq/class/bound/depth, reader alpha/beta, ply and kind), continue taking the early return but deliver `alpha` rather than stored TT-derived value. *No qsearch continuation* is enabled by this treatment. For a fail-low UPPER bound returned under the one-point window (alpha, alpha+1), alpha is a boundary-valued, still fail-low-class return. V tests practical sensitivity to the **reported stored score**, not validity of an actual perfect chess upper bound.
- **B — BLOCK_ONE_RETURN:** reuse the unchanged P6S1 exact one-return bypass; qsearch continues its ordinary code below the original shortcut. Must reproduce the exact P6 previous blocked arms.

Each of the 2 cases receives 2 SEE arms × 3 TT arms × 2 independent cold native processes = **24 native UCI processes** (no new independent chess positions). If the target is not encountered or V has no numerical difference from original TT value, label NON_DELIVERY/NULL_VALUE_DIFFERENCE and retain the cell. No substitution with another later TT read.

## Gates and measurable endpoints
1. Verify P0 source R2 SHA, P2 original SHA, P6S0 targeted key SHA, and P6S1 existing four-cell source result SHA before new P7 data.
2. Original SF16 source commit is `68e1e9b3811e16cad014b590d7443b9063b3eb52`; classical `Use NNUE=false`, depth12, Threads1 Hash16MiB MultiPV1, source chess legality unchanged.
3. I and B are baseline regression: exact UCI `bestmove`, final cp/mate score, nodes, PV identical to prior P6 on all four conditions; cold repeats exact; first eligibility prefix identical.
4. V: log original exact TT value, read alpha/beta, writer bound/depth, and delivered alpha; confirm at most one value substitution and the exact P6S0 target is matched; forbid changes outside matched site. Score changes are a separate intervention, not evidence of TT natural indirect mediation.
5. Three categorical root outcomes per SEE arm produce two distinguishable contrasts: score-only sensitivity `Y_{S,V} != Y_{S,I}`; continuation sensitivity `Y_{S,B} != Y_{S,I}`; and score-vs-continuation consistency `Y_{S,V} == Y_{S,B}`. Report all, even when value-only manipulation is null.
6. Evaluate whether interventions shift the SEE-response identity in the two original opposite cases, using the categorical predicate `1[Y_{ON,*} != Y_{OFF,*}]`. Do not use numeric subtraction on UCI moves.
7. This experiment does **not** isolate the full qsearch alpha-beta causal frontier nor prove that a particular TT writer was necessary in all possible engine executions; a future explicit qsearch continuation-trace and alternative bound mediation court would be needed.

## Source architecture
Stockfish C++ modifies the returned score at the **original matched TT early-return instruction**; not move generator, TT entry storage, or evaluation. Python-chess replays game to root and orchestrates 24 actual native processes. Rust independently compares original P6 with P7 reported effects; Go enforces explanation claim tiers if a later court justifies promotion. No bot authored GitHub commits; read-only CI only.

**Entry judgment:** P7_QSEARCH_SCORE_VS_SEARCH_CONTINUATION_PRECOMMITTED / CASES_2_AND_29_POST_P6_DISCLOSURE / NO_NATIVE_P7_RESULT_YET / C3X_0.16_NOT_OPEN.
