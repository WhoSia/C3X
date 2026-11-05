# C3X 0.29-P42/R6 — Original C3b Lineage Recovered, Post-Do-Move Identity Repair, and Joint Native Game14 Experiment

Date: 2026-11-05 KST. **P42/R6 original-source audit and new read-only native workflow QUEUED; no new chess-result PASS.** This project shall not substitute an easier metrics/provenance paper for the difficult causal–strategic correspondence problem.

## 1. What the deeper historical archaeology actually found

Previous P42/R5 language inaccurately suggested that only the 0.24 quiet/qsearch C3a/C3b overlays existed. Direct GitHub source search identified **Game14-specific historical 0.27** originals already built:

- `tools/c3x_027_game14_passive_lineage_overlay.py`: exact capture-guard contact, DO_MOVE_EXECUTED, CHILD_ENTERED, CHILD_VALUE_RETURNED, PARENT_CANDIDATE_VALUE, source main frame/root-depth diagnostics.
- `tools/c3x_027_game14_C3b_passive_ancestor_overlay.py`: source frame snapshots, source child return, candidate comparisons at intervening ancestor frames, frame return and root-frame return observers.
- `harness/c3x_027_game14_ABC_passive_lineage.py`: old source-only frozen Game14 provenance, original A/B/C cold replays, private trace, public aggregation; explicit natural mediation FALSE.
- `harness/c3x_027_game14_C3b_ancestor_root_court.py`: strict candidate/ancestor/root event-sequence court requiring native frame-id agreement, **not** final move mediation PASS.
- `tools/c3x_027_game14_root_boundary_court.py`: iterative-deepening root-leader comparison remains observational only, no causal value transfer proof.
- `tools/c3x_027_game14_lineage_build.sh`, `.github/workflows/c3x-027-game14-ABC-native-lineage.yml`: original strict-order instrument source stack and historical read-only replay.

**Corrections:** The latest R5 patch is not the first capture-source-to-parent instrument. It adds local `bestValue` assignment semantics, independent post-`do_move` child key rather than speculative prefetch, and same-native-run link to strict source original C3b. Its novelty must be judged against the original implemented pipeline, not against a falsely truncated archive. Historical G4-G9 actual outcome remains HOLD without a qualifying native receipt.

## 2. Concrete original-source correctness issue

Pinned official Stockfish16 `src/position.cpp`, commit `68e1e9b3811e16cad014b590d7443b9063b3eb52`, documents that `Position::key_after(Move)` is only for **speculative TT prefetch** and **does not recognize castling, en passant or promotions**. Moreover it computes a simplified Zobrist hash without all bookkeeping required by a fully executed `Position::do_move()` (special board state including rights and EP). Consequently the equality `pos.key_after(move) == post_do_move_position.key()` is **not a general semantic invariant**.

Both old historical Game14 local overlays and the old 0.24 matching logic can use predicted `key_after` as a preliminary expected-child key. For a special/history-sensitive move they could miss a real child execution and report an apparent lineage failure. This is a **potential false-negative condition**, not evidence that historical Game14's actual targeted capture was a special move or that existing original observations were wrong.

New `tools/c3x_029_p42_r5_game14_capture_local_lineage_overlay.py` was corrected (commit `8fb072bd...`) to initialize child identity to zero at guard contact, and **set child_key=pos.key() only inside the original post-`pos.do_move(move,...)` source site**, after matching native Stack frame, move and root call. Later child-entry/return events use actual native key, not the approximate prefetch. Historical scripts/receipts remain untouched.

New `tools/test_c3x_029_p42_r6_exact_child_key_source.py` adds 6 synthetic/source-surgery cases (unique source event, idempotence refusal, duplicate anchor, missing original guard, actual-key-after-do-move, no extra operator mutation in helper); not equivalent to native compiled chess.

## 3. R5 factual defect: Python was initially syntactically invalid

Reinspection of `harness/c3x_029_p42_r5_game14_local_spine_court.py` detected a literal backslash-n in active Python dictionary syntax inserted by an earlier update. This is an actual authored source defect that would prevent the court from importing on a future runner. Commit `2229bae16...` replaces the bad escape with real newline and fixes related comment formatting. Earlier queued CI runs were NOT declared PASS, and the detected syntax error did not constitute a chess-theoretic negative result.

Separate native workflow YAML parsing error in earlier R5 run `42040835703` had already been preserved as a technical failure. These remain valid software reliability deficits, not causal falsification.

## 4. New R6: original G4-G9 and corrected key in SAME physical execution

`tools/c3x_029_p42_r6_joint_original_c3b_and_real_child_build.py` takes the historical full `c3x_027_game14_lineage_build.sh` **as read-only**, verifies patch order and makes a temporary derived recipe with the new local actual-key overlay added after old C3b and before compilation. It records original/derived recipe SHA values locally.

`harness/c3x_029_p42_r6_same_execution_local_ancestor_court.py` consumes the **same** native A/B/C historical run's original old C3b raw private C-arm trace and new actual-key C-arm trace (not separately executed test engines), requires both cold replay groups and compares:
1. original source C3b root call, actual source move and parent position key against the new guard event;
2. original C3b complete frame/ancestry trace through the unchanged `harness/c3x_027_game14_C3b_ancestor_root_court.py` checker;
3. native old parent candidate score against the new actual returned/assessed parent value;
4. original C3b unrestricted root candidate identity against new root move context.

`harness/test_c3x_029_p42_r6_same_execution_local_ancestor_court.py` has 10 adversarial synthetic cases (full synthetic join, partial, third candidate, altered score, wrong source key, root-call drift, missing cold replay, absent local child, parser separation, nonnumeric native field). They **are authored**, not newly native-PASS.

The paper-relevant result would be a source-native same-execution full local-to-ancestor *candidate path*. Even **PASS_JOINT_SOURCE_LOCAL_AND_OBSERVED_ROOT_CANDIDATE_ONLY** still means **no proof** that the candidate value caused final unrestricted bestmove, no uniqueness of natural TT mediation, no objective chess value, no human-relevant strategy.

`.github/workflows/c3x-029-p42-r6-game14-joint-causal-spine.yml` reuses original 0.27 frozen Game14 data, original SHA-locked StageA, legal native replay, exact historical A/B/C target, nonbot read-only Actions and source-license/privacy gates. It additionally runs new joint-court and publishes only aggregates, keeping full player history, source hash keys, raw native lineages and modified GPL engine binary private.

As last checked, **[new native R6 run 42053604937](https://github.com/WhoSia/C3X/actions/runs/42053604937) was QUEUED**, as are earlier R5 runs; no claim of successful binary compile, integrated source contact, native score path, or experimental value difference.

## 4A. Critical historical mode separation: Game14 runs with NNUE disabled

Direct original-source inspection of `harness/c3x_018_native_TT_lineage_factorial_6_8.py`, the `play(...)` function used transitively by the frozen Game14 A/B/C runner, confirms the actual UCI commands:

```
setoption name Threads value 1
setoption name Hash value 16
setoption name MultiPV value 1
setoption name Use NNUE value false
```

The original Game14 experiment therefore tests Stockfish16 **classical-evaluation search architecture with NNUE disabled**. It can support search-program TT/SEE→value→root causal investigation but provides **no direct NNUE-representation mediation evidence**. Later attempts to connect NNUE's features to independent strategic chess future must use a separately predeclared NNUE-enabled source-native cohort, then establish transfer to the same stable chess consequence. Never misreport the original Game14 causal evidence as neural feature attribution.

## 4B. Mathematical source identity nuance: zero is not 'missing'

The old local court required both physical source Zobrist keys to be nonzero; 64-bit keys have no general semantic guarantee of nonzero. R6 now disambiguates uninitialized child state via explicit `did_move` and `child_entered` flags, not an invalid numeric nonzero predicate. Added **two** synthetic regression cases for valid zero-valued parent/child keys. R5 authored local-court test count is now **14**, not 12, while R6 adds 6 source-surgery tests and 10 joint-ancestry tests. These are source/test-design repairs, not new empirical chess outcomes.

## 5. Direct reading of primary v4 Sandmann et al. 2026

TinyFish fetched primary `https://arxiv.org/html/2508.21380v4` (exact published web original v4). Its key claim, relevant to the flagship problem: intermediate Leela policy layers can hold causally functioning future move representations while final policy selects a different move; steering against late safety preferences recovers **71.7%** of forgotten puzzles. Study uses **8,648 forgotten** filtered positions (not an equivalent 8,648 fresh stockfish games), and reports **97.0%** of forgotten positions where the policy's own value head favors the correct resulting move. Original v4 additionally reports 87.3% sacrifices in the forgotten filtered subset and quiet alternative in 68.3%. These figures pertain to their Leela transformer network, not Stockfish NNUE+alpha-beta root. They strongly weaken the novelty of saying “algorithmic future representation does not determine action”; C3X must establish a different source-executable and strategically faithful causal correspondence with prospective validation.

The PDF/byte original **remains absent from verified Drive holdings**; browser full original v4 reading is not an immutable Drive byte seal. In the missing-file register, change only source-read status, not Drive possession.

## 6. Hard flagship scientific frontier (not an easy metrics paper)

- **G1 computational:** establish the exact intervention's physical and chronological writer/reader/SEE event, actual branch entry and returned score and bounds; distinguish `bestValue` improvement from alpha mutation and beta cutoffs.
- **G2 source causal:** establish the descendant score's effects through all ancestor frames and all relevant root candidate scoring, including potential TT writes/aspiration retries and multi-path compensation; discriminate a guard-only channel from a parallel-search compensation channel, not merely posthoc log order.
- **G3 strategic bridge:** with full exact chess history, define a *prior-selected* adversarial future-property claim independently of revealed final root; test actual engine consumed computational information against the same external chess contingency through genuine legal counterfactuals, not square identity/mobility/mate2/prose.
- **G4 transfer:** new game/event-disjoint prospective data, source-identical interventions, full-root candidate support (previous P8 had third-candidate emergence 4/10 flipped conditions), strong source-based competitor baselines; retain null/failed cases.

The full candidate-level outcome of R6's source join (if observed) would still be **one evidentiary bridge**, at most a few pages of an eventual substantial paper. Natural path-specific causal claims remain an identification problem with source-specific changing event support.

## Research OS and status

GitHub executable source, original 0.27 immutable evidence; Notion semantic project state; Drive raw original bytes; only `WhoSia` author/committer, **no github-actions[bot] repo writes**. This R6 version adds a real run-ready protocol and source-correctness repair; native results and heldout strategic confirmation remain HOLD.
