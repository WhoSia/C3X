# C3X 0.27 — Exposed Game-14 Single-Guard Falsification Contract

Date 2026-10-20. This case and its treated-only capture-pruning event were selected **after** observing the September-16 TT-FIRST outcomes. This is exploratory, not independent prospective confirmation.

## Freeze before the counterfactual result
Use original September-2026 game14 source_game_sha256 0822ec4ddab0339d51a65f3a9d077a1245b2402b111e78a3aa90d2a4d9a83652. Frozen original September16 source-only JSON 9372e0fdce2c8499e8d12f6bef5d1bfaef40a2d5b7160cc48513085567c9098d. Historical StageA private SHA b0eb51ab779609db346c75d65a6a65fd31efc9a648111d042cfec5199a4afde1 and public SHA 4572edd4c0761c3875aed421b08880ff142c21f691fe940c7c6d760dbb397be5 must be reproduced under read-only source patch before TT suppression.

Trial A: original OBS; root bestmove b3a4. Trial B: physically matched TT-FIRST suppression at the already presealed STRICT-else-BROAD reader; bestmove f3f4. A directly instrumented source-exact extra capture-pruning SEE call returned FALSE, and source-level NO_DISCOVERED_ATTACK_CONTINUE branch executed; observed twice under cold duplicates, Actions run 39355044167.

Trial C: same TT-FIRST reader suppression plus **only one matched capture-prune guard continuation bypass**. Require equality of exact source key64, root_call, native move, SEE threshold (taken from observation B); SEE routine itself and its return Boolean unchanged, all other capture guards unchanged, no forced TT change, all original build settings fixed. Duplicate cold sessions. Count explicit EXACT_ONE_EVENT_REENABLED log, require once per executable session, and physical TT reader contact. Mark scientific outcome:
- If final root returns to b3a4: supports candidate guard as causal contributor under this specific joint intervention, but not proof of sole/natural mediator (search-state interaction).
- If root remains f3f4: the guard is insufficient to restore original root selection; refutes this simple mediation candidate.
- If root takes third move: shows strong context-dependent influence, not direct restoration.
- If exact source event absent, cannot match or reproducibility fails: HOLD.
No result may be labeled a blinded validation. Physical contact and changes in nodes are necessary to interpret interventions. Full source log private, public summary deidentified by game index and SHA; no original PGN or modified GPL stockfish binary redistributed.
