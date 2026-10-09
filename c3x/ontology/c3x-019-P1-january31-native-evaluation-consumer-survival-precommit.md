# C3X 0.19 P1 — January 31-Arm Native Evaluation Survival, Prior Target-Event Attrition Audit

**ADAPTIVE full-sample diagnostic, declared before the new native-assignment observations; not a new independent holdout.** Use exactly all previously fixed January 2026 games 1–16 and STRICT/BROAD source-pair role arms (31 eligible: 15 STRICT, 16 BROAD), with their already selected physical writer target and second root-call handle. There are only 25 unique source game/target/call pairs: overlap disclosed rather than treating 31 as independent.

The 0.18 all-31 TT shadow epoch audit observed 29/31 selected V-BOTH arms lose old-version-addressed second reader_block, although that second root call still executes and a native hit on the same full64 key occurs with a new writer epoch (epoch+1). This does **not** test whether genuine Stockfish main/qsearch TT value-as-evaluation assignment still executes.

## Fixed intervention and independent native-use witness

Frozen SF16 68e1e9b3811e16cad014b590d7443b9063b3eb52, depth12, Threads1, Hash16MB, NNUE disabled, true original halfmove/fullmove FEN clocks. Exact original source full64 physical key, slot, epoch, and the original selected two root-call handles. For every eligible original role arm, run its UNMODIFIED V-BOTH source intervention **twice cold** with the new **read-only post-assignment** watcher at the second call. Never restore bytes or shadows, do not retarget and do not allow any shadow-only inconsistent arm in this followup.

Save original actual reader_block list, independent true native post-assignment uses, shadow TT probe key/slot/epoch/serial/raw depth/bound/value, root entry, exact six-field UCI. Fail closed for any mismatch against the immutable original January V-BOTH six-field UCI and recorded actual blocked TT reader calls or if native watcher censored. Process all sixteen, including the game without a STRICT pair.

## Risky adaptive predictions

A1_NATIVE_SURVIVAL_AT_LEAST20: at least 20 of the 29 originally old-epoch-ineligible second reader arms must still have at least one actual native TT score-as-evaluation assignment at that SAME second root call with matching full64 key. Otherwise FAIL.
A2_MATCHED_NATIVE_SCORE: in all cases counted as native survivors, actual cached score-as-evaluation use must report a full64 matched live shadow key, a native hit in the watched window and a post-assignment value; any alleged use that lacks this evidence => FAIL-CLOSED.
A3_NATURAL_SOURCE_UNCHANGED: all 31 original V-BOTH outputs and actual gate contacts exactly match frozen prospective January original UCI and original native treatment contact sets, with two cold repeats. Any drift => HOLD.
A4_DENOMINATOR: all sixteen games and exactly 31 source role arms retained, zero selectors shifted. Any absent case => HOLD.
A5_DISTINCT_PAIR_COUNTS: report 25 unique source game/physical target/root-call pairs and preserve duplicated STRICT/BROAD roles separately.

Successful A1 demonstrates a **general retrospective diagnosis of false "consumption disappearance" from target-epoch mismatch**, NOT an independent confirmation of a transportable root-choice causal mediation rule. Earlier preregistered January J2, J3 and J4 remain FAIL. The full raw score/bound/depth changes and any cases with no native assignment must be disclosed rather than reselected.
