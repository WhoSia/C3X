# C3X 0.29-P9 — Third-Candidate Emergence, Root-Leader Nonidentifiability & Source-Path Research Contract

2026-10-31. Retrospective archival calculations and a finite mathematical construction only. NO fresh Stockfish run, independent raw-artifact replay, or prospective validation.

## Source authority
- Preintervention registry: c3x/forecasts/c3x-022-P2-TWIC-puzzle32-exact-UCI-preregistered-stageA-20261010.json (preseal commit 1abc7c82f753c3d7c3c540ee3426dfb790e26d22).
- Native receipt: c3x/receipts/c3x-022-P2-TWIC-puzzle32-stageB-literal-UCI-falsification-and-depth-20261010.json (raw member SHA f8c9210cfb9f158d038e70045a1839c3ecebb487781dbc59ce9615b2491a1899).
- Chess/depth audit: c3x/ontology/c3x-022-P2-exact-bestmove-cross-ecology-falsification-and-depth-chess-forensics.md.
- Earlier reproduction contract: tools/c3x_029_p8_archived_candidate_support_reanalysis.py.

## Result A — asymmetric third-candidate outcomes
| Game | Source order | Untreated | TT-FIRST | Class | Divergent root-leader depths |
|---|---|---|---|---|---|
| 4 | O | b5c3 | c2c8 | other baseline | 11,12 |
| 4 | F | c2c8 | c2d1 | third | 9,10,12 |
| 10 | O | f8f7 | f4g3 | third | 6,8,10,11,12 |
| 10 | F | a8e8 | f8f7 | other baseline | 6,7,8,10,12 |

These post-outcome selected development cases falsify a symmetric unconditional opposite-order restoration rule, but do not identify a unique native gate.

## Result B — nonmonotone leader divergence
Game4/F differs at 9,10,12 but not 11. Game10/O differs at 6,8,10,11,12 but not 7,9. Game10/F differs at 6,7,8,10,12 but not 9,11. Game7/F differs at depth 12 only. Therefore first divergent leader is not a continuous source-exact mediator path.

## Proposition — Root-leader-only nonidentifiability
For a finite root candidate set M of size at least 2 and observed leaders L_d∈M, define model A with score_A(d,m)=1 when m=L_d and 0 otherwise; model B with score_B(d,m)=0 for every m, breaking ties with L_d first at each depth. The two models produce the same entire observed leader sequence while their latent selection mechanisms differ. Consequently root-leader observations alone do not identify strict-score selection versus tie priority. This is a constructed observation-interface theorem, NOT an assertion about the actual Stockfish tie policy, score semantics, or natural TT→SEE mediation.

## Next falsifiable experimental gate
1. Treat TWIC games 4 and 10 as retrospective development witnesses, and 3,12,13,14 as baseline-disagreement/no-flip controls.
2. Preseal candidate-survival events keyed by game history, root UCI, iteration, root call, node/parent identity, writer/reader, signed return score, bound, alpha-beta window, parent consumption, aspiration retry, and root leader update.
3. Predeclare competing hypotheses: value/bound crossing, move-order/tie, TT propagation, aspiration, SEE, and root candidate entry/exit; test instrumentation noninterference.
4. For new source-disjoint PGNs, preregister both binary flip and exact UCI across ALL legal candidates (or abstain), reporting clusters by chess game rather than treating nested O/F and STRICT/BROAD cells as independent.
5. Chess-legal explanations of c2d1 and f4g3 must be separately verified and not confused with engine-internal causes.

## Claim ledger
PASS (archival analysis): source-order asymmetry, nonmonotone leader-divergence patterns, elementary nonidentifiability construction.
HOLD: independent raw SHA roundtrip, node-level causal chain, fresh native execution, independent-cohort transport, human comprehension gain.
No historical failed hypothesis is retroactively promoted.