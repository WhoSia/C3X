# C3X 0.29-P42/R9 — Actual Source-Native Draw-Score Path Contact and Node-Parity Counterfactual

Date: 2026-11-06 KST. Research director's **mechanistic falsification experiment**, not a new main-paper or new strategic value certificate. The hard scientific objective remains identifying a computation that both causally determines a move and faithfully corresponds to strategically meaningful counterfactual chess futures.

## Source-grounded motivation and state of evidence

Source-locked Game14 (NNUE OFF), three-arm original bestmoves A=b3a4, B=TT_FIRST f3f4, C=single actual capture_prune bypass b3a4. R5 native #42153949082 exposed a **fail-low-like descendant** with child-to-parent candidate evidence 2/2 and **zero immediate parent bestValue adoption**. R6 #42154152915 exposed observed ancestor candidate edges and depth9 B/C root divergence, **not causal root choice**. R8 #42156025333 physically suppressed 2/2 targeted TTEntry::save attempts in each D-arm cold replay, while D still selected b3a4; these targeted TT writes are **not necessary** under the tested intervention.

The next question is not 'which easy metric might correlate with root choices?' but 'which actual source execution path, if any, could transmit the branch's effects despite no locally improving returned score and no required target-descendant TT save?'

Pinned official Stockfish16 `src/search.cpp` commit `68e1e9b3811e16cad014b590d7443b9063b3eb52` contains exactly the node-sensitive draw return:

```cpp
Value value_draw(const Thread* thisThread) {
    return VALUE_DRAW - 1 + Value(thisThread->nodes & 0x2);
}
```

The original source calls this function at two sites: cycle/draw-related alpha update and terminal-or-maximum-ply draw return. Entry into an additional searched branch can change the node counter used later, but **no evidence yet shows a draw-score call even occurred in the Game14 source experiment**. A source-independent narrative about the move's chess merits cannot be derived from a node-parity artifact.

## Registered source intervention before native outcome

`tools/c3x_029_p42_r9_original_value_draw_node_parity_intervention.py` adds an observer at the source native `value_draw` function itself, so that **all actual calls** are recorded; if `C3X042_R9_DRAW_PARITY_NEUTRAL=1`, return `VALUE_DRAW` instead of the original node-sensitive `VALUE_DRAW-1+(nodes&2)`. If the variable is absent, return the exact original value. Record actual original, modified return, node_mod4 and mode, but **no chess source game, TT keys, FEN, personal identifiers or private traces in public artifact**. This is a deliberately BROAD source intervention, not a selective, natural mediator value-set experiment.

The original Game14 R8 ABC+D harness with the exact original 0.27 source/StageA SHA and TT-write D-arm is run twice **on the same derived binary**:
- normal `value_draw` branch, with raw trace private,
- all source `value_draw` outputs neutralized to `VALUE_DRAW`, with raw trace private.

The `harness/c3x_029_p42_r9_native_value_draw_court.py` compares physical count of actual calls and the chosen root result, with original A/B/C controls required to reproduce before an explanatory verdict. `R8` target TT write intervention remains active for D in both suites, but the primary comparison is **normal versus draw-neutralized original C** under the exact original baseline/TT/guard structure; broader modification of A/B may create control drift and HOLD.

- If there are **zero actual value_draw calls in both complete native A/B/C/D suites**, the node-mod4 draw-return pathway cannot be the causal explanation for these executions. This is a precise negative, not a statement about all node-sensitive paths.
- If positive calls and root does not change, global parity neutralization did not change the tested D-arm final choice; not proof of no intermediate draw influence.
- If positive calls and root changes, the broad draw-parity value modification is implicated *at source-function level*, but path isolation, source reachability to root, other draw-related computations and strategic consequence remain unproven.
- If the originally required root actions, original StageA hash, exact source provenance, source original value, draw event parser or R8 physical TT suppression fail, **HOLD**; do not cherry-pick an independent result.

**Critical methodological limitation:** function-level observations are aggregated over cold engine processes and ABCD worlds, because this immediate challenge is source-contact elimination. A positive aggregated count **alone** does not identify which C-world frame/score is the decisive causal site. Even a causal choice difference requires original caller/frame/root lineage, legal move and opponent-response meaning. Conversely a zero count under complete source instrumentation eliminates the named function-level pathway in these measured executions regardless of per-world labels.

## Implementation and execution

- [Source-locked source patch](../tools/c3x_029_p42_r9_original_value_draw_node_parity_intervention.py)
- [8 synthetic source tests](../tools/test_c3x_029_p42_r9_original_value_draw_node_parity_intervention.py)
- [Derived immutable original R8 build](../tools/c3x_029_p42_r9_derived_original_draw_build.py)
- [Two-suite source-native causal court](../harness/c3x_029_p42_r9_native_value_draw_court.py)
- [12 adversarial verdict/source-event tests](../harness/test_c3x_029_p42_r9_native_value_draw_court.py)
- [Read-only native Actions workflow](../.github/workflows/c3x-029-p42-r9-native-draw-causal-court.yml), started runs [42162890316](https://github.com/WhoSia/C3X/actions/runs/42162890316) / [42162927070](https://github.com/WhoSia/C3X/actions/runs/42162927070) as inspected. The latest revision uses an **explicit uploaded-artifact allowlist**, so source/raw intermediate files are never published if an earlier step fails.

There is no established new empirical R9 outcome at report creation. Earlier R5/R6 workflow failures included a real SyntaxError and a synthetic string-match test which mistaken a comment `pos.do_move()` for executable move mutation. Those were fixed in R7; R5/R6/R8 authentic later successes are not invalidated by old technical failures. All source/test workflow definitions are GitHub-human-authored (WhoSia); Actions permission contents:read, no bot commits.

## Against strategic overclaim and toward the original hard problem

If this alternative path is eliminated, the remaining search mechanisms include real alpha-beta/PV bound adoption elsewhere, TT readers/writers outside the target subtree, history/capture-history updates, move ordering, node/resource timing and aspiration re-search. C3X must source-isolate each family with true physical interventions, not narrate whichever correlation survives.

Even if a mechanism finally explains Game14's source-level root switch, that only solves an algorithmic *why*. Strategically meaningful *because of* additionally demands a predeclared chess-consequence property across adversarial legal continuations, independently judged, whose corresponding computation affects the decision with prospective transport on heldout games. Game14 used NNUE OFF and is postselected; the neural feature and chess meaning bridge remains the main open problem.

**Report status:** source code and Actions run registration completed; R9 native source-contact/causal verdict unresolved until original Actions logs and artifacts checked. No new paper promotion. Drive original-byte mirror still separately unresolved.
