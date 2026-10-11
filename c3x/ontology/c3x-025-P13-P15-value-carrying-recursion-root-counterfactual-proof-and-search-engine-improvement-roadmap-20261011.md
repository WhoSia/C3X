# C3X 0.25-P13–P15 — From Actual Recursion Returns to Causal Search Science and Independently Stronger Engines

**Research programme charter recorded 2026-10-11 after P11/P12 original exposed native evidence, BEFORE P13 native value-assignment source intervention.** P11 successfully recorded native TT actual bound returns 24/24 with original full64 score-field writer, SEE guard 24/10 true continue-prunes, root score updates20; P12 recorded the same 24 TT actual return events and 24 true direct C++ caller stack exits with unique frame IDs (cold-parity original b1c3 and 8657 nodes). These observations are strong micro-operational facts, **not** a complete TT→SEE→root unique mediator chain.

## New theory: value-carrying source graph
Define a dynamic execution trace `G=(V,E,id,parent,source_state)`, where `V` are actual native search/qsearch calls and executed field events. Types of edges:
- `W`: original full64 verified field writer → native TT slot reader,
- `R`: actual branch-triggered `return ttValue` → immediate C++ caller (P12, certified in 24 source examples),
- `A`: actual caller `value := -search(...)` or `-qsearch(...)` assignment, witnessed at the **source call site** with unique child call ID, source score, negamax sign and declared alpha-beta/depth/retry state,
- `D`: the assigned value participated in actual parent `bestValue`/candidate comparison and update or cutoff,
- `S`: native original deterministic `see_ge` with exact occupied/threshold, branch guard result, executed continue/fallthrough **on that same causal descendant or counterfactual alternative**,
- `U`: actual root candidate score/PV change, iterative deepening/rescore/retry, selected `bestThread->rootMoves[0]` and literal final UCI.
By definition, the presence of `W,R,S,U` without `A,D` on the **same uniquely identified path** is not a causal mediation certificate. Same root id alone is insufficient.

**Core challenge:** a return value can be delivered to a caller but then not alter any selected candidate (fail-low), may produce a cutoff before any SEE, or may be overwritten by another return. A solver must classify every observed return by actual downstream *uses*, not by the eventual final UCI alone. Both observed root changed and unchanged outcomes can mask intervening effects (P6 compensation theorem).

## P13 source-native tests
1. Enumerate all pinned upstream SF16 `search.cpp` active **negamax child-call assignment sites**, including qsearch, LMR scout/PV full searches, null-move, ProbCut, verification and singular branches. Freeze their source anchor SHA and exact counts before per-site observation; only explicitly instrumented sites are covered, others **CENSORED_SITE**.
2. At actual original call site bracket child's frame exit and the caller's returned `value` assignment without changing operator/evaluations. Source tag must include `child_call_id, parent_call_id, call_site_id, original_child_return_score, parent_assigned_negated_score, parent_original_alpha/beta/depth/PV`; enforce sign `parent_assigned=-child_return`, except explicitly transformed/saturated score conversions.
3. Instrument exact parent `bestValue` and candidate update paths and root score update after child returns; no path may be spliced from distinct cold runs, search iterations, root candidates or TT epochs. Prefix cap is **per operator class** with explicit censor, not a single global first-N log; a watch targeted to a known original code site is allowed only if fixed before observing the native results of that new experiment.
4. Certificate: `W→R→A` is a native *value dataflow* witness. `W→R→A→D→U` is an actual native value-to-root propagation witness (if the unique exact chain really occurs), but **still not** a causal *mediator-specific TT→SEE natural effect* without controlled mediator interventions and rival path exclusion.
5. SEE: `S` on a different stack sibling with same root ID does not qualify. If a TT return occurred before SEE in one traversal, it cannot be retroactively attributed to SEE that follows later unless a genuine counterfactual TT intervention changes that descendant activation and exact native state matching is verified.

## P14 causally identified frontier bifurcation
- In original same-position matched cold actual source states, preregister narrowly targeted TT field consumer/score-only vs move-order-only vs TT-refresh separate *real interventions* and paired sham, with full return/writer/guard/SEE source provenance and causal graph where possible; never mutate SEE Boolean itself unless explicitly labeled a non-natural forced-operator manipulation.
- Partition `ROOT_CHANGED` and `ROOT_STABLE` cases; require multi-depth baseline root contenders, aspiration windows and root candidate survival/eviction.
- Design negative controls: a different-root-order scorer with no same-order survival (September#107); a same-order repeated contender that loses at depth12 (July#52). These remain **exposed development** examples and cannot be used as unseen M5 tests.
- Distinguish actual source causal mechanics (source-policy perturbation changes the root on controlled tests) from observationally underidentified *natural* TT→SEE mediation; even native full execution graphs require interventions/assumptions for natural indirect effects.

## P15 broader technical ambition and independent engine evaluation
- A "mechanism-aware TT controller" is a *hypothesis* only; optimize move-hint choice, score-bound usefulness, generation refresh, and replacement separately with reversible source-pinned patches; ensure no illegal chess semantics, fragile self-mate, repetition, rule50 or tablebase regression.
- Separate hardware/performance courts: matched native nodes, search speed, memory/TT occupancy and warm/cold cache, plus independently sourced legally licensed opening-paired colour-swapped strength matches with preregistered stop and uncertainty. Minimum 100 opening pairs is **necessary but not sufficient for practical Elo claims**; power analysis, sequential boundaries and repeated seeds are required.
- Scientific prediction court: a new M5 exact UCI forecaster is separate from technical engine performance; new source originally selected without engine, SHA and FEN4 disjoint checks, complete literal UCI human Git seal before any TT-FIRST intervention, group clusters by game/event and preserve NEGATIVE.

**Current boundary 2026-10-11:** P11 and P12 are actual native successes with limited visibility and unmeasured engine performance; no full P13–P15 native experiments or prospective model improvement have been conducted. Human WhoSia Git commits, Actions read-only, official SF16 GPLv3 and Lichess rights preserved.
