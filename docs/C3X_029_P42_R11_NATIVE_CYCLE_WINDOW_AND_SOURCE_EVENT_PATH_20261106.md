# C3X 0.29-P42/R11 — Native Cycle-Alpha Windows, Cutoffs, and First Comparable Source Event

Date: 2026-11-06. **Pre-outcome research protocol**; existing verified R10 source-site intervention is a factual premise, but R11 has not yet produced a native cutoff observation at creation. This is a few-page prerequisite for the hard causal-computation↔strategic-future research, not an independent easy metrics paper.

## Actual inherited source-native result

Pinned original Stockfish16 `68e1e9b3811e16cad014b590d7443b9063b3eb52`, historical postselected Game14 and `Use NNUE=false`, original A=b3a4, TT_FIRST B=f3f4, one exact capture-prune guard bypass C=b3a4. R5 targeted child parent bestValue adoption zero; R8 suppression of all targeted extra-descendant TTEntry::save attempts does not prevent C restoration. New real native R9/R10 intervention identifies a global source-function and then its **cycle-alpha search caller** that, if neutralized, moves B back to b3a4 while leaving A=b3a4. Terminal draw-return source site is physically never contacted in the 16 R10 A/B runs. Original cycle-alpha event counts: A 380, B 562 per cold; site1-neutralized A and B 288 per cold. [R10 original native run](https://github.com/WhoSia/C3X/actions/runs/42164306431), [SHA-sealed R10 manifest](../evidence/C3X_029_P42_R10_TWO_NATIVE_DRAW_SITES_RECEIPT_MANIFEST_20261106.json).

A broad site intervention changes thousands of future code decisions. It is **not** proof that a particular naturally executed draw event caused a root move or that the search favored a strategically good move.

## The exact pinned original source mechanism

The key block before any main move search:
```cpp
if (!rootNode && pos.rule50_count() >= 3
    && alpha < VALUE_DRAW && pos.has_game_cycle(ss->ply)) {
    alpha = value_draw(pos.this_thread());
    if (alpha >= beta)
        return alpha;
}
```
and `value_draw = VALUE_DRAW-1+Value(nodes & 0x2)`. The mutable source state includes the incoming alpha/beta window, node counter, frame/depth and game-cycle access. The **actual source comparison** `alpha >= beta` can return before entering other search code. If a changed draw score changes this comparison, a direct cutoff mechanism becomes plausible; if cutoff counts are identical, alternate window continuation/research remains possible. Both scenarios remain nonidentifying without event-level source ancestry and root competition.

## R11 registered method

[Passive source patch](../tools/c3x_029_p42_r11_original_cycle_window_event_overlay.py) is inserted **after** original R10's two exact source sites, retains the original assignment/branch and records at the actual conditional:
- native position `pos.key()` for **private** matching only;
- source stack `ply`, `depth`, current root context, original node modulo four;
- incoming `alpha`, `beta`, actual `value_draw` candidate, post-assignment alpha and actual `alpha>=beta` immediate cutoff.
- preserves R10's original source site logging to cross-check event count exactly (fail closed if any mismatch).

[Derived build](../tools/c3x_029_p42_r11_derived_native_cycle_window_build.py) retains original 0.27→R8→R9→R10 immutable exact patch order. [Native two-arm court](../harness/c3x_029_p42_r11_native_cycle_alpha_window_court.py) runs actual pinned Game14 A and TT_FIRST B twice, normal source mode0 and cycle-site neutral mode1, same compiled binary. Requires original R10 stable bestmove A=b3a4/B=f3f4 in mode0 and A=B=b3a4 in mode1; physical TT_FIRST reader proven each trial. All source event identities remain private.

Two classes of output are distinguished:
1. **Execution census**: actual source cycle calls and actual immediate cutoffs, candidate sign, before/after alpha, parent window class, source alpha updates, under each mode and arm; all measured rather than guessed.
2. **Strict comparable-prefix court**: for normal versus neutral executions of same arm and cold index, event identity matches only while (native Zobrist key, ply, search depth, contextual root move, *pre-return alpha and beta*) agree. Counts of matching-prefix changed draw candidate and changed immediate cutoff are published, never the private keys, FEN, move history or per-frame score.

This prefix approach is deliberately conservative: **matching source event signatures do not prove identical causal ancestry** if TT/window state differs at unobserved branches, and a first divergence in the observed trace does NOT prove the first causal divergence. Strict prefix mismatch holds any claims of a shared natural state beyond that point. A single zero cutoffs difference does not eliminate other re-search paths.

## Predeclared admissibility and falsifiers

- No original source/StageA SHA or source exact patched build: technical HOLD.
- R10 original A/B or neutralized A/B root choices change unexpectedly: HOLD, don't rename them.
- Source event count differs from R10 source site 1 count, or any `candidate`, `beta`, actual cutoff disagree with the source `value_draw` formula: HOLD, not a numerical discovery.
- Cold source chronology differs: report separately even if both root choices same (root repeatability does not imply identical internal state).
- First matched event has different returned draw value but **same cutoff**: cannot claim local cutoff mediated final choice; pursue alpha-dependent continuation.
- First matched event has different cutoff: **plausible source mechanism in a matched local state**, but still no identification of final root dependence until the exact event is surgically controlled and its ancestry checked. A candidate with no cutoff can still influence downstream alpha windows.

Nine [source surgery tests](../tools/test_c3x_029_p42_r11_original_cycle_window_event_overlay.py) and fifteen [native event/court synthetic tests](../harness/test_c3x_029_p42_r11_native_cycle_alpha_window_court.py) are written; these are NOT new original native PASS. [Read-only native run #42177462049](https://github.com/WhoSia/C3X/actions/runs/42177462049) queued on creation. Raw source keys/private TT logs and modified GPL binary never published. Actions contents:read; only human WhoSia GitHub commits.

## Next genuine experiment after source-world observation

If matched event evidence supports a specific cycle-alpha cutoff change, freeze its source context (root, position key privately, original alpha/beta, ply/depth, ordering/ordinal), then run **isolated intervention on only that source-executed event** and report negative/third-root results too. Event selection from postselected Game14 is *development*, not prospective explanation. Independent same-source legal chess continuations and adversarial counterplay must then be judged separately; especially Game14 NNUE OFF cannot claim neural-feature-level mechanistic explanation.

A source state intervention may alter other events, so a convincing complete paper will need planned natural-control/sham interventions, rival algorithms and a new game/event-disjoint cohort. Never repackage the preliminary cutoff census as the flagship result.

## 2026-11-06 — Native outcome verified with exact artifact SHA

[Native run #42177462049](https://github.com/WhoSia/C3X/actions/runs/42177462049) finished **SUCCESS** including actual source compilation, original 16-game Stage A SHA reproduction, two independent A/B cold replays, unchanged historical original B f3f4 and cycle-alpha neutralized B b3a4. Independently downloaded [artifact #13483623242](https://github.com/WhoSia/C3X/actions/runs/42177462049/artifacts/13483623242), enumerated ZIP member and parsed actual JSON. Public ZIP SHA256 `39b27d086931c41faaf9ed4b0afdd9628d1e0780e9340dbf729b673cc0fc0bd7`, member `C3X042_R11_CYCLE_ALPHA_NATIVE_WINDOW_COURT.json` SHA256 `5ca3e30831cccf3efe7f52cb73eaf4fa98eaca481279bb46276fd39a3028642d`; [sealed human-authored receipt](../evidence/C3X_029_P42_R11_NATIVE_CYCLE_WINDOW_RECEIPT_MANIFEST_20261106.json).

| Physical source arm | Actual source cycle-window events per cold | Immediate `alpha>=beta` cutoffs per cold | Natural root move |
|---|---:|---:|---|
| Original A | 380 | 364 | b3a4 |
| TT_FIRST B | **562** | **552** | f3f4 |
| Cycle-alpha-neutralized A | 288 | 288 | b3a4 |
| Cycle-alpha-neutralized B | 288 | 288 | **b3a4** |

On the strictly **same pre-return source input** prefix (key, ply, depth, root context, old alpha, beta) the two cold repeats reproduced **A: 27 compared events, 27 candidate-return disagreements, 2 cutoff disagreements; B: 33 compared events, 33 candidate-return disagreements, 4 cutoff disagreements**. This proves that unchanged original source-frame/window inputs can lead to a different physical cutoff under one source value change. The complete dynamic trace after the prefix is *not* the same execution history. The actual original A/B source window counts and intervention-root outcomes do NOT prove that the first cutoff difference caused the root move or that exactly 4 cases are causally sufficient.

**Follow-up R12 frozen before outcome:** exhaustively intervene each of the four original B prefix-33 source events whose native candidate->zero replacement would flip immediate cutoff, one event at a time, with cold-replay identity checks and exact private source chronology. See [R12 preregistration](C3X_029_P42_R12_FOUR_MATCHED_SINGLE_CYCLE_EVENT_CAUSAL_CHALLENGES_20261106.md). No NNUE/independent chess strategy/paper promotion from R11 alone.
