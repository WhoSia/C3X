# C3X 0.29-P42/R8 — Targeted TT Write Side-Effect Necessity Experiment (Predeclared Native Four-Arm Court)
Date: 2026-11-06 KST. **Experimental implementation / hypothesis commitments frozen before the native R8 outcome is known.** Not a completed result at creation. This is support for the difficult causal–strategic chess explanation program, not an easy separate paper.

## Motivating native discovery (R7)

Authentic source-locked, original September 2026 Game14 TT_FIRST/root reversal (A b3a4, B f3f4, C one actual capture_prune guard bypass b3a4) was reproduced in new native R5 **#42153949082** and R6 **#42154152915**. The new actually executed C-arm targeted descendant produced `parent_assignment=0/2` and `value>alpha=0/2`, despite a complete guard→do_move→child entry→return→parent assessment in 2/2. The original C3b source candidate edges to a root candidate were observed 3 per run (2/2) and the first B/C iterative-deepening boundary difference occurs depth9. This contradicts the *direct targeted child-value to parent-bestValue adoption* narrative but does not identify which different path causes action restoration.

## Proposed decisive intervention (strictly conditional causal question)

**D-arm:** keep the original actual source-targeted guard bypass and actually search its newly re-enabled branch, but **suppress `TTEntry::save` writes while executing that exact descendant subtree** in the same frozen Stockfish16 source and root setup.

A (untreated), B (TT_FIRST with original guarded pruning), C (TT_FIRST + exact one guard bypass, normal TT writes), D (TT_FIRST + exact one guard bypass, targeted descendant TT writes suppressed). The D-arm changes one family of side-effects rather than merely observing candidate scores.

**Source implementation:**
- `tools/c3x_029_p42_r8_guard_descendant_tt_save_intervention.py` extends the working old-C3b+R5 stack after the native `do_move` and before the source-matched `undo_move`. Thread-local `c3x042_r8_target_descendant` marks only the actual requested descendant, with `Threads=1`.
- Pinned official Stockfish16 `src/tt.cpp` `TTEntry::save` is the real TT entry write boundary. Env `C3X042_R8_DROP_DESCENDANT_TT_SAVE=1` returns before writing an entry **only when the marker is active**. When unset, original writes continue; a source count of candidate writes is logged separately.
- `tools/c3x_029_p42_r8_derived_native_build.py` preserves all immutable original 0.27 source overlay ordering and the new R5/R6 key correction. Runs the extra source patch before compilation, records original/derived recipe SHA.
- `harness/c3x_029_p42_r8_same_engine_tt_save_causal_court.py` executes the original three-arm Game14 harness twice from frozen StageA and official game-source SHA, once with normal TT and once under drop. It checks the untouched A/B and normal C source action/root invariants; D must have positive native suppressed TT write counts in **both** cold runs. All source keys, full histories, raw TT log and binary remain private.
- `.github/workflows/c3x-029-p42-r8-native-targeted-tt-write-counterfactual.yml`: read-only actual source compilation, real historical cold replay and aggregate-only public artifact. Human WhoSia source authors only; github-actions[bot] never pushes or commits.
- 8 source and 9 verdict **synthetic** tests discriminate source anchor failure, no contact, missing cold replay, partial TT suppression, unintended A/B change, root restoration success/failure and third-move emergence.

## Falsification and the meaning of possible outcomes (declared BEFORE result)

| Physical D-arm root outcome | What is supported, with verified suppression | What is NOT inferred |
|---|---|---|
| D = b3a4 (still restored) | TTEntry save writes *within this targeted extra branch* are **not necessary under this tested intervention** for the historical root restoration | No claim that other TT writes, TT reads, move ordering, or other paths cannot matter |
| D = f3f4 (returns to treated root) | Suppressing those writes destroys restoration in the tested source setting; this TT write family is **functionally necessary under intervention**, subject to no source-state confounding and resource accounting | No claim of unique natural mediation, meaning or strategic optimality |
| D = third root move | Dynamic candidate support changes and may implicate TT writes in root competition | No binary O/F interpretation, no global root value |
| 0 target write attempts, no true suppression, changed A/B, missing physical guard contact, source/build/legality failure | HOLD without a causal conclusion | No substitution of an authored test for a native experiment |

An actual TT writer is not necessarily read again. **Follow-up if D differs:** require source-local writer key/epoch; causal reader consumption tied to the same source writer and window/root action, and a complementary test preserving writes while perturbing alternate history/order effects. A functional necessity result alone does not establish path exclusivity.

Even if D is b3a4, the research is not exhausted: other indirect TT state outside the targeted child, branch search order, alpha/beta windows, history tables and aspiration retries can explain root restoration. If D differs but target write counts confirm contact, inspect source intent against unexpectedly modified writer telemetry and UCI search budget; keep opposite controls.

## Temporal and scientific scope

This is a **post-discovery mechanistic development intervention** in Game14 selected after prior root choice and its observed fail-low local branch. It is not event/game-disjoint prospective proof. It targets Stockfish16 with **Use NNUE=false**, so cannot establish NNUE representation. First scientific priority is discriminating causal computation, then source-stable relation to independently checked *adversarial chess future*, then prospective transport.

Do not report favorable semantics or a new publication based on D alone. The anticipated eventual hard paper must explain when an actual value-bearing computation is both causally necessary for the chosen chess move AND faithful to a meaningful counterfactual strategy.

## Source publication and governance

[Native source R5/R6 negative court](C3X_029_P42_R7_NATIVE_FAIL_LOW_WITH_ROOT_RESTORATION_CAUSAL_DIAGNOSIS_20261106.md), [R5 public receipt manifest](../evidence/C3X_029_P42_R7_R5_NATIVE_PUBLIC_RECEIPT_MANIFEST_20261106.json), [R6 public receipt manifest](../evidence/C3X_029_P42_R7_R6_NATIVE_JOINT_PUBLIC_RECEIPT_MANIFEST_20261106.json). GitHub=code and human audit, Notion=semantic judgment, Drive=immutable source bytes; original Drive ZIP mirror is NOT claimed.

**Any failures of synthetic regression, source compilation or native action replay are source failures, not chess causal falsification.** Declare only completed original-source outputs with SHA and correct source cohort.

## 2026-11-06 — Observed native outcome after the preregistered source intervention

The original four-arm native execution **[42156025333](https://github.com/WhoSia/C3X/actions/runs/42156025333) COMPLETED SUCCESS**, including source compilation, original 16-game frozen StageA byte verification, two separate ABC control runs, physical target-subtree TTEntry::save interception, data-rights checks and aggregate public artifact upload. Initial R8 runs failed at synthetic test assertion counting and C++ cross-translation-unit linkage; these technical failures are preserved, not confused with scientific falsification. After repairs, the authentic result is:

| physical condition | root bestmove |
|---|---|
| A original | `b3a4` |
| B TT_FIRST suppressed | `f3f4` |
| C single original source-matched capture_prune bypass | `b3a4` |
| D same C bypass, all TTEntry::save calls in actually entered target descendant suppressed | `b3a4` |

From the actual public JSON original: in the two native cold replays, the normal C target descendant attempted **[2,2] TT saves**; the D intervention physically suppressed **[2,2] saves**. The D decision still restored b3a4. The declared status therefore is `PASS_SOURCE_EXACT_TARGET_TT_SAVE_INTERVENTION_TT_WRITES_NOT_NECESSARY_FOR_THIS_RESTORATION_UNDER_TESTED_INTERVENTION`.

**This is a negative causal-necessity result for exactly this source-scoped write class**, not evidence that TT in general is irrelevant. The D-arm's search branch counts also changed (as expected of a TT perturbation). Neither the root nor the independent strategic evaluation is thereby identified as a child-search mediated effect.

Verified artifact: ID `13474427631`, name `c3x042-p42-r8-tt-descendant-four-arm-public-only`, downloaded ZIP SHA256 `d2bb1696a3eac5539d880ba786fc8cfae293aa509ac3d6e102d94fc4c3291728`; exact `C3X042_R8_CAUSAL_TT_SIDE_EFFECT_COURT.json` member SHA256 `26505c41e3f2660228a36c3ab28b26671b499fd465d6e957b477461b470fa773`. See [immutable human-authored public receipt manifest](../evidence/C3X_029_P42_R8_NATIVE_FOUR_ARM_PUBLIC_RECEIPT_MANIFEST_20261106.json).

### New mechanistic hypothesis raised by pinned source inspection: node-sensitive draw evaluation

Official **pinned** Stockfish16 `src/search.cpp` implements:
```cpp
Value value_draw(const Thread* thisThread) {
    return VALUE_DRAW - 1 + Value(thisThread->nodes & 0x2);
}
```
The source's `Position::do_move()` increments node count. Hence an extra entered branch could, in principle, affect future draw-score evaluation through node-count parity **without** an improving local parent return score or a targeted TTEntry::save write. This is a **concrete untested competing causal mechanism**, not a claim that Game14 actually passes through a draw or that such a node-parity effect explains its reversal. Other possibilities include history/capture-history, move ordering, aspiration retries, TT writes elsewhere and resource ordering. A real next causal test must instrument **actual reachable use of `value_draw` and its site chronology**, before attempting a novel source intervention. No move-quality or NNUE-neural explanation follows.

