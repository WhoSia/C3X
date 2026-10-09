# C3X 0.15 P6 — Exact TT Return Edge Counterfactual (PROPOSED, NOT EXECUTED)

**Governance, 2026-10-09:** Formal 0.15 OPEN, P6 NOT EXECUTED. Existing P0 R2 source SHA 1e932aa881eaef549c770211c078d930cd8d675e5688644e1bc36ab31bae4534, P2 result SHA e930f0b489301c656690d09f4821583a28eead04e43382b545bda35b71279256, P1 presealed predictions remain immutable. The old procedural sealed four-game holdout is not opened.

## Real empirical motivation

P4 native fullkey writer/reader tracing showed 30/64 different TT event streams, and **30/30 first recorded disagreements had different full position keys**, not matched key with different bound. P5's broad post-SEE TT-return suppression affected source SEE response identity in 13/64 worlds, but suppressed 571,160 TT early returns in the SEE-treated conditions, so no single TT read has been shown necessary.

## Primary problem

Among the original 64 TWIC pinned-root source worlds, test whether blocking **one exact, originally executed TT early return** changes the Stockfish16 original-root-SEE response and its search trace, without suppressing any other TT return or touching legal moves.

Use exact upstream Stockfish16 source commit 68e1e9b3811e16cad014b590d7443b9063b3eb52, classical route Use NNUE=false, Threads1, Hash16 MiB, MultiPV1, depth12.

## P6-S0 original OFF-only target selection, before P6 treatment output

1. With semantically inert writer sidecar, run native SEE-OFF on each original legal source-game history. Verify exact P2 untouched UCI bestmove/score/PV/nodes/counters.
2. After first **eligible original PIN-root SEE candidate**, find first actual main/qsearch TT early return with last physical writer known and matching **full64 position key**. Record TT cluster and slot offset, key, writer class, stored bound/depth, write-sequence, consumer ply/current alpha-beta, and original source site ordinal.
3. If none exists, retain NO_ELIGIBLE_EDGE for that game; never substitute another selected by known P2/P5 response.
4. Hash each of the 64 original target identities (including the absence markers) and commit the target manifest **before** any blocked-edge experimental output. No treatment-based root selection.

## P6-S1 native counterfactual in fixed target registry

- Treatments: S=OFF/SEE and B=TT_ALLOW / TT_BLOCK_ONCE_MATCHED_TARGET. In each world, execute all four cells with two independent cold SF16 processes each.
- Matched target requires same full position key, writer class, bound/depth, concrete slot location and writer-write sequence or explicitly reports nonmatching lineage. Suppress AT MOST ONE originally permissible main/qsearch TT early return in each process. Other TT saves, probes, low16 native table implementation, move order, legal moves and SEE site guards remain unchanged.
- If this producer/consumer edge is not naturally reached in a treatment arm, report UNDELIVERED_EDGE and never substitute a new TT event. Retain the original 64 world intention-to-treat population and report actual matched-event exposure as denominator for narrower claims.
- All ALLOW outputs must exactly reproduce P2 original/surgical SEE UCI; cold pairs exact. No candidate or no edge must not invisibly produce output differences. Search active alpha-beta and original TT writer provenance must be logged.
- For observational TT bookkeeping, do NOT mark a blocked return as a genuinely taken cutoff.

## Predeclared judgments

Root bestmove/score/PV/nodes response to the exact TT-return bypass is one operational software counterfactual. Source-by-single-return interaction may be computed on categorical bestmove change indicators, but no natural indirect effect/mediation share is identified without stronger assumptions. The strongest licensed positive claim is: **in this exactly versioned, replayed SF16 search, bypassing this one declared matched read changes the reported outcome**. A negative or unmatched witness is equally important.

Any observed divergence preceding eligible code treatment, sham mismatch, FEN/history drift, P1 prediction refitting, or unknown TT writer identity is a failing gate. Necessity of a particular computation beyond this bounded run, learned NNUE tactical neurons, and chess-perfect minimax optimality remain unproven.

**Prospective status:** P6_PROPOSED_NOT_EXECUTED / SINGLE_TT_RETURN_CAUSAL_EDGE_HOLD / ORIGINAL_P1_PREDICTION_FAILURE_PRESERVED / C3X_0.16_NOT_OPEN.
