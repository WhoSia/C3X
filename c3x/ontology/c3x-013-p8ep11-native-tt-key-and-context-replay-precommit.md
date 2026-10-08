# C3X 0.13 P8-EP11 — Native TT Entry/Position Identity and Context-Conditioned Single Return Replay

**Precommit before EP11 UCI measurements.** Scientific status: development-stage reverse engineering, no causal chess strategy certificate. Do not automatically open 0.14.

## Explanandum and ancestry
EP10 on previously frozen CECLUB root (full six-field FEN `2rq1rk1/p4ppp/bp1bnn2/3pN3/2pP3P/1P2PPP1/PB2NRB1/R2Q2K1 w - - 1 17`) found that blocking the 32nd MAIN TT early return at UCI depth12 with MultiPV2 restricted to legal root `f3f4,g3g4` changed f3f4-minus-g3g4 gap from +31 to −8 cp. The chronological ordinal persisted under swapping `searchmoves` order but the native TT key/position identity was unknown. This is the *same pre-used game*: not a fresh holdout or independent validation. G9.4/G9.5 earlier TT attribution is binding prior art.

## Surgical instrumentation
Pinned upstream Stockfish `sf_16` exact commit `68e1e9b3811e16cad014b590d7443b9063b3eb52`. Build source layers EP9 counters -> EP10 ordinal one-shot -> EP11 context/provenance patch. The new EP11 callback replaces exactly the call from native MAIN and QSEARCH TT early bound returns, not the TT itself. Every actual blocked event emits *actual* `pos.key()` 64-bit Zobrist identity, `pos.fen()` full six-field board representation, TT bound and stored depth, rule50 count, `ss->ply`, local remaining depth, α and β, returned value and actual execution ordinal. Keyed selection uses (site MAIN, key, ply, depth), and it blocks at most one eligible bound return. Do not treat key alone as an intervention invariant; TT entries differ across transposition histories and engine versions, and full repetition history is not in FEN.

## Outcome-independent grid
At depth12 and depth8, repeat each cold UCI process twice, Threads=1, Hash=16MiB, MultiPV=2, root legal pair. Both root candidate-list orders `f3f4 g3g4` and `g3g4 f3f4`.
- Sham EP10 NONE vs EP11 NONE (exact bestmove, depth, candidate scores, PV, nodes).
- Anchor EP10 MAIN ordinal32 vs EP11 MAIN ordinal32 (same exact output and one event selected). Record event fingerprint under original and reversed root-order.
- **Identity selection**: take the TT key, ply, remaining depth found in the *first* original-order depth12 EP11 ordinal32 cold run; WITHOUT changing those targets, attempt EP11 key-targeted replay across both root candidate orders × both depths × both cold repeats.
- Negative selector control for a nonexistent 64-bit hash `ffffffffffffffff` at fixed ply+depth+site. It must select zero events and produce the same output as EP11 NONE; if not, report invalid rather than repair.
- Falsifier outcomes: event key, full FEN, TT bound/stored depth and 50-move clock equality across orders, keyed replay ordinal stability (or lack thereof), effect on candidate preferences and raw scores. **Any result including mismatch or no match must be retained.**

Controls: do not count repeated searches or multiple selected candidate ordinals as independent games, do not claim equal work budget from equal depth, no NNUE causation or high-level chess meaning from an implementation target. Remain reproducible and preserve GPLv3 upstream source, hashes and exact code patches.

## Literature distinction
Méndez et al. (2023) *Metamorphic Testing of Chess Engines* DOI 10.1016/j.infsof.2023.107263 offers engine-output consistency relations on more than 40k positions; the published 2025 Martin et al. replication demonstrates search order/depth/realistic-source sensitivity and warns against labeling all disagreements as software faults. Clark et al. (2023) *Metamorphic Testing with Causal Graphs* DOI 10.1109/ICST57152.2023.00023 uses causal graph structures to derive testable input-output expectations. C3X's native event context is implementation evidence; an actual causal DAG over board concepts must not be presumed from this analogy.

## Custody and graduation
Authentic human WhoSia authorship only, read-only GitHub Actions, raw ZIP in existing Drive C3X source folder, research added to existing Notion Lab. EP11 scientific verdict separated into (1) source-level event identification; (2) key-conditioned portable replay under one changed root list; (3) high-level stable chess meaning. Only (1) and potentially (2) are permitted this stage. P8 stays OPEN; 0.14 may be considered when independent source/engine replication, concept mediation and product evaluations are explicitly deferred or met, not to bury the gaps.
