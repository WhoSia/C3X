# C3X 0.18 — Cross-Horizon TT Evaluation Consumer Rank Transport Court (2025-11)

**PRECOMMITTED BEFORE SELECTION AND ANY ENGINE OUTCOMES.** This is a genuinely new source-month and game-histories cohort. The October 2025 sixteen are a prior negative discovery (V source gate 0/16 bestmove changes); do not reuse their positions, targets or scores.

**Source:** Lichess broadcast 2025-11 PGN (public, CC BY-SA 4.0) https://database.lichess.org/broadcast/lichess_db_broadcast_2025-11.pgn.zst. Source-only workflow decompresses first valid standard games, first 512 eligible containing >=70 plies, original game SHA ranking, smallest 12 game SHA values. Same **originally declared sampling rule**: ply 30 + (first 8 hex of canonical game SHA modulo 15). Reject duplicate games and any FEN4 overlap with earlier 12 historical or October 16, record all rejection reasons and preserve full mainline PGN UCI history. No Stockfish process or score may be evaluated during sample freeze.

**Search source:** frozen SF16 `68e1e9b3811e16cad014b590d7443b9063b3eb52`, 1 thread, 16 MB hash, NNUE disabled, MultiPV 1. Root choice O = original first, F = observed original game played-legal move forced to front, Z = no-contact sham, standalone legal-EP FEN with original halfmove/fullmove counters (NOT 0/1 reset). Original move history retained; it is **not played** for this court. Depth 8 and depth 12 **both** prespecified.

**Passive observation and target ranks:** For each world × depth, run O, F, Z double cold (verify O=Z exact full UCI core). Repeat F with optional `C3X018_TT_DISCOVERY=1` to enumerate first 32 physically consistent, bound-qualified TT evaluation correction reads in search order, with strict 64-bit full-key writer shadow. Keep list, do NOT rank by effectiveness. Precommit three **0-indexed positions** `0, 7, 23` (= first, eighth, twenty-fourth). If fewer reads, return `RANK_NOT_ELIGIBLE` and do not substitute another. At each eligible rank, choose that event's key64, physical slot, slot-local epoch and run cold V twice. Assert at least one physical selected reader blocked to count treatment as fired. Preserve non-firing arms, exact six-field UCI tuple and SHA receipts.

**Predeclared risk tests:**
- `T1_FIRST_ZERO`: at depth 12, the **first** passive TT evaluation consumer rank changes the *categorical bestmove* in **no more than 2 of 12** fixed roots. >2 is FAIL; this reflects the negative October observation, not a claim of an invariant.
- `T2_LATE_HAS_ROOT_EFFECT`: among all eligible depth12 rank 7 and rank 23 treatments, **at least one** actually blocks a reader and changes bestmove. No flip = FAIL (and not-contacted cases are non-confirmations). This is an intentionally risky temporal-location hypothesis.
- `T3_DEPTH_MODULATION`: at least one *same original game source root* exhibits a difference in V root-impact (bestmove-changed boolean at an eligible rank) between depth 8 and depth 12. Otherwise FAIL.
- `T4_PHYSICAL_WRITER_READ_INTEGRITY`: all *claimed* V writer-reader physical payloads are equal at full64/slot/epoch/raw TTEntry fields, with a preceding nonzero in-process writer ID. Any mismatch FAIL; no contacts => NOT_TESTED.
- `T5_ROOT_SHAM`: O and Z final 6-field UCI core exact in **every** completed world/depth; any mismatch is FAIL-CLOSED.
- `T6_FULL_DENOMINATOR`: all 12 × 2 = 24 world-depth cells and their 3 planned ranks are retained, even if no target. No outcomes-driven replacement or dropping.

**Important authority:** Rank 23's TT read is not necessarily at deeper recursive ply or a later root trial. Record reader `ply`, `depth`, `alpha`, `beta`, writer serial and root ancestry if obtainable; observed event sequence ordinal alone cannot be called causal temporal distance. Source V gate may affect branch evaluations but no unique natural TT mediator is proven.

**Source-only stage first, SHA freeze, then native stage.** Any post hoc repair must be append-only and preserve failure receipts.
