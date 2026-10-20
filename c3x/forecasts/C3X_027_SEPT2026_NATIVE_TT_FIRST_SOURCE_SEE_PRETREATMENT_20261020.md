# C3X 0.27 — September-2026 TT-FIRST Prospective Source-Event Experiment Preseal
Date: 2026-10-20 KST. Execution order: new source-only freeze -> untreated native Stage A -> THIS HUMAN-WRITTEN GIT PRESEAL -> FIRST TT suppression.

## Immutable Stage A custody
New independent 16 Lichess September2026 broadcast games source-only: SHA256 `9372e0fdce2c8499e8d12f6bef5d1bfaef40a2d5b7160cc48513085567c9098d`, successful source freeze run 39348434657. Full untreated Stockfish16 source-discovery stage A: Actions run 39351313113 SUCCESS, public forecast SHA256 `4572edd4c0761c3875aed421b08880ff142c21f691fe940c7c6d760dbb397be5`, private StageA SHA256 `b0eb51ab779609db346c75d65a6a65fd31efc9a648111d042cfec5199a4afde1`; artifact c3x027-sept-stageA-before-native-TT-treatment from that original run. Original pinned source: Stockfish16 68e1e9b3811e16cad014b590d7443b9063b3eb52, patched with original 0.23 TT/SEE source tracing. Stage A 16 source games, 7 O/F root differences, 62/64 physically eligible game-order-rule source cells, no source TT reader suppressions and no SEE boolean actuation.

## Frozen treatment policy, untouched by outcomes
- Analyze ALL 16 new games as primary denominator; source noneligibility is HOLD, not a zero effect or zero-contact.
- Only O root candidate order. Select first eligible source policy in fixed order STRICT then BROAD. Never select after looking at treated outcomes.
- Use pre-existing physical TT reader FIRST suppression (`mode="V"`, existing `first_pair` SHA-registered target tuple, `mask_filters(RULES[role],pair,"FIRST")`) and keep SEE Booleans passive. No engine source patch changes between untreated and intervention runs.
- Rebuild the exact historical Stockfish source overlays in GitHub Actions using original native code. Recompute Stage A in the same new runner to recover private physical source keys, require byte-identical private SHA and public forecast SHA to the above two immutable results **before any TT intervention**.
- For each eligible original game, compare duplicate cold original OBS and duplicate cold V under identical single-thread, cold hash, root world and clocks. A mismatch or drift is FAIL rather than silently dropping the game.
- Require actual matched physical TT slot/key/epoch/root_call and writer-reader lineage before calling a treatment contact.
- Record source-chronological native TT use, actual physical suppressed reader, matching SEE identities after the source event (first32 visibility and censor flag), original/treatment final root moves, root choice flip. Natural TT→SEE→root mediation requires additional consumer/parent-chain proof, and remains HOLD even if chronology matches.
- Per-game baseline exact O bestmoves are frozen in `C3X027_SEPT_PRE_TT_FORECAST.json`. The 7/16 O-versus-F contrast is a pre-treatment observation, not a prediction of 7 intervention flips.
- Public result may include aggregate status counts and deidentified game indices, hashes and root UCI; never publish private physical TT event keys, unredacted original PGN, player details or modified GPL engine binary.

## Falsification gates
(a) Stage A SHA mismatch, (b) original bestmove vs preregistered O literal changes, (c) no physical source block but claimed contact, (d) observed native SEE original!=delivered or injected SEE bool, (e) chronology match only from pre-event or censored path asserted as global result, (f) source-only game SHA overlap, (g) source intervention without a cold duplicate all prohibit causal promotion. SEE event presence/absence is an observed bounded prefix, never global under cap.
