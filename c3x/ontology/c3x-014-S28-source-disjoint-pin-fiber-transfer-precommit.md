# C3X 0.14 — Prospective TCEC Season 28 Independent-Season Chess-Pin Fiber Transfer Court

**Formal status:** C3X 0.14 remains **OPEN**; this is an internal experiment, not a Pn formal substage or 0.15 activation. Proposed 0.15 name remains exactly **C3X 0.15 — Causal Chess-Concept Fibers, Search-Operator Differentiation & Transportable Tactical Ontologies**, but NOT OPEN. Do not touch existing P1 sealed held-out game cohort. No bot-authored commits.

## Chronological hard boundary
Existing discovery source: original official TCEC S29 Superfinal 100 games `master-archive/TCEC_Season_29_-_Superfinal.pgn`; preceding C3X 0.14 law corpus (702 chess-law absolute-pin instances, 31 law feature tuples) and 40 prescored-frozen worlds; 400 native SF16 searches in five arms gave 11 intervention-output binary response signatures in those **40 original worlds**, 18/40 responders, four repeated chess-law groups only 14 cases. These exploratory signatures and group keys are **discovery** data, never replicated successes yet.

**New source before results:** official TCEC S28 Superfinal, different season/game PGN but **SAME TCEC provider** and potentially same competitors/openings. Exact TCEC-Chess/tcecgames Git commit `3dd69a40b3cf6ccc74144df7411ef4e8e2140286`; repo path `master-archive/TCEC_Season_28_-_Superfinal.pgn`; raw Git blob SHA1 `9c702d0e8f646f65f28f1555652937d58d397ad4`. This season predates S29 and is not a prospectively collected future season. Honest claim is **different-season/source-game transfer**, not held-out provider/engine transfer. Never read SF16 outputs from S28 until chess-law selection is frozen.

## Source-only cohort compilation independent of engine score
Read all actual PGN games in archived original; validate chess legality and PGN headers; analyze plies 18–120 inclusive, actual side to move; king-absolute pins only by `chess.Board.is_pinned(side,piece)` cross-checked against queen/rook/bishop king-ray exact slider geometry via existing original S29 classifier. Deduplicate game-ID + 6-field FEN + pinned square and keep at most one root witness per original source game.

The four already declared S29 repeated chess-law subtype tuples are prespecified as primary target **regardless of S28 frequency**:
1. `PAWN, QUEEN, DIAGONAL, ZERO, cannot capture pinner`.
2. `PAWN, QUEEN, FILE, NONZERO, cannot capture pinner`.
3. `ROOK, QUEEN, DIAGONAL, ZERO, cannot capture pinner`.
4. `PAWN, ROOK, FILE, NONZERO, cannot capture pinner`.

Freeze **up to eight roots per target law subtype** by first appearance in chronological official game order, with distinct source games; then fill to **64** root witnesses from other unrepresented feature tuples (novel law tuple per game), finally earliest other source games until capacity. Do NOT engineer patterns to balance successful SF16 outcomes. Fixed exact source cohort selection algorithm and all source-game legal denominators preserved; if one prespecified type is absent, report 0 and never replace its denominator with alternative. The 64 roots represent chess-game-balanced source-only opportunities, **not random engine chess positions**. Fixed score-blind selection under previous known subtype labels is eligible for source-disjoint phenotype evaluation, but not independent discovery of the feature-label vocabulary.

## Frozen mechanical conditions & planned causal source transfer
Use source-pinned SF16 original tag `sf_16` commit `68e1e9b3811e16cad014b590d7443b9063b3eb52`, `Use NNUE=false` CLASSICAL, Threads1, Hash16MiB, MultiPV1, depth12, fresh SF16 process per arm and source root, two deterministic cold repeats. Exact native source-only C++ SEE pinned recapture exclusion and WeakQueen own-/enemy-side blocker score interventions already frozen in previous S29 discovery:
- OFF = original SF16.
- SEE_UNMASK = suppress SEE pinned recapture mask (ONLY a *static-exchange heuristic*, not chess legal move generation).
- WQ_OWN = suppress classic WeakQueen score subtraction only if own queen-side blocker exists.
- WQ_ENEMY = suppress classic WeakQueen subtraction only if attacker-side blocker exists.
- WQ_BOTH = suppress both.
Separate `C3X014_PIN_INTERVENTION` env knob; each mode records actual source event firing and search output. For 64 worlds ×5 arms×2 cold = **640** native Stockfish16 processes, no use of outside compute/server. All 64 OFF must be validated against separate original unpatched stockfish16 searches if possible; if not, run untouched native checker in same CI and compare strict bestmove, cp/score flags, PV, nodes. Treatment fired=0 ⇒ unchanged exact chess output including nodes/PV (negative control), every cold test strict repeat, and actual normal source move generation untouched.

### Primary outcome & admission
Primary is **exact four-bit bestmove change pattern** on actual source frozen roots `SEE_UNMASK,WQ_OWN,WQ_ENEMY,WQ_BOTH`; record all 16 possible patterns including zero and actual source fire counts, plus no-firing controls, score and PV. Compare distribution to S29's pre-disclosed 11 profile set. Quantify **covered/novel patterns**, total worlds with any effect, and conditional mechanism hit/firing, plus particular repeated source-law target group signatures. New unseen patterns are not a priori proof of genuine new concepts. Source season is sampling unit and 64 games within one engine tournament still correlated; cold starts not independent games.

**No cherry-picked latent taxon promotion**: do not name 11 (or more) independent learned chess concepts solely from different treatment response patterns, or claim root pin causal mediator when the global search touches unrelated positions. Control repeated matching law types, root-specific operator opportunity, engine evaluator routing and search-node counts. A full causally identified subtype requires an object-restricted intervention and root piece mediation; new provider and separate engine families are additional independent transfer gates.

**Explicit scientific fail/hold if** fewer exact legal worlds than 64, source hash mismatch, prior route changed, the original engine is not preserved, or any sham/nofire/cold condition fails. Partial science source-only work may remain factual but must not falsely be called 640 native tests.

## Source-only supplementary duplicate-position audit (BEFORE S28 engine outcomes were read)

The immutable S28 score-blind source-only selection ZIP for CI #37892996179 was downloaded and compared against the independently existing S29 source-only PIN census ZIP, before reading any trial response in CI #37893361180. Source original S28 frozen JSON SHA256 `1152473ed8d8793361f922434c75c7da2b9a58e0aa68a59466fc65179d6ac5e4`; S29 census original frozen JSON SHA256 `cfb2c4b0631959cfcdd5bf1eb098f7b41c40468a7b22e434e95ef8936cc43ead`. **0 exact (six-field FEN, pinned square) duplicates** between the 64 S28 frozen roots and ALL prior S29 source-only 702 PIN witnesses, and 0 shared with S29 selected 40 positions. However the S28 64 roots contain **63 unique exact six-field FENs**, not 64: S28 original official games **61 and 62** share exactly `1n1k1b1r/3p1pp1/B3q3/pNp5/1pP4p/4p1P1/PPQ1PP1P/3RK2R b K - 0 18`, pinned source square `d7` with same `PAWN,ROOK,FILE,NONZERO,FALSE` law tuple. Two game histories are not two independent **position** objects. RETAIN both originally frozen source entries, DO NOT change source selection after scores; report 64 distinct game IDs vs 63 distinct FENs and give both game-cluster and exact-position-deduplicated summaries for causal response. If their original source history yields unequal responses on identical FEN, report their history-dependent difference rather than silently deduplicate on FEN.
