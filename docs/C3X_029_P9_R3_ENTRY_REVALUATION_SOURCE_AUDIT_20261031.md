# C3X 0.29-P9-R3 — Entry versus Revaluation: Source-Evidence Audit

2026-10-31. Archived sources and Drive primary-paper sections reviewed. No fresh Stockfish execution.

## Primary literature verified in Google Drive
- Knuth & Moore (1975), An Analysis of Alpha-Beta Pruning. Original PDF: https://drive.google.com/file/d/118TK7JM2aeQpgl5TsACOSjIoQkuo_YL5/view . Successor ordering and Fig. 4 show search effort need not monotonically improve with a naive perfect-ordering intuition.
- Marsland (1986), A Review of Game-Tree Pruning. Original PDF: https://drive.google.com/file/d/1c9-iqvrTW_6JZqHM6VUtSvCYRuM-E_fZ/view . Iterative deepening reorders root moves; aspiration and PVS may cause re-search. Do not attribute root-leader variation to TT alone.
- Avin, Shpitser & Pearl (2005), Identifiability of Path-Specific Effects. Original PDF: https://drive.google.com/file/d/1itH3x0Agp5wFwHuOpnc9C5ANuyfmIDtr/view . Traces do not establish a natural path-specific causal effect without identification assumptions.

## Two operational hypotheses
A legal root candidate is not newly made legal by a TT reader intervention.
H-N: in a specified depth and aspiration attempt, the candidate was not processed/completed under control, but is processed under treatment.
H-V: the candidate is processed under both, but value/bound, comparison, search-order, or root-update behavior changes.
These mechanisms can coexist at different depths. Presence or absence in incomplete logs cannot determine non-entry.

## Case facts, development only
TWIC4/F natural c2c8 -> FIRST c2d1, leader divergences at depths 9,10,12.
TWIC10/O natural f8f7 -> FIRST f4g3, leader divergences at 6,8,10,11,12.
Four third-move role outcomes correspond to two games, not four independent positions. Original aggregate Stage B receipt does not establish a per-candidate parent-to-root causal chain.

## Evidence admission
Match full chess history/FEN6, exact engine build, root iteration, aspiration attempt, candidate move, node/parent and call identity, actual search entry/completion, TT writer/reader/bound score, signed parent consumption, SEE gate, root update, and final selected move.
Reject mechanism inference when instrumentation perturbs original bestmove/nodes. A censored or absent trace => UNKNOWN.
Controls: TWIC3,12,13,14 source-order disagreement with no final flip.
Prior-art and scientific novelty verdict: developmental hypothesis refinement only; no fresh causal verification, cohort generalization, or new theorem.

Source native verdict: https://github.com/WhoSia/C3X/blob/main/c3x/receipts/c3x-022-P2-TWIC-puzzle32-stageB-literal-UCI-falsification-and-depth-20261010.json
