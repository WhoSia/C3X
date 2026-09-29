# C3X 0.7.0-G9.5-P15 — Chess-Structure → Search Pair Mediation

## 1. Return-to-origin question

P14 established a replicated scientific object that is recognizably chess-native: a prospectively frozen unordered legal-move pair whose preference edge can be reversed by removing an exact semantic search event.

P15 asks the next question required by the original C3X explanandum:

> **What minimal chess-board structural difference makes the search event causally matter for one near-equal move rather than the other?**

The endpoint is no longer a finer search taxonomy. It is a bridge from a controlled board difference to a controlled search difference to a concrete legal-move preference.

## 2. Separate science from the commentator product

C3X now has two binding tracks. The scientific mainline earns novel authority for marginal move preference through prospective interventions. The explanation-implementation track builds the eventual PGN → commentary system and may borrow external chess/XAI/NLP methods.

P15 belongs only to the science track. It should eventually provide evidence objects that the commentary system can consume, but natural-language usefulness is not a P15 success criterion.

See `docs/C3X_TWO_TRACK_CONSTITUTION.md`.

## 3. Fresh evidence

The official Lichess monthly broadcast index was checked on 2026-09-29. Completed monthly broadcast containers were available through August 2026, not September.

P15 therefore reuses July/August 2026 bytes only as provider containers. It scans the first 4,096 games per source and excludes every recoverable P1–P14 candidate/decoy hash. Sixteen fresh positions per source are frozen before engine outcomes: 32 positions × three engines = 96 engine worlds.

P14 witnesses such as Bb7/Be7, a6/bxa5, Qa4+/Bb4 and Rae8/Rfe8 are development donors only. They cannot vote in P15.

## 4. Pair qualification remains outcome-separated

P15 retains the P14 unordered-pair qualification logic:

1. enumerate every legal root move;
2. cold 10k-node restricted probe for every legal move;
3. top eight by deterministic engine-relative score;
4. two cold 30k-node confirmations per shortlisted move;
5. stable only when both non-mate cp scores agree exactly;
6. contextual 80k-node bestmove under frozen history;
7. support a pair only when both moves are stable, the absolute gap is ≤50 cp, and contextual bestmove lies in the pair;
8. freeze one cross-engine pair per position by support count → median gap → max gap → lexical pair ID.

Orientation is not a selection bonus.

## 5. Board intervention grammar

The board intervention is deliberately smaller than a human chess concept.

P15 relocates exactly one non-king, non-pawn piece to an empty square reachable by that piece's occupancy-aware move geometry. The relocated piece cannot be the moving piece of either frozen candidate, and neither its source nor destination may be any candidate source/destination square.

The resulting counterfactual must:
- remain a valid nonterminal chess state;
- keep the same side to move;
- preserve material exactly;
- preserve legality of both frozen candidate moves;
- remain out of check;
- change the legal-root-move count by at most six;
- change the relocated piece's attack set on at most ten squares.

P15 does **not** assert that every edited board occurred in a natural game history. The edit is a rule-valid structural probe.

## 6. Target vs sham

For each frozen pair, define the relocated piece's pair-local relation vector:

`[attacks A.from, attacks A.to, attacks B.from, attacks B.to]`.

A **TARGET** edit changes this relation vector asymmetrically between the two candidates.

A **SHAM** edit preserves the relation vector.

A TARGET and SHAM can form a matched edit pair only when they relocate the same piece by the same Chebyshev distance. This keeps intervention footprint close while changing the pair-local structural relation only in the TARGET arm.

Up to eight mechanically ranked target/sham candidate pairs are generated without engine intervention outcomes.

## 7. Marginality preservation before search outcomes

The same target/sham edit pair is admitted only if at least two engines active on the original pair independently preserve the pair on both edited boards:

- both moves legal;
- two cold 24k-node restricted scores per move;
- exact non-mate repeatability;
- absolute pair gap ≤50 cp on TARGET and SHAM.

The selected edit pair maximizes supporting engines, then minimizes edited gaps and board collateral, then uses lexical identifiers.

Neither edited-board native bestmove nor any exact-event removal outcome may be consulted for this freeze.

## 8. The search mediator

P15 keeps the P14 exact semantic skeleton unchanged:

- MAIN;
- MOVE_ORDER_SEED;
- ply 1;
- depth 5–8;
- repeated full key;
- same most-recent TT move;
- LOWER or UPPER bound.

The semantic anchor is the move that was **BASELINE_DISPREFERRED on the original B0 board** for that engine.

Private event addresses are reconstructed separately on original, TARGET and SHAM boards. Address identity across boards or engines is neither required nor claimed. For each bound and board, the lexically first eligible event mapped to the anchor candidate is selected from that board's native trace, then removed with the inherited T_ONLY intervention.

## 9. Three-board factorial

Each admitted engine world exposes:

`B0_ORIGINAL × {NATIVE, T_ONLY}`

`B1_TARGET   × {NATIVE, T_ONLY}`

`BS_SHAM     × {NATIVE, T_ONLY}`

The B0↔B1 comparison is the primary board × search factorial. BS is a footprint-matched negative control.

Per board/bound, search susceptibility is classified as:
- NO_EVENT;
- EVENT_NULL;
- EVENT_PAIR_REVERSAL;
- EVENT_THIRD_ESCAPE.

## 10. Operational mediation, not Pearl natural effects

P15 does not identify natural direct or indirect effects and does not invoke unobserved cross-world mediator counterfactuals.

Its strongest class, **FULL_BRIDGE**, is an observed factorial collapse pattern:

1. B0-native and TARGET-native choose opposite members of the same frozen pair;
2. at least one common bound has an eligible fired semantic event on both boards;
3. removing those local events makes B0 and TARGET choose the same frozen pair member;
4. the matched SHAM does not reproduce the same collapse pattern;
5. no third-move escape is allowed in the bridge-defining cells.

This is an operational mechanistic bridge:
`board relation edit → search susceptibility interaction → pair-preference difference`.

Lesser classes preserve useful negative information:
- SUSCEPTIBILITY_MODULATION;
- DIRECT_BOARD_ONLY;
- SEARCH_ONLY_NO_BOARD_LINK;
- NULL.

## 11. Replication

The primary replicated bridge signature is:

`target_relation_delta_role | bound | FULL_BRIDGE`

and requires at least:
- three witnesses;
- two engines;
- two positions;
- both source months.

If FULL_BRIDGE does not replicate, a weaker susceptibility-modulation signature can replicate only with four witnesses spanning two engines, two positions and both sources.

No signature may be refit after outcomes.

## 12. Mechanism Bridge Cards

Every confirmed witness should materialize a compact chess-native card containing:
- original, TARGET and SHAM FENs;
- frozen pair in UCI and SAN;
- exact board edits;
- pair-local relation-vector delta;
- collateral footprint;
- per-engine pair gaps;
- native/T_ONLY root decisions;
- susceptibility states by bound;
- observed factorial class;
- explicit claim ceiling.

These cards are the first scientific artifact designed to be consumed later by the PGN explanation implementation.

## 13. Novelty boundary and adjacent literature

Existing chess-XAI work includes neural commentary generation, concept-guided commentary, piece-ablation/SHAP-style position attribution, and board-state interventions in chess-playing language models. Those lines motivate useful implementation and rival tests, but they do not substitute for P15's prospectively frozen **board edit × internal exact-search intervention × near-equal pair preference** factorial.

The implementation track should actively reuse good ideas from that literature. The science track must keep its novelty claim narrower: causal identification of a move-pair preference boundary through linked board and search interventions.

## 14. Authority ceiling

A P15 PASS can license a statement of the form:

> Under these declared engines and budgets, this prospectively frozen low-collateral board relation edit changed whether a declared exact search event controlled the preference edge between these two near-equal legal moves, with the same operational bridge pattern replicated under the frozen rule.

It cannot yet license:
- “the engine understands space/initiative/prophylaxis”;
- human strategic intent;
- objective chess truth;
- a universal chess law;
- native search-address identity across engines;
- or a finished natural-language explanation.

## 15. Stop rule

Run the frozen fresh campaign once. If structural support is too sparse or the bridge fails, close that ceiling. Do not tune the board relation grammar, collateral budget, pair-gap threshold, event class, or bridge definition after outcomes.
