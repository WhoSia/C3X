# C3X 0.30/P11-S4A–S4B — Original Stockfish16 TT Site Observation and First Source-Site Intervention

**Actual date:** 2026-11-11 KST. **Software version remains C3X 0.30** and chat index remains C3X32. **Origin:** [formal D1 decision](C3X_030_DECISION_D1_NATIVE_CAUSALITY_FIRST_20261111.md), requiring noninterfering physical engine event observation *before* causal intervention. No claims of NNUE, human chess education effectiveness, future strategic plan transport or final C3X 0.29 Game14 mediation resolution.

## A. S4-A authentic source TT probe/save observation and noninterference — 12 actual Stockfish16 searches

**Source** unmodified upstream original `68e1e9b3811e16cad014b590d7443b9063b3eb52`. Exact original `src/search.cpp` SHA256 `21b79baa7ce9dabec5b3b9e3854bed9869a1935277247832e550cf395bccd644`. Source patch SHA `c20f955120a18f52a0b31bb0a317fe9605b183297de1e8b50381f0b1d3fedb73`. Original stockfish16 binary SHA `6458324545ef0f43b5a74de75c980e08413251247bba500d9befac113a43f325`; patched binary SHA `7fbce6ebc91627afbd558f18503971ac7bf0fbbfcf4be7765b7c6dd02d54cbb7`. Both separately compiled from SAME pinned source revision.

**Implementation**: [source-anchored strict patch maker](../harness/c3x_030_p11s4a_stockfish_trace_patch.py), [real UCI source-noninterference court](../harness/c3x_030_p11s4a_native_trace_court.py) and nine synthetic fail-closed tests. Original normal `search` `tte = TT.probe(posKey, ss->ttHit)` and normal final `tte->save(...)` main-search sites at ply 0–3 are each observed (capped 64 probe and 64 save events per process); not a complete qsearch, ProbCut, all TT stores, TT-entry ancestry graph, or parent/root edge graph. Trace emitted ONLY to child engine stderr. Main C++ source decision values, TT saved entry payloads and hit signal are unmodified in S4-A.

- Three **reused P11 development FENs**, all from prior actual 20 positions: Queens Gambit ply4, Sicilian Najdorf ply4 and English ply4.
- Both original and patched engines use Threads1, Hash16 MiB, Skill20, UCI_LimitStrength false, NNUE false, each `go nodes 12000`, two consecutive searches within same UCI process for each original/modified run. Equal settings, legal histories.
- 3 FEN × 2 engines × 2 searches = **12 original native searches, 144,166 actual nodes**, **384 bounded trace events** = 64 probe +64 save per FEN.
- Original/trace variant matched **bestmove, depth, actual nodes, score and reported PV exactly** in every paired search; **0 mismatches**. Wall time/NPS are NOT included in an equality claim and can change from instrumentation.
- [**Original GitHub native CI SUCCESS #42972198720**](https://github.com/WhoSia/C3X/actions/runs/42972198720); nine synthetic tests pass.
- Three preceding CI failures [#42971677033](https://github.com/WhoSia/C3X/actions/runs/42971677033), [#42971819703](https://github.com/WhoSia/C3X/actions/runs/42971819703), [#42971949933](https://github.com/WhoSia/C3X/actions/runs/42971949933) and one [#42972085248](https://github.com/WhoSia/C3X/actions/runs/42972085248) reflect patch-source anchor ambiguity, backslash escaping, wrong assumption there was exactly one `bestValue` TT write (actually 3 source sites), and invalid Python statement separator. No evidence was altered or science gate loosened; all failures retained in GitHub history.
- Source JSON SHA256 `3daa015325a5bd45cc8e63feb9c70bb7a5efb57e6f6f0d73dc9714c14d020c15`; original CI artifact ZIP SHA256 `188e975514abccb13c9a9a8511cd8e37793f42916176a4f604abf9c3a8a390a0`. [**Exact native S4-A original ZIP sealed in Drive**](https://drive.google.com/file/d/1gcLAYGBam2uUB11JwnhlGnf1Ho-a9BmY/view). Note source JSON includes actual 128 raw search event records per tested FEN.

**Gate A decision: PASS for these 3 developer positions**. This proves trace noninterference to tested selected search output fields under the fixed protocol, NOT invariant behavior for all legal positions or all hardware.

## B. S4-B exact preobserved physical TT-hit key mask vs sham — 18 native searches

**Preselection strictly before viewing S4-B results**. S4-B downloads the preceding immutable S4-A GitHub original artifact and verifies exact raw SHA `3daa0153...` prior to any run. For each of SAME 3 FENs, the selection rule picks the **first S4-A main-search TT.probe event with ply=1 and hit=1**, using only real recorded engine trace, not a desired later winning move. Sealed target position keys (decimal):
- Queens Gambit ply4 `4160624996999542926`.
- Sicilian Najdorf ply4 `288240010984383972`.
- English ply4 `2688154765401883805`.

**Physical intervention**: [exact upstream search.cpp patcher](../harness/c3x_030_p11s4b_targeted_tt_mask_patch.py) changes ONLY the `ss->ttHit` Boolean (from `true` to `false`) in the ordinary original `TT.probe` search path **iff `ply==1` AND `posKey==first previously observed real hit key` AND hit was true**; ordinary original TTEntry storage remains. A sham key `18446744073709551615` follows the **same compiled modified binary** but never contacts it in these trials. Source C++ emits bounded masked-site evidence `C3X_S4B_MASKED key=... ply=1 hit_became=0`; source event can contact repeatedly (10 logged contacts per tested position). **Do not call this a one-event intervention**—it is one *specified position key and source hit family*, contacted multiple times.

**Arms** for each fixed developer FEN: (1) unmodified baseline native engine, (2) exact same modified binary with sham mask target key, (3) exact same modified binary with preselected actual TT key. Two consecutive searches per arm, `go nodes 12000`, identical UCI settings, same full history/FEN. 3 FEN ×3 arms×2 searches = **18 actual native searches, 216,210 actual nodes**.

| Prior S4-A selected developer FEN | baseline/sham two successive root choices | actual physical keyed-hit masking two root choices | targeted bestmove changes vs sham |
| --- | --- | --- | ---: |
| Queens Gambit ply4 | `b1c3` → `b1c3` | `e2e3` → `b1c3` | **1/2** |
| Sicilian Najdorf ply4 | `c2c3` → `f1c4` | `f1c4` → `f1c4` | **1/2** |
| English ply4 | `g1f3` → `e2e3` | `d2d4` → `e2e3` | **1/2** |

- **Sham matches original in all six moves and depths/scores/nodes/PVs** (0 observed mismatches across two trials per three FENs).
- **Physical selected-hit contact is observed in all three FENs**, 10 logged matching source hit suppressions per position, sham receives **zero** actual contacts. Code caps log output, so 10 means visible bounded contacts, not necessarily all physical repeated contacts.
- **Three of six target-treatment trials changed the final root bestmove** compared with the identity-controlled sham, one per developer FEN; for the other three, root decision stays but scores/PVs/nodes change. Some targeted runs have **different search depth or actual nodes** from baseline even at the same requested node budget; do NOT claim matched *realized* search work after intervention. The changed search itself is part of the intervention's computational effect.
- No source-child→parent→root trace has been reconstructed. A **source-site physical manipulation of a TT hit signal demonstrably changes root bestmove under a fixed requested-budget condition**, but identifying *which exact computation or ancestor-value effect transmits* still HOLD.
- [Real CI SUCCESS **#42972990269**](https://github.com/WhoSia/C3X/actions/runs/42972990269); nine synthetic test contracts pass. [S4B real runner](../harness/c3x_030_p11s4b_exact_key_mask_court.py). One preliminary [failed CI #42972845504](https://github.com/WhoSia/C3X/actions/runs/42972845504) caught Python missing parenthesis in source patcher, corrected without changing native experiment.
- S4-B original raw JSON SHA256 `081ee839f883d538081f1d2d15c43db1aa31cb12e4e713e1cda81815d5e59300`; S4-B original ZIP SHA256 `d57a4a6610b45c06ebc5d0650cd2a34b5e2a0a694fe112a4d8bc73e11e07a32e`.
- [**Original S4B source-trace + three-arm native results ZIP sealed in Drive**](https://drive.google.com/file/d/1Y7OmCNZXIhVH5tcMFOEe4eNKFTy9YVCs/view).

## C. Rulings: what can be claimed, what is still HOLD

| Claim | S4 decision |
| --- | --- |
| Original Stockfish16 `search.cpp` MAIN TT lookup and final store sites can be read-only logged on 3 previous FENs without changing selected UCI output values | **PASS in S4-A tested 12 searches** |
| Pinned selected real source TT hit key is physically contacted under the mask, with same compiled binary negative key sham | **PASS S4-B physical contact + sham controls** |
| Root bestmove can change due to masked TT-hit source signal under this fixed requested-node protocol | **PASS development pilot** — 3/6 targeted trials, one per FEN |
| One *individual* native TT table entry is uniquely responsible | **HOLD** — multiple contacts to a selected position key, actual cached entry contents and other search state not individually isolated |
| Child→parent→root score transmission is reconstructed | **HOLD** — no ancestry correlation instrumentation or paired per-node mediation |
| Generalization to an independently sampled FEN/game cohort | **HOLD** — all 3 FENs and first-hit target key metadata were drawn from previously inspected P11/S4-A development records |
| Stronger-than-static future plan robustness under varied opponent policies | **HOLD** — no new independent future-response experiment in S4 |
| NNUE conceptual causal feature importance, real educational impact | **HOLD** — engine uses `Use NNUE=false`, no learner study |
| Frozen prospective 8-eligible-game broadcast cohort | **HOLD 7/8** — not modified or redefined |

## D. Next implementation gate

**0.30/P11-S4C — Root-ancestor event path evidence**, not a new generic XAI method implementation. For **one sealed source FEN and selected key**, instrument search entry/return of ancestry correlations (include currentMove stack chain and `ss->ply` carefully), TT hit, cutoff values, parent `bestValue` and root candidate/rank update; show actual data-flow before declaring mediator. Restrict source event mask to one occurrence or clearly retain repeated-key-family scope; add negative keys and equivalent work controls. If source logger changes engine decisions under the chosen protocol, HOLD. Then preregister **unseen** independent positions and full game histories and confirm outcomes without target cherry-picking. Only then use independent Berserk strategy tree to test whether TT-driven root switch corresponds to a response-robust plan.

Preserve source experiment exact SHAs on GitHub/Drive, Notion verdict and no GitHub-Actions[bot] contributor changes. Existing P11/S1–S3 archives are untouched.

**Missing-only C3X original scholarship unchanged**: Björnsson (2024) *Chess and Explainable AI*; Bratko & Kopec (1982) original chapter; Gadwal et al. (1993) *Tutoring Bishop-Pawn Endgames*; Herbeck & Barth (1996) ICCA article; Demura & Kaneko (2024) ICGA final version. No newly supplied research PDF was ingested in this S4 development cycle.
