# C3X 0.13 P6-T — Matched-Ply Pawn Status Trajectories and Co-Activation Court

Status: OUTCOME-BLIND DEVELOPMENT EXTENSION AFTER P5 SUPPORT FAILURE; no confirmatory chess strategy/causality.

Use the exact P5-A 16 previously frozen September 2026 Lichess broadcast groups from c3x_013_p5_source_partition.extract. Do not select new games. Legally replay complete game mainlines (not just the frozen ply32), retaining existing Chess960/PGN parser HOLD, and the short game's valid early plies without falsely treating unobserved later plies as zero. Opening a new ply region AFTER learning that P5 at ply32 has no passed-pawn positives is exploratory only.

For each VALID game, report separately after ply 16,32,48,64,80,100: eligible length denominator; own-side and any-side passed-pawn prevalence, isolation count and occurrence of both colors having passed pawns. Games in the same competition may not be independent, and snapshots within the same game are repeated measures, not independent trials.

Formal invariance test for every strictly legal nonpromoting, noncapturing PAWN PUSH:
- own-color isolated-pawn count is unchanged (file occupancy support invariant);
- own-color passed-pawn count never decreases, and can increase at most one (only moving own pawn changes its status when enemy pawns fixed);
- opposite-color passed-pawn count never decreases, but it CAN increase because the moving pawn crosses an enemy pawn's forward-blocking rank. Simultaneous passed-pawn activation is permitted and must be counted. This is not a chess strategy advantage theorem.
Promotion, captures and en passant are separate transition classes and are NOT covered by this lemma.
- Track chess-rule-checked count of all eligible quiet pawn pushes and any invariant violations as an execution failure; zero violations only verifies consistency of these predicates with the law.
- Report co-activation counts, not just one-sided passed pawn successes.
- Full-game result and PGN [%eval] must NOT enter feature trajectories or update experiment selection.

No engine outcome in this P6-T court, no causal concept, no cross-engine/explanatory human authority.