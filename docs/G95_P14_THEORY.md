# C3X 0.7.0-G9.5-P14 — Unordered Legal-Move Pair Transport

## 1. Successor question
P13 established nine local exact-event W→R preference-boundary crossings but no frozen W/R-oriented transport signature. One position simultaneously showed Berserk b6→Qc7 and Stockfish 19 Qc7→b6. P14 does not relabel those observations. It prospectively asks whether the unordered legal-move pair itself is a better transport object while direction remains engine-conditional.

The terminal scientific object is therefore a legal chess edge:
`{move A, move B}`,
not a telemetry class and not an engine-independent ranking.

## 2. Prospective quotient
The only quotient introduced by P14 is pair-label permutation: swapping the arbitrary storage labels A and B must not change the scientific verdict. Canonical lexical UCI order is retained for reconstruction, but all transport signatures use only label-swap invariants.

This follows the Research OS rule learned from P13: a newly noticed quotient becomes a successor estimand, never a retroactive rescue. It also follows the MQR pressure that an invariance group earns authority only when its target, probe, interventions, distinctions and reopening path are explicit.

## 3. Fresh evidence
As of 2026-09-29 the official Lichess monthly broadcast index publishes completed data through August 2026, not September. P14 therefore reuses the completed July/August provider bytes as source containers but excludes every recoverable P1-P13 target and decoy hash. It scans a larger 3,072-game prefix and selects twelve new positions per source. P14 evidence is fresh at the position/world level even though the monthly byte containers are shared with P13.

## 4. Engine-level qualification
For every fresh position and engine:
1. enumerate every legal root move;
2. cold-search each move independently for 10k nodes;
3. keep the top eight by deterministic engine-relative score;
4. re-run each shortlisted move twice at 30k nodes;
5. call a move stable only when the two non-mate cp scores agree exactly;
6. separately obtain the 80k shared-search contextual bestmove under the inherited prime/decoy history.

No exact-event intervention has run yet.

## 5. One pair per position, chosen across engines
An engine supports unordered pair {A,B} only if both moves are stable, their absolute isolated gap is ≤50 cp, and that engine's shared contextual bestmove is A or B.

A position admits a pair only with support from at least two engines. If several pairs qualify, selection is frozen by:
1. maximum supporting-engine count;
2. minimum median absolute gap;
3. minimum maximum absolute gap;
4. lexical pair ID.

Whether engines agree or disagree on direction is deliberately not a selection bonus. After pair choice, baseline geometry is classified as CONSENSUS_ORIENTATION or SPLIT_ORIENTATION.

## 6. Exact event and engine-relative relation
P14 preserves the P13/P12 exact skeleton unchanged: MAIN MOVE_ORDER_SEED, ply 1, depth 5–8, repeated full key, same most-recent TT move, LOWER/UPPER.

Private P13 root-child observation maps each event to a frozen pair member. The public target relation is not raw A/B. It is:
- BASELINE_PREFERRED, or
- BASELINE_DISPREFERRED.

That relation survives arbitrary pair-label swapping.

## 7. Orientation-free causal effects
For an active engine world:
- EDGE_REVERSAL: baseline member becomes the other pair member;
- EDGE_PRESERVED: baseline member remains root bestmove;
- EDGE_TO_THIRD_ESCAPE: intervention selects a move outside the pair.

These categories are invariant under A↔B relabeling.

## 8. Same-position cross-engine geometry
For a fixed position and pair, exact native addresses need not match across engines. P14 asks for semantic transport instead.

For one target_relation × bound key, MULTIENGINE_REVERSAL requires at least two engines to exhibit EDGE_REVERSAL. It becomes RECIPROCAL_MULTIENGINE_REVERSAL when those engines started from opposite baseline pair orientations, and CONSENSUS_MULTIENGINE_REVERSAL when they started from the same orientation.

This is stronger than merely observing two unrelated local flips, but weaker than claiming shared native implementation.

## 9. Replication
Event-level orientation-free reversal replication requires at least three witnesses spanning two engines, two positions and both sources for the same:
`position_geometry | target_relation | target_bound | gap_band | EDGE_REVERSAL`.

Reciprocal geometry is separately replicated only if the same semantic transport key yields RECIPROCAL_MULTIENGINE_REVERSAL on at least two positions spanning both sources.

## 10. Authority ceiling
P14 can establish local pair-edge causality, semantic cross-engine transport and, if earned, replicated reciprocal geometry. It cannot establish objective move truth, human strategic intent, cognition, or algorithm identity. Root-child semantic-event exposure is not per-candidate node allocation.

## 11. Stop rule
Run the frozen 24-position / 72-engine-world campaign once. A failed orientation-free transport test is a transport ceiling, not permission to subdivide MOVE_ORDER_SEED after outcomes.
