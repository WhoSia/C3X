# C3X 0.30 — P11/S4G Original TT Mask + Native Invocation Value-Flow, and S4G/R1 Physical-Receipt Correction

**Research date:** 2026-11-11 KST. **Version C3X 0.30 retained**, C3X conversation 32. D1 scientific direction = actual Stockfish search event→child return→parent/root causality, not new ungrounded XAI wordings. The separate F1 SARFA / independent response / native causal three-gate comparison protocol remains a **hypothesis, not a proven better method**.

## 1. New S4G real native source experiment — exactly 36 actual searches and 432,459 actual native nodes

[**S4G actual native GitHub CI #42994310105 SUCCESS**](https://github.com/WhoSia/C3X/actions/runs/42994310105), 9 source/receipt tests, [exact source patch](../harness/c3x_030_p11s4g_masked_invocation_patch.py), [native paired court](../harness/c3x_030_p11s4g_native_paired_court.py). First [#42994112549 FAILED](https://github.com/WhoSia/C3X/actions/runs/42994112549) for strict S4E patch anchor mismatch; corrected **before any successful native outcomes**, retaining failure and no custom changes to Stockfish original.

Same exact [upstream original Stockfish16 commit `68e1e9b3811e16cad014b590d7443b9063b3eb52`](https://github.com/official-stockfish/Stockfish/commit/68e1e9b3811e16cad014b590d7443b9063b3eb52), `Use NNUE=false`, Skill Level20, Threads1, Hash16MiB, `go nodes 12000`, two consecutive searches per arm. **Three already-seen development FENs**, QG ply4, Sicilian Najdorf ply4, English ply4, target TT ply1 position keys were selected from an **earlier SHA-frozen original S4B source** `081ee839f883d538081f1d2d15c43db1aa31cb12e4e713e1cda81815d5e59300` before S4G effects.

Six arms ×3 FEN ×2 real UCI searches = **36 native searches**:
- true original upstream binary;
- **sham**, same modified binary with unrelated key;
- **zero**, same modified binary real key with mask budget 0;
- **one**, mask first real qualifying hit once;
- **two**, mask first two qualifying hits;
- **many**, mask up to 10,000 matching hits per engine process, **first 8 events only are logged in stderr**, not all real hits.

This S4G **same modified binary** includes a source-level per-invocation ID/parent ID, TT hit, normal return, and root candidate value, plus actual physical `C3X_S4G_MASK ordinal=... id=... parent=... oldhit1→0` at the exact key and ply1. Read-only return/root source logger is filtered to the immediate last completed target-key main-search child rather than flooding unrelated candidates. Original TT.probe and TT save source calls remain. Raw native moves/nodes/depth/score/PV exactly match between **original, sham and zero-dose** arms; targeted 1/2 doses do not change the selected root bestmoves here.

| Previously observed FEN | Root bestmove switches vs sham (original / zero / one / two) | Many-dose switches vs sham | Physical mask receipts logged in one / two / many |
| --- | --- | --- | --- |
| Queen's Gambit ply4 | 0/2 each | **1/2** | 1 / 2 / 8 (lower-bound under logging cap) |
| Sicilian Najdorf ply4 | 0/2 each | **1/2** | 1 / 2 / 8 (lower-bound) |
| English ply4 | 0/2 each | **1/2** | 1 / 2 / 8 (lower-bound) |

Same-binary intervention results: **0/6 root choice changes for 0,1,2 dose**; **3/6 root choice changes for many**, exactly one first-trial difference per original FEN. These are developer repeated-position results, not independent validation. Actual node/depth differences after target intervention are allowed/recorded and no same-realized-work claim is made.

**Original actual native S4G JSON SHA256** `71cecc490edad3090263e7695359e21568b8206a53fe213cff633c12c18ccecf`; original artifact ZIP SHA256 `1fcdbdcfe078b978238f9be5c7b6b42f27c1c448e894456814f3e579830d5672`. [**Original S4G native 36-search ZIP sealed on Google Drive**](https://drive.google.com/file/d/12is3OFfSluIeZJE6h8cXEtYN_HQWaf6Z/view).

## 2. Critical S4G/R1 independent raw-byte correction: hit=false is NOT proof of physical intervention

S4G original raw result field named `observed_links_with_masked_TT_hit` was **overly broad and ambiguous**. Its underlying predicate counted **ALL post-probe `ttHit=false` events**, including genuine **naturally missing TT entries**, as well as actually suppressed hits. In many-dose arm the prior aggregate was **63 post-probe hit=false return-root value links**. This number **must NOT** be represented as 63 actual manipulated TT source-to-root links.

A strict independent read-only correction [`harness/c3x_030_p11s4g_r1_physical_mask_receipt_audit.py`](../harness/c3x_030_p11s4g_r1_physical_mask_receipt_audit.py) re-downloads the **exact original S4G JSON SHA `71cecc...`**, rechecks source status and nodes, and matches *real source intervention receipts* `C3X_S4G_MASK` to **the exact child invocation ID + real root parent invocation ID** in the *same* logged normal-return→root negamax arithmetic record, with exact mask key, ply1, hit before true/after false and `root_candidate_value == -child_return_value`.

**Corrected source-identified physically masked invocation returns that are also root candidate value links:**
- Queen's Gambit **6**
- Sicilian Najdorf **6**
- English **6**
- **18 in total** (out of at least 8 logged physical mask receipts per FEN; unlogged further intervention contacts are unknown, not zero).

In the bounded trace from the 1/2-hit dosage arms, **zero** such complete physical mask→normal-return→root arithmetic edges were logged, which must NOT be interpreted as proof no change elsewhere occurred. The larger-dose arm also has only bounded partial log, so `18` is a **verified observed subset**, not a census of all actual native causal transmission.

[**S4G/R1 actual immutable original correction CI #42994910019 SUCCESS**](https://github.com/WhoSia/C3X/actions/runs/42994910019), 4 adversarial synthetic source-identity tests, **0 new native searches**, derived audit JSON SHA256 `062b6e4d6b07c16bef20736b197691bd0b0d95ca88b391b87a2b448a903ccb4f`, original R1 audit ZIP SHA256 `e7f2531ea1a296f7b6e104af2b9012f112c47c22ca8d004b355479c1c2404088`. [**Verified source-physical R1 correction ZIP sealed on Google Drive**](https://drive.google.com/file/d/1U8GFNgv-HzGHPBSMOWvU8Gg3WtZ59g26/view).

**Scientifically distinct statements:**
1. **PASS** under tested source / developer FENs: a physical source-hit mask occurred (real source log) on an identified invocation, the **same** invocation later produced an observed normal search return, and a real candidate root event with its exact parent ID carried its sign-negated value. **18 observed full physical-source arithmetic links** (not 63).
2. **PASS** in same FEN paired design: repeated source hit masking changed root bestmove **3/6** while single/two did not, with same modified source binary and independent sham.
3. **HOLD**: proving *each* of those 18 source hits caused the value to differ counterfactually, or proving a **specific TT table entry** alone caused an ancestor score/root selection switch. Need same-node matched pre/post intervention with full early-cutoff/qsearch, full trace and no log truncation, and independently selected game histories. A value linked to a physical intervention in a treated run does **not** by itself demonstrate the intervention changed that value.
4. **HOLD**: any claim that this native program already outperforms Puri/SARFA, Cui strategy trees or learned language models in their original benchmarks. Our [F1 four-comparator contract](C3X_030_S4E_R1_AND_F1_TRIANGULATED_SOURCE_RESPONSE_CAUSAL_COMPARISON_20261111.md) has only **synthetic** unit validation, no user-blind factual labels and no authentic same-case original paper comparators.

## 3. Next scientific design decision

**P11/S4H (planned, not executed):** smaller bounded instrumented intervention worlds with complete TT key-hit and early return coverage, per-invocation parent-update recording, explicit before/after root candidate value *for same move and comparable depth*, and sham controls. Prefer a selective bounded event logger filtering by precommitted key/parent ID without using a global 240-event cap for decisive traces. Then preregister **new independent complete game histories** before running source causal estimates. Group case analyses by game, not related FEN checkpoint. A negative TT effect or failed chain is a real result.

**F1 method innovation decision:** tri-gated SARFA sensitivity + independently evaluated opponent reply strategy + native provenance is promising as a **more conservative explanation-certification method**, not yet a proven superior algorithm. Benchmark fixed false-claim risk vs coverage, grouped holdout paired independent labels and source/judge work, not fabricated human preference.

## 4. Literature holdings and research OS

No new 00_INTAKE original scholarly PDF in this particular S4G cycle; earlier [Gadwal et al. (1993) 36pp author manuscript held](https://drive.google.com/file/d/1iRfADIUxHmiVD4vOEVsaTAZw2ivYtFcy/view) in `10_PAPERS`, typeset Applied Intelligence version not collated. Remaining exact unowned full originals: Björnsson 2024 *Chess and Explainable AI*; Bratko–Kopec 1982 original chapter; Herbeck–Barth 1996 ICCA; Demura–Kaneko 2024 ICGA. Their author/academic-library paths remain legal options, publisher restrictions not misrepresented as free PDFs.

The historical C3X 0.29 prospective eligible cohort remains **7/8 HOLD** (not promoted or reset).
