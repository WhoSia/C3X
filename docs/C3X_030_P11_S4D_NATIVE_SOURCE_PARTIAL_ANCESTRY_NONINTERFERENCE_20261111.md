# C3X 0.30/P11-S4D — Read-only TT-Hit / Normal-Return / Root-Candidate Correlation Court

**Date:** 2026-11-11 KST, C3X 32, **software version unchanged: 0.30**. Scientific lineage: [D1 — native causal proof first](C3X_030_DECISION_D1_NATIVE_CAUSALITY_FIRST_20261111.md) → [S4A/S4B physical TT source interventions](C3X_030_P11_S4A_S4B_ORIGINAL_NATIVE_TT_SITE_MASK_AND_SHAM_20261111.md) → [S4C1/S4C2 one-hit null and same-binary dose results](C3X_030_P11_S4C1_S4C2_TT_HIT_DOSAGE_AND_MISSING_PAPERS_20261111.md) → **S4D read-only partial ancestry observation**.

## Decision

Do **not** call the earlier 3/6 masked root-move changes a causal child→parent→root transfer proof. The S4D goal is narrower and falsifiable: check whether original `search.cpp` can be *read-only instrumented* at (i) exactly the sealed ply-1 key TT probe, (ii) its regular/main-search normal-return value, and (iii) the root-candidate score-update site, without changing a matched original engine's move, depth, measured nodes, score or PV.

All three original target keys and full FEN/histories come from [the original S4-B raw JSON](https://github.com/WhoSia/C3X/actions/runs/42972990269) **SHA256 `081ee839f883d538081f1d2d15c43db1aa31cb12e4e713e1cda81815d5e59300`**, selected before S4D outcomes. They are previously inspected development positions, *not new unseen confirmation*.

## Real original native experiment

- Pinned upstream Stockfish16 `68e1e9b3811e16cad014b590d7443b9063b3eb52`; separate original and read-only logger source builds, SHA receipts in artifact. `Use NNUE=false`, `Skill Level=20`, `UCI_LimitStrength=false`, `Threads=1`, `Hash=16 MiB`, requested 12,000 nodes/search.
- [Source-anchored TT/return/root read-only patch generator](../harness/c3x_030_p11s4d_source_trace_patch.py) and [full native evidence and audit runner](../harness/c3x_030_p11s4d_native_ancestry_court.py), with **9 synthetic source/receipt tests**.
- Three prior FENs (Queen's Gambit ply4, Sicilian Najdorf ply4, English ply4) × two consecutive `go nodes 12000` per binary × two source variants = **12 ACTUAL original native searches, 144,166 actual nodes**.
- Strict original/modified outcome agreement on **bestmove, depth, actual node count, score and PV**: **0 differences across all six matched trial pairs**.
- Bounded source diagnostics actually recorded (all source events included in verified original JSON):

| Already-known developer source FEN | TT probe observations at sealed key | Normal-return observations at sealed key | Root-candidate score observations | Shared raw parent/root move codes |
| --- | ---: | ---: | ---: | ---: |
| Queen's Gambit ply4 | 22 | 14 | 180 | 1 |
| Sicilian Najdorf ply4 | 31 | 24 | 180 | 1 |
| English ply4 | 37 | 25 | 180 | 1 |

The 180 root observations per FEN reach the *bounded logger cap*, so they are NOT comprehensive root ranking over all iterations. The same raw parent move code as a root candidate provides **structural compatibility**, not verified dynamic value propagation. Most importantly, the normal-return source site covers only the final `return bestValue` path; **TT early cutoffs, ProbCut, other early returns and qsearch do not enter the logged normal-return stream**. Their absence from this partial record cannot be interpreted as absence of such actual search mechanisms.

The logger does **not** change TT hit flags, TT entries, root candidates or return values. It only emits stderr diagnostics. Actual root-causal interventions in this particular S4D run: **ZERO**; S4B/S4C preceding interventions remain separately archived.

### Gate provenance and failures

- First [failed original CI #42987551874](https://github.com/WhoSia/C3X/actions/runs/42987551874): main-search `return bestValue` anchor occurred at two original locations; source patch **fail-closed**.
- Second [failed CI #42987699926](https://github.com/WhoSia/C3X/actions/runs/42987699926): revised patch work did not yet match uniquely; evidence retained, no outcome-based target selection.
- Corrected anchor includes the uniquely identified normal-search-to-`qsearch()` boundary. [**Authentic native CI #42987751024 SUCCESS**](https://github.com/WhoSia/C3X/actions/runs/42987751024); 9 test cases pass, both native binaries compile, actual native outputs and physical event sites verified.
- Original S4D JSON **SHA256 `7309a9b6302bfeed405fbf2843a6b33d0140c9ac0ec2d794d2ae81f0`**, complete published GitHub Actions original ZIP **SHA256 `e9e2b6ee7ace5b7030cdbcba614c653aaafae84e49eb742d8d2e39f2d0834851`**.
- [Exact real native S4D source and output evidence ZIP preserved in Google Drive 04_SEALED_RESULTS_COURTS](https://drive.google.com/file/d/1pOMxyIXRSNTYKU6oZuH6MRT9z6ZxEurF/view).

## Mechanistic judgment — promote observation, NOT mediation

**PASS (restricted)**: at this exact pinned engine revision, 3 source FENs and fixed UCI protocol, real TT probe hits, normal-return values and root candidate updates can be observed *in one engine source* without changing final engine output. Matching raw root-parent move codes exist in each FEN. This supports building an actual dynamic correlation system; it does **not** yet constitute one.

**HOLD (not executed or not demonstrated):**
1. A TT-hit-specific *dynamic* child-return→parent-search-value update→root-candidate score propagation. S4D lacks per-invocation stack instance IDs, early-return capture, and temporal identity linking; raw move code equality across iterations can falsely join distinct executions.
2. Single exact TT entry causal effect, replacement validity and per-probe store-to-load ancestry (source hit mask is keyed position and hit flag, not independently identified physical table slot).
3. The reason high-dose masking affects root choice while 1/2-hit masking in S4C does not: a return-value-mediated explanation requires same-binary paired intervention + full before/after trace, not independent observational source excerpts.
4. Independent preregistered unseen positions; 3 FENs are inherited development examples.
5. Full strategic plan robustness and human education effect; this used classical evaluation and 12K requested nodes, not a prospective learning design.
6. Historic 0.29 prospective cohort **7/8 HOLD**, denominator not redefined.

## Next architectural decision

**P11/S4E — Dynamic invocation and edge trace** should assign per-node *unique invocation IDs*, parent invocation IDs, complete main-search return exit categories, root move + relevant alpha/beta before/after fields, and a bounded lossless audit stream per query. First establish noninterference against original native Stockfish. Only then repeat the predeclared same-binary TT dose intervention with the *same logging patch* for sham and target and reconstruct specific `TT-hit → node return → parent update → root move` records, rejecting missing edges and stopping on partial traces. Independently predeclare new full-game histories before any generalization claim.

This avoids mistaking source-probe observability, raw move-code overlap or root bestmove changes for a causal explanation of a long-term strategic plan. Keep negative results and fail-closed source patch history.

## Research corpus status

No new C3X original source files acquired in this S4D code cycle; prior **Gadwal et al. (1993)** 36-page author manuscript is held in [Drive 10_PAPERS](https://drive.google.com/file/d/1iRfADIUxHmiVD4vOEVsaTAZw2ivYtFcy/view). Missing actual original texts remain Björnsson 2024 survey, Bratko/Kopec 1982 original book chapter, Herbeck/Barth 1996 paper, Demura/Kaneko 2024 final article, subject to lawful author-manuscript/library access. Gadwal 1993 publisher typeset variant remains an edition-comparison HOLD, not content missing.
