# C3X 0.29-P42/R5 — Game14 Source-Exact Local Causal Spine: Native Experiment Started, Full Mechanism Not Yet Established

**Date:** 2026-11-05 KST. PI technical report. **This is a genuinely new original-Stockfish experiment implementation and launched read-only Actions attempt; not a reported successful new native result.**

## Scientific question—not a proxy paper

The central challenge remains to link a computational cause of a chess move to its independently justified strategic meaning. Before that deep bridge can be attempted, recover what the source-activated single capture-pruning guard actually changes in a value-bearing execution. Game14 historical three-arm causal reversal was already observed in native Stockfish16 [0.27 Memo03](C3X_027_MEMO03_SOURCE_EXACT_CAPTURE_GUARD_CAUSAL_REVERSAL_20261020.md); do NOT claim that this R5 discovered it. Root results A b3a4, B (TT_FIRST) f3f4, C (TT_FIRST plus one source-exact capture_prune guard bypass) b3a4, in historical two-cold replay. The single event exists only in B/C search, so natural TT→guard→root mediation is not identified by treating the nonexistent A-world event as a fixed mediator.

## Actual earlier source tools audited and retained

- `tools/c3x_024_P2_passive_native_descendant_lineage_overlay.py` traces actual `DO_MOVE_EXECUTED`, `CHILD_ENTERED`, `CHILD_RETURNED_TO_PARENT` from exact T3/T4 site, but these cover **quiet_prune** and **qsearch_prune**, not Game14's `capture_prune`. It cannot be relabeled a Game14 success.
- `tools/c3x_024_P2_R2_passive_ancestor_root_value_overlay.py` adds source `PARENT_CANDIDATE_VALUE`/frame returns for that prior prepatched T3/T4 chain; this does not establish final winner causality.
- `tools/c3x_025_P13_R4_original_writer_to_q_assignment_overlay.py` has valid qsearch original writer-to-parent evidence on its own source chain, but cannot be grafted blindly into this Game14 overlay chain.
- Exact original Game14 build recipe `tools/c3x_027_sept_capture_counterfactual_build.sh` applies source patches in strict order and pins official Stockfish16 commit `68e1e9b3811e16cad014b590d7443b9063b3eb52`. We do not modify this source recipe, prior case registration or original experiment code.

## New R5 real native source instrumentation (not merely proposed)

`tools/c3x_029_p42_r5_game14_capture_local_lineage_overlay.py`: a passive C++ source-anchored overlay inserted after the prior exact single-capture guard bypass and before the native build. It arms only when the C3X027 intervention actually re-enables that one source-matched capture-pruned candidate, then records:
1. `GUARD_FALLTHROUGH` at exact targeted guard with source parent/child keys and root-call identity;
2. `ACTUAL_DO_MOVE` only for the same Stack frame/move and expected actual child position;
3. `MAIN_CHILD_ENTERED` or `QSEARCH_CHILD_ENTERED` only at child Stack +1 and child key;
4. `CHILD_RETURNED_TO_PARENT` with the actual searched value after possible PV re-search and before undo;
5. `PARENT_VALUE_ASSESSED` only in the parent after original legal position restoration and stop check;
6. optional `PARENT_BESTVALUE_ASSIGNED` only inside the source `if(value>bestValue)` assignment.

Private raw trace uses **C3X042_R5_LOCAL_TRACE** (not historical `C3X027_CAPTURE_BRANCH_LOG`); private TT keys are never placed in uploaded public receipts. The new overlay does not independently instrument all recursive ancestors, root candidate ranking or chess meaning. Its presence must not be confused with successful engine compilation or source execution.

`tools/c3x_029_p42_r5_derived_native_build.py` derives a temporary build script from the exact old 0.27 recipe by injecting the passive R5 overlay before native make. The historical build script remains unchanged and the SHA of both recipes is retained locally.

`harness/c3x_029_p42_r5_game14_local_spine_court.py`: fail-closed trace court checks source event identity, expected ordered native events, key/frame transition, child score→parent assessment agreement, optional source bestValue assignment, two separate cold replays and no extra local event. Output is PUBLIC aggregate status only, never raw key or full source history.

`harness/test_c3x_029_p42_r5_game14_local_spine_court.py` authored 12 synthetic negative/positive regressions. **Source authored, test PASS not yet witnessed at record time.**

## Source anchoring verified separately

The six main/qsearch non-mutated source anchor strings (`MAIN_DO`, `MAIN_UNDO`, `MAIN_STOP`, `MAIN_ADOPT`, `MAIN_ENTRY`, `Q_ENTRY`) were located **once each** in authentic original pinned official Stockfish16 `src/search.cpp` through authenticated GitHub fetch. That check alone does NOT prove the exact fully layered build will compile; older overlays may change an anchor, or a runtime site may not be reached.

## Source-exact nuance discovered on follow-up: bestValue is not root choice

Original pinned Stockfish16 `search.cpp` handles a returned candidate by first checking `if (value > bestValue)`, assigning `bestValue=value`, and **only then** checking `if (value > alpha)` to modify `bestMove`, maybe cut off on `value>=beta`, and/or update `alpha`. Therefore:

- Seeing an actual `PARENT_BESTVALUE_ASSIGNED` is **not equivalent** to alpha crossing, parent bestMove replacement, or ultimate root candidate victory. A source child may improve a fail-low node's bestValue while leaving alpha and local bestMove untouched.
- R5 local court now reports two-replay window-relation classifications of the actually compared numeric value against alpha/beta, and explicitly distinguishes `bestvalue_only_assignments` from `parent_alpha_crossings`.
- These are **local numerical search-window relations**, not verified exact chess values, nor final engine decision explanations. Fail-soft bounds and aspiration re-search require their original provenance, depth, type and entire dynamic execution to make stronger claims.
- A new 12th synthetic regression intentionally constructs a bestValue improvement **without** an alpha crossing, and verifies that the court does not collapse the two. New tests remain authored/pending actual Actions execution, not a new PASS.

**New decisive integration gate:** original A/B/C bestmove identities, one-event source physical contact and cold replay must all be reproduced by native historical harness *before* local spine admission. Earlier R5 workflow classified rather than asserted `ORIGINAL_ROOT_RESTORED`; this was corrected in commit `c2347261` and recorded as a design repair, not a fresh native experiment.

## Falsification-first outcome interpretation

- **No exact bypass event**: original R5 source alignment FAIL/HOLD; not a causal witness.
- **Bypass but no do_move**: the bypassed candidate still did not enter an ordinary executed source move; do not claim searched new child.
- **Do_move but no child entry/return**: incomplete or uninstrumented source path; explicitly HOLD.
- **Child returned, no parent assessment/assignment**: no local value-adoption proof; possible secondary TT/order/re-search route must be investigated.
- **Child score assessed but not improving parent bestValue**: no positive local bestValue assignment. It can still influence later execution indirectly; cannot say it directly won parent competition.
- **Actual parent adoption**: one real value-bearing local edge, still **not full ancestor→unrestricted root mediation or unique natural TT mediation**.
- **Any root move differs from historical A/B/C, or StageA SHA changes**: non-interference FAIL; do not posthoc replace historical case or quietly change the target.

## Real execution status, chronology

1. Read-only source-local syntax/synthetic test workflow [42040472157](https://github.com/WhoSia/C3X/actions/runs/42040472157) was **QUEUED** as last checked. No PASS claimed.
2. Initial native workflow [42040835703](https://github.com/WhoSia/C3X/actions/runs/42040835703) **FAILED BEFORE JOB START** because an unquoted colon in the YAML step name made the workflow invalid. Preserve this technical failure; it is not an engine/causal falsification.
3. Corrected native workflow [42041087886](https://github.com/WhoSia/C3X/actions/runs/42041087886) **QUEUED** at last check. Do not claim compiled binary, native path, restoration or confirmed positive local path until original logs are downloaded, checked and compared with the source SHA, game SHA and two cold trials.
4. Workflow permissions `contents: read`; actions do not commit/push/tag. Only aggregate public artifacts permitted; private player source/physical TT keys, full game history and GPL-modified engine binary not uploaded.

## Novelty/meaning: still HOLD

Even if the R5 local chain passes, the research question of why the resulting search prefers the strategically meaningful root move remains open. External legal chess consequences for b3a4 vs f3f4 require source-specific opponent response study, independent value adjudication and, for actual engine 'reason', computation-to-semantics alignment. No substitute mobility/short-horizon mate/low-regret paper is authorized as the flagship claim. Newly planned experiment must ultimately distinguish guard-mediated value flow from alternate TT/aspiration compensation and demonstrate prospective transport to new game/event-disjoint sources.

**Research OS:** Notion semantic; Drive original bytes; GitHub executable code and receipts. Human `WhoSia` author/committer only; no `github-actions[bot]` commits. Research version remains C3X 0.29 P42/R5; no 0.30 or paper PASS at this stage.
