# C3X 0.18 — Stockfish16 vs Stockfish17 Bound-Conditioned TT Evaluation Route Compatibility (Cross-Version)

**Frozen before native results.** This is a separate **same-family cross-version architecture** challenge, *not* a second independent chess engine. Stockfish 16 commit `68e1e9b3811e16cad014b590d7443b9063b3eb52`; Stockfish 17 tag `sf_17` exact commit `e0bfc4b69bbe928d6f474a46560bcc3b3f6709aa`.

**Input:** exact 12 November game positions selected prior to native outcomes (November blind source-only SHA `2971fe617f39fbba6d40fb0b09d8a18ce247d5865dc807fcdab9a594e3473402`). Both engine versions search the **original halfmove/fullmove six-field FEN** at depths 8 and 12. No source game changed after engine outputs.

**Structural site:** In SF16, (i) main search `ttValue != VALUE_NONE && TT_BOUND_ACCEPTS(ttValue > eval)` and (ii) qsearch `ttValue != VALUE_NONE && TT_BOUND_ACCEPTS(ttValue > bestValue)`. In SF17 corresponding concepts use `ttData.value`, `ttData.bound` and corrected static evaluation; qsearch additionally has a tablebase/mate-guard condition. Both implementations use the TT value as a better local evaluation, but **the correct semantics and thresholds differ**; equating their score units or call IDs is forbidden.

**Operator:** Per engine source-exact `C3X018_GLOBAL_TT_EVAL_GATE=both` removes the full branch use of the TT value-as-eval override at **all** eligible main and qsearch nodes. This is explicitly NOT the physically targeted single writer V intervention and should never be mixed with the October 16 first-eligible-reader P1 test. In both baseline and gated modes each search starts cold, 1 thread and 16MB hash, MultiPV1. Stockfish16 has optional classical evaluation (Use NNUE=false), Stockfish17 requires NNUE network and cannot be treated as a matched static-eval implementation. Network binaries are compiled/downloaded by the version's own `make net` target and hashed, never redistributed.

**Fixed outcomes:** For each version and both depths, exact source-root bestmove, score label/value, nodes, PV, and actual source gate contact count (capped logs), each condition repeated cold. No exclusion of unchanged or not-fired cells. 12×2×2 version×2 gate = 96 condition cells, each cold double = 192 processes.

**Risk predictions:**
- `C1_STRUCTURAL`: both source versions compile with a source-matched bound-conditioned TT-value-as-eval gate in main and qsearch. Missing source site = FAIL, not silently substitute another feature.
- `C2_PERTURBATION`: global gate changes bestmove in at least one version-depth-world cell. Zero = FAIL.
- `C3_VERSION_NONIDENTITY`: at least one world-depth has a *different binary change response* between SF16 and SF17. Identical responses all cases = FAIL. This tests one narrow form of algorithm version dependence, not general validity.
- `C4_GATE_REACHED`: at least one gate contact is observed in each version-depth group; missing -> FAIL.
- `C5_FROZEN_DENOMINATOR`: all 12 games preserved at each version-depth-gate, full cold repetition; any missing is HOLD not silently dropped.

**Boundary:** This is same-family transfer only. It does not prove TT physical writer identity across versions or human chess-concept causal explanation. A genuinely architecturally independent engine is a separately required follow-up.
