# C3X 0.23-P1-R4 — Counterfactual Search-Frontier Bifurcation & Exchange-Legality Mediation

**Design precommit 2026-10-11; NOT EXECUTED. Existing six 5-May broadcast source cases are DEVELOPMENT only.**

## Hypothesis

A verified full64 Stockfish16 TT first consumer changes admissibility of later search branches. One-sided native SEE events may result from that different search frontier. Their correlation with final bestmove does NOT prove natural mediation.

Frozen reference: source32 JSON SHA 0ff43e28dcb3a5e48dea6b61e4450fc8bb9e1f96363871c33c4b73524664db61, untreated native StageA SHA fe88afe49d7d43db7b81c37decab783f2b68311ed2ca10b6f42be4268bdb3442, T1 actual full computational state SHA 1975a515755e31a4c9445239750bde88211a13c328f667d86cabba2ce58effeb.

## Identification gates

1. Instrument original main/qsearch native search recursion entry and exit, plus actual TT score-as-eval assignment, actual TT return cutoff and SEE source-call consumer. Use ONE monotonic native event serial. Keep original chess legal move generation, unmodified native SEE inputs and alpha/beta state.
2. For each original and physically TT-FIRST blocked search trace, find the earliest **common parent search node and fully measured live search state** after actual selected TT use. Require complete original ancestor key sequence, source root candidate, native move, parent/child key, ply, depth, alpha/beta, PV status, rule50, input occupancy, native branch site and actual continue/prune outcome. Duplicate or censored identity is HOLD.
3. Only when that parent source state is uniquely aligned and original search branch choice is physically observed, freeze the single target parent branch and original outcome in a separate pre-intervention receipt. No choosing an SEE event by rootcall name or by downstream final move.
4. Intervene once on *that original native parent branch admission decision*, crossed with TT original vs exact TT FIRST. Use cold duplicate, source-invalid sham, actual branch contact validation, actual SEE invocation/threshold, root candidate depth leader and exact UCI. A missing target in either arm is NO_CONTACT, never fall back to another node.
5. For a source-aligned native descendant position, reconstruct legal board path, actual opponent **legal** recapture options and piece-to-square attacker/defender edges. Pseudo-attacks from pinned pieces are not legal recapture proof. R3 found only 1/6 descriptive root recapture-count differences, not a proven mediator.

## Falsification

If no same parent state is visited in both arms, report PATH_DIVERGENCE and no fixed-node intervention. If branch intervention makes a real SEE gate fire but does not change candidate survival or final UCI, that is a negative mediation-control endpoint, not grounds to redefine the target. The R2-T2 exact-source SEE operator negative and independent M1 111/124 vs M0 117/124 negative remain authoritative. The original native SEE output occupied Bitboard must never be read uninitialized.

Any proposed new M3 exact UCI prediction needs NEW legal/rights-reviewed source-only cohort with literal forecasts sealed before any new TT counterfactual search. Cases already viewed here cannot be called heldout.

**R4 status: PRECOMMIT DESIGN ONLY. No R4 native intervention or prospective predictive success claimed.** Lichess broadcast CC BY-SA 4.0, puzzle CC0, modified Stockfish binary GPLv3 requirements and TWIC original source HOLD remain enforced.
