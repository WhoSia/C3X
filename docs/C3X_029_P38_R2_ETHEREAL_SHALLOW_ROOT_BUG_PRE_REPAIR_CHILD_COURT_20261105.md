# C3X 0.29-P38/R2 — Technical Invalidation and Pre-Repair Child-Position Referee Contract

2026-11-05 KST. **Registered BEFORE any repaired Ethereal native results.** This is a technical re-execution of the SAME P37 predictor archive and 8 event families; it is NOT a prospective model experiment or newly independent 16-game sample.

## Fatal R1 referee failure: a green CI is not a real search

R1 Ethereal v12.75 CI [41981821764](https://github.com/WhoSia/C3X/actions/runs/41981821764) completed SUCCESS and original P37 forecast hashes PASS, but source output recorded **actual nodes 2–5 and depth 1** in all 32 requested 96,000/192,000-node calls; **12/16 had no opponent reply because the PV was only one candidate root move**. The apparent `C3X 4/4, PV 3/4` on the remaining four cases is scientifically **INVALID**. Root-restricted `root_moves=[candidate]` apparently malfunctions in this historical Ethereal/UCI integration. The original raw artifact remains preserved unchanged; it must never be used as a legitimate refutation of P37's 11/15 Stockfish PV superiority.

## Single precisely targeted repair, declared before new result

For every **unchanged** case and one of its two **unchanged** Stockfish24k candidate moves:
1. Reconstruct all original 30 source UCI halfmoves on chess.Board, verify source FEN and candidate legality.
2. **Execute candidate itself on that board** with `board.push(candidate)`; now run unmodified Ethereal 12.75 **unrestricted from the resulting child position**, with no `root_moves` / `searchmoves` at all. The engine's first PV move is an opponent reply by construction; verify full PV legality in the post-candidate world. Preserve original source move stack.
3. Native `go nodes 96000` and `go nodes 192000` are run in fresh processes. For a **nonterminal** post-root board REQUIRE observed `info["nodes"] >= 90% * requested` and `depth >= 3`. If not, **TECHNICAL_HOLD**, never score or filter the case. Terminal states are `UNDEFINED` not model errors, and do not waive the gate for other positions.
4. First opponent reply identical at 96k and 192k => `REFERENCE_STABLE`; different => `REFERENCE_UNSTABLE` and excluded ONLY from stable-label score (raw both retained); missing => `UNDEFINED`. The exact original 16 pre-96k P37 predictions remain immutable, with identical event/group denominators and no model tuning or game substitution.
5. Report stable/evaluable count, per-method stable label agreement, paired event-level PV-only vs C3X-only, and a secondary 96k count. These are **cross-engine algorithm preference labels**, NOT chess truth or human strategic-value evidence. An older handcrafted Ethereal12.75 has a different strength, valuation and node accounting from Stockfish16; do not claim equal engine strength or CPU fairness.

If this repair fails native node/legality gating, STOP this branch rather than trusting shallow or missing labels. After valid cross-engine result, return to chess-rule-grounded forecast Q with cost-matched baselines; the C3X 3-ply baseline is **not full NNUE causal C3X**.

## Exact source/commits

Original P37 eight-event manifest SHA256 `77ebaa409e7c2099cc6cce3419c2f55ded295d925ab441dc2d13c16b67c2c361`. Original forecast JSON SHA256 `da395f0eb16e7b294af2056dadd92b579770aa8f1ae288d1d358132685807051`. P38 Ethereal v12.75 release original Git SHA `b55ed96881f163940569145fbcc4e222d7272338`. No source/predictor bytes changed. Existing R1 invalid receipt and independent R2 post-failure repair are different numbered methods; do not overwrite original.

Research OS: Notion meaning, Drive raw data, GitHub user-authored code and tests. GitHub Actions contents:read / artifact-only and never github-actions[bot] writes.
