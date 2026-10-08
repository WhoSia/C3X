# C3X 0.13 P5-B - Cross-Budget Prediction Precommit

Status: DEVELOPMENT_ONLY; no chess mechanism or human outcome authority.

Source: P5-A's already frozen 16 September broadcast groups. Retain 14 valid ply-32 boards and both source HOLDs, never replace. Game [%eval] metadata and results are excluded from engine outcome measurement.

Eligibility: cold 10k nodes per legal root, top eight, two cold 30k exact-cp repeats per root, contextual 80k bestmove; select the smallest-gap pair within 50cp containing contextual bestmove. No after-outcome pair rescue.

Prospective feature predictions from existing chess rule snapshots AFTER each candidate move, all in initial mover perspective:
- CENTER: higher own center occupancy predicts preferred move.
- ISOLATION: fewer own isolated pawns predicts preferred move.
- PASSED: more own passed pawns predicts preferred move.

A zero difference is UNTESTABLE, not a successful prediction. Freeze features before new depth-12 outcomes. Test with two independent Stockfish16 depth-12 processes and two-root MultiPV. Reject unequal depth, mate, repeat inconsistency and missing pair. Any concept requires >=4 distinct broadcast groups, including >=2 observations for each signed feature-difference class, even to claim *developmental predictive transfer*. Descriptive prediction is never an intervention-based cause. Same engine, same provider, and no human outcome; no causal certificates.

Fail closed on source SHA/selection drift or chess legality errors. Preserve ALL negative results and source denominators.