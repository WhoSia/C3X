# C3X 0.15 — P11 Source-Exact Root Child-Return Relay Gate (PRE-OUTCOME)
Date: 2026-10-09 KST. Flowing Versioning: C3X 0.15 stays live, C3X 0.16 opens the separate chess concept-operator research problem.

## Fixed source event from P10-R2
SF16 upstream 68e1e9b3811e16cad014b590d7443b9063b3eb52, pinned TWIC R2 world #2 source board full Key=5622551786424219112, first retained ROOT candidate mismatch at source rootDepth4, native Move1380 (f3e5), moveCount42, root alpha130/beta162; original TT policy I root child return14, V=130, B=0 at this iteration, root candidate stored score BOTH -32001. This is a CHILD RETURN difference, not yet a ROOT STORED SCORE mutation or a natural mediator proof. No events are chosen after observing P11 output.

## Targeted source change
AFTER child Stockfish::search returns and BEFORE actual rootNode candidate processing, optionally replace exactly one root child return value (V=130 or B=0, never other values) with original I=14 when ALL conditions match: frozen root full Key; depth4; move1380; moveCount42; alpha130; beta162. Apply once per SF16 process, no edit to legal chess moves, PV reporting, search window setup, TT writer/reader, prior qsearch or selected target identity. Denote clamp G; sham S executes same observer but always leaves value unchanged.

## Exact 48 native factorial
Two outcome-exposed source cases (#2, #29), SEE OFF/ON, existing TT value-policy I/V/B, root G vs S, 2 cold processes = 48. Expected source contact: #2 V and B G: exactly once per SEE state, #2 I G and ALL #29 conditions: zero; all S: zero. If unanticipated source value/window/move or duplicate trigger is found, FAIL CLOSED. Every S arm must fully match original P10 R2 UCI bestmove, score kind/value, nodes, PV and micro-source contacts. Every fixed arm duplicated exactly across cold runs.

For G measure bestmove, reported score, nodes, first root PV divergence depth, root event type and 0.15 original context binary effect; report source contact under G even if bestmove unchanged. Separate: root child-return relay effect; source micro-event first retained difference; root stored-score mutation. Exact G impact on root bestmove is **not** naturally necessary TT-to-root mediation because clamping is artificial and numerous other pathways may survive.

## Scientific status
P11 precommit only. Original 0.15 prospective P1 C1 overall accuracy 42/64 vs trivial B0 53/64 FAIL retained. TT natural mediation, cross-engine transfer and NNUE latent concepts HOLD.
