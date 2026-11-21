# C3X 0.31/P3-X3 — Non-mutating pre-futility TT-state witness: prespecified native source-patch study

**Frozen before new R39 native searches, 2026-11-21.** Engine P3-X1/X2 and all original P2 labels are already known; this is **mechanism-development observational source instrumentation on exposed cases**, not blinded cohort evidence. It is explicitly not a causal mediation identification or TT-state restore/swap.

## Exactly frozen seven source events

Select all six original P2 signed `null_cut=1` **incremental** final-root changes conditional on futility-off: `P2-013-1`, `P2-021-1`, `P2-041-1`, `P2-052-1`, `P2-056-1`, `P2-058-1`, and the original P2 same-completed-depth **futility-only** root flip `P2-005-0` as a contrast. These are **post-outcome selected**, not population-representative or seven independent families. Their source `OPEN` event identity, complete legal game history, original per-arm `bestmove` and source `C3X_R33_CLOSE` remain exactly those fixed in P2-B1/B2.

**Source and environment:** identical pinned Stockfish16 original commit `68e1e9b3811e16cad014b590d7443b9063b3eb52` and original NNUE SHA `5af11540bbfefcb54e38c5dd000cab4b469dfa7599a1d55be5d2722c20a8929b`. Replay the exact seven patch overlay stack through `R33-prospective-gates.patch` that generated the P2 source binary (its SHA `ce13b5899ab6862a621ee6033ac661f7ded0abf3f2b4ea073a163b0c3154afa1`). Then add only [R39 source snapshot patch](../patches/stockfish16/R39-source-gate-tt-snapshot-readonly.patch), build a new separately hashed binary.

## Physical observational guard and exact experiment

Original Stockfish16 `TT.probe` refreshes `genBound8` on lookup. **Never add a second `TT.probe` at the registered source event**, as that is not passive. The R39 patch only reads the **already probed** `ss->ttHit, tte, ttMove, ttValue, ss->ttPv`, parent `statScore`, original source `posKey, alpha/beta`, original `rule50` and `nodes` from the actual existing source function. It records `C3X_R39_PRE` with primitive typed values. No TT entry is edited, no `std::hash` side effects or dynamic memory allocations introduced in the source search apart from source-event logging. Enabling logging occurs only when `C3X_R39_TT_SNAPSHOT=1` and the *original frozen* target source event is physically reached.

At each of **7 frozen cases × 3 source arms** `sham (F=0,N=0)`, `futility_only (F=1,N=0)`, `both_off (F=1,N=1)`, run:
- `R39 observer OFF` 1 fresh actual SF16 process, with all remaining C3X R33 flags matching the original P2 arm; assert same native public UCI, root best/producers, original R33 signed source OPEN/CLOSE, and no R39 PRE record.
- `R39 observer ON` 2 fresh actual SF16 processes, with **the same engine and targeted R33 flags**. Each must reproduce original P2 UCI/root/target CLOSE and have exactly one `C3X_R39_PRE` with correct event/key, and both cold repeats must have **byte-identical R39 PRE snapshot and native source stderr**. If observer-on changes the actual engine move, mark **OBSERVATION_INTERFERED** and withhold TT claims.

**Total prespecified new engine executions = 7 × 3 × 3 = 63.** Original game histories are not reselected and no new TT source probe is executed. Read-only CI builds and instruments original source; preserves source diff, compiler version, patched binary/NNUE identity and all original STDOUT/STDERR to private Drive.

### Exact observational questions and limits

1. Is the pre-futility `TT hit`/move/depth/bound/value/entry eval, `ttPv` and parent `statScore` the **same across sham/F-only/Both** for each original same source event? If not, physical event identity or observer is contaminated and claim is HOLD.
2. Do the seven source events involve an **already existing TT hit**, or a TT miss/replaceable slot? A *miss* does not imply that TT is unimportant downstream; a *hit* does not make the TT field causal.
3. Does a pre-futility snapshot correlate with later root changes? Since all seven are **post-outcome selected**, this is descriptive, not a predictor estimate or necessity/sufficiency demonstration.
4. **No post-event TT inference** without a separate safe instrumentation of TT writes. Importantly, the same physical TT slot may be reused for another key; a later raw pointer value would not certify same-position identity.
5. A future **actual TT/history/budget mediator restore/swap** must manipulate and reverse a specific state slice at an identified later search boundary with shams and complete causal trace; no such mediator restore is performed in P3-X3.

**Critical fail-closed boundary:** If patch does not compile/apply, original source UCI/producer differs, source PRE/OPEN identity mismatches, or the observer probes TT a second time, **retain failure and don't claim a verified source snapshot**. This protocol and source diff are committed before new R39 CI execution.
