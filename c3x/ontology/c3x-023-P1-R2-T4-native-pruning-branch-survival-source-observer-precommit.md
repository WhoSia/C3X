# C3X 0.23–P1–R2–T4 — Native Pruning-Branch Execution and Search-Path Survival Audit (PRE-EXECUTION CHARTER)

**Status:** FROZEN_PROTOCOL_BEFORE_T4_NATIVE_BRANCH_OBSERVER_EXECUTION; this is an additive experiment inside **ACTIVE 0.23**, not activation of 0.24. Date: 2026-10-11 KST.

## Fixed source and inherited evidence

- Exactly two previously selected **development** roles: **May 2026 Lichess broadcast #11 / F / STRICT / qsearch_prune / original SEE 0** and **#2 / O / STRICT / quiet_prune / original SEE 1**. No alternate case selection. Holds #1/#12 and first32-censored #8/#3 remain HOLD.
- Physical TT FIRST, source-specific native SEE singleton, exact T1 original-frame identity, and SHAM-before-FLIP belong to T3. Locked before first intervention in Git commit `31ed4f0bf7fa23a90f582ad074c75921bcb450fc`. T3 canonical native runs `38070604820` and `38070768528` SUCCESS; 16 cold runs, 4/4 actual source flip contacts, 4/4 sham source contacts, 4 TT-first physical reads suppressed.
- Source S0 SHA256 `0ff43e28dcb3a5e48dea6b61e4450fc8bb9e1f96363871c33c4b73524664db61`; untreated Stage A `fe88afe49d7d43db7b81c37decab783f2b68311ed2ca10b6f42be4268bdb3442`; T1 native source `6c0440693c83ba0cd219d396b7d1cb2cdd14e3324f0c0f77485edf1df288c0a8`; T2 source artifact `830536f445330b739a7a3b7e88ce4227e9ab9db43cf277f08a01ed5f9dc0ef69`.
- **No new experimental site** chosen after the T3 `b1b4` outcome; T4 is post-outcome descriptive mechanistic follow-up, not an independent prospective test.

## Distinguish three levels rigorously

**L1 — SEE contact and Boolean:** Native `Position::see_ge` yields an original Boolean; T3 may return a different delivered Boolean at exactly one original source site. SHAM must return original.

**L2 — *actually executed* immediate branch:** In the pinned Stockfish16 source `search.cpp`, both sites use `if (!see_ge(...)) continue;` (after replacement by our instrumented wrapper). T4 must observe and log **ACTUAL_CONTINUE** from inside the taken source `if` arm, or **PASSED_SEE_GUARD** only after the `if` arm is bypassed, not infer it by counting total nodes or the pre-branch SEE log. `PASSED_SEE_GUARD` is *not* necessarily `SEARCHED_MOVE` or `SURVIVED_ALL_LATER_PRUNING`. Main quiet search has further later gates.

**L3 — downstream search and terminal effects:** In all 4 arms per case retain exact cold depth 1–12 root leader, source score, final UCI/nodes/bound and intervention contacts. A different L2 outcome is not an identified unique causal chain to the final root choice unless descendant ancestry and all alternative path changes are separately observed.

## Primary source-level contract (8 arm worlds)

For `TT0_SHAM`, `TT1_SHAM`, `TT0_FLIP`, `TT1_FLIP` in BOTH frozen cases:

1. Reconstruct original exact T3 binary from pinned SF16+ordered overlays and additionally instrument **only** the two previously instrumented `quiet_prune` and `qsearch_prune` conditional guard statements with a read-only, opt-in, exact-T3-target branch observer. No new SEE/TT mutations.
2. Prove exactly one target native source contact and exactly one matching executed branch event per arm. Fail closed if zero, more than one, mixed site, different path, wrong original Boolean or no physical TT writer→reader proof in TT1 arms.
3. For #11, original Boolean 0 predicts SHAM `ACTUAL_CONTINUE`, flipped Boolean 1 predicts `PASSED_SEE_GUARD`; for #2, original Boolean 1 predicts SHAM `PASSED_SEE_GUARD`, flipped 0 predicts `ACTUAL_CONTINUE`. **These predictions follow syntax and are controls, not novel discoveries.**
4. A no-observer T3 replay and T4-passive observer replay must agree on the complete end UCI object, per-depth root records, node counts, and all treatment-contact counts. Mismatches are `OBSERVER_PERTURBATION_HOLD`, never scientific negatives.
5. Cold repeats must match byte-for-byte after eliminating no fields; no early truncation of source events. If additional trace collection is censored, report `PATH_CENSORED`.
6. Compare `#11` (terminal SEE-negative) and `#2` (joint-only positive), retaining the null and all historical M1/M2 failures.
7. Public artifacts use derived aggregate/short UCI and provenance SHA + attribution only. No third-party full PGN/FEN/player headers, no private TWIC letter, no modified Stockfish binary/source redistribution. License scan PASS is **not** permission.

## Contrasts fixed before T4 execution

Define for any measured numeric outcome Y, after all four valid arms:
`Delta_TT = Y(1,0)-Y(0,0)`;
`Delta_SEE = Y(0,1)-Y(0,0)`;
`Delta_joint = Y(1,1)-Y(0,0)`;
`I_Y = Y(1,1)-Y(1,0)-Y(0,1)+Y(0,0)`.
Here TT=1 denotes first-reader blocking and SEE=1 denotes a single forced source Boolean flip. For **nodes**, compute `I_nodes` descriptively only; it is not a causal mediator effect or per-node additive semantics. **Do not apply arithmetic to categorical bestmove IDs**; compare the four literal exact-UCI strings and first common-depth leader/score divergence instead.

Historical T3 node contrasts at #2: `20,062 / 41,685 / 46,783 / 47,563`, hence `I_nodes = -20,843`. At #11: `64,424 / 68,114 / 64,426 / 68,116`, hence `I_nodes = 0`. Both are derived from prior outcomes, NOT prospective T4 branch evidence. Nodes are search effort, not directly the number of pruned descendants.

## Authority ceiling / gates

- **T4_BRANCH_SOURCE_CONTACT_PASS** only after actual instrumented branch event and 8/8 cold observer equivalence; **T4_DOWNSTREAM_TRACE_HOLD** until an independent lineage chain identifies descendant visits/omissions, with explicit first divergence and censoring.
- **NATURAL_TT_TO_SEE_MEDIATION_UNIDENTIFIED** remains mandatory even if branch event switching is validated, because the SEE Boolean was artificially forced.
- **C3X 0.24 remains PROPOSED**. Future M3 predictions must be Git-sealed on a truly new chess source **before outcomes**; development T4 cannot count as external validation.
- Actions workflow must have `contents: read` only, no write permissions, no push/commit from Actions, and no `github-actions[bot]` commits/co-authorship.
