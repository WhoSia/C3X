# C3X 0.18 — Adaptive December Case11 Old-Reader Collision Disambiguation

**ADAPTIVE AFTER OUTCOMES; does not modify D1 and is NOT an independent confirmatory sample.** December 12-game source and all 96 interventions are sealed. Prior complete native JSON SHA `93742e35c09f83a24aeea91f3632227165bb9208c606e3b81766e54d512a9883`. Provenance audit `c3x/receipts/c3x-018-december-role-target-earlier-reader-collision-audit-20261010.json` discloses exactly 7/96 marginal role-selected TT physical triples whose first targeted reader occurs **before** the selected old role event; all seven are in category `old`.

For December game #11, source `old` chosen passive reader at ordinal 33 has `writer_age_writes=90`, within-arm `reader_root_call=9`, `reader_root_move=1431`, `ply=1`, `raw_bound=2`; **but** the same physical `(key64=16448589199907615799, slot=0, epoch=2)` was previously consumed at ordinal 11, `writer_age_writes=18`, within-arm root call 5. The original V physical triple thus suppresses the **earlier** read, and its bestmove change from `b2b3` to `c1f4` cannot be credited specifically to the age90 reader.

## Frozen adaptive new operator before use

Source-exact overlay augments the existing TT V gate with optional simultaneous predicates:
- global accepted write age `>=64` at the actual consumer,
- root-call index exactly `9`,
- root candidate native `1431`,
- search ply `1`,
- original writer bound `BOUND_LOWER=2`.

Define four cold double-repeat trials on the *same* SHA-frozen game and same fixed physical triple: BASE (F, no selective V), V_ALL (original unfiltered physical gate), V_AGE64 (only age>=64), V_EXACT (age>=64 plus root_call9/root_move1431/ply1/bound2). A wrong-root-call8 plus age64 is **negative control**. O/F/Z controls must exactly replay the frozen original FEN source result.

Report all actual source reader contacts, their age/root/bound/ply, final UCI six-field core and first positive TT reader return. Fail closed if V_EXACT doesn't contact an original source event; never retarget to another key or shift root call. Do not assume identical numeric writer serial or root call across arms after trajectory divergence.

## Rival predictions

- **A11_EARLIER_SCREEN:** V_EXACT (age>=64, rootcall9 only) does **not** change bestmove relative F. If it does change, FAIL.
- **A11_EARLY_ONLY:** V_AGE64 (any rootcall but minimum 64 writes) does **not** change bestmove. If it does, FAIL.
- **A11_SOURCE_CONTROL:** BASE and wrong-root-call8 gate are exact final UCI matches with no wrong-call suppression. Any difference FAIL.
- **A11_LOCAL_CONTACT:** V_EXACT physically suppresses at least one actually source-matched TT V reader with full64 writer raw payload match. Missing => NOT_TESTED rather than assign age-specific causal interpretation.

These are **post-hoc exploratory** falsification conditions. Even a PASS demonstrates only that this physical target's earlier and later consumer roles are not interchangeable within one source root; natural TT mediation remains HOLD.