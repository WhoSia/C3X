# C3X 0.29-P21 — Real Lichess Twelve Source Move Chess-Law Probe
Date 2026-10-31. A SOURCE-DATA CHECK, not a new competitive explanation benchmark.

## Research question
Can the twelve original recorded Lichess 2026-06 moves be reconstructed even at the basic independent board-law level before proceeding to strategy or comparing C3X versus BinProp?

## Source and observed execution
Canonical existing repo manifest c3x/cohorts/c3x-016-P4-Lichess-12-standalone-FEN-source-geometry-3x4-preoutcome.json. Independent local Python probe encoded each original four-field FEN and UCI move and checked: source piece exists, correct player, no friendly capture or king capture, geometric move rule, unblocked sliding lines, and no attacked own king after move. Result **12/12 PASS_BOUNDED_NON_SPECIAL_MOVE_ONLY**. Each move is non-special. This is a bounded newly executed source-derived verification, NOT a full independent chess-library verification or whole game PGN/history reconstruction. It does not certify rule50/repetition, original Lichess full history, complete legal move generation or Stockfish preference.

Per-case: S1 h3h1; S2 a5b4; S3 f4h3; I1 e4f5; I2 d8d5; I3 e4d6; D1 a6e2; D2 e6h3; D3 e5f3; N1 f2g1; N2 g6f7; N3 e8e5 — all passed bounded checker.
Actual original 0.16 P2 Go source audit independently previously reported 24/24 legal original source game histories / 2038 plies, six tests; this is historical inherited evidence with Go source held in private Drive ZIP, NOT repeated in current session. README: cmd/c3x016-broadcast-legality/README.md.
Prior C3X 0.18 original native history/FEN difference: source scope unchanged; bounded four-field board legality does not restore history/engine choice.

## Deliverables
tools/c3x_029_p21_source_move_legal_probe.py and tools/test_c3x_029_p21_source_move_legal_probe.py. The source tool intentionally rejects or HOLDS unsupported special moves; it is NOT a substitute for python-chess or original Go full-law verification. New tests include all twelve actual manifest rows plus synthetically wrong-side, missing-piece, self-check, blocked ray, and unsupported castling. Native chess / original PGN re-run remains HOLD. Source geometry motif label is NOT an explanation of move quality.

## Scientific next
1. Reconcile actual original full PGN game-histories from source SHA with the public source freeze before doing engine interventions.
2. Select independent newly blind games for actual competing candidate pairs; never promote these exposed twelve to heldout.
3. Confirm legal move universe with separate full chess rules engine; then create opponent replies and nearby-negatives under fixed analysis budget.
4. Benchmark actual C3X concept claims against BinProp's engine-grounded motif labels and ACT-Eval claim-error/coverage under matched data and game-level inference.
Scientific claim: newly checked **limited source move legality on archived historical board states**, not new chess explanation robustness or model performance.
