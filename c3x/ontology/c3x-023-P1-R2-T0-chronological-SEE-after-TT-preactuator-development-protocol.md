# C3X 0.23-P1-R2-T0 — First Real TT Score-Use to SEE-Event Source Chronology

**Development-only protocol following observed R1 #38062242676; BEFORE running the new chronological logger.**

## Frozen outcomes motivating this *diagnostic*, not new heldout prediction

P1-R1 independent Lichess May2026+CC0 cohort previously selected before native; actual physical FIRST reader blocked **124/124 eligible role cells**; source path key match in 124/124, **2508 unique observed SEE events** across them; **57** role transcripts censored at 32 native SEE events. Among these 124, 7 role bestmoves changed representing May2026 broadcast **4 different games**; no CC0 puzzle bestmove changed. Historical M1 crossorder accurate **111/124** vs nochange M0 **117/124**, no positive model claim.

Important: these source SEE matches were *within the same rootcall and path hash*, but chronological order relative to TT score consumption was **not yet measured**. An SEE event before the first selected TT-source use cannot mediate that first use.

## Six fixed, post-outcome-development-only probes

Exactly these role cells, not reselected for favorable results:

- May game #1, O, STRICT (TT effect known)
- May game #8, O, BROAD (TT effect known)
- May game #11, F, STRICT (TT effect known)
- May game #12, F, STRICT (TT effect known)
- May game #2, O, STRICT (TT no-flip control)
- May game #3, O, STRICT (TT no-flip control)

Use original S0 JSON SHA `0ff43e28dcb3a5e48dea6b61e4450fc8bb9e1f96363871c33c4b73524664db61`; Stage A SHA `fe88afe49d7d43db7b81c37decab783f2b68311ed2ca10b6f42be4268bdb3442`; exact full64 TT source writer/reader and cold Stockfish16 source plus native parent path overlay; no SEE Boolean mutation.

## New monotonically ordered witness (opt-in only)

`play(... ordered_source_trace=True)` parses the actual synchronized Stockfish single-thread UCI `info string` lines in occurrence order for:
- actual TT `reader_block` with full64 key, physical slot, epoch, source root-call;
- native score/cutoff source `c3x019_native_use` event at same key/root call, **not just probe hits**;
- original passive native SEE call at `quiet_prune|qsearch_prune|capture_prune|qsearch_futility`, retaining original SEE return and ancestor path fingerprint.

A common SEE event `E` qualifies **AFTER_FIRST_REAL_TT_SOURCE** only if:
1. native TT original physically used score or a proven cutoff for that selected key/source rootcall at emitted line ordinal `L_U`;
2. counterfactual physical first reader `reader_block` at source key, slot, epoch, call at `L_B` (with writer->reader proof);
3. same **unique** SEE source event key+parent+ordered 64bit ancestry hash+site+native move+threshold occurs at `L_O > L_U` and `L_V > L_B`, respectively.

This log-ordinal source serial is monotonic in the **single-thread** UCI observed channel but does not prove a fully equal computational state: alpha/beta, search depth, ply, PV/nonPV and occupied bitboard are **not** yet logged. The chronology is a necessary condition, not sufficient mediation proof.

If no unique shared post-source event within capped first32 SEE logs: `HOLD_CENSORED` if either transcript truncated, otherwise `NO_OBSERVED_CHRONOLOGICAL_COMMON_NODE`, not global absence. Duplicates rejected. If any watched source isn't used before V or reader source block doesn't fire, `NO_SOURCE_CONTACT/HOLD`. Do not roll back to original 0.22 D2 rootcall-first SEE flip or posthoc redefine a TT episode.

## Release

Posthoc six-cell diagnostic is explicitly DEVELOPMENT. Only aggregate counts and original modified GPL/Stockfish source hash and original Lichess BY-SA/CC0 provenance are public. Do not publish raw original broadcast PGN or player names, and do not infer previous TWIC email reply. Outputs pass 0.23 technical byte gate (not a blanket legal waiver).

**T0 executes no SEE actuator. P1-R2 subsequent controlled SEE site intervention requires another frozen source signature + search state depth/alpha/beta/occupied and an independent control.**
