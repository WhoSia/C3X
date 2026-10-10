# C3X 0.21-P2 — Chess Decision Primitives & Search-State Causal Mediation: Microstructural Board Transitions, Source-Exact TT Value-Use Interventions, Probe-Only Lineage Rewriting, Multi-Depth Candidate Rivalry & Bounded Legal-Move Counterfactuals

**Status: PRE-OUTCOME P2 NATIVE FACTORIAL CONTRACT — 2026-10-10, C3X 0.21 ACTIVE.**

## Research mission

Explain *which legal move Stockfish chooses* via two different causal intervention levels: (i) same-board source-exact synthetic TT reader-block interventions in search history, (ii) **legal** chess candidate/response-space interventions using UCI `searchmoves`, never board corruption. Their outcomes are compared with 635 *already engine-blind-frozen* legal root-move chess decision primitives. No “Atomic Chess” variant: all positions are ordinary Standard Chess.

### Historical recovery (0.11–0.20)

- C3X before 0.15: plan-affordance trajectories, pairwise near-equal move contrasts, anonymous candidate `CPP_224`, prospectively rejected independent universal rules; never infer robust factors from training examples.
- C3X 0.13–0.15: native Stockfish16 **SEE pinned-piece recapture**, target root pinned identity and attack rays; **WeakQueen own/opponent blocker penalty** interventions, qsearch. S29 root-conditioned SEE intervention 13/40 categorical flips; S28 17/64 games (16/63 unique FEN), with nonmonotone broad-vs-targeted effects. Pin geometry label → reaction class extrapolation failed.
- C3X 0.16–0.17: independent legal chess tactic validation and puzzle defenses; multiple candidate moves, response enumeration; distinct board truth vs engine computed search vs intervention result.
- C3X 0.18–0.19: exact full64 TT physical writer, epoch and reader lineage; distinguish probe from native `eval=ttValue` assignment and actual TT cutoff. Frozen F19.5 FAIL and K4 first-return 0/4 FAIL remain.
- C3X 0.20: one adaptive game3 second child-return edit restored original bestmove; six-point alpha=−190 ladder 6/6 correctly classified, sharp −190↔−189 final-choice switch. Not universal.
- C3X 0.21-P1 (new disjoint March16): 635 source-only legal action primitives frozen SHA `c14711c0e31bde26c2c7fc6e77f1f2fdf0ac70180a517b91f71845f1fd78ed3f`; 16 games × 2 roles = 32, eligible actual first reader blocks 31, full categorical bestmove flips 2 (#4 BROAD, #9 STRICT), native SHA `5ee15c3ec48be0042a9bb0ae7566808737f56e7568c2b29d43f00ae64afcb259`.
- P1-R1 exact second-consumer watch: 31/31 second physical probes, 30/31 native value-as-eval, 2/31 cutoff; in #4 BROAD the next evaluation was **genuinely used**, in #9 STRICT physical TT was **probed but no selected use** (SHA `e9765a9d9c2254866cba80a968ed4f10013d7ee0b2ff93f41c4d203daed98a8c`). Do not equate a raw probe with a consumed value.

## P2-A fixed full-factorial source experiment (same board; **31 eligible × 4 arms**)

Immutable March16 / P1 source-world and physical writer pair. 32 predefined cells STRICT/BROAD, full denominator retained, including game7 STRICT NO_ELIGIBLE.

- ZERO: V TT mode with no selected root reader-block filter (physical target present); compare complete UCI to original F.
- FIRST: block physical full64 TT reader at the **first** frozen source call only; compare complete UCI to P1 original V.
- SECOND: block the **second** frozen root source call only; call may not contact due to path change; report observed **native** reader_block and do not credit nominal intervention.
- BOTH: block both frozen source calls; may fail to contact second when first block changes path. Record first-vs-second delivered dose as two bits (00/10/01/11).
- Every arm independent cold twice, same frozen source chess board/clock, Stockfish16 `68e1e9b3811e16cad014b590d7443b9063b52`, threads1/hash16/NNUE-off/depth12. Explicit first and second root call/epoch/slot/key64 physical identity required, no source retargeting.
- Principal comparison: **categorical bestmove**, actual contact, and arm-level causal interaction in #4 BROAD and #9 STRICT; all other 29 eligible cells are unchanged-selection negative comparison. A positive 2×2 nonadditivity at categorical move choice is evidence of *context-dependent search decision dynamics*, not a numerical interaction coefficient.
- Second-call TT watcher on the original FIRST arm is the independent already frozen R1 probe/use evidence; do not infer SECOND activation just from watcher presence. Source-aligned first observed root split and depthwise root leader from actual traces are secondaries.
- **Prior-prediction gate:** ZERO must equal frozen F full UCI, FIRST equal prior P1 V full UCI. Cold mismatch, physical target drift, unaccounted reader blocks, source log censorship → TECHNICAL_HOLD. Failures retained with case ID; all 32 roles remain in output.

## P2-B chess legal-move counterfactual (original same-board position; constrained root admissibility)

Previously P1 flipped cases fixed **before new P2 outcomes**:
- game4 BROAD: original F root legal move `h8h4` (rook captures h4 pawn) vs V `g5h4` (pawn captures the *same* h4 pawn).
- game9 STRICT: F `a6b7` (queen reposition) vs V `f6h5` (knight reposition).
- On **the unchanged March source position and clocks**, run unmodified Stockfish16 `searchmoves` contexts: (i) both moves only, (ii) F move only, (iii) V move only. Cold twice. Do not silently carry TT memory across engine processes; fresh process every arm. UCI score/nodes/PV and final move are outputs. These `searchmoves` runs alter root search admissibility, not the natural chess board; their numeric scores must not be falsely equated to unconstrained F/V original scores.
- Independently match both legal actions to pre-frozen `Xi(s,a)` from **all 635 moves**: square occupancy delta, attack-edge generation/loss, attackers/defenders per target, pinned geometry, reply legal set SHA/count, captures/checks and recaptures. Enumerate actual legal reply moves; do not relabel a feature contrast as a unique Stockfish motive.
- Hypothesis H_B: For #4, both constrained root options capture the same original white pawn on h4 and have equal immediate opponent legal move counts (29/29); any Stockfish preference is attributable to search/position details *beyond reply-count or target-square-only summaries*. For #9, F and V have different piece/square transitions and 40/41 immediate replies. These chess facts are frozen and not chosen from P2 score.
- Threat/defense hierarchy: legality, move-specific attack/control, forcing replies, quiescence/SEE recapture, TT consumer, alpha-window/candidate order, final bestmove. Avoid conflating “geometric attacked square” with legal exchange or “same final cp” with same chosen move.

## Expected scientifically valuable outcomes

If FIRST affects choice while SECOND alone does not, source first-reader path is a bounded causal switch; if SECOND or BOTH reverses the chosen move independently, later state is an additional mechanism. For #9 probe-only R1, outcome of SECOND is especially adversarial. A no-contact SECOND is NOT a negative causal intervention. The legal searchmoves result can establish how two legal move alternatives fare under controlled restriction, not why baseline V preferred one without a deeper source lineage.

The *next* experiment can test original 0.15 root-specific SEE/pin and WeakQueen operations on exact March parent positions, but **those code branches and exact source eligible events must be anchored before selecting them**, with no P2-A results used to choose target operation. All 0.20 alpha-mediation failures and old universal motif claims remain historical.

## Engineering

main-only WhoSia commits; preserve source SHA and historical CI; no Actions bot writes; minimal changes to shared harness with default behavior byte-identical; source test and sham before one consolidated CI; label run failure vs scientific FAIL. No invented chess concept law, no one-cell denominator disguised as a universal result.
