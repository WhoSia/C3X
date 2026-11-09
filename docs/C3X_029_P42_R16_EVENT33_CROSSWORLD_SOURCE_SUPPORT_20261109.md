# C3X 0.29–P42/R16 — Original B Event33 Dynamic Cross-World Source-State Support

Date 2026-11-09 KST. **Pre-outcome methodological identification question**. Aim remains deep explanation: actual search-decision cause + independently defensible adversarial chess future. This is an original-source identification stage, not a separate easy paper.

## Original data preserved, no after-the-fact event renaming

Original pinned Stockfish16 (NNUE OFF) Game14 historical postselected experimental outcomes:
- B original TT_FIRST f3f4;
- C exact one capture-prune guard bypass b3a4;
- B33 exactly the 33rd B-world cycle-alpha return neutralization b3a4;
- R14 actual source C and B33 share depth9 leader native1112, score−89 but differ average by 1; the two interventions do not create identical states;
- [R15 original native combined run #42550661689](https://github.com/WhoSia/C3X/actions/runs/42550661689): C+B33 still b3a4 in both cold repeats, depth9 same C root summary; yet the first 33 B-world source-event identities **do not match** the combined execution (negative preintervention native prefix in both cold). This is why natural mediation cannot be inferred from the ordinal or shared root move.
- R15 public ZIP SHA `53c9c8d74c565c35e4a5d3e4373ce28595836aef5f9fc3b833bf265ee57e6d81` and member SHA `b0d14396991c7387dd41a74fb315b470397f8eb30e61d5ee0638a6c369a96f5d`, independently downloaded and read. [Human SHA receipt](../evidence/C3X_029_P42_R15_NATIVE_COMBINED_SOURCE_INTERVENTION_RECEIPT_20261109.json).

R15 showed that ordinal number 33 in a changed search is *not the same physical source event* as B original event33. In search with altered visited-node support, naming two nodes by their order is not an intervention on a common stable variable. R16 examines the stronger physical identity criterion without rewriting original stored trace or selecting a new winning event.

## R16 predeclared observable, interpretations and privacy

Run original R14 physical A/B/C and B33, and R15 combined C+B33 under the same pinned original build, with the original strict StageA and exact source/legal game source invariants. Freeze the original B-world native event33 as `b[32]` (per actual engine subprocess).

Search **all actual C and C+B33 cycle-alpha events** for the target event signature, without assuming ordinal preservation. For each of B, C and C+B33 count:

1. **Board-context match:** `(position_key, ply, depth, root_move)`. Same board/hash alone does not guarantee identical search window or game history; these are a narrower four-field *source context*.
2. **Search-window match:** plus `(old_alpha,beta)`, essential to whether the alpha-beta draw threshold has the same immediate effect.
3. **Full measured source-computation match:** plus `nodes mod4`, which governs the actual draw score returned by the pinned Stockfish16 function.

Also compare the first native event of crossworld source identity divergence and C-vs-C+B33 12-depth root boundary identity, separating matching root leader/score from full root summary equality.

**Nonnegotiable claim ceilings:**
- No matches in C for B event33's board-context: that original B event lacks observed source-state support in this specific C run; rules out *literal same observed event* natural-mediation story in the measured runs (but not different events playing analogous roles).
- Same board but different window: no equivalence of score/bounds or cutoff rule.
- Same window but different node bit: cannot equate source draw-score calculation.
- One or more full signature matches: possible observational source support, NOT proven causal reachability, writer-reader lineage, unique source frame or actual strategic reason; multiplicity creates ambiguity.
- C+B33 source support can differ from C, as intervention itself changes the world. Never assume same ordinal or data set.
- Natural mediation, NNUE feature attribution, objective chess future and new-game prospective transport remain false in output regardless of how favorable the measured overlap looks.

Original source keys, score windows, PGNs, FEN and raw search logs remain private. Public JSON contains counts and truth conditions only. No bot commits; WhoSia authored source, read-only Actions.

## Reproducible executable protocol

[Native same-source crossworld matcher](../harness/c3x_029_p42_r16_original_event33_crossworld_source_support.py), [13 adversarial support and privacy tests](../harness/test_c3x_029_p42_r16_original_event33_crossworld_source_support.py), [strict original native workflow](../.github/workflows/c3x-029-p42-r16-native-event33-crossworld-support.yml). Started [R16 run #42551289145](https://github.com/WhoSia/C3X/actions/runs/42551289145). At this document's creation the source compile/native analysis was still running; no fabricated final R16 verdict.

The ultimate C3X flagship asks which source-consumed computation is *causally related to* a real, prospective, adversarial future quality distinction in chess. A cycle-bound source score might explain software action without being a scientifically satisfying chess strategy explanation. Keep those claims separate.
