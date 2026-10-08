# C3X 0.12 — Real Native UCI Execution Boundary

Stage: C3X 0.12
Status: ENGINEERING IMPLEMENTED / REAL-WORKFLOW RUN NOT VERIFIED

## Executable surfaces
- C++ UCI native probe: tools/c3x_012_uci_probe.cpp
- C++ MultiPV comparability gate: tools/c3x_012_uci_score_gate.cpp
- Real-engine workflow: .github/workflows/c3x-012-real-uci-smoke.yml
- SQLite source and repeated-run integrity: c3x/schema/c3x-012-uci-measurements.sql

## Real execution proposal
In a read-only GitHub Ubuntu Actions runner, install distribution Stockfish and chess 1.11.2. Construct the conventional Sicilian Najdorf opening after SAN moves e4 c5 Nf3 d6 d4 cxd4 Nxd4 Nf6 Nc3 a6. Check that c1e3 and c1g5 are legal. Freeze full FEN and SHA256; record the installed engine binary SHA256 and UCI identification; perform two bounded depth-8 UCI searchmoves runs; retain both raw JSON packets as build artifacts. Run SQLite synthetic authority and depth negative controls. No commits by CI.

## Authority
This is first real engine plumbing, not yet the main prospective near-equal reason experiment. Even if CI succeeds:
- chess legality is confirmed for the fixture only;
- candidate near-equality is not pre-established;
- search result reproducibility is not implied by two repeats;
- cause, mediation, strategy, text faithfulness, transfer, and source-ecology independence are not identified;
- 0.11 historical-FEN preseal does not become PASS;
- historical P23 FAIL, P24/P25 HOLD and Q0 DENIED remain.

## Next irreversible scientific action
Inspect actual Actions artifact and binary version, verify same-depth bounded cp and mover perspective, independently select qualifying near-equal pair, then freeze rival reason hypotheses and legal continuation interventions before any explanatory success judgment.

## Polyglot role evidence
C++ = actual UCI subprocess and typed score gate; Bash/YAML = runner orchestration; SQLite = event integrity and clustered repeat audit; Python only = rules-legal FEN fixture preparation. Rust deferred until there is an independently demonstrated typed event risk not covered by present boundaries.
