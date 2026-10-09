# C3X 0.15 P10 — Root-Candidate Mutation and Aspiration Re-search Provenance (PRE-OUTCOME)

**Date** 2026-10-09. C3X 0.15 remains live alongside C3X 0.16's new question. This P10 **does not become 0.16 independent multi-motif validation**.

## Problem
P7/P8/P9 show exact two TWIC roots (#2, #29) change root bestmove or evaluated score under root-object SEE and source-local TT/qsearch interventions. P8 logs first UCI-reported per-depth PV changes, but a PV report is downstream of source candidate updates and aspiration re-search: it is **not** the first internal causal branch and cannot prove specific TT-to-root necessary mediation.

## Original source and preserved arms
Original SF16 upstream `68e1e9b3811e16cad014b590d7443b9063b3eb52`, provenance-instrumented P8/P9-A1 stack. TWIC source R2, P2, P6S0, P6S1, P7, P8, P9-A1 input SHA-256 remain frozen; original two P6-outcome-exposed game worlds only. Fixed Threads1, MultiPV1, Hash16, depth12, Use NNUE=false. Limit at least 2 cold native processes per SEE OFF/ON × I,V,B,G,W,L for 48 searches, or report missing arms and do not call whole P10 pass.

## New passive ROOT instrumentation
1. Log at **each RootNode candidate score assignment** *in the actual SF16 C++ search function*: full source root key, actual root iteration/depth, native Move ID, root move ordinal, score returned by child, consumer alpha/beta before subsequent update, candidate score before/after, and whether current root PV assignment occurred.
2. Log after each root aspiration/re-search stable sort: root key, root depth, PV index, front move, score, score returned by search, alpha/beta window and event ordinal.
3. Log actor/source build, cold process, event count, retained first 1024 events, truncation count and digest. Do NOT alter move order, sorting, TT, alpha/beta, score, root selection or legal move generation.
4. For matched original and intervention, align events first by search iteration/depth, native move and event type rather than naive event-count ordinal only. Distinguish earliest **same candidate changed score**, **different candidate visit/order**, **different alpha/beta**, **post-sort front move**, and **reported per-depth PV**. If sequence alignment is ambiguous, `ALIGNMENT_AMBIGUOUS` and no assertion of first causal cut.
5. Preserve exact P9-A1 final core tuple (bestmove, score kind/value/bound tag, nodes, PV) and original P7/P8 target exposure for all twelve conditions plus exact two-cold repeat. If any passive tracing changes previous results: `FAIL_OBSERVER_NONINTERFERENCE`.

## Scientific question
A first observed root-candidate score difference is a narrower **execution provenance** than first UCI PV divergence. But it is NOT automatically the **first necessary cause**: to promote to `MICROINTERVENTION_IDENTIFIED`, independently manipulate the specifically aligned candidate update or aspiration re-search site with source-identified bounds and matched shams, and verify the root outcome under a separate precommitted gate. Event truncation defeats claims of global earliest event.

## Status and opening
`P10_ROOT_CANDIDATE_TRACE_PRECOMMITTED / NATIVE_NOT_YET_RUN / C3X015_CONTINUES / C3X016_SEPARATE_OPEN / TT_FULL_NATURAL_MEDIATION_HOLD`. Preserve P1 C1 primary 42/64 vs B0 53/64 FAIL.
