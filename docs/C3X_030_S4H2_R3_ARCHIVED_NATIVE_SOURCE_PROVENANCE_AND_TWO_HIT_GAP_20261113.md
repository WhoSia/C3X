# C3X 0.30 — S4-H2/R3 Archived Physical Event Audit and the Two-Hit Mediation Gap

**Date:** 2026-11-13 KST. **Conversation:** C3X 33. **Research version retained:** C3X 0.30. Original 0.29 prospective 7/8 remains HOLD. GitHub Actions bot did not author commits.

## Fixed prior design and custody

S4-H0 original outcome-blind manifest raw SHA256 `1741592a52675c5170fdb076bb96b6842cbdced43e40c8a85c82f80c4ba0d247`, verified by archive byte crosscheck [#43347450938](https://github.com/WhoSia/C3X/actions/runs/43347450938). S4-H2 was frozen before treatment outcomes: [#43347740057](https://github.com/WhoSia/C3X/actions/runs/43347740057). Four researcher-authored development game histories contain eight FENs (ply 8/10), not eight independent games. Eight other game histories are reserved as untouched holdout. Neither set represents a randomly sampled population of human games.

Pinned upstream Stockfish16: `68e1e9b3811e16cad014b590d7443b9063b3eb52`. Single thread, 16 MiB Hash, classical evaluation (NNUE off), `go nodes 12000`, two consecutive searches per fresh arm process. First eligible source TT-hit key selected by a source-only probe without root move, score, PV, or judge label. Same modified binary used for sham/zero/one/two/many; true upstream original compiled separately.

## Actual development-native outcomes

Native paired development run [#43349135747](https://github.com/WhoSia/C3X/actions/runs/43349135747): 96 real searches, 1,153,213 real nodes, 19 contract tests, all original/sham/zero controls identical. Sham-relative root move changes over 16 searches:

| Original | Sham | 0 hits masked | 1 hit masked | 2 hits masked | Many hits masked |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | 0 | 0 | 0 | 3 | 10 |

Pre-treatment source key discovery was performed separately; 8/8 development positions had an observed actual source hit. The many-arm source logs are capped at 8 physical receipts per position and **must not be interpreted as exactly 8 physical interventions overall**. Original raw result SHA256 `9806d9aa569150938ad49be6dc365ae4c2e415cf66f7c53b912ac1767ad5edae` [Drive ZIP](https://drive.google.com/file/d/1iUluZkb5jruOS6QOt-6YjKslWspxj0IC/view).

The raw v1 result reported signed link counts but did not preserve each event's full source mask ID/parent. R2 corrected the evidence schema by retaining bounded exact physical source receipts, actual invocation IDs, parent IDs and same-run signed child/root values. [R2 corrected real native CI #43349835109](https://github.com/WhoSia/C3X/actions/runs/43349835109): 96 **new repeated** native searches / 1,153,213 nodes, identical 0/0/0/3/10 choice-change pattern, full verifiable receipts. Original R2 JSON SHA256 `dc1f10272ccbc01c8097f4488057085535fe2cea7c75946895f6b5c81c149120`; [R2 original Drive ZIP](https://drive.google.com/file/d/1RVMbWX_gTicOXplsHSjByhqHsAzs8WNk/view). R2 is a fresh repeat on the same previously seen development cases, **not independent replication**.

## Independent archived-byte re-audit (R3)

[GitHub Actions #43350387650](https://github.com/WhoSia/C3X/actions/runs/43350387650) PASS; seven independent fail-closed test cases PASS, ZERO new native engine searches. [R3 preserved Drive ZIP](https://drive.google.com/file/d/1woQ4r0gBFEgLs7CoNdEJZmnPO4OYyFw_/view). R3 original-audit output SHA256 `70beff7b9a8edf9214cad6c0206f195ccc51efca8156711a08c4d6f6681c4f6d`.

R3 enforced that each recorded mask had the exact pre-frozen TT key, `ply=1`, `hit_before=1`, `hit_after=0`, unique and contiguous bounded ordinal; and each claimed value edge had the actual physical child invocation ID, equal parent ID, and `root_candidate.value == -child_return.value`. Ordinary TT misses never count as masks. Raw source and eligibility receipts were checked against SHA-pinned archived artifacts.

| Arm | Bounded physical mask receipts across 8 FENs | Physically linked signed child-return/root records | Root move changes over 16 searches |
| --- | ---: | ---: | ---: |
| original / sham / zero | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| one | 8 | 0 | 0 |
| two | 16 | 0 | **3** |
| many | **64 logged, truncated by design** | **43** | **10** |

**Scientific verdict:** `PASS_R2_PHYSICAL_SOURCE_PROVENANCE_ONLY`. The 43 signed records are authentic observed within-run arithmetic edges involving actual masked source invocation IDs. They are **not** 43 independently established counterfactual mediation effects or independent games. The three root-choice changes under two-hit treatment do NOT have a captured matching physical child-return-root signed edge. This is a genuine gap in **measurement coverage**, not proof of no mediator. The logger omits some early returns and qsearch, and bounded logs are incomplete.

## Next experiment: S4-I early-exit and causal value graph

Before any holdout treatment, instrument the Stockfish16 main-search TT early return/cutoff values and explicit parent/root score update sites with stable ID and return reason. Preserve source modification noninterference by native controls. Add qsearch coverage only if a defined trace failure requires it, preventing unnecessary whole-tree logging and performance-induced search perturbation.

Predefine a per-case event coverage denominator and a strict `mask -> changed child return -> changed parent/root candidate -> changed bestmove` **across arms**, not merely same-run `root=-child` arithmetic. Never align IDs between separate engine runs without a stable cross-run state identity. Qualify no-effect cases and negative controls. Only then decide whether to open eight-game S4H2 holdout, and separately obtain independent explanation labels for F3 SARFA/response/native/fusion comparison.

## Final admission

PASS: historical pre-outcome H0 raw identity, native source-hit eligibility, same-binary development paired dose, archived R2 mask provenance, R3 independent re-audit.

HOLD: complete ancestor/root causal mediator, source-specific effect of an individual TT entry, prospective independent holdout results, 0.29 7/8, NNUE strategic explanation, response robustness, prior-paper superiority and user learning benefit.
