# C3X 0.21 — Prospective Root-Choice Transmission & Alpha-Gate Generalization Court: Independent March Ecology, Source-Aligned Candidate Promotion, Multi-Depth Decision Forecasts & Competing-Mechanism Falsification

**Status: ACTIVE — user-approved, 2026-10-10.** NOMOS Flowing succession of 0.20. Research goal: *explain which legal chess move Stockfish selects and why TT and search interventions change that selection*.

## Two connected explanatory layers, neither subordinate to the other

**Native engine mechanism:** Stockfish16 full64 transposition key, physical TT writer/reader epochs, actual evaluation substitution versus bound cutoffs, alpha/beta and aspiration retry, rootMove score/averageScore, PV and root order, search extensions/reductions, quiescence, and depth-by-depth candidate survival. Measure actual source effects, not inferred TT cache labels.

**Chess mechanism:** Board-specific tactical and positional causes of candidate superiority: which side threatens what, legal reply availability, exchange consequences and king safety, and whether a tactical fact persists or disappears after one ply. Never accept motif detection alone as a causal explanation of Stockfish final choice.

## Chess microtheory registry (candidate features, not yet validated claims)

1. Pin: absolute-to-king / relative-to-more-valuable-piece / partial directional restriction; pinning piece type, pinned piece value, protected victim, unpin or interposition candidate, whether moving pinned piece is legal.
2. Skewer / x-ray: king-first check skewer versus relative skewer, alignment and blocker removal, recapture defense, whether rear target remains attacked after forced response.
3. Fork / double attack: direct or discovered, attacked valuable targets, defended targets, checking vs nonchecking, counter-fork, zwischenzug.
4. Discovered attack / discovered check / double check: blocking-piece departure, forcing reply set, exchange sequence.
5. Overloading / deflection / decoy: defensive commitments, legal alternatives, defender exchange and re-protection.
6. Removal of defender / interference / clearance / line-opening: material, tempo, and square control.
7. Trapped piece / hanging piece / exchange: legal safe escapes, SEE-inspired net capture risk, pin-constrained recapture, sacrifice compensation.
8. King safety: legal checks, exposed king ray, mating-net geometry, flight squares, back-rank constraints.
9. Pawn microstructure: passed/connected/isolated/doubled/backward, pawn lever, passer blockade, promotion races, outpost support.
10. Mobility and space: legal mobility versus attacked-square occupancy, piece coordination, restriction of key squares and control of open files/diagonals.
11. Zugzwang / opposition / tempo: forcing moves, move order, king-pawn endgame parity, fortress/counterplay.
12. Tactical–positional interactions: pin x-ray that changes a SEE exchange, overloading that turns an apparently defended target into a fork, aspiration-window effect that changes search time spent resolving an otherwise stable motif.

Each microfeature must state legal-move semantics and **coverage**, ambiguity, false positives, game phase, and observable response. Use precise machine-detectable predicates for an initial subset and human-reviewed labels for motifs that require tactical proof. Unknown ≠ absent.

## Layered chess–engine contrast court

For each fixed game in **already engine-free frozen March16** (source JSON SHA-256 `d79e48633be2b683176f1a6d4650aeea1b7584f11c85c2349a5bddda113febee`):
- **P0 source-only:** positions, legal moves, checking moves, pin geometries, direct aligned skewers, attack-defense and pawn geometry. No evaluations, bestmoves, or Stockfish used. Freeze feature JSON SHA, versioned definitions, per-position denominators *before* engine outcomes.
- **P1 native baseline:** replay original F and V FIRST under exactly frozen depth12/Threads1/Hash16/NNUE off with source TT actual reader/cutoff and writer witnesses; record same position / board / clock / initial root order, depth4 and depth12 root choice.
- **P2 source-aligned mediation:** assess candidate scoring, gate crossing and root-order progression; align only on source-coherent move and prehistory. Compare root choice changes with microfeatures *after* freezing features, report no-evidence cases as well.
- **P3 chess counterfactuals:** choose **a priori** bounded legal perturbations of position or move constraints that delete a specific motif (e.g. removal of pin or x-ray) and preserve other major board facts as much as possible. Since this changes chess positions, treat it as a separate board counterfactual from same-position C++ search-state intervention. Validate legality and no king-exposure; independent controls.
- **P4 cross-ecology:** predict distinct game outcomes from a held-out month, and later cross-engine source semantic mapping. Do not transplant raw Stockfish TT conventions into another engine.

## Risks and falsification

- 0.19 February F19.5 **FAIL**, January J2/J3/J4 **FAIL**, 0.19 K4 **FAIL 0/4**, unbounded P1 R5 **FAIL** preserved.
- 0.20-B game3 SECOND_ONLY restored original F final bestmove, and 0.20-C game3 six-target alpha gate ladder PASSED 6/6 with one-point threshold discontinuity. Both remain **adaptive known-position** causal evidence; do not promote to prospective new-position effect.
- Original March prospectively registered alpha-gate root leader / final-bestmove predictions **are not rewritten by this expansion**. Chess feature analysis forms an orthogonal pre-registered explanatory layer.
- An algorithmic pin ray without tactical value, a skewered geometrical alignment without a forcing sequence, or different bestmoves without actual source contact are NOT positive causal evidence.
- Chess taxonomy is a working ontology. Evaluate explanatory yield by unique source-linked decision contrasts and invalidated rival explanations, not total feature count.

## Engineering & governance
Maintain main-only WhoSia attribution, immutable receipts, sha256 source provenance, negative controls, no Actions bot commits, local tests before one consolidated native run. Keep transformations pure/deterministic, avoid instrumenting only for richer logs, ensure source-only chess feature freeze precedes native inspection. Do not use GitHub Actions merely to rename or add prose. The next gate is a functional chess-microfeature extractor and its tests, then read-only source freeze.
