# C3X 0.29-P42/R10 — Which Native Draw-Score Call Site Alters the Root? Two-Site Source Intervention Court

Date 2026-11-06 KST. **Hypothesis registered before independent R10 native outcome.** This experiment addresses one concrete remaining cause of historical Game14 search divergence; it is NOT an alternative easy “metric paper” and neither defines nor solves chess-strategic meaning.

## Verified historical foundation and evidence custody

Pinned official Stockfish16 `68e1e9b3811e16cad014b590d7443b9063b3eb52`, `Use NNUE false`, immutable September Game14 original source SHA `0822ec4ddab0339d51a65f3a9d077a1245b2402b111e78a3aa90d2a4d9a83652`.

- [R5 #42153949082](https://github.com/WhoSia/C3X/actions/runs/42153949082): actual source guard→child→returned score→parent candidate, direct parent bestValue adoption **0/2**.
- [R6 #42154152915](https://github.com/WhoSia/C3X/actions/runs/42154152915): actual old C3b and new child key same-run source candidate edges to root observed, **not final move cause**.
- [R8 #42156025333](https://github.com/WhoSia/C3X/actions/runs/42156025333): physically suppress the 2 targeted `TTEntry::save` attempts per C/D cold run; D still returns original b3a4; *those targeted writes not necessary under intervention*.
- [R9 #42163439611](https://github.com/WhoSia/C3X/actions/runs/42163439611): truly source-native broad `value_draw` parity neutralization changed **B TT_FIRST f3f4 → b3a4**, A remained b3a4, replicated **twice**; **288 actual `value_draw` calls per A/B cold run**, both TT physical readers valid. Public artifact 13478215738 downloaded/inspected; JSON member SHA256 `718ccdc234b753863c267956d5cd92df7c15ce33306baf652413c4ff434b2eec` and ZIP SHA256 `756e228f0ea134a2d0a22697fbea612303c85ca7c8549db64eaaa777635aabcf` independently measured in session. [R9 receipt](../evidence/C3X_029_P42_R9_NATIVE_VALUE_DRAW_AB_RECEIPT_MANIFEST_20261106.json).

R9 first four-arm whole neutralization [#42162927070](https://github.com/WhoSia/C3X/actions/runs/42162927070) failed because original history A/B labels ceased to match an intentionally intervened source program. This was scientific applicability failure of fixed-baseline verdict, not source compiler failure; the unchanged original source control remained successful. R9 next independently probed neutral A/B without forcing those labels.

## Exact original source and two natural call sites

Official pinned `src/search.cpp` has one original `value_draw(Thread*)` function:
```cpp
return VALUE_DRAW - 1 + Value(thisThread->nodes & 0x2);
```
This was verified to execute in real Game14, and original source contains two distinct caller sites:
1. **Cycle-alpha**: early rule-50/cycle detection condition, `alpha = value_draw(pos.this_thread());` followed by possible alpha-beta cutoff.
2. **Terminal draw**: the stopping / position draw / max ply path's `: value_draw(pos.this_thread());` return.

R9 changed both together, so R9 alone **does not locate which original source caller changes final choice**, even though the broad source function causal lever is real. This is a substantive mechanism-identification gap.

## R10 pre-outcome factorial source-site intervention

Source patch [`tools/c3x_029_p42_r10_source_site_specific_draw_parity_overlay.py`](../tools/c3x_029_p42_r10_source_site_specific_draw_parity_overlay.py) requires R9 source provenance and replaces both original call sites by a wrapper that (i) still calls original `value_draw`, (ii) logs source site, native ply, node mod 4, original value and actually returned value, and (iii) returns `VALUE_DRAW` instead of the original score ONLY for a caller selected by `C3X042_R10_NEUTRAL_DRAW_SITE`. Modes:
- 0: original no call site neutralized;
- 1: cycle-alpha call site neutralized everywhere it physically occurs;
- 2: terminal draw return site neutralized everywhere it physically occurs;
- 3: both call sites neutralized, intended to reproduce already verified R9 broad intervention.

The R10 original-source native [derived build](../tools/c3x_029_p42_r10_original_site_draw_build.py) preserves original strict 0.27 + R8/R9 order, uses the same complete game history/official source and StageA SHA. The [native A/B court](../harness/c3x_029_p42_r10_native_original_AB_draw_site_court.py) performs modes 0,1,2,3, each A untreated and B TT_FIRST, **two cold repetitions each**. Total 16 source-native calls, each with private per-source-site trace. Original physical TT reader verified in all B repetitions.

**Predeclared outcome alternatives (no relabeling afterwards):**
- **Mode 1 flips B, mode 2 doesn't:** cycle-alpha value_draw site is functionally involved under global *site-specific* intervention; still require value/bound/ancestor/root lineage.
- **Mode 2 flips B, mode 1 doesn't:** terminal draw return site is involved.
- **Both individually flip B:** both sites have some functional ability to change the outcome; no uniqueness claim.
- **Neither individually flips B but mode 3 does:** a nonadditive, multi-site/threshold interaction; **do not** invent a unique mediating call.
- **A changes, another root candidate appears, missing physical source site contact, cold instability, or baseline/mode3 reproduction fails:** separate admissibility and dynamic-support verdicts; no prespecified model-matching claim.
- **No source calls at a selected site:** exclude that site as the cause of its intervention outcome on this tested execution; don't invent a draw mechanism from code inspection alone.

All `value_draw` source calls are under source-global site intervention, **not** a single mutable natural mediator set; site-specific involvement is not a proof of natural TT_FIRST→capture-guard→root mediation. Physical root decisions may also be affected by altered transposition state and subsequent search.

## Source/test/CI proof ceilings

- [9 synthetic source surgery tests](../tools/test_c3x_029_p42_r10_source_site_specific_draw_parity_overlay.py)
- [14 synthetic native event/court negative and interaction tests](../harness/test_c3x_029_p42_r10_native_original_AB_draw_site_court.py)
- [Read-only R10 native workflow](../.github/workflows/c3x-029-p42-r10-native-site-specific-draw.yml), initial [run #42164169618](https://github.com/WhoSia/C3X/actions/runs/42164169618) started; final outcome NOT known at report authoring.
- Public artifact is **allowlisted aggregate-only JSON and attribution**, without private PGN, FEN, raw physical node trace, TT keys, binary or personal chess source. Human WhoSia commits, Actions `contents: read`, never bot-authored repository writes.

## Original research challenge beyond R10

Even if the precise source-call site is isolated, C3X must establish which site return value propagates (or is overruled) through changing windows/TT ancestry to an unrestricted root choice, and—beyond this program-execution result—whether the consumed representation corresponds to a **predeclared strategically meaningful adversarial chess future**, across independent engine/value adjudication and game/event disjoint prospective testing. None is yet demonstrated by R10; Game14 is historical and NNUE OFF.
