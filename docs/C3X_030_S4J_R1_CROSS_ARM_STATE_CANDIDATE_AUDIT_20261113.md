# C3X 0.30 — S4-J/R1 Cross-arm Search-State Candidates and Archived Re-verification

**Date:** 2026-11-13 KST. **Conversation:** C3X 33. **Research version:** 0.30 (not 0.33). Previously sealed 0.29 7/8 prospective-cohort HOLD and 0.30 S4-H2 eight-game untouched holdout remain unchanged.

## Question and design

Can genuine native TT early-return events in Sham versus two-hit masked Stockfish searches be paired by search state rather than by **run-local invocation IDs**?

Patch anchored to Stockfish16 original commit `68e1e9b3811e16cad014b590d7443b9063b3eb52`, reused exact original S4-H2/R2 frozen TT keys and legal development positions. Both sham and two-hit arms use the **same patched binary**, and the third arm is the true original upstream binary. Fixed 2 trials/arm, 12000 nodes/trial, NNUE off, one thread and fixed Hash. Only 8 **development** FENs from 4 researcher-authored games were used. No holdout case opened.

Source-level fingerprint for each bounded early TT `return ttValue` event:
`(position TT key, search depth, alpha, beta, ply=1, PV flag, cut-node flag)`.

Two state fingerprints are treated as **unique candidates** only when each occurs exactly once in its respective *observed* arm trace. Repeated occurrences are marked ambiguous, never arbitrarily assigned by ordinal or event ID. Differences in values within candidate states are descriptive, not causal mediation proof. Fingerprints are not full legal-history identity: excluded-move status, path/history, search stage and TT table contents may differ. Moreover two consecutive search trials share a process, and events are bounded (8 per arm process). Therefore all matches are **candidate**, not identified cross-world invocation IDs.

## Actual real native experiment

- Native [S4-J successful run #43354844857](https://github.com/WhoSia/C3X/actions/runs/43354844857): **48 new Stockfish searches, 576,619 nodes**, eight regression tests PASS; every original–sham noninterference comparison PASS.
- Raw native JSON SHA-256: `cdfa9d7ba18052a8fee19905c864883f68adb4bda30809da0a4719bb6f60c6d8`.
- [S4-J original immutable Drive ZIP](https://drive.google.com/file/d/1ZurLY2ATvZGzjaL9aB5uiCu5125NOIbl/view).
- Two initial failed CI executions [#43354672806](https://github.com/WhoSia/C3X/actions/runs/43354672806), [#43354695644](https://github.com/WhoSia/C3X/actions/runs/43354695644) are preserved. The latter exposed a too-strict source assertion that expected exactly one `return ttValue` throughout Stockfish search.cpp, although other search functions may also return that expression. Replaced with a specific anchored event-site assertion; exact original patch site remained unchanged.

| State trace category | Observed |
| --- | ---: |
| Sham TT early-return log events | 41 |
| Two-hit TT early-return log events | 44 |
| State fingerprints appearing in both arms | **25** |
| Unique-in-both-arms candidates | **21** |
| Repeated/ambiguous candidates | **4** |
| Different return values among 21 unique candidates | **0** |
| Two-hit root bestmove changes over 16 searches | **3** |

Saturation caveat: each original native process logs at most eight TT early cutoffs, with two trials per process; the event totals are **bounded log counts**, not complete search-tree event totals.

### Focus on root-changing cases

| Position | Two-hit root changes | Unique candidates | Distinct candidate return values |
| --- | ---: | ---: | ---: |
| Italian ply 10 | 2/2 | 0 | 0 (no candidates; traces saturated at 8 in each arm) |
| London ply 8 | 1/2 | 1 | 0 (the single shared candidate retains its return value) |

A newly observed TT early-return event can occur after masking; however this cannot yet prove that an event absent from the bounded sham trace would have been absent from the full sham search. A matching signature can describe a distinct historical context; score equality of matched candidate events cannot establish unchanged causal influence.

## Independent archived-byte audit

[S4-J/R1 success #43355260989](https://github.com/WhoSia/C3X/actions/runs/43355260989): separate read-only CI recovered the original S4-J ZIP artifact, required exact immutable native JSON SHA-256 and **recomputed every candidate match** from original event arrays instead of accepting the stored aggregate counts. Six fail-closed mutation regression tests PASS. Independently reproduced:

`sham=41, two=44, shared=25, unique=21, ambiguous=4, changed_values=0, root_changes=3`.

New native searches: **0**. Audit result JSON SHA-256 `70861ea784ab2a26bdb3302fbf8076e64a7530521f063722c17062b04c56800d`. [Drive R1 independent audit ZIP](https://drive.google.com/file/d/1_QqtzXPud9O8mNw9OxBHRetRIJNCZso_/view).

## Scientific inference boundary

**PASS:** Actual source-native bounded TT cutoff state fingerprints; reproducible cross-arm candidate comparison; noninterfering original–sham controls; precise original-archive re-audit.

**HOLD:** Complete main-search/qsearch return coverage; disambiguated invocation ancestry between runs; the exact TT-cell causal mediator in root-choice changes; representative population sampling; independent holdout validation; source computation ↔ response-robust future chess plan join; superior explanation quality versus existing papers; original 0.29 prospective 7/8.

Finding: **all 21 unambiguous observed candidate states returned identical values**, even while three root decisions changed under two-hit masking. This does not imply a mechanism was found. It localizes the next measurement need to absent/unmatched or unobserved paths and root updates, especially the saturated Italian ply-10 trace.

## S4-K preregistration proposal (NOT executed)

1. Add legal root-branch move identity, excluded-move flag, and return reason to the source-local state record. Record whether each event occurred in trial 1 or 2, since ordinal counters currently span a two-search process.
2. Restrict additional logging to specific affected root branches and preserve exact source physical mask contacts. Log the corresponding parent/ancestor score-update sites with explicit known-value flags, while keeping separate processes and never equating same ordinal with the same invocation.
3. Detect evidence truncation: report precise total events observed versus logged, retain SATURATED/UNKNOWN rather than a false negative. Compare original–sham results for complete equality and abort if instrumentation drifts.
4. Define an edge-level claim taxonomy: SOURCE_MASK, SEARCH_STATE_CANDIDATE, WITHIN_RUN_SIGNED_EDGE, CROSS_ARM_VALUE_CHANGE, ROOT_BESTMOVE_CHANGE. Require separate explicit evidence gates, including absence of confounding re-search state, before using the term causal mediation.
5. Only after a separately SHA-locked S4-K development protocol and successful negative controls consider the 8-game held-out cohort. Do not use holdout data for selecting a mechanism.

All commits are written via user GitHub connection as WhoSia; GitHub Actions never commits.
