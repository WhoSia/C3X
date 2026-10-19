# C3X 0.27 — Independent Stockfish16 SEE Boolean Replay and Factorial TT×SEE Source Reconciliation
Date: 2026-10-20. Status: SOURCE-TARGET BOOLEAN REPLAY PASS (TWO CASES); ALGORITHM-WIDE EQUIVALENCE HOLD; NATURAL CAUSAL MEDIATION HOLD.

## Original source grounding
Stockfish16 fixed source git 68e1e9b3811e16cad014b590d7443b9063b3eb52 `src/position.cpp` defines `Position::see_ge(Move, Bitboard&, Value)` and wrapper `see_ge(Move, Value)`. It compares early target piece value minus threshold, origin value and dynamic attacker exchanges, with pseudo-legal attack/x-ray propagation and pinned-piece restrictions. Fixed MG piece values in `src/types.h`: pawn 126, knight 781, bishop 825, rook 1276, queen 2538; arbitrary P1/N3/B3/R5/Q9 exchange units from earlier exploratory audit are not native SEE units.

Original C3X 0.23 preactuator Git-sealed forecast `c3x/forecasts/c3x-023-P1-R2-T2-exact-native-SEE-targets-before-first-actuator-20261011.json` records for BOTH selected source events `t1_occupied_present=0` and `t1_occupied_out=0`. Thus precisely these two source calls are the default wrapper, not externally supplied occupied bitboards. The independent C3X 0.27 Python replay computes hypothetical occupied after root capture internally.

## Independent CI
Original passive Stockfish16 SEE FEN replay CI with SHA-frozen historical source-only, stage A, preactuator exact targets and original T3 harness. Independent Python reimplementation `tools/c3x_027_independent_see_algorithm_audit.py`, primary entrypoint `.github/workflows/c3x-027-see-live-fen.yml`, native run https://github.com/WhoSia/C3X/actions/runs/39342739907, main commit a5085ceb4797ded9992a88d73902f36ec78de540, SUCCESS.

Actual log: `C3X027_SOURCE_SEE_REPLAY [('f6e4', 0, False)×4, ('d1e2', 1, True)×4]` and `C3X027_SOURCE_SEE_REPLAY_PASS 8`. Each source event matched all four cold SHAM observations. Case May game11 qsearch_prune f6e4 threshold -95cp, native false and independent false; game2 quiet_prune d1e2 threshold -43cp native true and independent true. The checker follows source MG values, least valuable attacker and occupied x-ray updates but uses python-chess pin helpers, NOT a formally proven bitwise port of all Stockfish internals. The two cases can both be short-circuited by early bounds, so this PASS is a **narrow test** and not a validated replay of long SEE swap sequences or pinned occupancies. Do not claim general source equivalence; adversarial targeted SEE tests still required.

## Factorial intervention source history, not newly executed
Pre-existing real native 0.23 T3 receipt `c3x/receipts/c3x-023-P1-R2-T3-native-source-exact-SEE-TT-two-by-two-operator-interaction-20261011.json`:
- Game11 qsearch_prune:
  - TT0 SEE_SHAM c7d6, 64424 nodes, score -95; TT1 SEE_SHAM d8b8, 68114 nodes, -104.
  - TT0 SEE_FLIP c7d6, 64426 nodes, -95; TT1 SEE_FLIP d8b8, 68116 nodes, -104.
  - TT intervention changes final root, SEE bool do-flip adds 2 nodes but no extra terminal difference.
- Game2 quiet_prune:
  - TT0 SEE_SHAM e1g1, 20062 nodes, -8; TT1 SEE_SHAM e1g1, 41685 nodes, -8.
  - TT0 SEE_FLIP e1g1, 46783 nodes, +1; TT1 SEE_FLIP b1b4, 47563 nodes, -4.
  - Neither individual perturbation changes categorical final bestmove but joint interventions change root to b1b4: local, factorial nonadditivity. The SEE flip is an artificial intervention, not a naturally changed SEE Boolean under fixed arguments.
Both cases are prior, post-exposure selected development data. Even where a root changes, there is no certified natural TT→SEE mechanism. Source call activation, input or consumer branch may differ under TT intervention; a causal mediation claim needs matched source traces and fresh prospective cases.

## Manuscript Results section (bounded)
The exact Stockfish exchange tests had survived in the original pre-intervention target manifest. That manifest also resolves an ambiguity left by the chess replay: neither test passed an external occupied bitboard; each used the ordinary two-argument SEE wrapper. Reading the pinned Stockfish16 source, we recovered its actual piece values and threshold-update rules, rather than comparing its Boolean with our earlier approximate pawn-unit exchange score. A separate Python implementation agreed with the native Boolean for all eight repeated observations across the two chosen source events. This agreement is local; it does not validate the port on complex exchange or pinned-piece positions.

The existing source intervention results show why local correctness is not enough for a model-level explanation. In the first development position, suppressing the physical TT source reader changed the chosen root move, while the targeted SEE return flip did not add a further root-choice change. In the second position, the root move survived either intervention in isolation but changed only when both operators were altered together. Such nonadditivity is real evidence of interaction between controlled search interventions. It is not evidence that TT naturally changed the output of `see_ge` at identical arguments. A faithful explanation must distinguish interventions on the SEE Boolean from changes in whether or how SEE is called.

## Next experiment and gates
1. Add exhaustive comparative testing for SEE algorithm independent implementation against native Stockfish `see_ge` on stratified random chess FENs and forced exchange/pin/x-ray edge cases, including `occupied` supplied paths, with reference native raw Boolean and original MG values. The current two cases may be resolved at source's early thresholds without entering attack loop, hence missing test coverage.
2. For TT→SEE activation, reuse original T3 factorial harness, but compare exact per-arm contact counts / native event identity, return consumers, and root choice. Use genuinely independent, preregistered newly sampled game cohort; old 2-case results are exploratory.
3. Preserve 0.23 prior negative SEE actuation results, C3X 0.19 K4 FAIL, and 0.25 M6 1/64 as separate facts. Human transfer and innovation claims remain HOLD.
