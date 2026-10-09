# C3X 0.19 — Critical Causal Identification Erratum: Shadow Writer Address vs Actual TT Evaluation Use

**2026-10-10; preserve all historical outputs and failures.** This corrects causal *interpretation* of C3X018 P0/P1 rather than editing its historical SHA or its genuine observed source writer transition.

## Distinct events that must never be conflated

(A) Analyst-selected physical target: full64 key + TT physical slot + old write epoch1.
(B) An old-epoch V-gate reader_block: our experimental software has PREVENTED native use on a matched source branch.
(C) Native TT value-as-evaluation use: the original engine actually EXECUTED the assignment of eval=ttValue after all bound/eval branch conditions.

Source gate (B) is intentionally keyed by shadow writer state; this is not a native Stockfish TTEntry field. Native use (C) is determined by engine bytes, TT probe and search conditions. The old interpretation implicitly treated the disappearance of (B) after epoch1→epoch2 as disappearance of (C), without independently measuring (C).

## Falsifying ten-arm native experiment

[Native source run #37996723901](https://github.com/WhoSia/C3X/actions/runs/37996723901); [SHA-pinned source receipt](../receipts/c3x-019-P0-orthogonal-TT-payload-shadow-and-native-eval-use-20261010.json).

January #2 STRICT, first blocked value reader rootcall4, selected second call5. Native old version depth0, shadow epoch1 writer serial60; subsequent accepted native TTEntry::save replacement depth1, epoch2 writer serial130. Cached value stays -89, bound LOWER, cached static eval -284.

Each old/new raw payload and shadow-tag treatment was tested both with V BOTH (source intervention targets both calls) and with first V blocked but second source branch ALLOWED to execute normally; the latter logs immediately after native eval=ttValue. All ten arms cold repeated independently.

| Treatment | Raw TT depth at call5 | Shadow epoch | Old-epoch reader_block? | Genuine TT eval assignment when allowed? |
|---|---:|---:|---|---|
| NONE | 1 | 2 | no | yes |
| SKIP | 0 | 1 | yes | yes |
| FULL both restored | 0 | 1 | yes | yes |
| BYTES_ONLY | 0 | 2 | no | yes |
| SHADOW_ONLY | 1 | 1 | yes, with raw mismatch | yes |

**Correction:** Native TT evaluation use at call5 remained present in the unrescued natural modified arm (epoch2). Conversely, restoring only the analytical shadow old-epoch tag caused the V reader_block to reappear **without restoring the underlying TTEntry bytes**. This is an instrumentation-target artifact, not evidence a natural computation was recovered.

## Still supported

The frozen actual depth-driven SF16 payload overwrite remains real; writer serial60→130, slot epoch1→2, TT stored depth0→1 while raw score/bound/eval remain equal. Old physical writer epoch1 was genuinely replaced. The physical *old-version-addressed* V operator no longer matches after that overwrite. Those source facts remain true.

## No longer supportable

It is NOT correct to assert that a version mismatch by itself proves the naturally used TT score-as-evaluation branch disappeared. It is NOT correct to treat restored V reader_block as evidence that native TT consumption was absent until restored. There is still no independently transported natural root bestmove causal explanation. The earlier prospective January J2/J3/J4 predictions and the first unbounded P1 R5 negative control remain FAIL.

## Mechanism ontology

Let E be native engine TT bytes + current search state (window, ply, root context, control flow), and L the analyst shadow writer state. Without instrumentation, normal native use is U(E), not a predicate on L. Source selective suppression uses gate G(E,L,q), which additionally depends on an old-version target q. Changing L alone can change G without changing E; a later native score assignment may still be possible. This is an identification-limit statement specific to our instrument, not a universal new chess law.

**Correct vocabulary:** writer version replacement; loss of old-version V targeting; native TT evaluation still used in January case #2; old-version gate restored under a synthetic metadata rewrite. Continue source-only reverse engineering and independent blind followups, but do not overclaim endogenous TT mediation of final root choice.
