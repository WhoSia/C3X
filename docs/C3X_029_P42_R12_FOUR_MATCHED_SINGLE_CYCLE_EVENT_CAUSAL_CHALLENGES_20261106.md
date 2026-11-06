# C3X 0.29-P42/R12 — Exhaustive Four Original Cycle Cutoff Events, Isolated One at a Time

Date: 2026-11-06 KST. **Source-target and selection criteria frozen before native R12 outcome is read.** An explicitly source-native experimental chapter toward the difficult causal-computation↔chess-strategic-future link, not a publication on a trivial metric.

## The empirically supported causal frontier

Original pinned Stockfish16 `68e1e9b3811e16cad014b590d7443b9063b3eb52`, Game14 postselected, NNUE OFF. A=b3a4; B=TT_FIRST f3f4; C=one specific source `capture_prune` guard bypass b3a4; R8 targeted descendant TTEntry::save writes are not necessary under physically tested intervention; R5 targeted child score fails to directly improve parent `bestValue`. R9 and R10 verified that a *broad* change to the original cycle-alpha `value_draw` callsite (the early `alpha=value_draw(); if(alpha>=beta)return alpha;`) restores B=b3a4, while the other terminal draw return caller is unvisited in actual Game14.

R11 [actual original native source run #42177462049](https://github.com/WhoSia/C3X/actions/runs/42177462049) succeeded, with direct ZIP/JSON SHA custody [sealed manifest](../evidence/C3X_029_P42_R11_NATIVE_CYCLE_WINDOW_RECEIPT_MANIFEST_20261106.json). Real immediate source cutoffs per cold: original A **364/380**, original B **552/562**; globally cycle-neutralized A **288/288**, B **288/288**. Original B versus B-neutral first **33 identical native pre-return source-event states** (position key, ply, depth, root move, incoming alpha/beta), with **33 changed returned draw scores and 4 changed source-level immediate cutoff decisions** in each cold replay. This is precise native algorithmic evidence but doesn't identify the natural root mediator.

## R12 precommitted intervention and scientific decision

**Select ALL four original B source events within those first 33 source-matched windows** for which replacing the actually returned `-1` or `+1` by `0` changes the truth of the original `candidate >= beta` branch. The four source event ordinals must be derived mechanically from a fresh unmodified B engine cold run; require both independent cold controls to select exactly the same four. This selection is **root-choice-blind and exhaustively covers the specifically identified eligible first-prefix events**, not a new bestmove-based candidate discovery or a claim about all 562 source cycle events.

R12 source overlay [`tools/c3x_029_p42_r12_single_cycle_event_intervention.py`](../tools/c3x_029_p42_r12_single_cycle_event_intervention.py) uses one **shared thread-local ordinal across Stockfish16's Root, PV and NonPV template instantiations**. Only event ordinal `C3X042_R12_TARGET_ORDINAL` in a fresh cold engine process replaces the original cycle-alpha `value_draw` return by `VALUE_DRAW=0`; all other original source evaluations and returns, game setup and TT reader actions remain native, except follow-on consequences of the one event. The event is not selected after seeing its root move. Source R11 event/window and source R10 actual original value return remain privately recorded and compared to baseline. `0` or absent selector means ordinary control, not perturbation.

Source ancestry controls: original B cold baseline must choose `f3f4`; the exact four event IDs chosen twice must agree; the source before the chosen event must have identical actual position key, ply, depth, node mod 4, root context and incoming alpha/beta; at the chosen event, the native draw candidate becomes `0`, and immediate cutoff flips. If any other event in that original prefix differs in its return, if actual source event is absent, if the exact physical TT reader is not present, if source keys/alpha windows drift before target, or if original frozen source SHA/StageA input fails, **HOLD** without mechanistic claim.

All four selected calls are separately intervened and each replicated **twice**, preserving unrestricted root choice support, including a novel third move. A single-event B→b3a4 reversal would show **functional single-event sufficiency for this source-specific move outcome under that intervention**, but not unique natural mediation. If **all four individually fail to restore B**, the broad R10 source-site restoration cannot be reduced to any of those four single early cutoff differences individually (though it may depend on their combination or on later events); that would be a substantial negative mechanistic result. Every mixed/null case is retained.

The new [source runner and outcome court](../harness/c3x_029_p42_r12_native_single_cycle_event_court.py), [immutable derived Stockfish native build](../tools/c3x_029_p42_r12_derived_original_single_cycle_build.py), [source tests](../tools/test_c3x_029_p42_r12_single_cycle_event_intervention.py) and [adversarial causal court tests](../harness/test_c3x_029_p42_r12_native_single_cycle_event_court.py) are designed. Read-only Actions [run #42178768272](https://github.com/WhoSia/C3X/actions/runs/42178768272) ran initial source tests and started actual source compilation on initial inspection. Earlier run [#42178655046](https://github.com/WhoSia/C3X/actions/runs/42178655046) failed at a test fixture missing the shared source state anchor, a **test fixture defect**, preserved and corrected; not a chess causal negative. R12 actual root outcomes are **unknown at document pre-registration**.

## Why this is not the final chess paper

Even after event-level source-specific single-state intervention, the dynamical search can branch and write TT or history state, altering other routes. Showing an executable source cause in a selected old Game14 does not show that the computation corresponds to objectively strategically valuable chess futures. A respectable full paper must further (i) prove actual downstream value/window/root path, (ii) challenge alternative causal routes with orthogonal interventions, (iii) relate computation to *independently evaluated adversarial responses and plans* with strong Cui-style k=3 partial-tree/BinProp baselines, and (iv) prospectively generalize to independent games. Original Game14 remains source-historical, NNUE OFF. No “novel C3X strategic explanation” claimed from R12 alone.

No modified GPL engine binary, raw game PGN, source Zobrist keys or private search trace is shared. GitHub WhoSia human author/committer, Actions `contents:read`, Notion semantic truth, Drive original bytes after verified mirror only.


## 2026-11-06 — VERIFIED REAL NATIVE SINGLE-EVENT RESULT (after predeclared protocol)

Read-only [native R12 success #42179676099](https://github.com/WhoSia/C3X/actions/runs/42179676099): exact pinned Stockfish16 built, immutable 16-case Stage A SHA reproduced, original Game14 B source/TT reader physical provenance confirmed, source parity/source window tested, each of **all four eligible first-33 original B-cycle events** independently perturbed with two `cold()` invocations. `cold()` invokes **two distinct native engine `play()` subprocesses**; R12 validates both physical traces are identical and that the one event is changed exactly once **per physical process**.

**Predeclared 4 candidate source ordinals from actual B original native source, prior to probing any root outcome: [30,31,32,33].** Actual controlled root moves:

| Native real single-cycle `value_draw` intervention in B | 1st cold() | 2nd cold() | Source pre-target key/window identity |
|---|---|---|---|
| no intervention, original TT_FIRST B | f3f4 | f3f4 | original |
| event #30 only | f3f4 | f3f4 | source-exact PASS |
| event #31 only | f3f4 | f3f4 | source-exact PASS |
| event #32 only | f3f4 | f3f4 | source-exact PASS |
| **event #33 only** | **b3a4** | **b3a4** | **source-exact PASS** |

This is **nontrivial executed-source single-event functional sufficiency** for this postselected old source program: changing just the 33rd original B `cycle-alpha` caller's returned draw value to `VALUE_DRAW=0` changes the unrestricted root bestmove from f3f4 to b3a4. The 30th/31st/32nd are genuine source-matched local cutoff changes but alone did not move the final root. Therefore a changed immediate cutoff is **not sufficient in general** to change the final root, and the fourth event is particularly consequential in this native run.

**The conclusion remains bounded**: the source change affects subsequent execution, which may pass through many new TT/search/history routes; R12 does NOT demonstrate the exclusive natural TT_FIRST→capture-guard→cycle event→root path or prove a chess strategically superior choice. There is no prospective heldout chess or NNUE-on evidence. A source-computation reason is not yet a human-understandable future-plan reason.

**Original artifact direct custody:** [public source-native ZIP #13484737380](https://github.com/WhoSia/C3X/actions/runs/42179676099/artifacts/13484737380) was separately downloaded and its JSON parsed. ZIP SHA256 `e497f08d8260e7e896d688f10d0fa9d8d6eed782f39918360a190792d1617a5e`, actual `C3X042_R12_SINGLE_SOURCE_EVENT_CAUSAL_COURT.json` member SHA256 `635ba63a784af37f8ae7199abaa6457c47208e41b2905984ec50a4aa0505b39c`. [Human-authored permanent receipt manifest](../evidence/C3X_029_P42_R12_SINGLE_CYCLE_EVENT_NATIVE_RECEIPT_MANIFEST_20261106.json). Raw source keys, TT history, search private event traces, original personal PGN, modified GPL binary remain undistributed.

### Native CI negative history and a serious provenance repair

- [R12 #42178655046](https://github.com/WhoSia/C3X/actions/runs/42178655046) failed synthetic fixture missing a shared counter anchor; test bug.
- [R12 #42178768272](https://github.com/WhoSia/C3X/actions/runs/42178768272) compiled/verified Stage A but failed source return check.
- [R12 #42179150643](https://github.com/WhoSia/C3X/actions/runs/42179150643) showed target ordinal 30 selected by the frozen rule, but reported an apparent second source mutation at combined log ordinal **311** (30+281). Direct inspection of original `harness/c3x_023_P1_R2_T0_chronological_post_TT_common_SEE_dev.py` revealed that **each `cold()` calls original `play()` twice in separate engine processes** and checks deterministic equality. The apparent second mutation was **the same real local 30th event in the second physical process**, not a surprise causal contact. The previous parser falsely treated two native processes as a single source ordinal stream. Revised R12 splits each double-native trace and demands byte-equivalent event identities before proceeding; early technical failures kept.
- [R12 #42179676099](https://github.com/WhoSia/C3X/actions/runs/42179676099) passed all source/physical provenance and measured the functional single-event root result above.

### R13 hard mechanistic priority

The source level now has a concrete intervention, not merely a correlation. **The next challenge is to trace the 33rd cycle-alpha event's changed cutoff through the actual ensuing full search and each root candidate competition**: compare root iteration boundary, TT reader/writer effects elsewhere, history/order updates, aspiration retries and source score bounds, while retaining source-identity correspondence only where valid. The original pre-selected C-arm capture-prune guard bypass and this B-arm cycle modification both restore b3a4 but that shared final action **does not establish the same natural mediation**. Only after mechanistic transport is identified should an independent chess judge test whether the computation reflects a meaningful adversarial future.
