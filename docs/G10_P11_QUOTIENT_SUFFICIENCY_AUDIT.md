# C3X G10-P11 — Post-result quotient sufficiency adversarial audit

Status: **DEMOTION-ONLY**. This audit was defined after the primary exhaustive conjugacy result and therefore cannot strengthen the primary verdict. It may only narrow or reject the pooled common-quotient interpretation.

## Trigger
The primary P11 exhaustive search found:
- no exact semantic conjugacy for any engine pair;
- no exact S4 conjugacy for any engine pair;
- one pooled nontrivial exact common-support quotient: `{00,11}|{01,10}`.

## Audit A — source-split recurrence
Repeat the full 15-partition exact common-support search independently on TWIC 1657 and TWIC 1658.

A pooled quotient is **source-robust** only if the same partition is an exact common-support quotient in each source separately.

Failure cannot be repaired by pooling.

## Audit B — fiber-consistency analogue
The empirical board-edit operators are not assumed to be temporal Markov chains. Therefore classical Markov lumpability is used only as a structural analogy, not as an authority claim.

For a candidate partition and engine/edit operator, compare states inside each quotient block whenever both source-state rows are observed.

Two levels are tested:
1. **support-fiber consistency**: the set of reachable quotient blocks is identical for all observed states in a block;
2. **probability-fiber consistency**: empirical transition probabilities to quotient blocks are exactly equal.

Untestable fibers caused by missing source-state rows are reported separately and never counted as passes.

## Demotion rule
- If source-split recurrence fails: label the pooled quotient **POOLED_ONLY_SOURCE_FRAGILE**.
- If observed fibers violate support consistency: additionally label **FIBER_INCONSISTENT**.
- Neither failure changes the primary exhaustive-search fact that a pooled exact common-support quotient exists.
- Either failure blocks any P11 transport-law promotion.

## Literature boundary
This audit is inspired by finite-state lumpability/state-aggregation criteria, where a valid quotient requires states in the same block to induce compatible transition behaviour toward quotient blocks. P11 uses a weaker descriptive board-edit operator, so it must not call support aggregation alone “Markov lumpability.”
