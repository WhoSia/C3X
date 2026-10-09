# C3X 0.18 — Architecturally Independent Ethereal TT Evaluation-Reuse Challenge

**PRECOMMITTED BEFORE ETHEREAL NATIVE EXPERIMENTS; THIRD AXIS.** Engine is the distinct Ethereal chess engine by Andrew Grant (`AndyGrant/Ethereal`), master SHA `0e47e9b67f345c75eb965d9fb3e2493b6a11d09a`, source `src/search.c`, GPLv3; this is **not** Stockfish 17 or a Stockfish family branch.

**Structural source comparison — do not assert isomorphism.** SF16/17 each contain a bound-conditioned TT value overriding a position static evaluation when the bound direction supports it. Ethereal's current `search.c` probes `ttValue` for TT cutoff and one-depth-lower fail-low, but uses `ttEval` to select the cached static evaluation at both `search()` and `qsearch()`. We will not label Ethereal's TT cache reuse as Stockfish V. A missing bound-as-eval value override is a **failure of exact source mechanism transfer**, not necessarily failure of memory-aware search more broadly.

**New cohort:** exact 12 source-only SHA-frozen November 2025 broadcast game histories `2971fe617f39fbba6d40fb0b09d8a18ce247d5865dc807fcdab9a594e3473402`. Same original legal EP, original H/fullmove FEN clocks, 8 and 12 depth, Threads1, Hash16, MultiPV1, **classical evaluation** Ethereal build `make basic` without EVALFILE or OWNER. No native sample selection after outcomes.

**Operator:** `C3X018_ETH_TT_CACHE_GATE=all` bypasses the stored TT *static evaluation cache* (not TT search value) at two source-exact callsites in main/qsearch; computes `evaluateBoard()` fresh. Report positive selected TT cache reuse branch contacts, at most 16 printed per cold native process to avoid telemetry interference. The baseline is identical except no environment gate. Each search launched in a new native process twice, with exact bestmove, score, nodes and PV comparison.

**Risk tests:**
- `I1_SOURCE_ROLE`: Ethereal's main and qsearch cached static eval reuse source sites exist and patch/compile, and no fabricated Stockfish V-specific bound-conditioned score-override is installed.
- `I2_READER_CONTACT`: actual cached-eval reuse is eligible at least once in every depth cohort (8,12).
- `I3_ROOT_IMPACT`: at least one of 24 source × depth cells changes categorical bestmove upon global cached-static-eval bypass. No change => FAIL.
- `I4_FULL_DENOMINATOR`: all 12 × 2 depths × 2 source arms, each cold repeated, complete. Any omitted world is HOLD.
- `I5_NONISOMORPHIC_BOUNDARY`: results must always distinguish Ethereal TT cached **eval** intervention from SF16/17 TT score-as-eval **value** intervention, even if bestmoves coincide.

**Scope:** This is an independent engine *implementation* of broader TT evaluation memory reuse, not replication of the exact SF16 value-as-evaluation causal mediator. Source touchpoints and contact must be verified and possible functional differences recorded without normalization of evaluation scales.