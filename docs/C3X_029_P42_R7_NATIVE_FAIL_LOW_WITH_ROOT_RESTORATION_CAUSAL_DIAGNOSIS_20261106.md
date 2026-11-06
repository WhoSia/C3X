# C3X P42/R7 — Native Game14 Negative Local Mediation and Original C3b Joint Root Candidate Witness (2026-11-06)

## Verdict (native evidence, not a manuscript)

**Historical Game14 source effect independently replayed; direct local bestValue mediation REFUTED for the measured target, observed same-execution ancestor/root-candidate path PASS, natural TT→SEE→root mediation and chess meaning STILL HOLD.** This is not a 0.30 version promotion, not a prospective cohort and not a discovery of a chess strategy concept.

### Raw provenance (public only)

- [R5 native run #42153949082](https://github.com/WhoSia/C3X/actions/runs/42153949082), public artifact ID **13473329210**, name `c3x042-p42-r5-game14-public-aggregate-only`, ZIP SHA256 `bdae6fd6592794ac6140c8edc83b8e01e6fc602ac6705abd19fd260d5ca38eba`. Verified contained `C3X042_R5_GAME14_LOCAL_ADMISSION.json` SHA256 `25329a234f3f605188f6b9b2b130b03b03d9007a752cdf90459de48020a32df1`.
- [R6 native run #42154152915](https://github.com/WhoSia/C3X/actions/runs/42154152915), public artifact ID **13474205793**, name `c3x042-p42-r6-native-joint-c3b-local-aggregate-only`, ZIP SHA256 `66547963fe814376fbc921361d3572c0f4e02c85edf590d98c9b3f138005806c`. Verified contained `C3X042_R6_JOINT_LOCAL_C3B_ADMISSION.json` SHA256 `de7b5341c44b5eb9dad5de4265975a562ecb9f6751e9ad8c4bc6b8dad90ced5c` and `C3X027_GAME14_ROOT_BOUNDARY_COURT.json` SHA256 `aad1da853ad3e57bab9a839d59deb802c27cf26a1a11bd005e0320eeec04d2ad`.
- Both public artifacts were downloaded, ZIP member names enumerated and JSON contents directly inspected. No private original full chess PGN, source TT key, source trace or GPL engine binary exposed. Upstream content rights scanner reported SCAN_PASS_NOT_A_LEGAL_LICENSE (a content scan, **not** legal approval).
- The original game ID14 source SHA256 is `0822ec4ddab0339d51a65f3a9d077a1245b2402b111e78a3aa90d2a4d9a83652`; Stage A private/public SHA256 `b0eb51ab779609db346c75d65a6a65fd31efc9a648111d042cfec5199a4afde1` / `4572edd4c0761c3875aed421b08880ff142c21f691fe940c7c6d760dbb397be5` reproduced. Original fixed Stockfish16 source `68e1e9b3811e16cad014b590d7443b9063b3eb52` with **Use NNUE=false**.

## R5 local source effect: counterintuitive negative

The R5 court reports exactly two complete native local source chains `GUARD_FALLTHROUGH -> ACTUAL_DO_MOVE -> MAIN/QSEARCH_CHILD_ENTERED -> CHILD_RETURNED_TO_PARENT -> PARENT_VALUE_ASSESSED`. **But source `PARENT_BESTVALUE_ASSIGNED` was NEVER emitted** in either cold run. Actual aggregate:

| field | native result |
|:--|--:|
| `full_local_spine` | 2 |
| `parent_assignment` | **0** |
| `parent_value_exceeds_alpha` | 0 |
| `window_fail_low_like` | 2 |
| `window_in_range` | 0 |
| `window_fail_high_like` | 0 |

The historical A/B/C actual bestmoves **b3a4 → f3f4 → b3a4** nevertheless reproduced. This **refutes the simple direct child-return score → immediate parent bestValue replacement → ancestor/root path** for the specifically armed source event as an observed causal story. It does NOT refute all indirect effects of entering that branch: TT writes, sibling ordering, histories, window/re-search, descendant state changes remain possible. It also does not prove value improvements did not occur at other events or later.

A condition `value <= alpha` is a numeric local search-window relation, not an independently exact chess-value judgment; no false claim that the game was strategically inferior follows.

## R6 same-physical-execution joint proof

Original 0.27 `c3x_027_game14_passive_lineage_overlay.py` and `c3x_027_game14_C3b_passive_ancestor_overlay.py` were run in the **same compiled Stockfish16 binary, same cold A/B/C executions** as the corrected P42 post-`do_move` key observer, preserving the legacy original source scripts/receipts. The R6 public court returns:

```json
{
  "status": "PASS_JOINT_SOURCE_LOCAL_AND_OBSERVED_ROOT_CANDIDATE_ONLY",
  "replays": 2,
  "source_c3b_candidate_edges": [3, 3],
  "local_actual_parent_assignments": 0,
  "root_causation_certified": false,
  "natural_mediation_certified": false,
  "chess_strategic_semantics_verified": false
}
```

The original source C3b private-aggregated observation found two root-frame paths in C (and no source C3b events in A/B), with **source_frame_id_certified=false** under its older weaker aggregate judge. The new strict same-native-run joint court did compare native C3b frame-ID evidence and parent candidate consistency; its PASS remains **observed candidate path** and not a score-change-caused-root-action claim.

### Root search boundary difference

12 common iterative deepening depth boundaries. **Four B/C divergent depth boundaries**. First B/C difference at **depth 9**:
- A: leader native 1373, score -89, average -88
- B: leader native 1373, score -74, average -70
- C: leader native 1112, score -89, average -79.

This is a strong **temporal localization of observable root ranking divergence**, not identification of the mechanism: early unlogged TT/return events and previous-depth writes can cause downstream depth-9 differences; the code's first observed boundary != first causal change.

## Actual R7 debugging discoveries & verifiable repairs

1. Prior R5 and R6 CI had genuinely failed; GitHub job logs showed source contract test false positive on comment text `pos.do_move(`, corrected via code-only lines in commit `0ce8bfb7`; the R5 source/synthetic CI [#42153532120](https://github.com/WhoSia/C3X/actions/runs/42153532120) and later [#42153949034](https://github.com/WhoSia/C3X/actions/runs/42153949034) succeeded.
2. Native overlay patch originally searched for `if(stop) return ZERO; \n\n if(rootNode)` but exact Stockfish16 has intervening **comments**. Error `P42_R5_HOLD_PARENT_ASSESS_ANCHOR_COUNT_0`, not an empirical negative. Repaired with unique rootNode opening anchor, commit `09fa7a47`; original NNUE OFF source and Stage A SHA remained stable.
3. R5 local court originally demanded pre-move `child64=0` equal to post-move actual Zobrist child key across all events. This was logically inconsistent with a real new child, and caused `HOLD_EVENT_IDENTITY_DRIFT`. Fixed to validate *uninitialized before do_move* then *stable actual post-do_move child identity*, commit `a7c53044`, regressions `f9f72a3b`.
4. No changes to original historical 0.27 code, source corpus, original run artifacts, old failed CI logs, or bot-origin commits. Action workflows are read-only; human WhoSia authors commits.

## Decisive next science—not an easy metric paper

**Challenge a now-disfavored causal chain:** The direct parent bestValue adoption hypothesis should no longer be used as default for Game14. Derive discriminating *source-native interventions* between at least:
- **H_TT:** the bypass permits a descendant TT write/reuse that changes a later competitive root candidate, despite the newly returned child score failing low locally.
- **H_HISTORY:** move-order/history/countermove or killer state is altered by the extra exploration and changes the subsequent search order/cutoff or resource usage.
- **H_RESEARCH:** aspiration/PV re-search or transposition-induced alternative branch changes the evaluated root landscape; the same numeric score need not travel along the local child→parent bestValue chain.
- **H_OTHER:** effects mediated by search control state (visited nodes, stop budget, TT replacement) or multiple overlapping paths.

Not all are mutually exclusive; do NOT call an effect unique based on a single intervention. Design source-exact **writer/reader event chronology** of the re-enabled subtree and first B/C divergence at depth9; then, with careful modularity constraints, intervene separately on (i) relevant TT writer/reader side effects, (ii) history/order updates and (iii) score usage. Freeze target before seeing new outcomes and run sham/non-contact controls. A null or mixed case must be reported.

The central intellectual goal remains explanation as a *causal–strategic correspondence*: source computation must be established as actual decision cause, AND independently reflect a valuable, adversarial chess future. Game14 with `Use NNUE=false` cannot be cited as an NNUE mechanism proof; full NNUE-on/heldout interpretation remains future work.

**Scientific adjudication:** local native evidence PASS; original root candidate path observational PASS; direct local bestValue mediation **negative**; complete causal root-action mechanism HOLD; actual strategic meaning HOLD; prospective cohort transport HOLD. These categories must never be collapsed.

## 2026-11-06 follow-up closure on one competing path: targeted TTEntry::save

The explicitly registered R8 physical counterfactual **was actually run successfully** on the original source, not merely designed: [Game14 native four-arm run #42156025333](https://github.com/WhoSia/C3X/actions/runs/42156025333). The source-targeted descendant made 2 TTEntry::save attempts per cold run, and D suppressed both 2/2 in each cold run. A/B/C reproduced `b3a4/f3f4/b3a4`, **D also selected `b3a4`**, so those specific TTEntry writes are *not functionally necessary* for root restoration under the tested intervention. Do not attribute the remaining phenomenon to another TT writer/reader or history heuristic without new source evidence. [Full R8 causal court and SHA-sealed artifact](C3X_029_P42_R8_TARGET_DESCENDANT_TT_WRITE_NECESSITY_EXPERIMENT_20261106.md), [receipt manifest](../evidence/C3X_029_P42_R8_NATIVE_FOUR_ARM_PUBLIC_RECEIPT_MANIFEST_20261106.json).

This sharpens but does not complete the mechanistic puzzle: neither direct local bestValue adoption nor the target descendant's `TTEntry::save` writes was necessary for the observed source-native root restoration. Source-valid alternative indirect paths remain open. Postselected Game14 and NNUE OFF restrictions still apply.
