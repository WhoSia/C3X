# C3X 0.27 — Passive Native SEE Board Reconstruction and Independently Legal Exchange Outcomes (2026-10-19)

## Scientific conclusion
Original Stockfish16 native SEE *call-time internal boards* were reconstructed at two exact preactuator source events using a passive SHAM-only FEN logger. The original T3 physical actuator and SEE return semantics remain unchanged. An independent python-chess legal-move enumerator evaluates only forced same-square capture/re-capture exchanges at total depths 1–6. Result: **SOURCE_NATIVE_LIVE_BOARD_RECONSTRUCTION_PASS / LEGAL_EXCHANGE_PROFILE_PASS / STOCKFISH_SEE_VALUE_EQUIVALENCE_NOT_PROVED / NATURAL_TT_SEE_ROOT_MEDIATION_HOLD.**

## Provenance / reproducibility
- Historical May 2026 licensed source-only cohort GitHub run 38059784922, artifact 11672233048, SHA256 0ff43e28dcb3a5e48dea6b61e4450fc8bb9e1f96363871c33c4b73524664db61.
- Native T3 preactuator source targets run 38069237414 artifact 11676392027 SHA256 830536f445330b739a7a3b7e88ce4227e9ab9db43cf277f08a01ed5f9dc0ef69.
- Reused historical original Stockfish16 sf_16 commit 68e1e9b3811e16cad014b590d7443b9063b3eb52; exact 0.23 overlay build and 2x2 native harness, including cold duplicate runs, SHA-verified immutable input.
- Passive patch only inserts a write of pos.fen() at exact original T3 source eligibility and first contact, and only in mode SHAM. It DOES NOT flip SEE Booleans, alter Position::see_ge, TT access, search-window or engine chess rules. Full live FENs are stored only as private workflow-local files and are NOT placed in public artifact.
- Initial run 39225792388 FAILED because missing validator path on initial commit snapshot, not scientific failure. Complete-source replay run 39225941924 SUCCESS: C3X027_LIVE_SEE_BOARD_PASS 8, four SHAM contacts for each event. Follow-up fully integrated run 39226227900 SUCCESS with full legal capture profile.
- Source patch: tools/c3x_027_see_live_fen_passive_patch.py; builder tools/c3x_027_see_live_fen_repro_build.sh; validators tools/c3x_027_see_live_fen_validate.py and tools/c3x_027_live_see_exchange_profile.py. Workflow .github/workflows/c3x-027-see-live-fen.yml.
- Full independent replay log https://github.com/WhoSia/C3X/actions/runs/39226227900 . Uploaded public artifact 12174366124 (eight files) contains C3X027_SEE_LEGAL_EXCHANGE_PROFILE.json and C3X027_SEE_BOARD_VALIDATION_SUMMARY.json. No raw FEN or PGN shared. Live FEN SHA-256 match within each event across four cold SHAM observations.

## Native SEE event 11
- Preregistered source: game11, qsearch_prune, native move 2908 = f6e4, Stockfish SEE threshold -95 cp, original SEE bool=FALSE, alpha -215 beta -214, ply2 depth0, rule50=7.
- Verified live internal FEN SHA256 starts c88e030423b9... (truncated here; full artifact).
- Legal same-square capture chain under selected nominal material metric P1 N3 B3 R5 Q9: at 1 ply +1, depths 2–6 -2. The move itself wins nominal one pawn but one legal opposing capture reverses to -2 net. The bivariate comparison (raw nominal -2 pawn units to Stockfish cp threshold -95) is not numerically calibrated without Stockfish piece-value and approximate SEE semantics; independent legal evaluation is not the native Boolean.

## Native SEE event 2
- Preregistered source: game2, quiet_prune, native move 204 = d1e2, threshold -43 cp, original SEE bool=TRUE, alpha -9 beta -8, ply2 depth2, rule50=2.
- Live FEN SHA256 starts b82091ca27b1...
- Legal same-square capture-chain profile at horizons 1–6 is 0 nominal units. This is compatible in sign with original SEE Boolean but does not recreate Stockfish's exact SEE implementation.

## Limitations
The original 0.23 T3 experiment was development/post-exposure selected. The full original native source returns and qsearch branch interaction cannot be promoted to natural TT→SEE→root mediation by independent local chess law evaluation alone. Rule50 and full history matter for long-horizon game outcomes but not the local legal exchange checks performed. The current legal exchange program assumes both players can stop captures and fixes target square; does not model all tactical alternatives, special multi-square captures or Stockfish SEE's relaxed recapture heuristics. At source event2, f6e4/d1e2 exact move legality is checked on the *internal* live FEN, not only the original root board.

## Rewritten manuscript Results paragraph
A central obstacle was reconstructing the board that Stockfish actually held when it called SEE, rather than reasoning from the original game position. We inserted a passive logger into the original pinned native T3 source chain. It wrote a position only when an already preregistered call matched all the original move, position-key, ancestry and search-window conditions, and only during the unmodified SHAM arm. Two target invocations were observed four times each. Their live-board hashes were stable, and a separate chess implementation confirmed the examined move was legal at each captured internal state. For f6e4, the one-ply capture gained one pawn unit, but the adverse immediate recapture changed the legal exchange balance to minus two units; this figure persisted to six exchange plies. For d1e2, the corresponding local balance stayed at zero. The original Stockfish SEE threshold tests were respectively false at -95 centipawns and true at -43 centipawns. The independent calculations characterize real legal exchanges at the native source states, not the exact algorithm used by Stockfish. Establishing whether the underlying exchange assessments mediate any later root decision remains a separate causal experiment.

## Next decisive step
Reimplement Stockfish16 Position::see_ge precisely in an independent verifier at the captured event FEN, move and threshold (or use a read-only actual SEE return trace verified against frozen Stockfish source). Ensure correct source-value units, optional occupied bitboard, pins and semantics; compare against captured original bool for each event. Only after this source-conformance test, run a source-matched natural TT intervention and trace event activation, return adoption and root choice with a prospectively frozen cohort. Scientific novelty is not claimed on these two observed samples alone.
