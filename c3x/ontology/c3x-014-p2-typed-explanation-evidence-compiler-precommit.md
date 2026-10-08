# C3X 0.14 P2 — Typed Explanation Evidence Compiler and Falsification Contract

An actual chess reasoning assistant must be able to distinguish **UCI numerical observation**, **native implementation intervention**, and **board-domain human-understandable causation**. The first two are not certificates of the third. This court is created after the P2 native test precommit, **before reading its main response**.

## Source and authenticity
Input: `P2_REAL_SIXTEEN_GAMES_TT_SCORE_CHOICE_PANEL.json` from P2 pinned scientific workflow, SHA256 explicitly supplied by final custody auditor, must match byte-for-byte. Require panel schema and all shams/cold controls PASS, positive native compiler source provenance pinned, P1 four-game heldout never opened. Reject missing or mismatching group IDs/roots/root pairs or malformed score-types. No narrative text may ever be generated without passing source integrity.

## Typed claim rights
- `LEGAL_BOARD`: check 6-field FEN and both candidate UCI moves using python-chess; no strategical advantage claim.
- `UCI_SCORE_OBSERVED`: score values within *same* SF16 version/white perspective, depth, pair and named arm. For true cp numerical differences, require both MultiPV entries `cp`, no upper/lower bound flag, both root moves legal and source integrity PASS. Not chess truth.
- `TT_PATH_RESPONSE`: requires native `main_blocked`/`q_blocked` strictly positive for specified intervention, sham exact, match engine binaries and restarts. May assert change **on that patched binary/limited fixed depth**. Cannot infer original cause of pawn concept or one persistent TT entry when entire cutoff family was disabled.
- `CHESS_CONCEPT_CAUSAL`: **unsupported/never available from P2**; a chess causal explanation requires an independently tested structural board manipulation and competing tactics account.
- `HUMAN_LEARNING_BENEFIT`: unsupported, requires blinded reader experiment.

## Falsification matrix
Exact SHA mismatch, source provenance mismatch, wrong/broken FEN, illegal candidate move, incomplete rank coverage, swapped score perspective or mate/cp, bound-reported cp, missing native event telemetry, native mode misuse, and root rank corruption must not be promoted to a positive human causal sentence. Even if a native score changes by hundreds of cp, the label is at most `TT_PATH_RESPONSE`. Every user-facing sentence is template constrained with an inline explicit conditional limitation.

## Product experiment
The compiler emits exactly one full evidence ledger per valid game-depth candidate panel. Export a compact MD report and machine JSON. Include a small internal mutation test suite on a copied frozen panel to require that tampering changes the verdict to REFUSED. Tested code and complete input panel retained in immutable GitHub Actions artifact. Not a synthetic chess outcome: compiler must consume the **actual preselected P2 engine measurements**.
