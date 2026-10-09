# C3X 0.19 P1B — January Game14 Native TT Cutoff vs Missing Evaluation Assignment

**ADAPTIVE after complete January all31 native assignment watcher.** Preserves original prospective January J2/J3/J4 FAIL and does not reclassify this as independent prediction.

Case #14 STRICT is the **only** one of the 29 lost-old-epoch-V-gate source arms with a new TT writer epoch but no actually executed second main/qsearch TT value-as-evaluation assignment. Source second root call8 has TT native hit for the same full64 key, physical slot0, new shadow epoch2, raw LOWER bound2, TT depth5, current recursive search depth3, window alpha701 beta702 and stored raw TT value1794. Such a record is consistent with Stockfish16's earlier **main TT cutoff** branch; the value-as-eval assignment is downstream of that branch and may never be reached.

## Fixed causal diagnosis

One frozen source case: January game #14, selector STRICT, originally selected source calls7/8 and physical key64 9126712024987466350, slot0, old epoch1. Run native source V-BOTH (first reader blocked, old epoch second gate no longer matches) twice cold with original full FEN clocks and the existing main/qsearch TT probe watcher. Instrument source at the **ACTUAL native return ttValue** in main TT cutoff (after the rule50<90 guard) and at the qsearch early-cutoff return. Source watcher must record actual post-decision TT cutoff RETURN, not merely the condition being evaluated or the TT.probe hit. Keep existing true evaluation assignment watcher.

Risk conditions declared now:
- C14_1_MAIN_CUTOFF: main native TT cutoff *return* for exact selected key and second rootcall8 fires at least once, with full64 live writer shadow match; absence FAIL.
- C14_2_EXPECTED_NO_EVAL_ASSIGNMENT: no post-assignment eval=ttValue occurs at selected second call (as previously audited); any new observed eval use means source or instrumentation drift, HOLD.
- C14_3_PRIOR_NATIVE_CORE_AND_GATE: full six-field UCI and actual TT V block list match the immutable previous January case14 STRICT source arm, twice cold, no watcher censor.
- C14_4_ACTUAL_CUTOFF_CONDITIONS: the actual returning record's bound is LOWER, TT depth >= recursive requested depth, and effective value >= beta, with rule50 guard actually passed at return site. If not, FAIL.
- C14_5_NO_GENERALIZATION: never claim all 29 were evaluated in the exact same source branch; a successful C14_1 would establish **28 native eval assignments + 1 actual TT early cutoff** among 29 original stale-version targeted arms, not a universal law or an outcome-level bestmove mediation.

If the cutoff is absent, retain the missing native-use case and investigate other early-return or search branch reasons; do not retarget another source.
