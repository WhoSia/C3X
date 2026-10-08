# C3X 0.14 P1 — Official TCEC S29 Source-Disjoint Pawn-Advance Pair Intake Precommit

**Precommitted before consulting any C3X 0.14 engine root scores.**

Independent source: TCEC-Chess/tcecgames, formal S29-final release tag at git commit `3dd69a40b3cf6ccc74144df7411ef4e8e2140286`, exact file `master-archive/TCEC_Season_29_-_Superfinal.pgn`, git blob SHA1 `68141d7a9afad301c237106c3b2a3324cb35b130`, size 5,160,096 bytes at the pinned revision. Official tournament source is not the Lichess broadcast read used in prior P8. However it shares the broad TCEC tournament ecosystem with former P8 TCEC; classify as **game/source-file independent, not external chess-domain ecology independent**.

Eligibility rules *without* engine scoring:
1. Parse each PGN mainline with pinned python-chess chess==1.11.2. Ignore comments/variations for board state. Require standard orthodox chess, valid board and a game with >=18 plies, stable provenance from Event, Round, White, Black, Date.
2. At exactly 18 played plies (White's 10th move), find any WHITE pawn currently on its original rank with BOTH single-step and double-step pawn pushes legal from that SAME square. Choose the lexicographically FIRST such same-pawn pair; do not choose based on Stockfish root scores, whether a candidate is played, or concept birth effects. Reject any game without such a pair.
3. Group by chess opening prefix FEN after 12 plies, and retain only one eligible game per opening group, chosen by smallest SHA256 of canonical tournament game ID. This prevents mirrored opening-book twins from being called independent source groups. The sample is not statistically IID; report coverage and duplicates.
4. Rank the eligible source groups by SHA256 of fixed salt `C3X_014_P1_TCEC_S29_SOURCE_FREEZE_V1` + canonical group id, select exactly 8 if available; if fewer, FAIL and preserve audit, no changing thresholds because of game output.
5. First four groups go to DEVELOPMENT and the other four to SEALED_HOLDOUT. The holdout group hashes and source-id receipts may be written, but no engine evaluation, intervention or concept-outcome labels may be calculated for those four during P1. Do not count moves from the same game or two cold repeats as independent data.
6. For each development game record its group hash, root full six-field FEN, both legal root moves, original game metadata, SAN and source SHA. For holdout only record a salted opaque group hash, with a separate inaccessible manifest stored in the artifact for the later designated validation stage; no algorithm sees their root pair until explicit unseal.
7. P1 intake is **not** a high-level causal test, depth/noise control, strategic mediation result or human explanation benchmark. At this stage label only frozen prospective game-source eligibility; any future search must separately precommit engine options, debt from prior source selection, depth/nodes budgets, TT interventions, independent engine and explanation authority.

First code must enforce file blob SHA before reading PGNs and output separate source/heldout manifests with member SHA-256, TCEC attribution and zero bot git writeback.
