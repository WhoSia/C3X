# C3X 0.30 — S4-I Native TT Early-Cutoff Diagnostic on the Frozen Development Cohort

Date: 2026-11-13 KST. Conversation: C3X 33. Retains C3X research version 0.30.

## Why this diagnostic is necessary

S4-H2/R3 independent physical source audit (CI [#43350387650](https://github.com/WhoSia/C3X/actions/runs/43350387650)) confirmed 43 signed masked-child/root arithmetic links under many-hit treatment but 0 such links under two-hit treatment, even though two-hit treatment changed the root move in 3 of 16 development searches. This is a coverage gap, **not** evidence that the change lacks a mediator. The original Stockfish16 `search.cpp` contains an early transposition-table cutoff `return ttValue` that the S4E general-return logger does not capture.

## Source patch and controls

- Fixed original Stockfish16 commit: `68e1e9b3811e16cad014b590d7443b9063b3eb52`.
- Built actual upstream and an amended single source-patched binary for both sham and two-hit mask. Source patch inserts a read-only bounded `C3X_S4I_TT_CUTOFF` receipt **immediately before** the literal `return ttValue;` within the TT early-cutoff branch, without changing the returned numeric value, TT object, mask, alpha/beta or search state.
- Reused *exact archived* R2 development eligibility keys from SHA `dc1f10272ccbc01c8097f4488057085535fe2cea7c75946895f6b5c81c149120`; keys were not chosen after examining the new outcome.
- All eight previously inspected development FENs (four game histories, two correlated snapshots each); no held-out positions.
- Three arms per FEN (upstream original, same-patched-binary sham, two-hit mask), two consecutive 12,000-node searches per arm. 48 actual fresh native searches.
- Read-only return logger is bounded to **8 cutoff events per engine process** and `other_stderr` retention is also bounded. Saturated values cannot be interpreted as an exact total.
- Fail-closed source patch and parser tests, original-sham noninterference in bestmove/depth/nodes/score/PV.

## Actual CI result

[Real native S4-I CI #43351378322 — SUCCESS](https://github.com/WhoSia/C3X/actions/runs/43351378322). 9 contract tests PASS, **48 fresh searches, 576,619 actual nodes**, all original/sham noninterference checks PASS. Native output JSON SHA-256 `6602886812f24da855f22554b59332fd22da61f6bf9200d8593fa734de820fc6`. [Original ZIP preserved in Drive](https://drive.google.com/file/d/1FZWbS5JwTWx8Yz0c6UQoE37mg0hoCQCT/view).

| Development position | Sham observed TT early returns (bounded) | Two-hit observed early returns (bounded) | Two-hit root move changes / 2 |
| --- | ---: | ---: | ---: |
| Italian ply 8 | 0 | 2 | 0 |
| Italian ply 10 | 8* | 8* | 2 |
| London ply 8 | 5 | 6 | 1 |
| London ply 10 | 7 | 7 | 0 |
| Pirc ply 8 | 5 | 5 | 0 |
| Pirc ply 10 | 3 | 3 | 0 |
| Scandinavian ply 8 | 8* | 8* | 0 |
| Scandinavian ply 10 | 5 | 5 | 0 |
| **Logged totals** | **41** | **44** | **3** |

\* TT early-return logs saturated at eight; true total events may be larger. Logged totals are lower bounds, not full path counts.

## Causal interpretation

A narrow, source-verified result is now available: in Italian ply 8, the sham trace logged no target-key TT early cutoff while the two-hit intervention trace logged two; in London ply 8, the corresponding bounded counts were 5 and 6. Both were obtained from the same modified binary with different masking conditions, while true upstream and sham agreed on final UCI results. Thus the intervention can accompany a **changed set of observed TT-short-circuit opportunities**, rather than merely removing a value at a permanently fixed single call.

However raw invocation IDs in separate engine processes cannot be aligned naively; same count, count increase or a signed arithmetic link does not identify the counterfactual ancestor that changed the root decision. The new logger only covers the TT early cutoff branch and only for the frozen ply-one key. Other return paths and qsearch remain unobserved.

**PASS:** actual bounded TT early cutoff source receipts, physical two-hit intervention, noninterfering negative control, observed root changes.  
**HOLD:** full root-choice mediation, unique TT cell direct effect, independent prospective holdout, response-robust chess plan, superiority over SARFA/SHAP/other methods, and original 0.29 7/8 prospective cohort.

## Next research gate: S4-J

Establish a cross-arm state identity composed of legal move prefix, search depth, PV/non-PV role, alpha/beta interval, and TT key; do not equate IDs across processes. Add full return-reason coverage only for the target's affected ancestry, and account for qsearch boundary. Validate that the logger does not alter bestmove/depth/nodes/score/PV in original-sham controls. Measure what fraction of the physically masked event's effect is observed through source-value transmission, with unknown states explicitly recorded. Do not unlock S4-H2 holdout before freezing the developed mechanism and label protocol.
