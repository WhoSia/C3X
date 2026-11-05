# C3X 0.29-P36/R3 — Original March 2026 Eight-Game Engine Screening Precommit

Date 2026-11-05 KST. **Committed before ANY engine score for the 8 selected March records**. Source and case identities already fixed in P36/R2 and uploaded to Drive. This is **EXPLORATORY PRE-OUTCOME**, not a proven new event/source-disjoint confirmatory holdout.

## Source/negative lineage audit

- R1 candidate July 2026 checksum mismatch, no selected games, no engine. Additionally current C3X README reveals an older **M6 July 2026 64-game engine-trial**, so July wasn't a new source even if the checksum matched; keep R1 disqualified and prohibit silent checksum overrides.
- March 2026 official Lichess broadcast file is SHA-valid `1a5ad83fc9f440dcdadde17b11cc81a953f4895aaf8b8588470b3078209dc7fc`, 16,446,491 bytes. **Not first acquired**: existing Research OS/C3X `01_SOURCE_ACCRUAL_RAW` Drive file `1RBSYSPAZXQdHYseDcHvv2k1K4PNK7pFT` was moved on 2026-10-17, original bytes are exactly identical to P36 download. C3X 25.md explicitly recorded no game legality, SHA, or engine checks at time of transfer. Later full prior-use exclusion is NOT established.
- P36/R2 source-only native CI [41957706609](https://github.com/WhoSia/C3X/actions/runs/41957706609) succeeded; first 1,000 unique eligible games in 1,348 scanned original PGNs; eight SHA256-ranked frozen original histories at ply30. Five parser tests PASS; old 0.18 original full-game UCI 16 distinct with zero overlap. **0.28 64 registry comparison still HOLD.**
- Original source+manifest Drive [byte-sealed artifact](https://drive.google.com/file/d/11szqoVSHKTeIaajHjxVgn9MoxVhUDBKY/view), manifest `P36_R2_MARCH_8_GAME_ENGINE_BLIND_MANIFEST.json`, GitHub zipped artifact SHA256 `c2d5a646f62af3a07a3efd3bc642eccfafb5440845c8e843ebb9ef3c4e325b4a`.
- Eight immutable game IDs: `00090c4e53df5b2d`, `00470a57672750d1`, `00846ac66ee43492`, `00f04cd20636fdc2`, `01662a4d51803d33`, `01af9df4f5e8e39f`, `01f4ddb70d4011c6`, `02154be9fa2cf21d`. **4/8 from American Cup Blitz**, therefore never pool naive independent-event confidence across all eight; identify game/event clusters.

## Exactly one original-engine diagnostic court

Use official untouched Stockfish16 Git commit `68e1e9b3811e16cad014b590d7443b9063b3eb52`, default `nn-5af11540bbfe.nnue` network (SHA `5af11540bbfefcb54e38c5dd000cab4b469dfa7599a1d55be5d2722c20a8929b`), Threads1, Hash16, UseNNUE=true, `MultiPV=2`, exactly **24,000 requested nodes per one full joint two-candidate search per board**. Fresh native process per board, complete original history reloaded via UCI sequence (not just a standalone FEN), legal ply30 position and FEN must match manifest.

For ALL eight games, without any post-score replacement, store:
- source identity, original game- and event-ID, root FEN and complete 30-ply UCI prefix and duplicate digests;
- first/second native candidate UCI, side-to-move-relative cp/mate score, PV, search depth, actual consumed nodes, legal opponent first reply per PV when present;
- paired score margin (positive absolute cp for non-mate); gap strata `near <20cp`, `intermediate 20..99cp`, `wide >=100cp`, `mate` separate. These thresholds are design descriptors, NOT a measured instability law.
- chess-law number of immediate legal opponent replies after each candidate (does not imply Q's usefulness).

**Vital:** MultiPV scores are search estimates at finite nodes, not objective move quality; March source acquired earlier and 4 American Cup Blitz games are clustered. If no near pairs occur, report zero: do NOT substitute new cases after inspecting engine output. The historical player continuation is not minimax truth; no C3X explanation model is run or awarded performance from this screening.

## Exact next question, but not scored in R3

R4 must predeclare ONE legal opponent-reply-conditioned outcome `Q` that distinguishes alternative moves and a genuinely game-disjoint future reference, then compare plain Stockfish score+PV, minimal foil-aware JSON and full C3X conditional explanation under matched compute budget and forecast capacity. Prior C3X P33 depth10/depth11 reversal requires horizon sensitivity and abstention. No claim of explanation superiority from R3 candidate screening.

Operating rule: GitHub human WhoSia authors only; read-only Actions for build/compute/artifact, Drive raw archive, Notion scientific interpretation. Do not promote source acquisition, tests, or neural trace into chess claim.
