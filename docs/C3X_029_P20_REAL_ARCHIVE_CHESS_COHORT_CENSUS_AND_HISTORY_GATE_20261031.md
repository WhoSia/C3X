# C3X 0.29-P20 — First Actual Archive-to-Benchmark Boundary Audit
Date 2026-10-31; based on directly fetched original GitHub archived source manifest and original native history receipt.

## Scientific question
Can the first accessible real-chess cohort be used as a fresh, source-independent explanation benchmark, or does the original artifact lack the data required by P11-P19?

## Source
c3x/cohorts/c3x-016-P4-Lichess-12-standalone-FEN-source-geometry-3x4-preoutcome.json
- 12 source-selected original Lichess 2026-06 states from separate games as declared by frozen selector.
- 3 each SKEWER_RAY, INTERFERENCE_RAY, DEFENDER_REMOVAL_RAY, NO_MOTIF_RAY_OPPORTUNITY.
- 4-field FEN, played_uci, source_ply and source_short_hash; original source SHA and selection manifest SHA.
- Frozen before that original experiment's engine score was opened, BUT now historical exposed data, NOT NEW heldout.
- Source geometry labels reflect source-selector pattern, not proof of relative quality or strategic merit.

## Decisive independent historical caution
c3x/receipts/c3x-018-real-chess-game-history-versus-FEN-native-20261010.json is a previous original native study: 16 complete reused game histories, full history vs standalone-FEN conditions at fixed Stockfish16 depth12/NNUE off/Threads1/Hash16. It records bestmove changes under history in 1/16 F and 3/16 O (overlapping categories not additive). Case2 original standalone O e1d1 but historical O c2b3; case15 standalone O f5e3 and historical O f5h6. Therefore the 12 4-field FEN cohort CANNOT be unconditionally treated as the full original game state. This is historical evidence and not a new run.

## P20 actual code
tools/c3x_029_p20_archive_chess_cohort_census.py directly reads that real checked-in manifest; tests enforce 12-case, 3x4 frozen motif strata, four-field-FEN scope and anti-corruption guards.
Result from source inspection: shape consistent, no candidate-vs-alternative score pairing, full legal opponent-reply enumeration, nearby-negative continuation or independently audited engine outcome in this manifest. Thus its scientific status is ARCHIVE_CENSUS_PASS_BENCHMARK_ADMISSION_HOLD, NOT a real BinProp competitive benchmark.
Under no circumstances infer performance from these 12 motive selector labels.

## Practical consequence
Use the 12 archived roots as DEVELOPMENT ONLY for baseline code integration and provenance-collision discovery; obtain new complete legal source games, lock game-disjoint source with independent candidate pairs, build correct positives/negatives/nearby negatives and test P11-19 with real chess labels. A 12-case tally is not a first scientific performance score.

## Local check status
P17 core Python was independently executed in the assistant's Python runtime on a synthetic 10-observation adversarial fixture, yielding row error 0.1 and game-macro error 0.5; that does not establish all repository test suites passed. Native engine, PGN replay, P20 CI results not verified.
