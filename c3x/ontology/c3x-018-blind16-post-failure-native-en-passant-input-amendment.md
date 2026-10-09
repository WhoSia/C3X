# C3X 0.18 — Blind16 Native Input Contract Amendment After Case16 EOF

**This is a post-initial-run repair, not a change to the originally preregistered forecasts or selected sources.**

The first sixteen-world Stockfish native run [#37982333162](https://github.com/WhoSia/C3X/actions/runs/37982333162) was **FAIL**: 15 worlds fully evaluated, case #16 ended with `PREMATURE_EOF_bestmove`. The exact source sample and preregistration remain unchanged; retain run #37982333162 permanently as failure evidence. Early summaries from 15 valid worlds were V bestmove change 0/15, W2 change 1/15; **do not** promote them to 16-world inference.

**Exact suspect:** case16 source FEN4 `r5k1/p1p2ppp/1pn1p3/q2p4/2PP4/4Q1P1/PP3P1P/R4K1R w - d6`. Full original mainline prefix ends with `d7d5`; the FEN-spec en-passant target `d6` may be present while a legal en-passant capture is unavailable. Stockfish's handling of this source FEN may differ from python-chess's `en_passant="fen"` export. Crash causality must be checked, not asserted from correlation.

**Repair:** For **all 16 games**, deterministically replay their immutable full historical UCI prefix with python-chess `chess==1.11.2`; assert its `en_passant="fen"` four-field output exactly equals the frozen source `fen4`, then supply the same board exported with `en_passant="legal"` to SF16 (and to the root-order operator's FEN4 match). This changes no pieces, side-to-move, castling right, move, sample membership, or candidate selection rule. Emit and preserve before/after FEN4 for every world; always apply the rule before any engine output. Do not suppress the raw source FEN from the archive.

**Authority:** This is an **amended execution contract**; native outcomes following this repair remain a prospective test of the preregistered predictions, but they are not claimed to be a pristine execution of the original FEN input contract. If the problem remains, FAIL-CLOSED with full diagnostic context; do not exclude the 16th world.
