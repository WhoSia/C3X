# C3X 0.13 P3 — Historical Cross-Engine Preference Contrast Diagnostic

**PRECOMMIT (before new Stockfish P16-position outcomes); development only.**

Frozen input: GitHub `c3x/certificates/g95-p16-local-minimal-full-bridge.json` from the independently archived **Ethereal** P16 run. Pair A `d6d5` (d5) versus pair B `e8g8` (O-O), worlds B0/TARGET/SHAM (SUBSET equals SHAM exactly). Reuse exact FEN; no source or pair change after outcomes.

New engine: installed distribution Stockfish 16 on a read-only Ubuntu CI runner; record binary SHA and UCI identity. Native legal PGN replay via pinned chess library. Per world perform **two independent engine processes**, each with complete `depth=12`, MultiPV=2, restricted root moves A and B, Threads=1, Hash=16. Convert score to original side-to-move perspective (BLACK); exclude mate and incomplete/mismatched-depth pair data.

Descriptive outputs: sign and magnitude of A-minus-B cp at B0,TARGET,SHAM; repeat reliability; rank ordering. Do not compare centipawn scales or equal-nodes budgets across Stockfish and Ethereal as if calibrated. Require pair margins within 50cp in every world as a *descriptive diagnostic* only. The original P16 Ethereal exact-search intervention is not available for native rerun; therefore **cross-engine causal transfer NOT TESTED**.

Adverse interpretations to retain: zero or opposite ranking, margin loss, edited-world instability, or no engine-level correspondence. Any such outcome narrows the old mechanism's reach and is not resolved by selecting a different move pair after inspecting results. The historical same-sham duplicate never counts as independent replication.

Authority: `REAL_SECOND_ENGINE_DESCRIPTIVE_DIAGNOSTIC_ONLY`. No human participant outcome, prospective novel source, semantic concept as partition, or causal mechanism transfer.