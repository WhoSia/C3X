# C3X 0.31/P2-D1 — Frozen Equal-Depth Diagnosis of the Seven New-Game Root Flips

**Status:** exploratory post-treatment-selected native follow-up, NOT independent blind replication and NOT a new source-event rate sample. **Frozen 2026-11-21 before this P2-D1 experiment executes.**

## Why this follow-up is required

P2 physically intervened on 128 source early-return events from 64 TWIC1670 source games at the original fixed 32,000-node budget, with seven actual final `bestmove` flips. Independent full-log audit found **only P2-008-1 of those seven ended at the same completed iterative-deepening depth** under baseline and treatment. Six differed in completed depth. Those are valid finite-budget total effects, **not automatically a within-depth move-preference contrast**. It is not acceptable to exclude the six and report a flattering 1/1 same-depth success rate.

## Frozen cases and source event identity

Exactly the seven previously observed flip events from independent [P2 court](C3X_031_P2_TWIC1670_TRUE_NATIVE_TRANSPORT_RESULTS_20261121.md), no case replacements:

| Frozen source event | Original 32k depth | Treatment 32k depth | Fixed-depth arms |
| --- | ---: | ---: | --- |
| `P2-008-1` | 13 | 13 | 13 |
| `P2-027-1` | 11 | 10 | 10 and 11 |
| `P2-028-0` | 16 | 15 | 15 and 16 |
| `P2-034-1` | 12 | 11 | 11 and 12 |
| `P2-035-0` | 12 | 10 | 10 and 12 |
| `P2-043-1` | 11 | 9 | 9 and 11 |
| `P2-055-0` | 17 | 13 | 13 and 17 |

That is **7 original games and 13 precisely selected depth cells**, each evaluated under:
1. pre-R33 patched R31-native reference search, no observation (`depth=d`);
2. R33-patched observer-disabled same-depth source search;
3. R33-patched observer-only, original target selected, no gates suppressed, repeated twice;
4. R33-patched *both* futility and null branch exits suppressed at the **exact pre-frozen original physical event**, repeated twice.

At maximum 13×6 = **78 source searches**. If a target is absent under a depth run or pre-treatment OPEN identity changes, count it as **`HOLD_TARGET_CONTACT`**; do not pick another target. If old reference, R33 observer-disabled and observer-only baseline don't match on normalized UCI, source proof and completed depth, stop as **`HOLD_BASELINE_PARITY`**. Cold pair disagreements must be reported, not averaged or scored as a negative chess result. Original frozen P2 source game SHA, source-event JSON SHA, R31 and R33 binary SHAs, and NNUE SHA must all match exactly.

## Primary diagnostic endpoints (not a new P2 success gate)

For each fixed-depth cell, report full baseline and treatment `bestmove`, completed depth, original selected source OPEN identity/contact, immediate return, and actual searched nodes. The primary comparison is the **originally completed reference depth** for each of the seven; the treatment-completed depth is an additional *registered sensitivity arm*. Record whether each original 32k-node root flip:
- **PERSISTS_AT_ORIGINAL_COMPLETED_DEPTH**, with physically matched contact and complete depth;
- **DOES_NOT_PERSIST_AT_ORIGINAL_COMPLETED_DEPTH** despite valid contact (negative result);
- **HOLD_TARGET_CONTACT** where physical target cannot be matched under changed stopping rule;
- **HOLD_BASELINE_PARITY_OR_REPLAY** if the source world changed unexpectedly.

A fixed-depth selected move contrast may still use different node counts/history states, and a source perturbation may move another root candidate or later aspiration attempt. **It does not certify equal search work, TT/history mediation, chess strategy superiority or learning benefit**.

## Claim and custody

Original P2 source [private 64-game freeze](https://drive.google.com/file/d/1Aj02UgRoHYw6sKqPjwOmtDETfTnESpe8/view), [precontact 128 target identities](https://drive.google.com/file/d/1xAoyKx1vqYASkf5wviz5SINWmfMylLal/view), [original 576 actual native searches](https://drive.google.com/file/d/1G7zGJTP2PMiNqx-6cjNc3s6QBqLhV5mq/view) and [independent original logs](https://drive.google.com/file/d/18h5eLTe89lQJY7_fwePwIau9jUNiGedw/view) are immutable.

Native P2-D1 logs belong in private Drive, small court and reproducible code GitHub, scientific judgments in [C3X 0.31 Notion](https://app.notion.com/p/41fef561cf9281ae8a62d4c153f11c01). Never rewrite original P2 labels or reinterpret the seven as a prospective sample. Keep failures/censored runs explicit.

**Next P3 source-state question:** On genuine same-depth survivors, which minimal physical TT/read/write, history or search-allocation state restores the original choice under a valid same-prefix sham-controlled intervention? The current protocol does not answer it.
